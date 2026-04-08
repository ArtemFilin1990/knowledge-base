#!/usr/bin/env python3
"""Tests for scripts/process_inbox.py."""
from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from datetime import date
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import process_inbox as pi


# ---------------------------------------------------------------------------
# to_kebab_case
# ---------------------------------------------------------------------------

class TestToKebabCase:
    def test_basic_latin(self):
        assert pi.to_kebab_case("Hello World") == "hello-world"

    def test_cyrillic(self):
        result = pi.to_kebab_case("Подшипник шариковый")
        assert result.isascii()
        assert "-" in result or result.isalnum()
        # Should transliterate to something like "podshipnik-sharikovyy"
        assert result.startswith("podshipnik")

    def test_special_characters_removed(self):
        result = pi.to_kebab_case("Test: (value) [item]!")
        assert "(" not in result
        assert ")" not in result
        assert "[" not in result
        assert "]" not in result
        assert "!" not in result
        assert ":" not in result

    def test_underscores_become_dashes(self):
        assert pi.to_kebab_case("some_value_here") == "some-value-here"

    def test_multiple_dashes_collapsed(self):
        result = pi.to_kebab_case("a - - b")
        assert "--" not in result

    def test_no_leading_trailing_dashes(self):
        result = pi.to_kebab_case(" -test- ")
        assert not result.startswith("-")
        assert not result.endswith("-")

    def test_empty_string_returns_article(self):
        assert pi.to_kebab_case("") == "article"

    def test_only_special_chars_returns_article(self):
        assert pi.to_kebab_case("!!!???") == "article"

    def test_numbers_preserved(self):
        result = pi.to_kebab_case("Type 6205")
        assert "6205" in result

    def test_mixed_cyrillic_latin(self):
        result = pi.to_kebab_case("Подшипник 6205-2RS")
        assert result.isascii()
        assert "6205" in result

    def test_dash_variants_normalized(self):
        result = pi.to_kebab_case("value—test–item")
        assert "—" not in result
        assert "–" not in result


# ---------------------------------------------------------------------------
# compute_sha256
# ---------------------------------------------------------------------------

class TestComputeSha256:
    def test_known_hash(self):
        text = "hello"
        expected = hashlib.sha256(b"hello").hexdigest()
        assert pi.compute_sha256(text) == expected

    def test_empty_string(self):
        expected = hashlib.sha256(b"").hexdigest()
        assert pi.compute_sha256("") == expected

    def test_unicode_text(self):
        text = "Привет мир"
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert pi.compute_sha256(text) == expected

    def test_deterministic(self):
        text = "same content"
        assert pi.compute_sha256(text) == pi.compute_sha256(text)


# ---------------------------------------------------------------------------
# extract_title_from_content
# ---------------------------------------------------------------------------

class TestExtractTitle:
    def test_from_h1(self):
        text = "# My Title\n\nSome content"
        assert pi.extract_title_from_content(text, "file.md") == "My Title"

    def test_from_filename(self):
        text = "Some content without heading"
        assert pi.extract_title_from_content(text, "my_test_file.md") == "my test file"

    def test_filename_without_md(self):
        text = "No heading"
        assert pi.extract_title_from_content(text, "test-name.md") == "test name"

    def test_first_h1_only(self):
        text = "# First\n\n# Second"
        assert pi.extract_title_from_content(text, "file.md") == "First"

    def test_h1_with_spaces(self):
        text = "#   Spaced Title   \nBody"
        assert pi.extract_title_from_content(text, "file.md") == "Spaced Title"

    def test_h2_not_extracted_as_title(self):
        text = "## Section\nContent"
        # H2 is not H1, so should use filename
        assert pi.extract_title_from_content(text, "fallback.md") == "fallback"


# ---------------------------------------------------------------------------
# classify_topic
# ---------------------------------------------------------------------------

class TestClassifyTopic:
    def test_bearing_keywords(self):
        assert pi.classify_topic("подшипник шариковый", "Подшипники") == "podshipniki"

    def test_bearing_with_standard(self):
        result = pi.classify_topic("подшипник по стандарту ГОСТ", "Стандарт подшипников")
        assert result == "podshipniki-standards"

    def test_bearing_with_maintenance(self):
        result = pi.classify_topic("монтаж подшипника на вал", "Монтаж")
        assert result == "podshipniki-maintenance"

    def test_bearing_equivalents(self):
        result = pi.classify_topic("аналог подшипника SKF", "Аналоги")
        assert result == "podshipniki-equivalents"

    def test_bearing_designation(self):
        result = pi.classify_topic("маркировка подшипника 6205", "Маркировка")
        assert result == "podshipniki-designation"

    def test_lubrication(self):
        assert pi.classify_topic("выбор смазки", "Смазка") == "lubrication-seals"

    def test_drive_systems(self):
        assert pi.classify_topic("привод ремня", "Ремни") == "drive-systems"

    def test_standards_only(self):
        # "iso" is also in bearing_keywords, so bearing check wins first
        # Use text that has standard keywords but NOT bearing keywords
        assert pi.classify_topic("стандарт DIN 625 для метизов", "Стандарты метизов") == "standards"

    def test_general_fallback(self):
        assert pi.classify_topic("совершенно другая тема", "Разное") == "general"

    def test_title_contributes(self):
        # Title contains bearing keyword, text doesn't
        result = pi.classify_topic("некоторый текст", "Подшипник 6205")
        assert result.startswith("podshipniki")


