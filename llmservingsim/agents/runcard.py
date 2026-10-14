#!/usr/bin/env python3
"""Run cards: one JSON card per run block (a set of runs launched for one purpose).

A card merges the experiment plan's claim and expected results with retrodiction, predictions scored
afterwards, a fingerprint whose mismatch refuses a comparison, and the positive-control and arm-active checks
that must be filled before a null or "arm lost" claim. Design: notes/design/T20261014-knowledge-runcard.md,
interface 3, plus the per-arm block "arms" (master, 2026-10-14). Stdlib only.

Usage:
  runcard.py new <card> --block-id ID --by "ROLE TASK"
  runcard.py fingerprint <card> --tree DIR [--inputs P...] [--env VAR|VAR=VAL...] [--build S] [--config PATH]
                                [--tool NAME=VALUE...] [--source-commit SHA] [--hash-exclude GLOB...]
                                [--flags TOKEN...]
  runcard.py fingerprint <card> --arm NAME [--env VAR|VAR=VAL...] [--inputs P...] [--flags TOKEN...]
  runcard.py set <card> [--control positive|arm-active RESULT]... [--runs ID...] [--seeds S...]
  runcard.py check <card>                                   # before launch
  runcard.py check --post <card> [--claim null|arm-lost|difference]   # before a claim; default null
  runcard.py score <card> [--hit IDX[=OBS]...] [--miss IDX[=OBS]...] [--raw-read] [--verdict TEXT]
  runcard.py compare <cardA> <cardB> [--arm-vars VAR...] [--arm-flags PREFIX...]

Exit codes: 0 pass, 1 check failed (each failure printed on its own line), 2 usage or file error.
Everything is printed to stdout.

Field rules:
- `--tree` that is its own git toplevel: tree_kind "git", tree = HEAD, dirty = tracked changes, tree_hash and
  source_commit null. Any other directory (e.g. a measurement tree copied inside another repository, where
  `git -C` would silently answer for the enclosing repository): tree_kind "dir", tree null, dirty null,
  source_commit = the required `--source-commit` (the commit the tree was built from), tree_hash = sha256 over
  the sorted (relative path, md5) of every regular file and (relative path, link target) of every symlink
  (symlinks are not followed), excluding paths with a component matching DEFAULT_EXCLUDE (.git, __pycache__,
  *.pyc, *.log, outputs, log, tmp__*) or any `--hash-exclude` glob (matched against the relative path and
  each component).
- fingerprint.dirty is `git status --porcelain --untracked-files=no` non-empty; untracked files do not count
  (inputs that matter are hashed under `inputs`). `check` refuses a dirty tree on a confirmatory card.
- An env variable that is not set is recorded as null, distinct from an empty string (a variable whose unset
  default differs from any explicit value must stay visible).
- `flags` is the run's command-line argv tokens, verbatim and in order. `--flags` must be the last option: every
  token after it is taken as given (so tokens starting with "-" need no quoting). `--arm-flags` likewise
  must be the last option of `compare`.
- `arms` maps an arm name to {"env": {...}, "inputs": {...}, "flags": [...]}: what differs per arm in the block.
- `compare` refuses when the common fingerprints differ in anything except the env vars named by --arm-vars and
  the flags named by --arm-flags, when the arm sets differ, when one arm's env, flags (minus the arm ones) or
  inputs differ between the cards, or when the arms inside one card disagree on a non-arm env var or flag.
  Flags are compared as ordered lists after dropping every token that starts with an --arm-flags prefix, plus
  the token after it when the flag has no "=VALUE" and the next token is a value (does not start with "-",
  or is a negative number).
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

LABELS = ("confirmatory", "exploratory")
TREE_KINDS = ("git", "dir")
CONTROLS = {"positive": "positive_control", "arm-active": "arm_active_check"}
DEFAULT_EXCLUDE = (".git", "__pycache__", "*.pyc", "*.log", "outputs", "log", "tmp__*")
CLAIMS = ("null", "arm-lost", "difference")
PRED_FIELDS = ("metric", "arm", "expect", "tolerance")


class UsageError(Exception):
    """Bad arguments or unreadable card: exit 2."""


def today():
    return datetime.date.today().isoformat()


def skeleton(block_id, by):
    return {
        "block_id": block_id, "created": today(), "by": by,
        "claim": "", "intent": "", "label": "",
        "retrodiction": {"checked": [], "answerable": None, "why_not": ""},
        "predictions": [],
        "positive_control": {"how": "", "result": None},
        "arm_active_check": {"how": "", "result": None},
        "fingerprint": {"tree": None, "dirty": None, "build": None, "inputs": {}, "env": {}, "config": None,
                        "tools": {}, "flags": [], "tree_kind": None, "tree_hash": None, "source_commit": None},
        "runs": [], "seeds": [], "score": None,
    }


def load(path):
    try:
        card = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise UsageError(f"cannot read card {path}: {e}")
    if not isinstance(card, dict):
        raise UsageError(f"card {path} is not a JSON object")
    return card


def save(path, card):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def md5(path):
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError as e:
        raise UsageError(f"cannot hash {path}: {e}")
    return h.hexdigest()


def git(tree, *args):
    r = subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise UsageError(f"git {' '.join(args)} failed in {tree}: {r.stderr.strip()}")
    return r.stdout


def is_git_toplevel(tree):
    r = subprocess.run(["git", "-C", str(tree), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return r.returncode == 0 and os.path.realpath(r.stdout.strip()) == os.path.realpath(tree)


def excluded(rel, globs):
    parts = rel.split("/")
    return any(fnmatch.fnmatchcase(rel, g) or any(fnmatch.fnmatchcase(c, g) for c in parts) for g in globs)


def tree_hash(tree, globs):
    """sha256 over (relative path, md5) of regular files and (relative path, link target) of symlinks."""
    root = Path(tree)
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in sorted(dirnames + filenames):
            full = Path(dirpath) / name
            rel = full.relative_to(root).as_posix()
            if excluded(rel, globs):
                continue
            if full.is_symlink():
                entries.append(f"{rel}\0link:{os.readlink(full)}")
            elif name in filenames and full.is_file():
                entries.append(f"{rel}\0{md5(full)}")
        dirnames[:] = [d for d in dirnames
                       if not excluded((Path(dirpath) / d).relative_to(root).as_posix(), globs)]
    h = hashlib.sha256()
    for e in sorted(entries):
        h.update(e.encode() + b"\n")
    return h.hexdigest()


def env_values(specs):
    out = {}
    for s in specs or []:
        if "=" in s:
            k, v = s.split("=", 1)
            out[k] = v
        else:
            out[s] = os.environ.get(s)
    return out


def filled(v):
    return v is not None and v != "" and v != [] and v != {}


def obj(card, key, f, prefix=""):
    """card[key] as a dict: a missing or null value gives {} (its fields then fail); any other non-dict value is
    recorded as a failure and also gives {}."""
    v = card.get(key)
    if v is None:
        return {}
    if not isinstance(v, dict):
        f.append(f"{prefix}{key}: must be an object, got {type(v).__name__}")
        return {}
    return v


# Fingerprint keys and the value types each may hold (null only where the design allows it).
FP_TYPES = {"tree": (str, type(None)), "dirty": (bool, type(None)), "tree_kind": (str,),
            "tree_hash": (str, type(None)), "source_commit": (str, type(None)), "build": (str, type(None)), "inputs": (dict,), "env": (dict,),
            "config": (str, type(None)), "tools": (dict,), "flags": (list,)}


# ---------------------------------------------------------------------------------------------- checks

def fingerprint_failures(card, f, prefix=""):
    """Key, type and tree-kind rules of the common fingerprint; returns it (or {})."""
    fp = obj(card, "fingerprint", f, prefix)
    for k, types in FP_TYPES.items():
        if k not in fp:
            f.append(f"{prefix}fingerprint.{k}: missing (run the fingerprint subcommand)")
        elif not isinstance(fp[k], types):
            f.append(f"{prefix}fingerprint.{k}: must be {' or '.join('null' if t is type(None) else t.__name__ for t in types)}")
    kind = fp.get("tree_kind")
    if "tree_kind" in fp and kind not in TREE_KINDS:
        f.append(f"{prefix}fingerprint.tree_kind: must be one of {', '.join(TREE_KINDS)}")
    elif kind == "git":
        if not filled(fp.get("tree")):
            f.append(prefix + "fingerprint.tree: empty (run the fingerprint subcommand)")
        if not isinstance(fp.get("dirty"), bool):
            f.append(prefix + "fingerprint.dirty: must be true or false for a git tree")
    elif kind == "dir":
        for k in ("tree_hash", "source_commit"):
            if not filled(fp.get(k)):
                f.append(f"{prefix}fingerprint.{k}: empty; a non-git tree is identified by tree_hash and source_commit")
        if fp.get("dirty") is not None:
            f.append(prefix + "fingerprint.dirty: must be null for a non-git tree")
    if isinstance(fp.get("flags"), list) and not all(isinstance(t, str) for t in fp["flags"]):
        f.append(prefix + "fingerprint.flags: every token must be a string")
    return fp


def pre_failures(card):
    f = []
    for k in ("claim", "intent"):
        if not filled(card.get(k)):
            f.append(f"{k}: empty")
    if card.get("label") not in LABELS:
        f.append(f"label: must be one of {', '.join(LABELS)}")
    r = obj(card, "retrodiction", f)
    if not filled(r.get("checked")):
        f.append("retrodiction.checked: list the existing results looked at")
    ans = r.get("answerable")
    if not isinstance(ans, bool):
        f.append("retrodiction.answerable: must be true or false")
    elif ans:
        f.append("retrodiction.answerable: existing results answer the question; do not launch")
    elif not filled(r.get("why_not")):
        f.append("retrodiction.why_not: say why existing results do not answer it")
    preds = card.get("predictions")
    if not isinstance(preds, list) or not preds:
        f.append("predictions: at least one prediction")
    else:
        for i, p in enumerate(preds):
            if not isinstance(p, dict):
                f.append(f"predictions[{i}]: must be an object")
                continue
            for k in PRED_FIELDS:
                if not filled(p.get(k)):
                    f.append(f"predictions[{i}].{k}: empty")
    fp = fingerprint_failures(card, f)
    if fp.get("dirty") is True and card.get("label") == "confirmatory":
        f.append("fingerprint.dirty: tree has uncommitted tracked changes; a confirmatory block needs a clean tree")
    if not filled(obj(card, "arm_active_check", f).get("how")):
        f.append("arm_active_check.how: empty")
    if not filled(obj(card, "positive_control", f).get("how")):
        f.append("positive_control.how: empty")
    obj(card, "score", f)  # null before scoring; any other non-object is malformed
    return f


def score_failures(card):
    """Every current prediction index is scored exactly once, as a hit or a miss."""
    f = []
    s = card.get("score")
    if s is None:
        return ["score: not scored (run the score subcommand)"]
    if not isinstance(s, dict):
        return []  # reported by pre_failures
    preds = card.get("predictions") if isinstance(card.get("predictions"), list) else []
    seen = []
    for part in ("hits", "misses"):
        entries = s.get(part)
        if not isinstance(entries, list):
            f.append(f"score.{part}: must be a list")
            continue
        for e in entries:
            i = e.get("index") if isinstance(e, dict) else None
            if not isinstance(i, int) or isinstance(i, bool):
                f.append(f"score.{part}: entry without an integer index: {e!r}")
            elif not 0 <= i < len(preds):
                f.append(f"score.{part}: index {i} out of range (0..{len(preds) - 1})")
            else:
                seen.append(i)
    dup = sorted({i for i in seen if seen.count(i) > 1})
    if dup:
        f.append(f"score: predictions {dup} scored more than once")
    missing = sorted(set(range(len(preds))) - set(seen))
    if missing:
        f.append(f"score: predictions {missing} not scored (rescore)")
    if s.get("misses") and s.get("raw_read") is not True:
        f.append("score.raw_read: a prediction missed; read the raw results and rescore with --raw-read")
    return f


def post_failures(card, claim):
    f = pre_failures(card)
    f += score_failures(card)
    if not filled(obj(card, "arm_active_check", []).get("result")):
        f.append("arm_active_check.result: empty; required before any claim")
    if claim in ("null", "arm-lost") and not filled(obj(card, "positive_control", []).get("result")):
        f.append(f"positive_control.result: empty; required before a {claim} claim")
    return f


def report(failures):
    failures = list(dict.fromkeys(failures))  # one line per distinct failure
    for line in failures:
        print(f"FAIL {line}")
    if not failures:
        print("OK")
    return 1 if failures else 0


# ---------------------------------------------------------------------------------------------- compare

_ABSENT = object()   # a missing key; cannot collide with any JSON value


def show(v):
    return "<absent>" if v is _ABSENT else repr(v)


def diff_maps(a, b, prefix, skip=()):
    out = []
    for k in sorted(set(a) | set(b)):
        if k in skip:
            continue
        va, vb = a.get(k, _ABSENT), b.get(k, _ABSENT)
        if va is _ABSENT and vb is _ABSENT:
            continue
        if va is _ABSENT or vb is _ABSENT or va != vb:
            out.append(f"{prefix}.{k}: {show(va)} != {show(vb)}")
    return out


def is_value(tok):
    return not tok.startswith("-") or re.match(r"^-\d", tok) is not None


def strip_flags(tokens, prefixes):
    """Drop the arm-specific flags (and their separate value token) from an argv list; None stays None."""
    if not isinstance(tokens, list):
        return tokens
    out, i = [], 0
    while i < len(tokens):
        t = tokens[i]
        if any(t.startswith(p) for p in prefixes):
            i += 1
            if "=" not in t and i < len(tokens) and is_value(tokens[i]):
                i += 1
            continue
        out.append(t)
        i += 1
    return out


def diff_flags(a, b, prefix, arm_flags):
    sa, sb = strip_flags(a, arm_flags), strip_flags(b, arm_flags)
    return [] if sa == sb else [f"{prefix}: {sa!r} != {sb!r}"]


def shape_failures(card, tag):
    """Type problems that make a card impossible to compare (reported as FAIL lines, exit 1)."""
    f = []
    fp = obj(card, "fingerprint", f, f"card {tag} ")
    for k in ("inputs", "env", "tools"):
        if k in fp and not isinstance(fp[k], dict):
            f.append(f"card {tag} fingerprint.{k}: must be an object")
    flags = fp.get("flags")
    if flags is not None and not (isinstance(flags, list) and all(isinstance(t, str) for t in flags)):
        f.append(f"card {tag} fingerprint.flags: must be a list of strings")
    arms = obj(card, "arms", f, f"card {tag} ")
    for name, arm in arms.items():
        if not isinstance(arm, dict):
            f.append(f"card {tag} arms.{name}: must be an object")
            continue
        for k in ("env", "inputs"):
            if arm.get(k) is not None and not isinstance(arm[k], dict):
                f.append(f"card {tag} arms.{name}.{k}: must be an object")
        fl = arm.get("flags")
        if fl is not None and not (isinstance(fl, list) and all(isinstance(t, str) for t in fl)):
            f.append(f"card {tag} arms.{name}.flags: must be a list of strings")
    return f


def compare_failures(a, b, arm_vars, arm_flags=()):
    f = shape_failures(a, "A") + shape_failures(b, "B")
    for tag, card in (("A", a), ("B", b)):
        fingerprint_failures(card, f, f"card {tag} ")
    if f:
        return f
    fa, fb = a.get("fingerprint") or {}, b.get("fingerprint") or {}
    for k in sorted(set(fa) | set(fb)):
        va, vb = fa.get(k, _ABSENT), fb.get(k, _ABSENT)
        if k == "flags":
            f += diff_flags(fa.get(k), fb.get(k), "fingerprint.flags", arm_flags)
        elif isinstance(va, dict) and isinstance(vb, dict):
            f += diff_maps(va, vb, f"fingerprint.{k}", arm_vars if k == "env" else ())
        elif va is _ABSENT or vb is _ABSENT or va != vb:
            f.append(f"fingerprint.{k}: {show(va)} != {show(vb)}")
    arms_a, arms_b = a.get("arms") or {}, b.get("arms") or {}
    for name in sorted(set(arms_a) ^ set(arms_b)):
        f.append(f"arms.{name}: present in only one card")
    for name in sorted(set(arms_a) & set(arms_b)):
        xa, xb = arms_a[name], arms_b[name]
        f += diff_maps(xa.get("env") or {}, xb.get("env") or {}, f"arms.{name}.env", arm_vars)
        f += diff_maps(xa.get("inputs") or {}, xb.get("inputs") or {}, f"arms.{name}.inputs")
        f += diff_flags(xa.get("flags"), xb.get("flags"), f"arms.{name}.flags", arm_flags)
    for tag, card in (("A", a), ("B", b)):
        arms = card.get("arms") or {}
        names = sorted(arms)
        for other in names[1:]:
            f += [f"card {tag} arms {names[0]} vs {other}: " + d for d in
                  diff_maps(arms[names[0]].get("env") or {}, arms[other].get("env") or {}, "env", arm_vars)]
            f += [f"card {tag} arms {names[0]} vs {other}: " + d for d in
                  diff_flags(arms[names[0]].get("flags"), arms[other].get("flags"), "flags", arm_flags)]
    return f


# ---------------------------------------------------------------------------------------------- commands

def cmd_new(a):
    p = Path(a.card)
    if p.exists():
        raise UsageError(f"{p} exists; not overwritten")
    p.parent.mkdir(parents=True, exist_ok=True)
    save(p, skeleton(a.block_id, a.by))
    print(f"wrote {p}")
    return 0


def cmd_fingerprint(a):
    card = load(a.card)
    inputs = {str(p): md5(p) for p in a.inputs or []}
    env = env_values(a.env)
    flags = list(a.flags or [])
    if a.arm:
        if a.tree or a.build or a.config or a.tool or a.source_commit or a.hash_exclude:
            raise UsageError("--arm takes only --env, --inputs and --flags")
        card.setdefault("arms", {})[a.arm] = {"env": env, "inputs": inputs, "flags": flags}
    else:
        if not a.tree:
            raise UsageError("fingerprint needs --tree (or --arm NAME)")
        tools = {}
        for t in a.tool or []:
            if "=" not in t:
                raise UsageError(f"--tool {t}: expected NAME=VALUE")
            k, v = t.split("=", 1)
            tools[k] = v
        if not Path(a.tree).is_dir():
            raise UsageError(f"--tree {a.tree}: not a directory")
        if is_git_toplevel(a.tree):
            if a.source_commit or a.hash_exclude:
                raise UsageError("--source-commit and --hash-exclude are for a non-git tree only")
            tree = {"tree_kind": "git", "tree": git(a.tree, "rev-parse", "HEAD").strip(),
                    "dirty": bool(git(a.tree, "status", "--porcelain", "--untracked-files=no").strip()),
                    "tree_hash": None, "source_commit": None}
        else:
            if not a.source_commit:
                raise UsageError(f"--tree {a.tree} is not a git toplevel: give --source-commit <sha> "
                                 "(the commit the tree was built from)")
            tree = {"tree_kind": "dir", "tree": None, "dirty": None,
                    "tree_hash": tree_hash(a.tree, DEFAULT_EXCLUDE + tuple(a.hash_exclude or ())),
                    "source_commit": a.source_commit}
        card["fingerprint"] = {
            "tree": tree["tree"],
            "dirty": tree["dirty"],
            "tree_kind": tree["tree_kind"],
            "tree_hash": tree["tree_hash"],
            "source_commit": tree["source_commit"],
            "build": a.build,
            "inputs": inputs,
            "env": env,
            "config": md5(a.config) if a.config else None,
            "tools": tools,
            "flags": flags,
        }
    save(a.card, card)
    print(f"fingerprinted {a.card}" + (f" arm {a.arm}" if a.arm else ""))
    return 0


def parse_idx(specs, n):
    out = []
    for s in specs or []:
        i, _, obs = s.partition("=")
        try:
            i = int(i)
        except ValueError:
            raise UsageError(f"bad prediction index {s!r}")
        if not 0 <= i < n:
            raise UsageError(f"prediction index {i} out of range (0..{n - 1})")
        out.append((i, obs if "=" in s else None))
    return out


def cmd_score(a):
    card = load(a.card)
    preds = card.get("predictions") or []
    if not isinstance(preds, list) or not all(isinstance(p, dict) for p in preds):
        return report(["predictions: must be a list of objects"])
    hits, misses = parse_idx(a.hit, len(preds)), parse_idx(a.miss, len(preds))
    idx = [i for i, _ in hits + misses]
    if len(idx) != len(set(idx)):
        raise UsageError("a prediction is scored more than once")
    missing = sorted(set(range(len(preds))) - set(idx))
    if missing:
        return report([f"score: predictions {missing} not classified as hit or miss"])

    def entry(i, obs):
        return {"index": i, **{k: preds[i].get(k) for k in PRED_FIELDS}, "observed": obs}

    card["score"] = {
        "scored": today(),
        "hits": [entry(i, o) for i, o in hits],
        "misses": [entry(i, o) for i, o in misses],
        "raw_read": bool(a.raw_read),
        "verdict": a.verdict,
    }
    save(a.card, card)
    print(f"scored {a.card}: {len(hits)} hit(s), {len(misses)} miss(es), raw_read={bool(a.raw_read)}")
    return 0


def cmd_set(a):
    if not (a.control or a.runs or a.seeds):
        raise UsageError("set: nothing to set (give --control, --runs or --seeds)")
    card = load(a.card)
    for kind, result in a.control or []:
        if kind not in CONTROLS:
            raise UsageError(f"--control {kind}: must be one of {', '.join(CONTROLS)}")
        block = card.get(CONTROLS[kind])
        if block is None:
            block = card[CONTROLS[kind]] = {"how": "", "result": None}
        if not isinstance(block, dict):
            return report([f"{CONTROLS[kind]}: must be an object"])
        block["result"] = result
    for key, new in (("runs", a.runs), ("seeds", a.seeds)):
        cur = card.get(key) or []
        if not isinstance(cur, list):
            return report([f"{key}: must be a list"])
        card[key] = cur + [v for i, v in enumerate(new or []) if v not in cur and v not in (new or [])[:i]]
    save(a.card, card)
    print(f"set {a.card}")
    return 0


def cmd_check(a):
    card = load(a.card)
    if a.post:
        return report(post_failures(card, a.claim))
    if a.claim:
        raise UsageError("--claim needs --post")
    return report(pre_failures(card))


def cmd_compare(a):
    return report(compare_failures(load(a.a), load(a.b), set(a.arm_vars or []), tuple(a.arm_flags or [])))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(message)


def build_parser():
    p = Parser(prog="runcard.py", description="Run cards (see module docstring).")
    sub = p.add_subparsers(dest="cmd", required=True, parser_class=Parser)
    s = sub.add_parser("new")
    s.add_argument("card")
    s.add_argument("--block-id", required=True)
    s.add_argument("--by", required=True)
    s.set_defaults(fn=cmd_new)
    s = sub.add_parser("fingerprint")
    s.add_argument("card")
    s.add_argument("--tree")
    s.add_argument("--arm")
    s.add_argument("--inputs", nargs="*")
    s.add_argument("--env", nargs="*")
    s.add_argument("--build")
    s.add_argument("--config")
    s.add_argument("--tool", nargs="*")
    s.add_argument("--source-commit")
    s.add_argument("--hash-exclude", nargs="*")
    s.add_argument("--flags", nargs=argparse.REMAINDER)
    s.set_defaults(fn=cmd_fingerprint)
    s = sub.add_parser("set")
    s.add_argument("card")
    s.add_argument("--control", nargs=2, action="append", metavar=("KIND", "RESULT"))
    s.add_argument("--runs", nargs="*")
    s.add_argument("--seeds", nargs="*")
    s.set_defaults(fn=cmd_set)
    s = sub.add_parser("check")
    s.add_argument("card")
    s.add_argument("--post", action="store_true")
    s.add_argument("--claim", choices=CLAIMS)
    s.set_defaults(fn=cmd_check)
    s = sub.add_parser("score")
    s.add_argument("card")
    s.add_argument("--hit", nargs="*")
    s.add_argument("--miss", nargs="*")
    s.add_argument("--raw-read", action="store_true")
    s.add_argument("--verdict")
    s.set_defaults(fn=cmd_score)
    s = sub.add_parser("compare")
    s.add_argument("a")
    s.add_argument("b")
    s.add_argument("--arm-vars", nargs="*")
    s.add_argument("--arm-flags", nargs=argparse.REMAINDER)
    s.set_defaults(fn=cmd_compare)
    return p


def main(argv=None):
    try:
        a = build_parser().parse_args(argv)
        if a.cmd == "check" and a.post and a.claim is None:
            a.claim = "null"
        return a.fn(a)
    except UsageError as e:
        print(f"ERROR {e}")
        return 2
    except OSError as e:
        print(f"ERROR {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
