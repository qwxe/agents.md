#!/usr/bin/env python3
"""Print one section, table rows or paragraphs of a rule file (stdlib only).

Usage:
    python3 agents/section.py FILE ID [--row KEY]... [--para TEXT]...

FILE is a markdown file, ID the leading token or text of one heading (for
example 0.3, I.12, "Core card — Fallback"). Without --row/--para the whole
section is printed. --row KEY prints the table header and separator plus the
rows of the section whose first cell starts with KEY (case-insensitive, leading
** ignored). --para TEXT prints the block starting at the first line that
begins with TEXT (after optional **). Exit 1 with a one-line stderr message on
no match, several matching headings, an unmatched KEY or an unmatched TEXT.
"""
import argparse
import re
import sys

HEADING = re.compile(r"^(#+)\s+(.*?)\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")


class SectionError(Exception):
    pass


def headings(lines):
    """Yield (index, level, text) of headings outside fenced code blocks."""
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = HEADING.match(line)
        if m:
            yield i, len(m.group(1)), m.group(2)


def find_section(lines, sid):
    """Return the lines of the unique section whose heading starts with sid."""
    heads = list(headings(lines))
    hits = []
    for n, (i, level, text) in enumerate(heads):
        if text == sid or (text.startswith(sid) and not text[len(sid)].isalnum()
                           and text[len(sid)] not in ".-_"):
            hits.append(n)
    if not hits:
        raise SectionError("no heading matches %r" % sid)
    if len(hits) > 1:
        raise SectionError("%d headings match %r" % (len(hits), sid))
    n = hits[0]
    start, level = heads[n][0], heads[n][1]
    end = len(lines)
    for i, lv, _ in heads[n + 1:]:
        if lv <= level:
            end = i
            break
    return lines[start:end]


def first_cell(line):
    cell = line.strip().strip("|").split("|")[0].strip()
    return re.sub(r"^\*\*", "", cell).strip()


def rows(section, keys):
    """Header, separator and matching rows per table; every key must match."""
    out = []
    matched = set()
    i = 0
    while i < len(section):
        if not section[i].lstrip().startswith("|"):
            i += 1
            continue
        j = i
        while j < len(section) and section[j].lstrip().startswith("|"):
            j += 1
        table = section[i:j]
        picked = []
        for line in table[2:]:
            cell = first_cell(line).lower()
            for k in keys:
                if cell.startswith(re.sub(r"^\*\*", "", k).lower()):
                    matched.add(k)
                    picked.append(line)
                    break
        if picked:
            out.extend(table[:2] + picked)
        i = j
    missing = [k for k in keys if k not in matched]
    if missing:
        raise SectionError("no table row starts with %r" % missing[0])
    return out


def para(section, text):
    """The block starting at the first line beginning with text."""
    start = None
    for i, line in enumerate(section):
        if re.sub(r"^\*\*", "", line.lstrip()).startswith(text):
            start = i
            break
    if start is None:
        raise SectionError("no paragraph starts with %r" % text)
    end = start + 1
    while end < len(section):
        line = section[end]
        if line.strip():
            end += 1
            continue
        nxt = end + 1
        while nxt < len(section) and not section[nxt].strip():
            nxt += 1
        if nxt < len(section) and (LIST_ITEM.match(section[nxt])
                                   or section[nxt].startswith((" ", "\t"))):
            end = nxt
            continue
        break
    return section[start:end]


def render(lines, sid, row_keys=(), para_texts=()):
    section = find_section(lines, sid)
    if not row_keys and not para_texts:
        return section
    parts = []
    if row_keys:
        parts.append(rows(section, list(row_keys)))
    for t in para_texts:
        parts.append(para(section, t))
    out = []
    for n, part in enumerate(parts):
        if n:
            out.append("")
        out.extend(part)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("id")
    ap.add_argument("--row", action="append", default=[], metavar="KEY")
    ap.add_argument("--para", action="append", default=[], metavar="TEXT")
    args = ap.parse_args(argv)
    try:
        with open(args.file, encoding="utf-8") as f:
            lines = f.read().splitlines()
        out = render(lines, args.id, args.row, args.para)
    except (SectionError, OSError) as e:
        print("section.py: %s" % e, file=sys.stderr)
        return 1
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
