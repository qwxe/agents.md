import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import section  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = """# Title

## 1.1 First (2026-01-01)

intro line

| Role | Reads | Gate |
|---|---|---|
| **master** | a | b |
| worker one | c | d |
| worker two | e | f |

**Common gates** apply here.

- item one
  continued
- item two

Closing paragraph.

```
## not a heading
```

### 1.1.1 Child

child text

## 1.2 Second (2026-01-02)

other text

## 1.2x Lookalike

x

## Core card — Fallback (x)

fb text

## Dup

a

## Dup

b
"""


@pytest.fixture
def lines():
    return FIXTURE.splitlines()


def test_section_includes_children_stops_at_same_level(lines):
    out = section.render(lines, "1.1")
    assert out[0].startswith("## 1.1 First")
    assert "child text" in out
    assert "other text" not in out
    assert "## not a heading" in out


def test_section_text_id(lines):
    assert "fb text" in section.render(lines, "Core card — Fallback")


def test_token_boundary(lines):
    assert section.render(lines, "1.2")[0].startswith("## 1.2 Second")


def test_no_match_and_multi_match(lines):
    with pytest.raises(section.SectionError):
        section.render(lines, "9.9")
    with pytest.raises(section.SectionError):
        section.render(lines, "Dup")


def test_row(lines):
    out = section.render(lines, "1.1", row_keys=["MASTER", "worker"])
    assert out == ["| Role | Reads | Gate |", "|---|---|---|",
                   "| **master** | a | b |", "| worker one | c | d |",
                   "| worker two | e | f |"]


def test_row_no_match(lines):
    with pytest.raises(section.SectionError):
        section.render(lines, "1.1", row_keys=["nobody"])


def test_para_with_list(lines):
    out = section.render(lines, "1.1", para_texts=["Common gates"])
    assert out[0].startswith("**Common gates**")
    assert out[-1] == "- item two"
    assert "Closing paragraph." not in out


def test_para_no_match(lines):
    with pytest.raises(section.SectionError):
        section.render(lines, "1.1", para_texts=["Nope"])


def test_row_then_para_separated_by_blank(lines):
    out = section.render(lines, "1.1", row_keys=["master"],
                         para_texts=["Closing"])
    assert out[-2:] == ["", "Closing paragraph."]
    assert "" in out


def run(*args):
    return subprocess.run([sys.executable, str(ROOT / "agents/section.py"),
                           *args], capture_output=True, text=True, cwd=ROOT)


def test_cli_errors_exit_1():
    r = run("AGENTS.md", "99.99")
    assert r.returncode == 1 and r.stdout == ""
    assert len(r.stderr.strip().splitlines()) == 1


def test_real_agents_03():
    r = run("AGENTS.md", "0.3")
    assert r.returncode == 0
    assert r.stdout.startswith("## 0.3 ")
    assert "12. Use the host test environment" in r.stdout
    assert "## 0.4" not in r.stdout


def test_real_agents_01_master_row_and_gates():
    r = run("AGENTS.md", "0.1", "--row", "master", "--para", "Common mandatory")
    assert r.returncode == 0
    assert "| master |" in r.stdout
    assert "| Claude implementer |" not in r.stdout
    assert "**Common mandatory read-before-action gates**" in r.stdout
    assert "- Read INTERFACE I.10" in r.stdout
    assert "The brief still explicitly" not in r.stdout
    assert len(r.stdout.encode()) < 9000


def test_real_agents_01_fallback_rows():
    r = run("AGENTS.md", "0.1", "--row", "Research fallback / task fallback",
            "--row", "Codex task worker", "--para", "Common mandatory")
    assert r.returncode == 0
    assert "| Codex task worker |" in r.stdout
    assert "| Research fallback / task fallback" in r.stdout
    assert "| master |" not in r.stdout


def test_real_codex_core_card():
    r = run("agents/CODEX.md", "Core card — Fallback")
    assert r.returncode == 0
    assert "Launch contract" in r.stdout and "Core card — Task worker" not in r.stdout
