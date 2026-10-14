#!/usr/bin/env python3
"""Tests for agents/gen_knowledge.py (stdlib unittest, well under 2 s).

Run: python3 -m unittest agents/test_gen_knowledge.py

Catalog (behaviour -> test):
- front-matter subset parsing (scalars, quotes, inline and block lists, comment lines) -> ParseTest
- each --check error class (missing field, bad enum/date, id != path, unknown category, evidence, supersedes,
  promoted_to both forms, pitfall/anomaly fields, occurrence format, unknown key) -> ValidateTest
- catalog content: sections, promotion candidates, stale, reference date, determinism -> BuildTest
- CLI: generate, --check clean/stale/invalid, --category, old reference date warning -> CliTest
"""
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_knowledge as gk  # noqa: E402

RULES = {
    "AGENTS.md": "# AGENTS.md\n\n## 0.5 How to write these files (2026-10-14)\n\ntext\n",
    "agents/INTERFACE.md": "# INTERFACE\n\n## I.16 Git and safety (2026-10-14)\n\n## Interface pitfalls (2026-10-14)\n",
    "agents/RESEARCH.md": "# RESEARCH\n\n## II.8 Research pitfalls\n",
}


def fact(id_, status="verified", updated="2026-10-14", evidence=('"ls x: ok"',), extra=""):
    cat = id_.split("/")[0]
    ev = "evidence:\n" + "".join(f"  - {e}\n" for e in evidence) if evidence else ""
    return (f"---\nid: {id_}\ntitle: Title of {id_}\ncategory: {cat}\nstatus: {status}\n{ev}"
            f"updated: {updated}\nby: implementer T20261014-kb\nread_when: before touching {id_}\n{extra}---\n"
            f"Body of {id_}.\n")


def pitfall(slug, occ=('"2026-10-14 T1 it happened"',), promote="none", promoted_to=None, extra="",
            typ="stale-path", logic="assumed-default"):
    pt = f"promoted_to: {promoted_to}\n" if promoted_to else ""
    occs = "occurrences:\n" + "".join(f"  - {o}\n" for o in occ) if occ is not None else ""
    return fact(f"pitfalls/{slug}", extra=(f"type: {typ}\nlogic: {logic}\n{occs}fix: do the right thing\n"
                                           f"promote: {promote}\n{pt}{extra}"))


