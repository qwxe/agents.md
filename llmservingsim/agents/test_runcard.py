#!/usr/bin/env python3
"""Tests for agents/runcard.py (run cards: plan + fingerprint + prediction + controls).

Run: python3 -m unittest agents/test_runcard.py   (stdlib only, well under 2 s)

Catalog (behaviour -> test), one test per behaviour:
- new writes a skeleton with every interface-3 field; refuses to overwrite     -> TestNew
- check: each required pre-launch field is enforced                          -> TestCheck.test_required_fields
- check: a complete card passes                                               -> TestCheck.test_complete_card_passes
- check: dirty tree refused for confirmatory, allowed for exploratory         -> TestCheck.test_dirty_*
- check: answerable retrodiction refuses launch                               -> TestCheck.test_answerable_fails
- fingerprint (common): HEAD, dirty (tracked only), md5, env incl. unset=null -> TestFingerprint.test_common
- fingerprint --arm fills arms[<arm>]                                         -> TestFingerprint.test_arm
- score: every prediction classified; miss -> raw_read false; --raw-read      -> TestScore
- check --post: score present, raw_read after a miss, controls per claim kind -> TestPost
- compare: arm vars ignored, everything else refused, per-arm env/inputs      -> TestCompare
- fingerprint --flags: argv tokens verbatim, order kept, common and per arm   -> TestFingerprint.test_flags
- compare: flags compared in order; --arm-flags drops a flag and its value    -> TestCompareFlags
- bad file / bad JSON -> exit 2                                               -> TestErrors
- verifier round 1 (2026-10-14): score completeness at --post, fingerprint
  keys and types, absent-vs-literal env, no tracebacks                        -> TestReview1
- fingerprint of a non-git tree: tree_kind dir, tree_hash, --source-commit,
  --hash-exclude; check rules for dir trees                                   -> TestDirTree
- set: control results, runs, seeds without hand-editing                     -> TestSet
- compare refuses cards without a valid fingerprint                          -> TestCompareNeedsFingerprints
"""
import contextlib
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runcard  # noqa: E402


def run(*argv, env=None):
    """Call runcard.main in-process; return (exit code, stdout+stderr text)."""
    out = io.StringIO()
    old = dict(os.environ)
    try:
        if env is not None:
            os.environ.update(env)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = runcard.main([str(a) for a in argv])
            except SystemExit as e:  # argparse usage errors
                rc = e.code if isinstance(e.code, int) else 2
    finally:
        os.environ.clear()
        os.environ.update(old)
    return rc, out.getvalue()


def complete_card():
    return {
        "block_id": "b1", "created": "2026-10-14", "by": "implementer T1",
        "claim": "claim 1: rate beats LRU", "intent": "first FI rate",
        "label": "confirmatory",
        "retrodiction": {"checked": ["results/x"], "answerable": False, "why_not": "no run at this rate"},
        "predictions": [
            {"metric": "ttft_mean", "arm": "ours", "expect": "lower than lru", "tolerance": "2 sd"},
            {"metric": "hit_rate", "arm": "ours", "expect": "higher", "tolerance": "0.01"},
        ],
        "positive_control": {"how": "KV size x2 must change TTFT", "result": None},
        "arm_active_check": {"how": "log line 'rate pool active'", "result": None},
        "fingerprint": {"tree": "abc123", "dirty": False, "build": "b", "inputs": {"w.jsonl": "d41d"},
                        "env": {"KV_DIV": "1"}, "config": "cfg", "tools": {"py": "3.12"},
                        "flags": ["--scheduling-policy", "fcfs"], "tree_kind": "git", "tree_hash": None,
                        "source_commit": None},
        "runs": [], "seeds": [], "score": None,
    }


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def write(self, card, name="card.json"):
        p = self.d / name
        p.write_text(json.dumps(card))
        return p

    def load(self, p):
        return json.loads(Path(p).read_text())


