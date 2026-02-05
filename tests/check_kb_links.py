#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
KB_FILES = [
    ROOT / "kb" / "ru" / "INDEX.md",
    ROOT / "kb" / "ru" / "overview" / "README.md",
]
LINK_PATTERN = re.compile(r"\[[^]]+]\(([^)]+)\)")


@dataclass(frozen=True)
class MissingLink:
    source: Path
    target: Path


def collect_links(markdown_path: Path) -> list[Path]:
    content = markdown_path.read_text(encoding="utf-8")
    links = []
    for match in LINK_PATTERN.finditer(content):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append((markdown_path.parent / target).resolve())
    return links


def main() -> int:
    missing: list[MissingLink] = []
    for markdown_path in KB_FILES:
        if not markdown_path.exists():
            missing.append(MissingLink(source=markdown_path, target=markdown_path))
            continue
        for target in collect_links(markdown_path):
            if not target.exists():
                missing.append(MissingLink(source=markdown_path, target=target))
    if missing:
        print("Missing links detected:")
        for entry in missing:
            rel_source = entry.source.relative_to(ROOT)
            rel_target = entry.target.relative_to(ROOT)
            print(f"- {rel_source} -> {rel_target}")
        return 1
    print("All checked links exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
