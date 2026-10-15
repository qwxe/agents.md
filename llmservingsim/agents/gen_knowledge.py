#!/usr/bin/env python3
"""Generate knowledge/KNOWLEDGE.md, the catalog of the knowledge base, from the entries under knowledge/.

Usage:
  python3 agents/gen_knowledge.py [--today YYYY-MM-DD]      write the catalog (reference date: today by default)
  python3 agents/gen_knowledge.py --check                  exit non-zero when an entry is invalid or the catalog
                                                           is stale; warns when its reference date is > 30 days old
  python3 agents/gen_knowledge.py --category <c>           print one category's table (for briefs)
  --root <dir>                                             repository root (default: this file's parent's parent)

Entry format: the human schema is F-knowledge in agents/FORMATS.md I.24 (the parser below validates it; original
design: notes/design/T20261014-knowledge-runcard.md section 3, interface 1); the writer rules are
agents/INTERFACE.md I.21 and storage/lifecycle routing agents/RECORDS.md I.8. Each entry is `knowledge/<category>/<slug>.md` with a front matter in a small YAML
subset, parsed here by hand (stdlib only): `key: value`, quoted strings, `[a, b]` inline lists, block lists of
`  - item` lines, and whole-line `#` comments.

The catalog records its reference date; --check regenerates with that date, so it does not fail just because
time passed. The Stale table lists entries with status `assumed` updated more than 30 days before that date.
Promotion candidates are counted in distinct task ids, never counting occurrences whose task is `legacy`: an entry
whose occurrences name at least 3 and whose `promote` is not `promoted`, `covered` or `rejected`; and a `type` or
`logic` tag whose occurrences, pooled over every pitfall entry carrying it, name at least 3 (listed when the tag
spans two or more entries; a one-entry tag is the entry row). `covered` means an existing rule already covers the
pitfall (`promoted_to` names it; no user approval needed). The generator never edits entries.
"""
import argparse
import datetime as dt
import difflib
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
CATALOG = "knowledge/KNOWLEDGE.md"
CATEGORIES = ["simulator", "environment", "tools", "workloads", "experiments", "results-state", "anomalies",
              "pitfalls", "agents"]
STATUSES = {"verified", "assumed", "refuted", "superseded"}
PROMOTES = {"none", "candidate", "proposed", "promoted", "covered", "rejected"}
NOT_CANDIDATE = ("promoted", "covered", "rejected")
LEGACY_TASK = "legacy"
REQUIRED = ["id", "title", "category", "status", "updated", "by", "read_when"]
OPTIONAL = ["evidence", "supersedes", "tags"]
PITFALL_REQ = ["type", "logic", "occurrences", "fix", "promote"]
PITFALL_OPT = ["promoted_to"]
ANOMALY_REQ = ["detect", "healthy", "action"]
STALE_DAYS = 30
CANDIDATE_TASKS = 3
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
OCCURRENCE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+\S")
SECTION_ID = re.compile(r"^(0|I|II)\.\d+$")
REF_LINE = re.compile(r"^Reference date: (\d{4}-\d{2}-\d{2})$", re.M)


# ---------------------------------------------------------------- parsing

def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1].replace('\\"', '"') if v[0] == '"' else v[1:-1]
    return v


