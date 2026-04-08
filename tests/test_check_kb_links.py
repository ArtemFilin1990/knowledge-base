#!/usr/bin/env python3
"""Tests for tests/check_kb_links.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

import check_kb_links as ckl


# ---------------------------------------------------------------------------
# collect_links
# ---------------------------------------------------------------------------

class TestCollectLinks:
    def test_basic_relative_link(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("[Link](./other/README.md)", encoding="utf-8")
        links = ckl.collect_links(md)
        assert len(links) == 1
        assert links[0] == (tmp_path / "other" / "README.md").resolve()

    def test_multiple_links(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "[A](./a/README.md)\n[B](./b/README.md)\n[C](./c/README.md)",
            encoding="utf-8",
        )
        links = ckl.collect_links(md)
        assert len(links) == 3

    def test_http_links_ignored(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("[Ext](https://example.com) and [Local](./file.md)", encoding="utf-8")
        links = ckl.collect_links(md)
        assert len(links) == 1

    def test_mailto_links_ignored(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("[Email](mailto:a@b.com)", encoding="utf-8")
        links = ckl.collect_links(md)
        assert len(links) == 0

    def test_anchor_links_ignored(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("[Section](#heading)", encoding="utf-8")
        links = ckl.collect_links(md)
        assert len(links) == 0

    def test_empty_file(self, tmp_path):
        md = tmp_path / "empty.md"
        md.write_text("", encoding="utf-8")
        links = ckl.collect_links(md)
        assert links == []

    def test_no_links(self, tmp_path):
        md = tmp_path / "plain.md"
        md.write_text("Just plain text without any links", encoding="utf-8")
        links = ckl.collect_links(md)
        assert links == []

    def test_link_with_spaces_in_text(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("[Link with spaces](./target.md)", encoding="utf-8")
        links = ckl.collect_links(md)
        assert len(links) == 1


# ---------------------------------------------------------------------------
# MissingLink dataclass
# ---------------------------------------------------------------------------

class TestMissingLink:
    def test_frozen(self):
        ml = ckl.MissingLink(source=Path("a.md"), target=Path("b.md"))
        with pytest.raises(AttributeError):
            ml.source = Path("c.md")

    def test_equality(self):
        a = ckl.MissingLink(source=Path("a.md"), target=Path("b.md"))
        b = ckl.MissingLink(source=Path("a.md"), target=Path("b.md"))
        assert a == b


# ---------------------------------------------------------------------------
# main (integration-style tests)
# ---------------------------------------------------------------------------

class TestMain:
    def test_returns_zero_when_all_links_valid(self, tmp_path, monkeypatch):
        # Create the required files structure
        kb_dir = tmp_path / "kb" / "ru"
        kb_dir.mkdir(parents=True)
        overview_dir = kb_dir / "overview"
        overview_dir.mkdir()

        index_md = kb_dir / "INDEX.md"
        index_md.write_text("[Overview](./overview/README.md)", encoding="utf-8")

        overview_readme = overview_dir / "README.md"
        overview_readme.write_text("# Overview", encoding="utf-8")

        # Monkey-patch the KB_FILES and ROOT
        monkeypatch.setattr(ckl, "ROOT", tmp_path)
        monkeypatch.setattr(ckl, "KB_FILES", [index_md, overview_readme])

        result = ckl.main()
        assert result == 0

    def test_returns_one_when_link_missing(self, tmp_path, monkeypatch):
        kb_dir = tmp_path / "kb" / "ru"
        kb_dir.mkdir(parents=True)

        index_md = kb_dir / "INDEX.md"
        index_md.write_text("[Missing](./nonexistent/README.md)", encoding="utf-8")

        monkeypatch.setattr(ckl, "ROOT", tmp_path)
        monkeypatch.setattr(ckl, "KB_FILES", [index_md])

        result = ckl.main()
        assert result == 1

    def test_returns_one_when_source_missing(self, tmp_path, monkeypatch):
        missing_file = tmp_path / "nonexistent.md"

        monkeypatch.setattr(ckl, "ROOT", tmp_path)
        monkeypatch.setattr(ckl, "KB_FILES", [missing_file])

        result = ckl.main()
        assert result == 1