class TestNew(Base):
    def test_new_skeleton_and_no_overwrite(self):
        p = self.d / "cards" / "b1.json"
        rc, _ = run("new", p, "--block-id", "b1", "--by", "implementer T1")
        self.assertEqual(rc, 0)
        c = self.load(p)
        self.assertEqual(set(c), set(complete_card()))
        self.assertEqual(c["block_id"], "b1")
        self.assertEqual(c["by"], "implementer T1")
        self.assertRegex(c["created"], r"^\d{4}-\d{2}-\d{2}$")
        for k in ("tree", "dirty", "build", "inputs", "env", "config", "tools", "flags", "tree_kind", "tree_hash",
                  "source_commit"):
            self.assertIn(k, c["fingerprint"])
        rc, _ = run("new", p, "--block-id", "b1", "--by", "x")
        self.assertEqual(rc, 2)


class TestCheck(Base):
    def test_complete_card_passes(self):
        rc, out = run("check", self.write(complete_card()))
        self.assertEqual(rc, 0, out)

    def test_required_fields(self):
        breakers = {
            "claim": lambda c: c.update(claim=""),
            "intent": lambda c: c.update(intent=None),
            "label": lambda c: c.update(label="maybe"),
            "retrodiction.checked": lambda c: c["retrodiction"].update(checked=[]),
            "retrodiction.answerable": lambda c: c["retrodiction"].update(answerable=None),
            "retrodiction.why_not": lambda c: c["retrodiction"].update(why_not=""),
            "predictions": lambda c: c.update(predictions=[]),
            "predictions[0].tolerance": lambda c: c["predictions"][0].update(tolerance=""),
            "predictions[1].metric": lambda c: c["predictions"][1].pop("metric"),
            "fingerprint.tree": lambda c: c["fingerprint"].update(tree=None),
            "fingerprint.dirty": lambda c: c["fingerprint"].update(dirty=None),
            "arm_active_check.how": lambda c: c["arm_active_check"].update(how=""),
            "positive_control.how": lambda c: c["positive_control"].update(how=""),
            "fingerprint.tree_kind": lambda c: c["fingerprint"].update(tree_kind="svn"),
        }
        for field, brk in breakers.items():
            with self.subTest(field=field):
                c = complete_card()
                brk(c)
                rc, out = run("check", self.write(c))
                self.assertEqual(rc, 1, out)
                self.assertIn(field, out)

    def test_dirty_confirmatory_fails(self):
        c = complete_card()
        c["fingerprint"]["dirty"] = True
        rc, out = run("check", self.write(c))
        self.assertEqual(rc, 1, out)
        self.assertIn("dirty", out)

    def test_dirty_exploratory_passes(self):
        c = complete_card()
        c["fingerprint"]["dirty"] = True
        c["label"] = "exploratory"
        rc, out = run("check", self.write(c))
        self.assertEqual(rc, 0, out)

    def test_answerable_fails(self):
        c = complete_card()
        c["retrodiction"]["answerable"] = True
        rc, out = run("check", self.write(c))
        self.assertEqual(rc, 1, out)
        self.assertIn("answerable", out)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