class Repo:
    """A throwaway repository root with rule files and a knowledge tree."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="gk_test_"))
        for rel, text in RULES.items():
            self.write(rel, text)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def entry(self, id_, text):
        return self.write(f"knowledge/{id_}.md", text)

    def errors(self):
        return gk.validate(self.root, gk.load_entries(self.root))

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = gk.main(list(args) + ["--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


class RepoCase(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def assertError(self, needle):
        errs = self.repo.errors()
        self.assertTrue(any(needle in e for e in errs), f"no error containing {needle!r} in {errs}")


class ParseTest(unittest.TestCase):
    def test_subset(self):
        meta, body = gk.parse_entry(
            "---\n# a comment line\nid: a/b\ntitle: \"quoted: with colon\"\ntags: [x, y-z]\nevidence:\n"
            "  - \"first item\"\n  - second item\nempty_list: []\n---\nthe body\n")
        self.assertEqual(meta["id"], "a/b")
        self.assertEqual(meta["title"], "quoted: with colon")
        self.assertEqual(meta["tags"], ["x", "y-z"])
        self.assertEqual(meta["evidence"], ["first item", "second item"])
        self.assertEqual(meta["empty_list"], [])
        self.assertEqual(body, "the body\n")

    def test_no_front_matter(self):
        with self.assertRaises(ValueError):
            gk.parse_entry("no front matter\n")

    def test_unterminated(self):
        with self.assertRaises(ValueError):
            gk.parse_entry("---\nid: a/b\n")

    def test_bad_line(self):
        with self.assertRaises(ValueError):
            gk.parse_entry("---\nthis is not a key\n---\n")


class ValidateTest(RepoCase):
    def test_valid_tree_has_no_errors(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.repo.entry("simulator/b", fact("simulator/b", status="superseded", evidence=(),
                                            extra="supersedes: simulator/a\n"))
        self.repo.entry("pitfalls/p", pitfall("p", promote="promoted", promoted_to="I.16"))
        self.repo.entry("pitfalls/q", pitfall("q", promote="promoted", promoted_to="agents/INTERFACE.md#Interface pitf"))
        self.repo.entry("anomalies/x", fact("anomalies/x", extra="detect: free -m\nhealthy: > 1 GB\naction: see I.16\n"))
        self.assertEqual(self.repo.errors(), [])

    def test_missing_field(self):
        self.repo.entry("simulator/a", fact("simulator/a").replace("read_when: before touching simulator/a\n", ""))
        self.assertError("read_when")

    def test_bad_status_and_date(self):
        self.repo.entry("simulator/a", fact("simulator/a", status="maybe"))
        self.repo.entry("simulator/b", fact("simulator/b", updated="14-10-2026"))
        self.assertError("status")
        self.assertError("updated")

    def test_id_must_equal_path(self):
        self.repo.entry("simulator/a", fact("simulator/other"))
        self.assertError("id")

    def test_unknown_category(self):
        self.repo.entry("gossip/a", fact("gossip/a"))
        self.assertError("category")

    def test_verified_and_refuted_need_evidence(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=()))
        self.repo.entry("simulator/b", fact("simulator/b", status="refuted", evidence=()))
        errs = self.repo.errors()
        self.assertEqual(sum("evidence" in e for e in errs), 2, errs)

    def test_evidence_items_must_be_non_empty(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=('""',)))
        self.repo.entry("simulator/b", fact("simulator/b", status="refuted", evidence=('"ok"', '"  "')))
        errs = self.repo.errors()
        self.assertEqual(sum("evidence" in e for e in errs), 2, errs)

    def test_evidence_inline_empty_string_list(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=()).replace(
            "updated:", 'evidence: [""]\nupdated:'))
        self.assertError("evidence")

    def test_evidence_must_be_a_list(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=()).replace("updated:", 'evidence: "[]"\nupdated:'))
        self.repo.entry("simulator/b", fact("simulator/b", status="assumed", evidence=()).replace(
            "updated:", "evidence: some text\nupdated:"))
        errs = self.repo.errors()
        self.assertTrue(any("simulator/a" in e and "evidence" in e for e in errs), errs)
        self.assertTrue(any("simulator/b" in e and "evidence" in e for e in errs), errs)

    def test_assumed_without_evidence_is_fine(self):
        self.repo.entry("simulator/a", fact("simulator/a", status="assumed", evidence=()))
        self.assertEqual(self.repo.errors(), [])

    def test_supersedes_target_missing(self):
        self.repo.entry("simulator/a", fact("simulator/a", extra="supersedes: simulator/gone\n"))
        self.assertError("supersedes")

    def test_promoted_to_section_id_missing(self):
        self.repo.entry("pitfalls/p", pitfall("p", promote="promoted", promoted_to="I.99"))
        self.assertError("promoted_to")

    def test_promoted_to_file_heading_missing(self):
        self.repo.entry("pitfalls/p", pitfall("p", promote="promoted", promoted_to="agents/INTERFACE.md#No such"))
        self.repo.entry("pitfalls/q", pitfall("q", promote="promoted", promoted_to="agents/NOPE.md#Pitfalls"))
        errs = self.repo.errors()
        self.assertEqual(sum("promoted_to" in e for e in errs), 2, errs)

    def test_promoted_requires_promoted_to(self):
        self.repo.entry("pitfalls/p", pitfall("p", promote="promoted"))
        self.assertError("promoted_to")

    def test_covered_requires_promoted_to(self):
        self.repo.entry("pitfalls/p", pitfall("p", promote="covered"))
        self.assertError("promoted_to")

    def test_pitfall_needs_occurrences(self):
        self.repo.entry("pitfalls/p", pitfall("p", occ=None))
        self.repo.entry("pitfalls/q", pitfall("q", occ=()))
        errs = self.repo.errors()
        self.assertEqual(sum("occurrences" in e for e in errs), 2, errs)

    def test_occurrence_format(self):
        self.repo.entry("pitfalls/p", pitfall("p", occ=('"yesterday something"',)))
        self.assertError("occurrence")

    def test_pitfall_bad_promote(self):
        self.repo.entry("pitfalls/p", pitfall("p", promote="maybe"))
        self.assertError("promote")

    def test_anomaly_fields(self):
        self.repo.entry("anomalies/x", fact("anomalies/x", extra="detect: free -m\n"))
        self.assertError("healthy")

    def test_category_specific_field_elsewhere(self):
        self.repo.entry("simulator/a", fact("simulator/a", extra="fix: something\n"))
        self.assertError("fix")

    def test_unknown_key(self):
        self.repo.entry("simulator/a", fact("simulator/a", extra="colour: blue\n"))
        self.assertError("colour")

    def test_unparsable_entry_is_an_error(self):
        self.repo.write("knowledge/simulator/a.md", "no front matter\n")
        self.assertError("simulator/a.md")


class BuildTest(RepoCase):
    def build(self, today="2026-10-14"):
        return gk.build(gk.load_entries(self.repo.root), today)

    def test_sections_and_rows(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.repo.entry("tools/t", fact("tools/t"))
        text = self.build()
        self.assertIn("Reference date: 2026-10-14", text)
        self.assertIn("agents/INTERFACE.md", text)
        for cat in gk.CATEGORIES:
            self.assertIn(f"## {cat}", text)
        self.assertIn("| `simulator/a` | Title of simulator/a | verified | 2026-10-14 | before touching simulator/a |",
                      text)
        self.assertLess(text.index("`simulator/a`"), text.index("## tools"))

    def test_pipe_in_title_is_escaped(self):
        self.repo.entry("simulator/a", fact("simulator/a").replace("title: Title of simulator/a",
                                                                   "title: a | b"))
        self.assertIn("a \\| b", self.build())

    def test_promotion_candidates_count_distinct_tasks(self):
        three = ('"2026-10-01 T1 x"', '"2026-10-02 T2 x"', '"2026-10-03 T3 x"')
        self.repo.entry("pitfalls/hot", pitfall("hot", occ=three, typ="t-hot", logic="l-hot"))
        self.repo.entry("pitfalls/same", pitfall("same", occ=('"2026-10-01 T1 x"',) * 3, typ="t-same", logic="l-same"))
        self.repo.entry("pitfalls/done", pitfall("done", occ=three, promote="promoted", promoted_to="I.16",
                                                 typ="t-done", logic="l-done"))
        self.repo.entry("pitfalls/no", pitfall("no", occ=three, promote="rejected", typ="t-no", logic="l-no"))
        cand = self.build().split("## Promotion candidates", 1)[1].split("## Stale", 1)[0]
        self.assertIn("`pitfalls/hot`", cand)
        for other in ("same", "done", "no"):
            self.assertNotIn(f"`pitfalls/{other}`", cand)

    def cand(self):
        return self.build().split("## Promotion candidates", 1)[1].split("## Stale", 1)[0]

    def test_legacy_occurrences_do_not_count(self):
        occ = ('"2026-10-01 legacy x"', '"2026-10-02 T1 x"', '"2026-10-03 T2 x"')
        self.repo.entry("pitfalls/old", pitfall("old", occ=occ, typ="t-old", logic="l-old"))
        cand = self.cand()
        self.assertNotIn("`pitfalls/old`", cand)
        self.assertNotIn("t-old", cand)
        self.assertNotIn("l-old", cand)

    def test_type_tag_counts_across_entries(self):
        self.repo.entry("pitfalls/a", pitfall("a", occ=('"2026-10-01 T1 x"', '"2026-10-02 T2 x"'),
                                              typ="silent-zero", logic="l-a"))
        self.repo.entry("pitfalls/b", pitfall("b", occ=('"2026-10-03 T3 x"', '"2026-10-04 legacy x"'),
                                              typ="silent-zero", logic="l-b"))
        rows = [ln for ln in self.cand().splitlines() if "silent-zero" in ln and ln.startswith("|")]
        self.assertEqual(len(rows), 1, self.cand())
        self.assertIn("type", rows[0])
        self.assertIn("`pitfalls/a`", rows[0])
        self.assertIn("`pitfalls/b`", rows[0])
        self.assertIn("| 3 |", rows[0])
        self.assertNotIn("l-a", self.cand())

    def test_logic_tag_counts_across_entries(self):
        self.repo.entry("pitfalls/a", pitfall("a", occ=('"2026-10-01 T1 x"',), typ="t-a", logic="trusted-report"))
        self.repo.entry("pitfalls/b", pitfall("b", occ=('"2026-10-02 T2 x"',), typ="t-b", logic="trusted-report"))
        self.repo.entry("pitfalls/c", pitfall("c", occ=('"2026-10-03 T2 x"',), typ="t-c", logic="trusted-report"))
        self.assertNotIn("trusted-report", self.cand())  # two distinct tasks only
        self.repo.entry("pitfalls/d", pitfall("d", occ=('"2026-10-04 T3 x"',), typ="t-d", logic="trusted-report",
                                              promote="promoted", promoted_to="I.16"))
        rows = [ln for ln in self.cand().splitlines() if "trusted-report" in ln and ln.startswith("|")]
        self.assertEqual(len(rows), 1, self.cand())
        self.assertIn("logic", rows[0])
        for e in "abcd":
            self.assertIn(f"`pitfalls/{e}`", rows[0])

    def test_covered_entry_is_not_a_candidate(self):
        three = ('"2026-10-01 T1 x"', '"2026-10-02 T2 x"', '"2026-10-03 T3 x"')
        self.repo.entry("pitfalls/cov", pitfall("cov", occ=three, promote="covered", promoted_to="I.16",
                                                typ="t-cov", logic="l-cov"))
        self.assertEqual(self.repo.errors(), [])
        self.assertFalse([ln for ln in self.cand().splitlines() if ln.startswith("| entry | `pitfalls/cov`")])

    def test_stale_uses_reference_date(self):
        self.repo.entry("simulator/old", fact("simulator/old", status="assumed", evidence=(), updated="2026-09-01"))
        self.repo.entry("simulator/new", fact("simulator/new", status="assumed", evidence=(), updated="2026-10-01"))
        self.repo.entry("simulator/ver", fact("simulator/ver", updated="2026-01-01"))
        stale = self.build("2026-10-14").split("## Stale", 1)[1]
        self.assertIn("`simulator/old`", stale)
        self.assertNotIn("`simulator/new`", stale)
        self.assertNotIn("`simulator/ver`", stale)
        self.assertNotIn("`simulator/old`", self.build("2026-09-20").split("## Stale", 1)[1])

    def test_deterministic(self):
        self.repo.entry("simulator/b", fact("simulator/b"))
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.assertEqual(self.build(), self.build())
        self.assertLess(self.build().index("`simulator/a`"), self.build().index("`simulator/b`"))


class CliTest(RepoCase):
    def test_generate_then_check(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        rc, _, _ = self.repo.cli("--today", "2026-10-14")
        self.assertEqual(rc, 0)
        self.assertTrue((self.repo.root / "knowledge/KNOWLEDGE.md").exists())
        rc, out, err = self.repo.cli("--check", "--today", "2026-10-20")
        self.assertEqual(rc, 0, out + err)

    def test_check_uses_catalog_reference_date(self):
        self.repo.entry("simulator/old", fact("simulator/old", status="assumed", evidence=(), updated="2026-09-01"))
        self.repo.cli("--today", "2026-09-20")
        rc, out, err = self.repo.cli("--check", "--today", "2026-10-14")
        self.assertEqual(rc, 0, out + err)

    def test_check_warns_on_old_reference_date(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.repo.cli("--today", "2026-08-01")
        rc, out, err = self.repo.cli("--check", "--today", "2026-10-14")
        self.assertEqual(rc, 0)
        self.assertIn("warning", (out + err).lower())

    def test_check_fails_when_catalog_stale(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.repo.cli("--today", "2026-10-14")
        self.repo.entry("simulator/b", fact("simulator/b"))
        rc, _, _ = self.repo.cli("--check")
        self.assertNotEqual(rc, 0)

    def test_check_fails_when_catalog_missing(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        rc, _, _ = self.repo.cli("--check")
        self.assertNotEqual(rc, 0)

    def test_check_fails_on_invalid_entry(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=()))
        self.repo.cli("--today", "2026-10-14")
        rc, out, err = self.repo.cli("--check")
        self.assertNotEqual(rc, 0)
        self.assertIn("simulator/a", out + err)

    def test_generate_refuses_invalid_entries(self):
        self.repo.entry("simulator/a", fact("simulator/a", evidence=()))
        rc, _, _ = self.repo.cli("--today", "2026-10-14")
        self.assertNotEqual(rc, 0)

    def test_category_prints_only_that_table(self):
        self.repo.entry("simulator/a", fact("simulator/a"))
        self.repo.entry("tools/t", fact("tools/t"))
        rc, out, _ = self.repo.cli("--category", "simulator")
        self.assertEqual(rc, 0)
        self.assertIn("`simulator/a`", out)
        self.assertNotIn("`tools/t`", out)

    def test_unknown_category_option(self):
        rc, _, _ = self.repo.cli("--category", "gossip")
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
