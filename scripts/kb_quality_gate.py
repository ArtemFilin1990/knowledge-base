#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

KB_ROOT = Path("kb")
TEMPLATE = Path("_templates/article.md")

ALLOWED_STATUS = {"draft", "verified", "deprecated"}

YAML_START = re.compile(r"^---\s*$")
YAML_KV = re.compile(r"^([A-Za-z0-9_]+)\s*:\s*(.*)\s*$")
ASCII_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_KEYS = ["id", "title", "topic", "tags", "status", "source", "created", "updated"]


def die(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"WARN: {msg}")


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    lines = text.splitlines()
    if not lines or not YAML_START.match(lines[0]):
        return {}, text

    end = None
    for i in range(1, min(len(lines), 200)):
        if YAML_START.match(lines[i]):
            end = i
            break
    if end is None:
        return {}, text

    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:]).lstrip("\n")

    fm: Dict[str, str] = {}
    for ln in fm_lines:
        m = YAML_KV.match(ln)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, body


def collect_readmes() -> List[Path]:
    if not KB_ROOT.exists():
        return []
    return [p for p in KB_ROOT.rglob("README.md") if p.is_file()]


def validate_paths(files: List[Path]) -> None:
    for p in files:
        parts = p.parts
        try:
            kb_i = parts.index("kb")
        except ValueError:
            continue

        for seg in parts[kb_i + 1:-1]:
            if " " in seg:
                die(f"Space in path: {p}")
            try:
                seg.encode("ascii")
            except UnicodeEncodeError:
                die(f"Non-ASCII folder in path: {p} (segment: {seg})")


def validate_readme(p: Path, ids: Dict[str, Path]) -> None:
    text = p.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_front_matter(text)

    if not fm:
        die(f"Missing YAML front-matter: {p}")

    missing = [k for k in REQUIRED_KEYS if k not in fm]
    if missing:
        die(f"Missing keys {missing} in front-matter: {p}")

    status = fm["status"].strip().strip('"').strip("'")
    if status not in ALLOWED_STATUS:
        die(f"Invalid status '{status}' in {p}. Allowed: {sorted(ALLOWED_STATUS)}")

    _id = fm["id"].strip().strip('"').strip("'")
    if not _id:
        die(f"Empty id in {p}")
    if _id in ids and ids[_id] != p:
        die(f"Duplicate id '{_id}' in {p} and {ids[_id]}")
    ids[_id] = p

    topic = fm["topic"].strip().strip('"').strip("'")
    if topic and topic != "[[TBD]]" and not ASCII_KEBAB.match(topic):
        die(f"topic must be kebab-case ASCII: '{topic}' in {p}")

    if status == "verified":
        if "[[TBD]]" in text or "[[TBD]]" in body:
            die(f"Verified article contains [[TBD]]: {p}")


def validate_required_files() -> None:
    idx = Path("kb/ru/INDEX.md")
    if not idx.exists():
        die("Missing kb/ru/INDEX.md")
    inbox = Path("inbox/README.md")
    if not inbox.exists():
        warn("Missing inbox/README.md (recommended)")
    if not TEMPLATE.exists():
        warn("Missing _templates/article.md")


def main() -> None:
    validate_required_files()

    readmes = collect_readmes()
    validate_paths(readmes)

    ids: Dict[str, Path] = {}
    for p in readmes:
        validate_readme(p, ids)

    print(f"OK: validated {len(readmes)} README.md files in kb/. Unique ids: {len(ids)}")


if __name__ == "__main__":
    main()