class TestFingerprint(Base):
    def setUp(self):
        super().setUp()
        self.repo = self.d / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "a.py").write_text("x = 1\n")
        git(self.repo, "add", "a.py")
        git(self.repo, "commit", "-qm", "init")
        self.head = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()
        self.inp = self.d / "w.jsonl"
        self.inp.write_text("hello\n")  # md5 b1946ac92492d2347c6235b4d2611184
        self.cfg = self.d / "cfg.json"
        self.cfg.write_text("{}")       # md5 99914b932bd37a50b983c5e7c90ae93b
        self.card = self.d / "c.json"
        run("new", self.card, "--block-id", "b", "--by", "t")

    def fp(self, *extra, env=None):
        rc, out = run("fingerprint", self.card, "--tree", self.repo, "--inputs", self.inp,
                      "--env", "RC_SET", "RC_UNSET", "RC_EXPL=7", "--config", self.cfg,
                      "--build", "build-1", "--tool", "py=3.12", *extra,
                      env={"RC_SET": "1", **(env or {})})
        self.assertEqual(rc, 0, out)
        return self.load(self.card)["fingerprint"]

    def test_common(self):
        os.environ.pop("RC_UNSET", None)
        (self.repo / "untracked.txt").write_text("u")
        f = self.fp()
        self.assertEqual(f["tree"], self.head)
        self.assertIs(f["dirty"], False)  # untracked files do not count
        self.assertEqual(f["inputs"], {str(self.inp): "b1946ac92492d2347c6235b4d2611184"})
        self.assertEqual(f["env"], {"RC_SET": "1", "RC_UNSET": None, "RC_EXPL": "7"})
        self.assertEqual(f["config"], "99914b932bd37a50b983c5e7c90ae93b")
        self.assertEqual(f["build"], "build-1")
        self.assertEqual(f["tools"], {"py": "3.12"})
        (self.repo / "a.py").write_text("x = 2\n")  # tracked change -> dirty
        self.assertIs(self.fp()["dirty"], True)

    def test_arm(self):
        rc, out = run("fingerprint", self.card, "--arm", "ours", "--env", "RATE_POLICY", "--inputs", self.inp,
                      env={"RATE_POLICY": "rate"})
        self.assertEqual(rc, 0, out)
        c = self.load(self.card)
        self.assertEqual(c["arms"]["ours"], {"env": {"RATE_POLICY": "rate"},
                                             "inputs": {str(self.inp): "b1946ac92492d2347c6235b4d2611184"},
                                             "flags": []})
        self.assertIsNone(c["fingerprint"]["tree"])  # common part untouched


    def test_flags(self):
        toks = ["--scheduling-policy", "fcfs", "--pcie-bw", "50", "-x", "--a=b"]
        rc, out = run("fingerprint", self.card, "--tree", self.repo, "--env", "KV_DIV", "--flags", *toks)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.load(self.card)["fingerprint"]["flags"], toks)
        self.assertEqual(self.fp()["flags"], [])  # common fingerprint without --flags
        rc, out = run("fingerprint", self.card, "--arm", "ours", "--env", "RATE_POLICY",
                      "--flags", "--lower-tier-eviction", "cost")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.load(self.card)["arms"]["ours"]["flags"], ["--lower-tier-eviction", "cost"])