# ---------------------------------------------------------------------------
# create_article_from_content
# ---------------------------------------------------------------------------

class TestCreateArticle:
    def test_basic_article(self):
        result = pi.create_article_from_content(
            content="# Test\n\nBody text",
            title="Test",
            topic="general",
            source_file="test.md",
            article_id="KB-RU-000100",
        )
        assert "id: KB-RU-000100" in result
        assert "title: Test" in result
        assert "topic: general" in result
        assert "status: draft" in result
        assert "source: inbox/test.md" in result
        assert "Body text" in result

    def test_tags_for_bearings(self):
        result = pi.create_article_from_content(
            content="Content",
            title="Test",
            topic="podshipniki",
            source_file="test.md",
            article_id="KB-RU-000101",
        )
        assert "bearings" in result
        assert "imported-from-inbox" in result

    def test_tags_for_standards(self):
        result = pi.create_article_from_content(
            content="Content",
            title="Test",
            topic="podshipniki-standards",
            source_file="test.md",
            article_id="KB-RU-000102",
        )
        assert "bearings" in result
        assert "standards" in result

    def test_h1_added_if_missing(self):
        result = pi.create_article_from_content(
            content="No heading here",
            title="My Title",
            topic="general",
            source_file="test.md",
            article_id="KB-RU-000103",
        )
        assert "# My Title" in result

    def test_h1_not_duplicated(self):
        result = pi.create_article_from_content(
            content="# Existing Title\n\nBody",
            title="Existing Title",
            topic="general",
            source_file="test.md",
            article_id="KB-RU-000104",
        )
        # Should contain exactly one "# " heading line
        h1_count = sum(1 for line in result.split("\n") if line.startswith("# "))
        assert h1_count == 1


# ---------------------------------------------------------------------------
# allocate_id  (with temp files)
# ---------------------------------------------------------------------------

class TestAllocateId:
    def test_sequential_allocation(self, tmp_path, monkeypatch):
        registry_path = tmp_path / "id_registry.json"
        registry_path.write_text(json.dumps({
            "next_id": 100,
            "prefix": "KB-RU-",
            "pad": 6,
        }))
        monkeypatch.setattr(pi, "ID_REGISTRY", registry_path)

        first = pi.allocate_id()
        assert first == "KB-RU-000100"

        second = pi.allocate_id()
        assert second == "KB-RU-000101"

        # Registry should now be at 102
        reg = json.loads(registry_path.read_text())
        assert reg["next_id"] == 102

    def test_default_registry(self, tmp_path, monkeypatch):
        registry_path = tmp_path / "missing.json"
        monkeypatch.setattr(pi, "ID_REGISTRY", registry_path)

        id_val = pi.allocate_id()
        assert id_val == "KB-RU-000202"


# ---------------------------------------------------------------------------
# extract_text_from_md
# ---------------------------------------------------------------------------

class TestExtractTextFromMd:
    def test_strips_front_matter(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text(textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test
            ---
            Body content here
        """), encoding="utf-8")
        result = pi.extract_text_from_md(md_file)
        assert "Body content here" in result
        assert "---" not in result

    def test_no_front_matter(self, tmp_path):
        md_file = tmp_path / "plain.md"
        md_file.write_text("Just plain text", encoding="utf-8")
        result = pi.extract_text_from_md(md_file)
        assert result == "Just plain text"


# ---------------------------------------------------------------------------
# move_to_processed (dry-run only to avoid side effects)
# ---------------------------------------------------------------------------

class TestMoveToProcessed:
    def test_dry_run_returns_path(self, tmp_path):
        file_path = tmp_path / "test.md"
        file_path.write_text("content")
        result = pi.move_to_processed(file_path, dry_run=True)
        # Should return the expected target path without moving
        assert "processed" in str(result)
        assert file_path.exists()  # Original file still exists

    def test_actual_move(self, tmp_path, monkeypatch):
        source = tmp_path / "inbox" / "test.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("content")

        processed_dir = tmp_path / "inbox" / "processed"
        monkeypatch.setattr(pi, "PROCESSED_DIR", processed_dir)

        result = pi.move_to_processed(source, dry_run=False)
        assert result.exists()
        assert not source.exists()

    def test_collision_handling(self, tmp_path, monkeypatch):
        source = tmp_path / "inbox" / "test.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("content2")

        processed_dir = tmp_path / "inbox" / "processed"
        year_month = date.today().strftime("%Y-%m")
        target_dir = processed_dir / year_month
        target_dir.mkdir(parents=True, exist_ok=True)
        # Pre-create a file with the same name
        (target_dir / "test.md").write_text("existing")

        monkeypatch.setattr(pi, "PROCESSED_DIR", processed_dir)

        result = pi.move_to_processed(source, dry_run=False)
        assert result.exists()
        assert "test_1" in result.name
