#!/usr/bin/env python3
"""Tests for scripts/validate_bearing_cards.py."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_bearing_cards as vbc


# ---------------------------------------------------------------------------
# parse_yaml_value
# ---------------------------------------------------------------------------

class TestParseYamlValue:
    def test_integer(self):
        assert vbc.parse_yaml_value("42") == 42

    def test_float(self):
        assert vbc.parse_yaml_value("3.14") == 3.14

    def test_string(self):
        assert vbc.parse_yaml_value("hello") == "hello"

    def test_quoted_string(self):
        assert vbc.parse_yaml_value('"hello"') == "hello"

    def test_single_quoted_string(self):
        assert vbc.parse_yaml_value("'world'") == "world"

    def test_empty_list(self):
        assert vbc.parse_yaml_value("[]") == []

    def test_list_with_items(self):
        result = vbc.parse_yaml_value('["a", "b", "c"]')
        assert result == ["a", "b", "c"]

    def test_list_without_quotes(self):
        result = vbc.parse_yaml_value("[a, b, c]")
        assert result == ["a", "b", "c"]

    def test_dict_returns_string(self):
        result = vbc.parse_yaml_value("{d: 25, D: 52}")
        assert isinstance(result, str)
        assert "{d: 25" in result

    def test_whitespace_handling(self):
        assert vbc.parse_yaml_value("  42  ") == 42
        assert vbc.parse_yaml_value("  hello  ") == "hello"


# ---------------------------------------------------------------------------
# parse_front_matter
# ---------------------------------------------------------------------------

class TestParseFrontMatter:
    def test_basic(self):
        text = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Test Card
            status: draft
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert fm["id"] == "KB-RU-000001"
        assert fm["title"] == "Test Card"
        assert fm["status"] == "draft"

    def test_no_front_matter(self):
        text = "Just text"
        fm = vbc.parse_front_matter(text)
        assert fm == {}

    def test_numeric_values(self):
        text = textwrap.dedent("""\
            ---
            d_mm: 25
            C_kN: 14.8
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert fm["d_mm"] == 25
        assert fm["C_kN"] == 14.8

    def test_list_values(self):
        text = textwrap.dedent("""\
            ---
            tags: ["bearing", "radial"]
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert fm["tags"] == ["bearing", "radial"]

    def test_multiline_list(self):
        text = textwrap.dedent("""\
            ---
            equivalents:
              - SKF 6205
              - FAG 6205
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert isinstance(fm["equivalents"], list)
        assert len(fm["equivalents"]) == 2

    def test_comments_skipped(self):
        text = textwrap.dedent("""\
            ---
            # This is a comment
            id: KB-RU-000001
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert fm["id"] == "KB-RU-000001"
        assert "#" not in fm

    def test_empty_value(self):
        text = textwrap.dedent("""\
            ---
            key:
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert fm["key"] is None

    def test_dict_value(self):
        text = textwrap.dedent("""\
            ---
            dims: {d: 25, D: 52, B: 15}
            ---
            Body
        """)
        fm = vbc.parse_front_matter(text)
        assert isinstance(fm["dims"], str)
        assert "d: 25" in fm["dims"]


# ---------------------------------------------------------------------------
# validate_bearing_card
# ---------------------------------------------------------------------------

class TestValidateBearingCard:
    def _write_card(self, tmp_path: Path, content: str) -> Path:
        p = tmp_path / "card" / "README.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_non_bearing_card_no_errors(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            title: Regular article
            topic: general
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert errors == []

    def test_missing_front_matter(self, tmp_path):
        content = "No front-matter here"
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert len(errors) == 1
        assert "отсутствует YAML front-matter" in errors[0]

    def test_missing_designation(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            topic: bearings-card
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert any("designation" in e for e in errors)

    def test_designation_as_string_error(self, tmp_path):
        # parse_yaml_value("some-text") returns a string, triggering the isinstance(desig, str) check
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            topic: bearings-card
            designation: some-bearing
            dims: {d: 25, D: 52, B: 15}
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert any("словарём" in e for e in errors)

    def test_missing_dims(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            topic: bearings-card
            designation: {base: "6205", suffixes: ["2RS"]}
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert any("dims" in e for e in errors)

    def test_empty_equivalents(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            topic: bearings-card
            designation: {base: "6205", suffixes: ["2RS"]}
            dims: {d: 25, D: 52, B: 15}
            equivalents: []
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert any("equivalents" in e and "пуст" in e for e in errors)

    def test_equivalents_not_list(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            id: KB-RU-000001
            topic: bearings-card
            designation: {base: "6205", suffixes: ["2RS"]}
            dims: {d: 25, D: 52, B: 15}
            equivalents: just-a-string
            ---
            Body
        """)
        p = self._write_card(tmp_path, content)
        errors = vbc.validate_bearing_card(p)
        assert any("equivalents" in e and "списком" in e for e in errors)
