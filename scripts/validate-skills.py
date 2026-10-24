#!/usr/bin/env python3
"""Validate Agent Skills metadata, references, and installable file scope."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
errors = []


def fail(message):
    errors.append(message)


def field(text, key):
    match = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1)
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


for skill_dir in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        continue
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{skill_file.relative_to(ROOT)}: frontmatter must start at byte 0")
        continue
    match = re.search(r"\n---\n", text[4:])
    if not match:
        fail(f"{skill_file.relative_to(ROOT)}: closing frontmatter delimiter missing")
        continue
    frontmatter = text[4 : match.start() + 4]
    name = field(frontmatter, "name")
    description = field(frontmatter, "description")
    if name != skill_dir.name:
        fail(f"{skill_file.relative_to(ROOT)}: name {name!r} must match directory")
    if not name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail(f"{skill_file.relative_to(ROOT)}: invalid skill name")
    if not description or len(description) > 1024:
        fail(f"{skill_file.relative_to(ROOT)}: description must be 1-1024 characters")
    if not text[match.end() + 4 :].strip():
        fail(f"{skill_file.relative_to(ROOT)}: body is empty")
    for link in re.findall(r"`(references/[^`]+)`", text):
        if not (skill_dir / link).is_file():
            fail(f"{skill_file.relative_to(ROOT)}: broken reference {link}")

for path in SKILLS.rglob("*"):
    if path.is_file() and path.name not in {"SKILL.md", "README.md"} and path.parent.name != "references":
        fail(f"unexpected file under skills/: {path.relative_to(ROOT)}")

if errors:
    print("Validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    raise SystemExit(1)

print(f"Validated {sum(1 for _ in SKILLS.glob('*/SKILL.md'))} skills and their references.")
