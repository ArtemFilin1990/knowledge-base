#!/usr/bin/env python3
"""Tests for scripts/generate_bearings_yml.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import generate_bearings_yml as yml


# ---------------------------------------------------------------------------
# _slug
# ---------------------------------------------------------------------------

class TestSlug:
    def test_basic(self):
        assert yml._slug("Hello World") == "Hello-World"

    def test_special_chars(self):
        assert yml._slug("a@b#c") == "a-b-c"

    def test_preserves_alphanumeric(self):
        assert yml._slug("abc123") == "abc123"

    def test_preserves_dash_underscore(self):
        assert yml._slug("a-b_c") == "a-b_c"

    def test_strips_leading_trailing_dashes(self):
        result = yml._slug(" hello ")
        assert not result.startswith("-")
        assert not result.endswith("-")

    def test_empty_string(self):
        assert yml._slug("") == ""

    def test_cyrillic(self):
        result = yml._slug("Привет")
        # Cyrillic should be replaced with dashes (non-ASCII, non-alnum)
        assert result == "-"  or result == ""  # stripped


# ---------------------------------------------------------------------------
# _xml
# ---------------------------------------------------------------------------

class TestXml:
    def test_basic_text(self):
        assert yml._xml("hello") == "hello"

    def test_ampersand(self):
        assert yml._xml("a & b") == "a &amp; b"

    def test_angle_brackets(self):
        assert yml._xml("<tag>") == "&lt;tag&gt;"

    def test_quotes(self):
        result = yml._xml('He said "hello"')
        assert "&quot;" in result

    def test_apostrophe(self):
        result = yml._xml("it's")
        assert "&apos;" in result

    def test_none(self):
        assert yml._xml(None) == ""

    def test_number(self):
        assert yml._xml(42) == "42"


# ---------------------------------------------------------------------------
# build_categories
# ---------------------------------------------------------------------------

class TestBuildCategories:
    def test_single_manufacturer(self):
        manufacturers = [{"manufacturer": "SKF", "country": "Sweden"}]
        lines, mfr_ids = yml.build_categories(manufacturers)
        assert len(lines) == 2  # 1 country + 1 manufacturer
        assert "SKF" in mfr_ids
        assert "Sweden" in lines[0]

    def test_multiple_countries(self):
        manufacturers = [
            {"manufacturer": "SKF", "country": "Sweden"},
            {"manufacturer": "NSK", "country": "Japan"},
        ]
        lines, mfr_ids = yml.build_categories(manufacturers)
        assert len(mfr_ids) == 2
        # 2 countries + 2 manufacturers
        assert len(lines) == 4

    def test_same_country_multiple_manufacturers(self):
        manufacturers = [
            {"manufacturer": "NTN", "country": "Japan"},
            {"manufacturer": "NSK", "country": "Japan"},
        ]
        lines, mfr_ids = yml.build_categories(manufacturers)
        assert len(mfr_ids) == 2
        # 1 country + 2 manufacturers
        assert len(lines) == 3

    def test_empty_country_fallback(self):
        manufacturers = [{"manufacturer": "NoName", "country": ""}]
        lines, mfr_ids = yml.build_categories(manufacturers)
        assert any("Прочие" in line for line in lines)

    def test_parent_id_hierarchy(self):
        manufacturers = [{"manufacturer": "SKF", "country": "Sweden"}]
        lines, mfr_ids = yml.build_categories(manufacturers)
        # The manufacturer line should have parentId referencing the country
        mfr_line = [l for l in lines if "SKF" in l][0]
        assert 'parentId="1"' in mfr_line


# ---------------------------------------------------------------------------
# load_specs
# ---------------------------------------------------------------------------

class TestLoadSpecs:
    def test_basic(self):
        rows = [{"designation": "6205", "d_mm": "25"}]
        result = yml.load_specs(rows)
        assert "6205" in result
        assert result["6205"]["d_mm"] == "25"

    def test_empty_designation_skipped(self):
        rows = [{"designation": "", "d_mm": "25"}]
        result = yml.load_specs(rows)
        assert len(result) == 0

    def test_missing_designation_skipped(self):
        rows = [{"d_mm": "25"}]
        result = yml.load_specs(rows)
        assert len(result) == 0

    def test_whitespace_stripped(self):
        rows = [{"designation": " 6205 ", "d_mm": "25"}]
        result = yml.load_specs(rows)
        assert "6205" in result


# ---------------------------------------------------------------------------
# load_equivalents
# ---------------------------------------------------------------------------

class TestLoadEquivalents:
    def test_basic(self):
        rows = [{"base_designation": "6205", "SKF": "6205", "FAG": "6205"}]
        result = yml.load_equivalents(rows)
        assert "6205" in result

    def test_empty_designation_skipped(self):
        rows = [{"base_designation": "", "SKF": "6205"}]
        result = yml.load_equivalents(rows)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# render_offer
# ---------------------------------------------------------------------------

class TestRenderOffer:
    def test_basic_offer(self):
        result = yml.render_offer(
            offer_id=100001,
            designation="6205",
            manufacturer="SKF",
            analog="",
            source_url="",
            category_id=5,
            country="Sweden",
            specs=None,
            equivalents=None,
        )
        assert '<offer id="100001"' in result
        assert "<name>" in result
        assert "Подшипник 6205 SKF" in result
        assert "<categoryId>5</categoryId>" in result
        assert "</offer>" in result

    def test_offer_with_specs(self):
        specs = {
            "type": "ball_radial",
            "series": "62",
            "d_mm": "25",
            "D_mm": "52",
            "B_mm": "15",
            "C_kN": "14.8",
            "C0_kN": "7.8",
            "mass_kg": "0.11",
            "rpm_grease": "13000",
            "rpm_oil": "16000",
        }
        result = yml.render_offer(
            offer_id=100002,
            designation="6205",
            manufacturer="SKF",
            analog="",
            source_url="https://example.com",
            category_id=5,
            country="Sweden",
            specs=specs,
            equivalents=None,
        )
        assert "25×52×15" in result
        assert '<param name="d" unit="мм">25</param>' in result
        assert '<param name="Тип">' in result
        assert "<url>" in result
        assert "<weight>" in result

    def test_offer_with_analog(self):
        result = yml.render_offer(
            offer_id=100003,
            designation="205",
            manufacturer="GPZ",
            analog="6205",
            source_url="",
            category_id=10,
            country="Россия",
            specs=None,
            equivalents=None,
        )
        assert "Аналог: 6205" in result
        assert '<param name="Аналог">' in result

    def test_offer_with_equivalents(self):
        equivs = {"SKF": "6205", "FAG": "6205", "NTN": "", "NSK": "", "GOST": "205"}
        result = yml.render_offer(
            offer_id=100004,
            designation="6205",
            manufacturer="SKF",
            analog="",
            source_url="",
            category_id=5,
            country="Sweden",
            specs=None,
            equivalents=equivs,
        )
        assert "Эквивалент SKF" in result
        assert "Эквивалент GOST" in result
        # Empty values should not appear
        assert "Эквивалент NTN" not in result

    def test_offer_without_manufacturer(self):
        result = yml.render_offer(
            offer_id=100005,
            designation="6205",
            manufacturer="",
            analog="",
            source_url="",
            category_id=5,
            country="Unknown",
            specs=None,
            equivalents=None,
        )
        assert "<vendor>" not in result

    def test_xml_escaping_in_name(self):
        result = yml.render_offer(
            offer_id=100006,
            designation='6205 "special"',
            manufacturer="A&B",
            analog="",
            source_url="",
            category_id=5,
            country="Test",
            specs=None,
            equivalents=None,
        )
        assert "&amp;" in result
        assert "&quot;" in result


# ---------------------------------------------------------------------------
# TYPE_LABELS constant
# ---------------------------------------------------------------------------

class TestTypeLabels:
    def test_all_types_present(self):
        expected_keys = [
            "ball_radial", "ball_angular", "ball_radial_thrust",
            "ball_thrust", "roller_radial", "roller_tapered",
            "roller_spherical", "roller_cylindrical", "needle",
        ]
        for key in expected_keys:
            assert key in yml.TYPE_LABELS
