#!/usr/bin/env python3
"""Tests for scripts/kb_quality_gate.py."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path
from unittest import mock

import pytest

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import kb_quality_gate as qg


# ---------------------------------------------------------------------------
# parse_front_matter
# ---------------------------------------------------------------------------

class TestParseFrontMatter:
    def test_basic(self):
        text = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test Article
            status: draft
            ---
            Body content here.
        """)
        fm, body = qg.parse_front_matter(text)
        assert fm["id"] == "KB-RU-000001"
        assert fm["title"] == "Test Article"
        assert fm["status"] == "draft"
        assert "Body content here." in body

    def test_no_front_matter(self):
        text = "Just some text without front-matter."
        fm, body = qg.parse_front_matter(text)
        assert fm == {}
        assert body == text

    def test_empty_string(self):
        fm, body = qg.parse_front_matter("")
        assert fm == {}
        assert body == ""

    def test_only_opening_delimiter(self):
        text = "---\nid: KB-RU-000001\ntitle: Test\n"
        fm, body = qg.parse_front_matter(text)
        assert fm == {}

    def test_multiple_keys(self):
        text = textwrap.dedent("""\
            ---
            id: KB-RU-000010
            title: Полный набор
            topic: bearings
            tags: ["tag1", "tag2"]
            status: verified
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-02
            ---
            Body
        """)
        fm, body = qg.parse_front_matter(text)
        assert len(fm) == 8
        assert fm["topic"] == "bearings"
        assert fm["tags"] == '["tag1", "tag2"]'

    def test_value_with_colon(self):
        text = textwrap.dedent("""\
            ---
            title: Part A: Description
            id: KB-RU-000001
            ---
            Body
        """)
        fm, _ = qg.parse_front_matter(text)
        # The regex only captures until end of line, but value part
        # starts after the first colon
        assert "Part A" in fm["title"]

    def test_body_after_front_matter(self):
        text = "---\nid: X\n---\n\n\nHello world"
        fm, body = qg.parse_front_matter(text)
        assert fm["id"] == "X"
        assert body == "Hello world"


# ---------------------------------------------------------------------------
# validate_paths (via die)
# ---------------------------------------------------------------------------

class TestValidatePaths:
    def test_valid_kebab_case_paths(self):
        files = [Path("kb/ru/bearings/deep-groove/README.md")]
        # Should not raise or call sys.exit
        qg.validate_paths(files)

    def test_space_in_path_dies(self):
        files = [Path("kb/ru/some folder/README.md")]
        with pytest.raises(SystemExit):
            qg.validate_paths(files)

    def test_path_without_kb_prefix_skipped(self):
        files = [Path("other/folder/README.md")]
        # Should not raise since there's no 'kb' in parts
        qg.validate_paths(files)


# ---------------------------------------------------------------------------
# validate_readme
# ---------------------------------------------------------------------------

class TestValidateReadme:
    def _write_readme(self, tmp_path: Path, content: str) -> Path:
        p = tmp_path / "kb" / "ru" / "test-topic" / "test-article" / "README.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_readme(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: test-topic
            tags: ["test"]
            status: draft
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            # Test
        """)
        p = self._write_readme(tmp_path, content)
        ids = {}
        qg.validate_readme(p, ids)
        assert "KB-RU-000001" in ids

    def test_missing_front_matter_dies(self, tmp_path):
        p = self._write_readme(tmp_path, "# Just a heading\nSome text")
        with pytest.raises(SystemExit):
            qg.validate_readme(p, {})

    def test_missing_required_key_dies(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            ---
            Body
        """)
        p = self._write_readme(tmp_path, content)
        with pytest.raises(SystemExit):
            qg.validate_readme(p, {})

    def test_invalid_status_dies(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: test
            tags: []
            status: published
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Body
        """)
        p = self._write_readme(tmp_path, content)
        with pytest.raises(SystemExit):
            qg.validate_readme(p, {})

    def test_duplicate_id_dies(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: test
            tags: []
            status: draft
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Body
        """)
        p = self._write_readme(tmp_path, content)
        other = tmp_path / "other.md"
        ids = {"KB-RU-000001": other}
        with pytest.raises(SystemExit):
            qg.validate_readme(p, ids)

    def test_verified_with_tbd_dies(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: test
            tags: []
            status: verified
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Some content with [[TBD]] placeholder
        """)
        p = self._write_readme(tmp_path, content)
        with pytest.raises(SystemExit):
            qg.validate_readme(p, {})

    def test_draft_with_tbd_ok(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: test
            tags: []
            status: draft
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Some content with [[TBD]] placeholder
        """)
        p = self._write_readme(tmp_path, content)
        ids = {}
        qg.validate_readme(p, ids)
        assert "KB-RU-000001" in ids

    def test_non_kebab_topic_dies(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: Bad Topic Name
            tags: []
            status: draft
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Body
        """)
        p = self._write_readme(tmp_path, content)
        with pytest.raises(SystemExit):
            qg.validate_readme(p, {})

    def test_tbd_topic_ok(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            topic: "[[TBD]]"
            tags: []
            status: draft
            source: inbox/test.md
            created: 2025-01-01
            updated: 2025-01-01
            ---
            Body
        """)
        p = self._write_readme(tmp_path, content)
        ids = {}
        qg.validate_readme(p, ids)
        assert "KB-RU-000001" in ids


# ---------------------------------------------------------------------------
# ALLOWED_STATUS / ASCII_KEBAB regex
# ---------------------------------------------------------------------------

class TestRegexes:
    def test_ascii_kebab_valid(self):
        for val in ("bearings", "deep-groove", "a1-b2", "x"):
            assert qg.ASCII_KEBAB.match(val), f"Should match: {val}"

    def test_ascii_kebab_invalid(self):
        for val in ("UPPER", "with space", "under_score", "-leading", "trailing-", ""):
            assert not qg.ASCII_KEBAB.match(val), f"Should not match: {val!r}"

    def test_allowed_status(self):
        assert qg.ALLOWED_STATUS == {"draft", "verified", "deprecated"}
