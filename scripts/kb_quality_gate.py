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
    body = "\n".join(lines[end + 1 :]).lstrip("\n")

    fm: Dict[str, str] = {}
    for line in fm_lines:
        match = YAML_KV.match(line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        fm[key] = value
    return fm, body


def collect_md_files() -> List[Path]:
    if not KB_ROOT.exists():
        return []
    return [path for path in KB_ROOT.rglob("README.md") if path.is_file()]


def validate_paths(files: List[Path]) -> None:
    for path in files:
        parts = path.parts
        if path.name != "README.md":
            continue

        try:
            kb_index = parts.index("kb")
        except ValueError:
            continue

        for segment in parts[kb_index + 1 : -1]:
            if " " in segment:
                die(f"Space in path: {path}")
            try:
                segment.encode("ascii")
            except UnicodeEncodeError:
                die(f"Non-ASCII folder in path: {path} (segment: {segment})")


def validate_article_front_matter(path: Path, ids: Dict[str, Path]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    front_matter, body = parse_front_matter(text)

    if not front_matter:
        die(f"Missing YAML front-matter: {path}")

    missing = [key for key in REQUIRED_KEYS if key not in front_matter]
    if missing:
        die(f"Missing keys {missing} in front-matter: {path}")

    status = front_matter["status"].strip()
    if status not in ALLOWED_STATUS:
        die(f"Invalid status '{status}' in {path}. Allowed: {sorted(ALLOWED_STATUS)}")

    article_id = front_matter["id"].strip().strip('"').strip("'")
    if not article_id:
        die(f"Empty id in {path}")
    if article_id in ids and ids[article_id] != path:
        die(f"Duplicate id '{article_id}' in {path} and {ids[article_id]}")
    ids[article_id] = path

    topic = front_matter["topic"].strip().strip('"').strip("'")
    if topic and topic != "[[TBD]]" and not ASCII_KEBAB.match(topic):
        die(f"topic must be kebab-case ASCII: '{topic}' in {path}")

    if status == "verified":
        if "[[TBD]]" in body or "[[TBD]]" in text:
            die(f"Verified article contains [[TBD]]: {path}")


def validate_topic_indexes() -> None:
    index_path = Path("kb/ru/INDEX.md")
    if not index_path.exists():
        die("Missing kb/ru/INDEX.md")
    inbox_readme = Path("inbox/README.md")
    if not inbox_readme.exists():
        warn("Missing inbox/README.md (recommended)")


def validate_template() -> None:
    if not TEMPLATE.exists():
        warn("Missing _templates/article.md")
        return
    text = TEMPLATE.read_text(encoding="utf-8", errors="replace")
    front_matter, _ = parse_front_matter(text)
    if not front_matter:
        warn("_templates/article.md has no YAML front-matter; recommended to include for consistency.")


def main() -> None:
    validate_topic_indexes()
    validate_template()

    readmes = collect_md_files()
    validate_paths(readmes)

    ids: Dict[str, Path] = {}
    for path in readmes:
        validate_article_front_matter(path, ids)

    print(f"OK: validated {len(readmes)} README.md files in kb/. Unique ids: {len(ids)}")


if __name__ == "__main__":
    main()