def _value(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    return _scalar(v)


def parse_entry(text):
    """Return (meta, body). Raises ValueError when the front matter is missing or outside the subset."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("no front matter (first line must be ---)")
    meta, key = {}, None
    for i in range(1, len(lines)):
        raw = lines[i].rstrip("\n")
        if raw.strip() == "---":
            return meta, "".join(lines[i + 1:])
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s+-\s?(.*)$", raw)
        if m and key is not None and isinstance(meta.get(key), list):
            meta[key].append(_scalar(m.group(1)))
            continue
        m = re.match(r"^([a-z_]+):(?:\s(.*))?$", raw)
        if not m:
            raise ValueError(f"front matter line {i + 1} is not `key: value`: {raw!r}")
        key, val = m.group(1), (m.group(2) or "").strip()
        meta[key] = [] if val == "" else _value(val)
    raise ValueError("front matter not terminated by ---")


def load_entries(root):
    """Return a list of (relpath under knowledge/, meta or None, body or error string), sorted by path."""
    base = Path(root) / "knowledge"
    out = []
    if not base.is_dir():
        return out
    for p in sorted(base.rglob("*.md")):
        rel = p.relative_to(base).as_posix()
        if rel == "KNOWLEDGE.md":
            continue
        try:
            meta, body = parse_entry(p.read_text())
            out.append((rel, meta, body))
        except ValueError as e:
            out.append((rel, None, str(e)))
    return out


# ---------------------------------------------------------------- validation

def _headings(path):
    try:
        return [re.sub(r"^#+\s+", "", ln).strip() for ln in path.read_text().splitlines() if re.match(r"^#+\s", ln)]
    except OSError:
        return None


def _rule_target_exists(root, target):
    """A section id (I.x, II.x, 0.x) heading in AGENTS.md or agents/*.md, or `agents/<FILE>.md#<heading prefix>`."""
    root = Path(root)
    if SECTION_ID.match(target):
        files = [root / "AGENTS.md"] + sorted((root / "agents").glob("*.md"))
        for f in files:
            for h in _headings(f) or []:
                if h == target or h.startswith(target + " "):
                    return True
        return False
    if "#" in target:
        rel, prefix = target.split("#", 1)
        heads = _headings(root / rel)
        return heads is not None and bool(prefix) and any(h.startswith(prefix) for h in heads)
    return False


def _task_ids(meta):
    out = set()
    for o in meta.get("occurrences") or []:
        m = OCCURRENCE.match(o)
        if m and m.group(2) != LEGACY_TASK:
            out.add(m.group(2))
    return out


def validate(root, entries):
    """Return a list of error strings `knowledge/<rel>: <problem>`."""
    errs = []
    ids = {rel[:-3] for rel, meta, _ in entries if meta is not None}
    for rel, meta, body in entries:
        where = f"knowledge/{rel}"
        if meta is None:
            errs.append(f"{where}: {body}")
            continue

        def err(msg):
            errs.append(f"{where}: {msg}")

        cat = meta.get("category")
        allowed = set(REQUIRED + OPTIONAL)
        required = list(REQUIRED)
        if cat == "pitfalls":
            allowed |= set(PITFALL_REQ + PITFALL_OPT)
            required += PITFALL_REQ
        if cat == "anomalies":
            allowed |= set(ANOMALY_REQ)
            required += ANOMALY_REQ
        for k in meta:
            if k not in allowed:
                err(f"field `{k}` is unknown or not allowed for category {cat}")
        for k in required:
            if k == "occurrences":
                continue  # checked with its format below
            if k not in meta or meta[k] in ("", None, []):
                err(f"missing field `{k}`")
        if meta.get("id") and meta["id"] != rel[:-3]:
            err(f"id `{meta['id']}` != path `{rel[:-3]}`")
        if cat and cat not in CATEGORIES:
            err(f"unknown category `{cat}`")
        if cat and rel.split("/", 1)[0] != cat:
            err(f"category `{cat}` does not match the folder `{rel.split('/', 1)[0]}`")
        if "/" not in rel:
            err("entries live in knowledge/<category>/")
        st = meta.get("status")
        if st and st not in STATUSES:
            err(f"status `{st}` not in {sorted(STATUSES)}")
        ev = meta.get("evidence")
        if "evidence" in meta and not isinstance(ev, list):
            err("`evidence` must be a list (block `  - item` lines or `[a, b]`)")
        elif isinstance(ev, list) and any(not isinstance(x, str) or not x.strip() for x in ev):
            err("`evidence` items must be non-empty strings")
        elif st in ("verified", "refuted") and not ev:
            err(f"status {st} needs at least one non-empty `evidence` item")
        up = meta.get("updated")
        if up and (not isinstance(up, str) or not DATE.match(up) or not _date_ok(up)):
            err(f"updated `{up}` is not YYYY-MM-DD")
        for k in ("title", "read_when"):
            if isinstance(meta.get(k), list):
                err(f"`{k}` must be one line")
        sup = meta.get("supersedes")
        if sup and sup not in ids:
            err(f"supersedes target `{sup}` does not exist")
        if cat == "pitfalls":
            occ = meta.get("occurrences")
            if not isinstance(occ, list) or not occ:
                err("pitfall needs at least one `occurrences` line")
            else:
                for o in occ:
                    if not OCCURRENCE.match(o):
                        err(f"occurrence `{o}` is not `YYYY-MM-DD <task id> <one line>`")
            pr = meta.get("promote")
            if pr and pr not in PROMOTES:
                err(f"promote `{pr}` not in {sorted(PROMOTES)}")
            pt = meta.get("promoted_to")
            if pr in ("promoted", "covered") and not pt:
                err(f"promote: {pr} needs `promoted_to`")
            if pt and not _rule_target_exists(root, pt):
                err(f"promoted_to target `{pt}` not found (a section id heading, or agents/<FILE>.md#<heading>)")
    return errs


def _date_ok(s):
    try:
        dt.date.fromisoformat(s)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------- catalog

def _cell(s):
    s = " ".join(s) if isinstance(s, list) else str(s or "")
    return s.replace("|", "\\|").replace("\n", " ")


def _table(rows):
    out = ["| id | title | status | updated | read_when |", "|---|---|---|---|---|"]
    for meta in rows:
        out.append(f"| `{meta['id']}` | {_cell(meta.get('title'))} | {_cell(meta.get('status'))} | "
                   f"{_cell(meta.get('updated'))} | {_cell(meta.get('read_when'))} |")
    return out


def _by_category(entries):
    cats = {c: [] for c in CATEGORIES}
    for _, meta, _ in entries:
        if meta is not None and meta.get("category") in cats:
            cats[meta["category"]].append(meta)
    for c in cats:
        cats[c].sort(key=lambda m: m["id"])
    return cats


def category_table(entries, category):
    rows = _by_category(entries)[category]
    return "\n".join([f"## {category} ({len(rows)})", ""] + _table(rows)) + "\n"


def build(entries, today):
    """Return the catalog text for the reference date `today` (YYYY-MM-DD)."""
    ref = dt.date.fromisoformat(today)
    cats = _by_category(entries)
    n = sum(len(v) for v in cats.values())
    out = [
        "# KNOWLEDGE.md — catalog of the knowledge base",
        "",
        "<!-- Generated by agents/gen_knowledge.py from knowledge/<category>/<slug>.md. Do not edit by hand. -->",
        "",
        f"Reference date: {today}",
        "",
        "Facts that agents need and that are not rules: the simulator, the environment, tools, workloads, "
        "experiments, the verification state of results, anomalies to detect, pitfalls met, agent tooling. "
        "Rules stay in the rule files and point here.",
        "",
        "- **Read**: the categories your brief names, then the entries whose `read_when` matches your task "
        "(`python3 agents/gen_knowledge.py --category <c>` prints one table). Status `assumed` is unchecked; "
        "`refuted` and `superseded` entries say what replaced them.",
        "- **Add or update**: any agent; the writer rules are `agents/INTERFACE.md` I.21 and the entry format is "
        "the docstring of `agents/gen_knowledge.py`. Search for the same `type`/`logic` before adding a pitfall; "
        "then regenerate this file and check with `--check`.",
        "",
        f"{n} entries. Categories: " + ", ".join(f"{c} ({len(cats[c])})" for c in CATEGORIES) + ".",
        "",
    ]
    for c in CATEGORIES:
        out += [f"## {c} ({len(cats[c])})", ""] + _table(cats[c]) + [""]
    rows = []
    for meta in cats["pitfalls"]:
        tasks = _task_ids(meta)
        if len(tasks) >= CANDIDATE_TASKS and meta.get("promote") not in NOT_CANDIDATE:
            rows.append(("entry", f"`{meta['id']}`", len(tasks), f"`{meta['id']}` ({_cell(meta.get('promote'))})"))
    for kind in ("type", "logic"):
        tags = {}
        for meta in cats["pitfalls"]:
            tag = meta.get(kind)
            if isinstance(tag, str) and tag:
                ids, tasks = tags.setdefault(tag, ([], set()))
                ids.append(meta)
                tasks |= _task_ids(meta)
        for tag in sorted(tags):
            metas, tasks = tags[tag]
            if len(metas) >= 2 and len(tasks) >= CANDIDATE_TASKS:
                rows.append((kind, _cell(tag), len(tasks),
                             ", ".join(f"`{m['id']}` ({_cell(m.get('promote'))})" for m in metas)))
    out += ["## Promotion candidates", "",
            f"Counted in distinct task ids (occurrences with task `{LEGACY_TASK}` do not count); threshold "
            f"{CANDIDATE_TASKS}. An entry row: one pitfall not yet promoted, covered or rejected. A `type` or "
            "`logic` row: a tag shared by several entries whose occurrences together reach the threshold. The "
            "master proposes the rule change to the user.", "",
            "| kind | candidate | tasks | entries (promote) |", "|---|---|---|---|"]
    for kind, name, n, ents in rows:
        out.append(f"| {kind} | {name} | {n} | {ents} |")
    out += [""]
    stale = []
    for c in CATEGORIES:
        for meta in cats[c]:
            up = meta.get("updated")
            if meta.get("status") == "assumed" and isinstance(up, str) and _date_ok(up) and \
                    (ref - dt.date.fromisoformat(up)).days > STALE_DAYS:
                stale.append(meta)
    out += ["## Stale", "",
            f"Entries with status `assumed` updated more than {STALE_DAYS} days before the reference date: "
            "verify them (status `verified` with evidence) or mark them `refuted`.", "",
            "| id | updated | read_when |", "|---|---|---|"]
    for meta in stale:
        out.append(f"| `{meta['id']}` | {_cell(meta.get('updated'))} | {_cell(meta.get('read_when'))} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--category")
    ap.add_argument("--today", help="reference date YYYY-MM-DD (default: today)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    a = ap.parse_args(argv)
    root = Path(a.root)
    real_today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    entries = load_entries(root)

    if a.category:
        if a.category not in CATEGORIES:
            print(f"unknown category {a.category}; one of {', '.join(CATEGORIES)}", file=sys.stderr)
            return 2
        print(category_table(entries, a.category), end="")
        return 0

    errs = validate(root, entries)
    for e in errs:
        print(e)
    cat_path = root / CATALOG

    if a.check:
        rc = 1 if errs else 0
        if not cat_path.exists():
            print(f"{CATALOG} missing: run python3 agents/gen_knowledge.py")
            return 1
        cur = cat_path.read_text()
        m = REF_LINE.search(cur)
        if not m:
            print(f"{CATALOG} has no `Reference date:` line: regenerate it")
            return 1
        ref = m.group(1)
        want = build(entries, ref)
        if cur != want:
            print(f"{CATALOG} is stale: run python3 agents/gen_knowledge.py")
            sys.stdout.writelines(difflib.unified_diff(cur.splitlines(True), want.splitlines(True),
                                                       CATALOG, "regenerated"))
            rc = 1
        age = (real_today - dt.date.fromisoformat(ref)).days
        if age > STALE_DAYS:
            print(f"warning: {CATALOG} reference date {ref} is {age} days old; regenerate it to refresh the "
                  "Stale table")
        return rc

    if errs:
        print(f"{len(errs)} invalid entr{'y' if len(errs) == 1 else 'ies'}; {CATALOG} not written")
        return 1
    cat_path.parent.mkdir(parents=True, exist_ok=True)
    cat_path.write_text(build(entries, real_today.isoformat()))
    print(f"wrote {CATALOG} ({len(entries)} entries, reference date {real_today.isoformat()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
