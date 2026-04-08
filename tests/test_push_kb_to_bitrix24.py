#!/usr/bin/env python3
"""Tests for scripts/push_kb_to_bitrix24.py (non-API functions only).

Tests cover pure functions and state management without making HTTP calls.
The `markdown` package is required by push_kb_to_bitrix24.py, so we skip
the entire module if it's not installed.
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    import push_kb_to_bitrix24 as bx
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

pytestmark = pytest.mark.skipif(not HAS_MARKDOWN, reason="markdown package not installed")


# ---------------------------------------------------------------------------
# _flatten
# ---------------------------------------------------------------------------

class TestFlatten:
    def test_simple_dict(self):
        out: list[tuple[str, str]] = []
        bx._flatten("", {"key": "value"}, out)
        assert ("key", "value") in out

    def test_nested_dict(self):
        out: list[tuple[str, str]] = []
        bx._flatten("", {"a": {"b": "c"}}, out)
        assert ("a[b]", "c") in out

    def test_list(self):
        out: list[tuple[str, str]] = []
        bx._flatten("items", [10, 20], out)
        assert ("items[0]", "10") in out
        assert ("items[1]", "20") in out

    def test_none_value(self):
        out: list[tuple[str, str]] = []
        bx._flatten("key", None, out)
        assert ("key", "") in out

    def test_deeply_nested(self):
        out: list[tuple[str, str]] = []
        bx._flatten("", {"a": {"b": {"c": "deep"}}}, out)
        assert ("a[b][c]", "deep") in out

    def test_mixed_dict_list(self):
        out: list[tuple[str, str]] = []
        bx._flatten("", {"items": [{"name": "x"}]}, out)
        assert ("items[0][name]", "x") in out


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic_latin(self):
        result = bx.slugify("hello world")
        assert result == "hello-world"

    def test_cyrillic(self):
        result = bx.slugify("Привет мир")
        assert result.isascii()
        assert "privet" in result

    def test_special_chars(self):
        result = bx.slugify("test/path.name")
        assert "/" not in result
        assert "." not in result

    def test_empty_fallback(self):
        result = bx.slugify("")
        assert result == "page"

    def test_custom_fallback(self):
        result = bx.slugify("", fallback="custom")
        assert result == "custom"

    def test_max_length(self):
        long_text = "a" * 500
        result = bx.slugify(long_text)
        assert len(result) <= bx.MAX_CODE

    def test_no_consecutive_dashes(self):
        result = bx.slugify("a   b   c")
        assert "--" not in result

    def test_no_leading_trailing_dashes(self):
        result = bx.slugify(" test ")
        assert not result.startswith("-")
        assert not result.endswith("-")


# ---------------------------------------------------------------------------
# parse_article
# ---------------------------------------------------------------------------

class TestParseArticle:
    def test_with_front_matter(self, tmp_path):
        md = tmp_path / "kb" / "ru" / "test" / "README.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(textwrap.dedent("""\
            ---
            title: My Article
            id: KB-RU-000001
            ---
            # My Article

            Some **bold** text.
        """), encoding="utf-8")
        # We need KB_ROOT to be set correctly for breadcrumb calculation
        import push_kb_to_bitrix24
        old_root = push_kb_to_bitrix24.KB_ROOT
        push_kb_to_bitrix24.KB_ROOT = tmp_path / "kb" / "ru"
        try:
            title, breadcrumb, html = bx.parse_article(md)
            assert title == "My Article"
            assert "<strong>bold</strong>" in html or "<b>bold</b>" in html
        finally:
            push_kb_to_bitrix24.KB_ROOT = old_root

    def test_without_front_matter(self, tmp_path):
        md = tmp_path / "kb" / "ru" / "test" / "README.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text("# Plain Title\n\nBody content", encoding="utf-8")
        import push_kb_to_bitrix24
        old_root = push_kb_to_bitrix24.KB_ROOT
        push_kb_to_bitrix24.KB_ROOT = tmp_path / "kb" / "ru"
        try:
            title, breadcrumb, html = bx.parse_article(md)
            assert title == "Plain Title"
            assert "Body content" in html
        finally:
            push_kb_to_bitrix24.KB_ROOT = old_root

    def test_title_from_folder_name(self, tmp_path):
        md = tmp_path / "kb" / "ru" / "my-topic" / "README.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text("No heading, no front-matter", encoding="utf-8")
        import push_kb_to_bitrix24
        old_root = push_kb_to_bitrix24.KB_ROOT
        push_kb_to_bitrix24.KB_ROOT = tmp_path / "kb" / "ru"
        try:
            title, breadcrumb, html = bx.parse_article(md)
            assert title == "my-topic"
        finally:
            push_kb_to_bitrix24.KB_ROOT = old_root

    def test_title_truncated(self, tmp_path):
        md = tmp_path / "kb" / "ru" / "test" / "README.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        long_title = "A" * 300
        md.write_text(f"# {long_title}\n\nBody", encoding="utf-8")
        import push_kb_to_bitrix24
        old_root = push_kb_to_bitrix24.KB_ROOT
        push_kb_to_bitrix24.KB_ROOT = tmp_path / "kb" / "ru"
        try:
            title, breadcrumb, html = bx.parse_article(md)
            assert len(title) <= bx.MAX_TITLE
        finally:
            push_kb_to_bitrix24.KB_ROOT = old_root


# ---------------------------------------------------------------------------
# load_state / save_state
# ---------------------------------------------------------------------------

class TestStatePersistence:
    def test_load_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(bx, "STATE_FILE", tmp_path / "nonexistent.json")
        state = bx.load_state()
        assert state == {"folders": {}, "articles": {}}

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        state_file = tmp_path / "state.json"
        monkeypatch.setattr(bx, "STATE_FILE", state_file)

        state = {"folders": {"test": 1}, "articles": {"art.md": {"landing_id": 42}}}
        bx.save_state(state)

        loaded = bx.load_state()
        assert loaded["folders"]["test"] == 1
        assert loaded["articles"]["art.md"]["landing_id"] == 42

    def test_save_creates_file(self, tmp_path, monkeypatch):
        state_file = tmp_path / "new_state.json"
        monkeypatch.setattr(bx, "STATE_FILE", state_file)
        bx.save_state({"folders": {}, "articles": {}})
        assert state_file.exists()


# ---------------------------------------------------------------------------
# FRONT_MATTER_RE
# ---------------------------------------------------------------------------

class TestFrontMatterRegex:
    def test_matches_standard_front_matter(self):
        text = "---\ntitle: Test\n---\nBody"
        match = bx.FRONT_MATTER_RE.match(text)
        assert match is not None
        assert "title: Test" in match.group(1)

    def test_no_match_without_delimiter(self):
        text = "No front matter here"
        match = bx.FRONT_MATTER_RE.match(text)
        assert match is None