class TestScore(Base):
    def test_score(self):
        p = self.write(complete_card())
        rc, out = run("score", p, "--hit", "0=12.1")
        self.assertEqual(rc, 1, out)  # prediction 1 not classified
        self.assertIsNone(self.load(p)["score"])
        rc, out = run("score", p, "--hit", "0=12.1", "--miss", "1=0.40", "--verdict", "partly")
        self.assertEqual(rc, 0, out)
        s = self.load(p)["score"]
        self.assertRegex(s["scored"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual([h["index"] for h in s["hits"]], [0])
        self.assertEqual(s["hits"][0]["observed"], "12.1")
        self.assertEqual(s["misses"][0]["metric"], "hit_rate")
        self.assertEqual(s["misses"][0]["observed"], "0.40")
        self.assertIs(s["raw_read"], False)
        self.assertEqual(s["verdict"], "partly")
        rc, out = run("score", p, "--hit", "0=12.1", "--miss", "1=0.40", "--raw-read", "--verdict", "partly")
        self.assertEqual(rc, 0, out)
        self.assertIs(self.load(p)["score"]["raw_read"], True)
        rc, _ = run("score", p, "--hit", "0", "--miss", "0", "1")  # same index twice
        self.assertEqual(rc, 2)
        rc, _ = run("score", p, "--hit", "0", "1", "5")  # out of range
        self.assertEqual(rc, 2)


class TestPost(Base):
    def scored(self, miss=False, raw_read=False, pc=True, aa=True):
        c = complete_card()
        c["score"] = {"scored": "2026-10-15", "hits": [{"index": 1}] if miss else [{"index": 0}, {"index": 1}],
                      "misses": [{"index": 0}] if miss else [],
                      "raw_read": raw_read, "verdict": "v"}
        c["positive_control"]["result"] = "detected 30% TTFT change" if pc else None
        c["arm_active_check"]["result"] = "seen 412 lines" if aa else None
        return self.write(c)

    def test_post(self):
        cases = [  # (card kwargs, claim, expected rc)
            (dict(), "null", 0),
            (dict(), None, 0),
            (dict(miss=True), "difference", 1),
            (dict(miss=True, raw_read=True), "difference", 0),
            (dict(pc=False), None, 1),          # default claim is null
            (dict(pc=False), "arm-lost", 1),
            (dict(pc=False), "difference", 0),
            (dict(aa=False), "difference", 1),
            (dict(aa=False), "arm-lost", 1),
        ]
        for kw, claim, want in cases:
            with self.subTest(kw=kw, claim=claim):
                args = ["check", "--post", self.scored(**kw)] + (["--claim", claim] if claim else [])
                rc, out = run(*args)
                self.assertEqual(rc, want, out)
        c = complete_card()  # no score at all
        rc, out = run("check", "--post", self.write(c), "--claim", "difference")
        self.assertEqual(rc, 1, out)
        self.assertIn("score", out)


class TestCompare(Base):
    def pair(self, mod_b):
        a = complete_card()
        a["fingerprint"]["env"] = {"KV_DIV": "1", "RATE_POLICY": "rate"}
        a["arms"] = {"lru": {"env": {"RATE_POLICY": None, "RWL_HW": "H100"}, "inputs": {}},
                     "ours": {"env": {"RATE_POLICY": "rate", "RWL_HW": "H100"}, "inputs": {"p.json": "m1"}}}
        b = copy.deepcopy(a)
        mod_b(b)
        return self.write(a, "a.json"), self.write(b, "b.json")

    def cmp(self, mod_b):
        rc, out = run("compare", *self.pair(mod_b), "--arm-vars", "RATE_POLICY")
        return rc, out

    def test_identical_and_arm_vars_pass(self):
        self.assertEqual(self.cmp(lambda b: None)[0], 0)
        self.assertEqual(self.cmp(lambda b: b["fingerprint"]["env"].update(RATE_POLICY="lru"))[0], 0)
        self.assertEqual(self.cmp(lambda b: b["arms"]["ours"]["env"].update(RATE_POLICY="x"))[0], 0)
        self.assertEqual(self.cmp(lambda b: b.update(runs=["r9"], claim="other"))[0], 0)

    def test_differences_refused(self):
        mods = {
            "tree": lambda b: b["fingerprint"].update(tree="def"),
            "dirty": lambda b: b["fingerprint"].update(dirty=True),
            "KV_DIV": lambda b: b["fingerprint"]["env"].update(KV_DIV=None),
            "w.jsonl": lambda b: b["fingerprint"]["inputs"].update({"w.jsonl": "zzz"}),
            "config": lambda b: b["fingerprint"].update(config="other"),
            "tools": lambda b: b["fingerprint"]["tools"].update(py="3.11"),
            "build": lambda b: b["fingerprint"].update(build="b2"),
            "RWL_HW": lambda b: b["arms"]["ours"]["env"].update(RWL_HW="A100"),
            "p.json": lambda b: b["arms"]["ours"]["inputs"].update({"p.json": "m2"}),
            "belady": lambda b: b["arms"].update(belady={"env": {}, "inputs": {}}),
        }
        for name, mod in mods.items():
            with self.subTest(diff=name):
                rc, out = self.cmp(mod)
                self.assertEqual(rc, 1, out)
                self.assertIn(name, out)

    def test_arms_disagree_within_card(self):
        a = complete_card()
        a["arms"] = {"lru": {"env": {"RATE_POLICY": None, "KV_DIV": "1"}, "inputs": {}},
                     "ours": {"env": {"RATE_POLICY": "rate", "KV_DIV": "10"}, "inputs": {}}}
        p = self.write(a)
        rc, out = run("compare", p, p, "--arm-vars", "RATE_POLICY")
        self.assertEqual(rc, 1, out)
        self.assertIn("KV_DIV", out)
        rc, out = run("compare", p, p, "--arm-vars", "RATE_POLICY", "KV_DIV")
        self.assertEqual(rc, 0, out)


class TestCompareFlags(Base):
    def pair(self, flags_a, flags_b, arm_flags_a=None, arm_flags_b=None):
        a, b = complete_card(), complete_card()
        a["fingerprint"]["flags"], b["fingerprint"]["flags"] = flags_a, flags_b
        if arm_flags_a is not None:
            a["arms"] = {n: {"env": {}, "inputs": {}, "flags": f} for n, f in arm_flags_a.items()}
            b["arms"] = {n: {"env": {}, "inputs": {}, "flags": f} for n, f in arm_flags_b.items()}
        return self.write(a, "a.json"), self.write(b, "b.json")

    def cmp(self, *pair_args, arm_flags=("--partial-eviction-decay", "--lower-tier-eviction")):
        return run("compare", *self.pair(*pair_args), "--arm-flags", *arm_flags)

    def test_common_flags(self):
        base = ["--scheduling-policy", "fcfs", "--partial-eviction-decay", "12.5", "--pcie-bw", "50"]
        cases = [  # (flags of B, expected rc)
            (list(base), 0),
            (["--scheduling-policy", "fcfs", "--partial-eviction-decay", "99", "--pcie-bw", "50"], 0),
            (["--scheduling-policy", "fcfs", "--partial-eviction-decay=99", "--pcie-bw", "50"], 0),
            (["--scheduling-policy", "fcfs", "--pcie-bw", "50"], 0),          # arm flag absent
            (["--scheduling-policy", "fcfs", "--partial-eviction-decay", "12.5", "--pcie-bw", "25"], 1),
            (["--pcie-bw", "50", "--partial-eviction-decay", "12.5", "--scheduling-policy", "fcfs"], 1),  # order
            (base + ["--extra"], 1),
        ]
        for flags_b, want in cases:
            with self.subTest(flags_b=flags_b):
                rc, out = self.cmp(base, flags_b)
                self.assertEqual(rc, want, out)
                if want:
                    self.assertIn("flags", out)
        rc, out = run("compare", *self.pair(base, cases[1][0]))  # no --arm-flags: every token counts
        self.assertEqual(rc, 1, out)

    def test_arm_flags(self):
        arms = {"lru": ["--lower-tier-eviction", "lru", "--pcie-bw", "50"],
                "ours": ["--lower-tier-eviction", "cost", "--pcie-bw", "50"]}
        self.assertEqual(self.cmp([], [], arms, arms)[0], 0)  # arms differ only in arm flags
        other = dict(arms, ours=["--lower-tier-eviction", "cost", "--pcie-bw", "25"])
        rc, out = self.cmp([], [], arms, other)
        self.assertEqual(rc, 1, out)
        self.assertIn("arms.ours.flags", out)
        rc, out = self.cmp([], [], other, other)  # inside one card, non-arm flag disagrees
        self.assertEqual(rc, 1, out)
        self.assertIn("--pcie-bw", out)


class TestErrors(Base):
    def test_bad_input(self):
        self.assertEqual(run("check", self.d / "missing.json")[0], 2)
        bad = self.d / "bad.json"
        bad.write_text("{not json")
        self.assertEqual(run("check", bad)[0], 2)
        self.assertEqual(run("bogus")[0], 2)


class TestReview1(Base):
    """Findings of the Codex verifier, round 1 (2026-10-14)."""

    def post_card(self, score):
        c = complete_card()
        c["positive_control"]["result"] = "seen"
        c["arm_active_check"]["result"] = "seen"
        c["score"] = score
        return c

    def test_post_requires_every_prediction_scored_once(self):
        def sc(hits, misses=()):
            return {"scored": "2026-10-15", "hits": [{"index": i} for i in hits],
                    "misses": [{"index": i} for i in misses], "raw_read": True, "verdict": "v"}
        cases = {"empty score": {}, "one of two": sc([0]), "twice": sc([0, 1], [1]),
                 "out of range": sc([0, 1, 2]), "bad entry": dict(sc([0]), misses=["x"])}
        for name, score in cases.items():
            with self.subTest(case=name):
                rc, out = run("check", "--post", self.write(self.post_card(score)))
                self.assertEqual(rc, 1, out)
                self.assertIn("score", out)
        c = self.post_card(sc([0, 1]))
        self.assertEqual(run("check", "--post", self.write(c))[0], 0)
        c["predictions"].append({"metric": "m", "arm": "a", "expect": "e", "tolerance": "t"})  # added later
        rc, out = run("check", "--post", self.write(c))
        self.assertEqual(rc, 1, out)

    def test_fingerprint_keys_and_types(self):
        bad = {"build": 3, "inputs": None, "env": [], "config": {}, "tools": "x", "flags": "--a"}
        for key in ("build", "inputs", "env", "config", "tools", "flags"):
            for mode in ("missing", "wrong type"):
                with self.subTest(key=key, mode=mode):
                    c = complete_card()
                    if mode == "missing":
                        del c["fingerprint"][key]
                    else:
                        c["fingerprint"][key] = bad[key]
                    rc, out = run("check", self.write(c))
                    self.assertEqual(rc, 1, out)
                    self.assertIn(f"fingerprint.{key}", out)
        c = complete_card()  # null build/config and empty containers are allowed
        c["fingerprint"].update(build=None, config=None, inputs={}, env={}, tools={}, flags=[])
        rc, out = run("check", self.write(c))
        self.assertEqual(rc, 0, out)

    def test_absent_env_differs_from_literal(self):
        a, b = complete_card(), complete_card()
        a["fingerprint"]["env"] = {"X": "<absent>"}
        b["fingerprint"]["env"] = {}
        rc, out = run("compare", self.write(a, "a.json"), self.write(b, "b.json"))
        self.assertEqual(rc, 1, out)
        self.assertIn("fingerprint.env.X", out)

    def test_no_tracebacks(self):
        rc, out = run("new", "/dev/null/card.json", "--block-id", "b", "--by", "t")
        self.assertEqual(rc, 2, out)
        self.assertNotIn("Traceback", out)
        self.assertEqual(len(out.strip().splitlines()), 1, out)
        breakers = {
            "retrodiction": lambda c: c.update(retrodiction="none"),
            "predictions": lambda c: c.update(predictions=["x"]),
            "fingerprint": lambda c: c.update(fingerprint="abc"),
            "arm_active_check": lambda c: c.update(arm_active_check=[]),
            "positive_control": lambda c: c.update(positive_control=1),
            "score": lambda c: c.update(score="done"),
        }
        for field, brk in breakers.items():
            c = complete_card()
            brk(c)
            p = self.write(c)
            for args in (("check", p), ("check", "--post", p), ("compare", p, p), ("score", p, "--hit", "0")):
                with self.subTest(field=field, args=args[:2]):
                    rc, out = run(*args)
                    self.assertIn(rc, (0, 1, 2), out)
                    self.assertNotIn("Traceback", out)
                    if args[0] == "check":
                        self.assertEqual(rc, 1, out)
                        self.assertIn(field, out)
        c = complete_card()
        c["arms"] = {"ours": "x"}
        p = self.write(c)
        rc, out = run("compare", p, p)
        self.assertEqual(rc, 1, out)
        self.assertIn("arms.ours", out)


class TestDirTree(Base):
    """A measurement tree that is a plain directory inside a git repository (reader test, item 23)."""

    def setUp(self):
        super().setUp()
        self.repo = self.d / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "top.py").write_text("t\n")
        git(self.repo, "add", "top.py")
        git(self.repo, "commit", "-qm", "init")
        self.tree = self.repo / "wt" / "ab"
        (self.tree / "serving").mkdir(parents=True)
        (self.tree / "serving" / "a.py").write_text("a = 1\n")
        (self.tree / "outputs").mkdir()
        (self.tree / "outputs" / "run.csv").write_text("x\n")
        (self.tree / "serving" / "__pycache__").mkdir()
        (self.tree / "serving" / "__pycache__" / "a.pyc").write_text("c")
        (self.tree / "sim.log").write_text("l")
        (self.tree / "data.bin").write_text("d")
        self.card = self.d / "c.json"
        run("new", self.card, "--block-id", "b", "--by", "t")

    def fp(self, *extra):
        rc, out = run("fingerprint", self.card, "--tree", self.tree, *extra)
        return rc, out, self.load(self.card)["fingerprint"]

    def test_dir_tree_fingerprint(self):
        rc, out, _ = self.fp()
        self.assertEqual(rc, 2, out)  # --source-commit required
        self.assertIn("--source-commit", out)
        rc, out, f = self.fp("--source-commit", "abc123")
        self.assertEqual(rc, 0, out)
        self.assertEqual((f["tree"], f["tree_kind"], f["dirty"], f["source_commit"]), (None, "dir", None, "abc123"))
        self.assertRegex(f["tree_hash"], r"^[0-9a-f]{64}$")
        h0 = f["tree_hash"]
        for junk in ("outputs/run2.csv", "serving/__pycache__/b.pyc", "other.log"):  # default exclusions
            (self.tree / junk).write_text("new")
            self.assertEqual(self.fp("--source-commit", "abc123")[2]["tree_hash"], h0, junk)
        (self.tree / "serving" / "a.py").write_text("a = 2\n")  # a source change
        h1 = self.fp("--source-commit", "abc123")[2]["tree_hash"]
        self.assertNotEqual(h1, h0)
        (self.tree / "data.bin").write_text("changed")
        self.assertNotEqual(self.fp("--source-commit", "abc123")[2]["tree_hash"], h1)
        self.assertEqual(self.fp("--source-commit", "abc123", "--hash-exclude", "*.bin")[2]["tree_hash"],
                         self.fp("--source-commit", "abc123", "--hash-exclude", "data.bin")[2]["tree_hash"])
        self.assertNotEqual(self.fp("--source-commit", "abc123", "--hash-exclude", "*.bin")[2]["tree_hash"],
                            self.fp("--source-commit", "abc123")[2]["tree_hash"])

    def test_git_tree_kind_and_no_source_commit(self):
        rc, out = run("fingerprint", self.card, "--tree", self.repo)
        self.assertEqual(rc, 0, out)
        f = self.load(self.card)["fingerprint"]
        self.assertEqual(f["tree_kind"], "git")
        self.assertIsNone(f["tree_hash"])
        self.assertIsNone(f["source_commit"])
        self.assertRegex(f["tree"], r"^[0-9a-f]{40}$")
        rc, out = run("fingerprint", self.card, "--tree", self.repo, "--source-commit", "abc")
        self.assertEqual(rc, 2, out)

    def test_check_dir_card(self):
        def dir_card(**fp):
            c = complete_card()
            c["fingerprint"].update({"tree": None, "dirty": None, "tree_kind": "dir", "tree_hash": "f" * 64,
                                     "source_commit": "abc123", **fp})
            return c
        self.assertEqual(run("check", self.write(dir_card()))[0], 0)
        for key, val in (("tree_hash", None), ("source_commit", ""), ("dirty", False)):
            for label in ("confirmatory", "exploratory"):
                with self.subTest(key=key, label=label):
                    c = dir_card(**{key: val})
                    c["label"] = label
                    rc, out = run("check", self.write(c))
                    self.assertEqual(rc, 1, out)
                    self.assertIn(f"fingerprint.{key}", out)
        c = complete_card()  # a git card needs tree and dirty
        c["fingerprint"].update(tree=None)
        rc, out = run("check", self.write(c))
        self.assertEqual(rc, 1, out)
        self.assertIn("fingerprint.tree", out)


class TestCompareNeedsFingerprints(Base):
    def test_unfingerprinted_cards_refused(self):
        for name, mod in {"no fingerprint": lambda c: c.pop("fingerprint"),
                          "skeleton fingerprint": lambda c: c["fingerprint"].update(tree=None, dirty=None),
                          "missing key": lambda c: c["fingerprint"].pop("tools")}.items():
            with self.subTest(case=name):
                c = complete_card()
                mod(c)
                p = self.write(c)
                rc, out = run("compare", p, p)
                self.assertEqual(rc, 1, out)
                self.assertIn("fingerprint", out)


class TestSet(Base):
    def test_set(self):
        p = self.write(complete_card())
        rc, out = run("set", p, "--control", "positive", "TTFT moved 30%", "--runs", "r1", "r2", "--seeds", "1")
        self.assertEqual(rc, 0, out)
        rc, out = run("set", p, "--control", "arm-active", "412 lines", "--runs", "r2", "r3", "--seeds", "1", "2")
        self.assertEqual(rc, 0, out)
        c = self.load(p)
        self.assertEqual(c["positive_control"]["result"], "TTFT moved 30%")
        self.assertEqual(c["positive_control"]["how"], "KV size x2 must change TTFT")
        self.assertEqual(c["arm_active_check"]["result"], "412 lines")
        self.assertEqual(c["runs"], ["r1", "r2", "r3"])  # appended in order, no duplicates
        self.assertEqual(c["seeds"], ["1", "2"])
        rc, out = run("set", p, "--control", "negative", "x")
        self.assertEqual(rc, 2, out)
        rc, out = run("set", p)
        self.assertEqual(rc, 2, out)  # nothing to set


if __name__ == "__main__":
    unittest.main()
