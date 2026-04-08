#!/usr/bin/env python3
"""Tests for scripts/generate_bearing_cards.py."""
from __future__ import annotations

import csv
import sys
from io import StringIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import generate_bearing_cards as gbc


# ---------------------------------------------------------------------------
# bore_code
# ---------------------------------------------------------------------------

class TestBoreCode:
    def test_small_diameter(self):
        assert gbc.bore_code(5) == "5"
        assert gbc.bore_code(8) == "8"

    def test_mapping_10(self):
        assert gbc.bore_code(10) == "00"

    def test_mapping_12(self):
        assert gbc.bore_code(12) == "01"

    def test_mapping_15(self):
        assert gbc.bore_code(15) == "02"

    def test_mapping_17(self):
        assert gbc.bore_code(17) == "03"

    def test_unmapped_under_20(self):
        # 13 mm has no standard ISO mapping, falls back to str(d)
        assert gbc.bore_code(13) == "13"

    def test_standard_20(self):
        assert gbc.bore_code(20) == "04"

    def test_standard_25(self):
        assert gbc.bore_code(25) == "05"

    def test_standard_30(self):
        assert gbc.bore_code(30) == "06"

    def test_standard_50(self):
        assert gbc.bore_code(50) == "10"

    def test_large_100(self):
        assert gbc.bore_code(100) == "20"


# ---------------------------------------------------------------------------
# bore_explanation
# ---------------------------------------------------------------------------

class TestBoreExplanation:
    def test_small_bore(self):
        result = gbc.bore_explanation(10)
        assert "d = 10 мм" in result

    def test_standard_bore(self):
        result = gbc.bore_explanation(25)
        assert "05 × 5 = 25 мм" in result

    def test_large_bore(self):
        result = gbc.bore_explanation(50)
        assert "10 × 5 = 50 мм" in result


# ---------------------------------------------------------------------------
# size_bucket
# ---------------------------------------------------------------------------

class TestSizeBucket:
    def test_small(self):
        assert gbc.size_bucket(10) == "small"
        assert gbc.size_bucket(17) == "small"

    def test_medium(self):
        assert gbc.size_bucket(18) == "medium"
        assert gbc.size_bucket(25) == "medium"
        assert gbc.size_bucket(30) == "medium"

    def test_large(self):
        assert gbc.size_bucket(31) == "large"
        assert gbc.size_bucket(50) == "large"
        assert gbc.size_bucket(100) == "large"


# ---------------------------------------------------------------------------
# kn_to_kgf
# ---------------------------------------------------------------------------

class TestKnToKgf:
    def test_basic_conversion(self):
        # 1 kN = ~101.97 kgf
        result = gbc.kn_to_kgf(1.0)
        assert result == round(1000 / 9.80665)
        assert result == 102

    def test_zero(self):
        assert gbc.kn_to_kgf(0.0) == 0

    def test_large_value(self):
        result = gbc.kn_to_kgf(14.8)
        expected = round(14800 / 9.80665)
        assert result == expected


# ---------------------------------------------------------------------------
# folder_name
# ---------------------------------------------------------------------------

class TestFolderName:
    def test_basic(self):
        assert gbc.folder_name("6205", []) == "6205"

    def test_with_suffixes(self):
        assert gbc.folder_name("6205", ["2RS"]) == "6205-2rs"

    def test_multiple_suffixes(self):
        assert gbc.folder_name("6205", ["2RS", "C3"]) == "6205-2rs-c3"

    def test_uppercase_base(self):
        assert gbc.folder_name("N205", []) == "n205"


# ---------------------------------------------------------------------------
# full_designation
# ---------------------------------------------------------------------------

class TestFullDesignation:
    def test_no_suffixes(self):
        assert gbc.full_designation("6205", []) == "6205"

    def test_seal_suffix(self):
        assert gbc.full_designation("6205", ["2RS"]) == "6205-2RS"

    def test_clearance_suffix(self):
        assert gbc.full_designation("6205", ["C3"]) == "6205 C3"

    def test_mixed_suffixes(self):
        result = gbc.full_designation("6205", ["2RS", "C3"])
        assert result == "6205-2RS C3"

    def test_b_suffix(self):
        assert gbc.full_designation("7205", ["B"]) == "7205-B"

    def test_2z_suffix(self):
        assert gbc.full_designation("6205", ["2Z"]) == "6205-2Z"


# ---------------------------------------------------------------------------
# get_equiv_row
# ---------------------------------------------------------------------------

class TestGetEquivRow:
    def test_full_match(self):
        equivs = {"6205-2RS": {"SKF": "6205-2RS1"}}
        result = gbc.get_equiv_row(equivs, "6205", ["2RS"])
        assert result is not None
        assert result["SKF"] == "6205-2RS1"

    def test_base_fallback(self):
        equivs = {"6205": {"SKF": "6205"}}
        result = gbc.get_equiv_row(equivs, "6205", ["2RS"])
        assert result is not None
        assert result["SKF"] == "6205"

    def test_no_match(self):
        equivs = {"6206": {"SKF": "6206"}}
        result = gbc.get_equiv_row(equivs, "6205", [])
        assert result is None


# ---------------------------------------------------------------------------
# load_catalog / load_equivalents (with temp CSV files)
# ---------------------------------------------------------------------------

class TestLoadCatalog:
    def test_basic_load(self, tmp_path):
        csv_path = tmp_path / "catalog.csv"
        csv_path.write_text(
            "designation,type,series,d_mm,D_mm,B_mm,C_kN,C0_kN,rpm_grease,rpm_oil,mass_kg\n"
            "6205,ball_radial,62,25,52,15,14.8,7.8,13000,16000,0.11\n",
            encoding="utf-8",
        )
        rows = gbc.load_catalog(csv_path)
        assert len(rows) == 1
        assert rows[0]["designation"] == "6205"
        assert rows[0]["d_mm"] == "25"

    def test_empty_catalog(self, tmp_path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text(
            "designation,type,series,d_mm,D_mm,B_mm,C_kN,C0_kN,rpm_grease,rpm_oil,mass_kg\n",
            encoding="utf-8",
        )
        rows = gbc.load_catalog(csv_path)
        assert rows == []


class TestLoadEquivalents:
    def test_basic_load(self, tmp_path):
        csv_path = tmp_path / "equivalents.csv"
        csv_path.write_text(
            "base_designation,SKF,FAG,NTN,NSK,GOST\n"
            "6205,6205,6205,6205,6205,205\n",
            encoding="utf-8",
        )
        equivs = gbc.load_equivalents(csv_path)
        assert "6205" in equivs
        assert equivs["6205"]["SKF"] == "6205"
        assert equivs["6205"]["GOST"] == "205"


# ---------------------------------------------------------------------------
# _equiv_table_rows
# ---------------------------------------------------------------------------

class TestEquivTableRows:
    def test_no_equiv(self):
        rows = gbc._equiv_table_rows(None, "ball_radial", [])
        assert rows == []

    def test_with_seal_suffix(self):
        equiv = {"SKF": "6205-2RS1", "FAG": "6205-2RSR", "NTN": "", "NSK": "", "GOST": ""}
        rows = gbc._equiv_table_rows(equiv, "ball_radial", ["2RS"])
        assert len(rows) == 2  # SKF and FAG have values
        # Should use SEALED_MANUFACTURER_NOTES
        assert any("SKF" in r[0] for r in rows)

    def test_angular_type(self):
        equiv = {"SKF": "7205-BEP", "FAG": "", "NTN": "", "NSK": "", "GOST": ""}
        rows = gbc._equiv_table_rows(equiv, "ball_angular", [])
        assert len(rows) == 1
        # Should use ANGULAR_MANUFACTURER_NOTES
        assert rows[0][0] == "SKF"

    def test_base_type(self):
        equiv = {"SKF": "6205", "FAG": "6205", "NTN": "", "NSK": "", "GOST": "205"}
        rows = gbc._equiv_table_rows(equiv, "ball_radial", [])
        assert len(rows) == 3  # SKF, FAG, GOST


# ---------------------------------------------------------------------------
# generate_card (smoke test — validates structure, not full content)
# ---------------------------------------------------------------------------

class TestGenerateCard:
    @pytest.fixture
    def sample_row(self):
        return {
            "designation": "6205",
            "type": "ball_radial",
            "series": "62",
            "d_mm": "25",
            "D_mm": "52",
            "B_mm": "15",
            "C_kN": "14.8",
            "C0_kN": "7.8",
            "rpm_grease": "13000",
            "rpm_oil": "16000",
            "mass_kg": "0.11",
        }

    def test_generates_valid_front_matter(self, sample_row):
        card = gbc.generate_card(sample_row, [], None, "KB-RU-000030")
        assert card.startswith("---\n")
        assert "id: KB-RU-000030" in card
        assert "designation:" in card
        assert "dims:" in card

    def test_generates_with_suffixes(self, sample_row):
        card = gbc.generate_card(sample_row, ["2RS", "C3"], None, "KB-RU-000031")
        assert "6205-2RS C3" in card
        assert "sealed" in card.lower() or "2RS" in card

    def test_generates_with_equivalents(self, sample_row):
        equiv = {
            "SKF": "6205-2RS1",
            "FAG": "6205-2RSR",
            "NTN": "6205LLU",
            "NSK": "6205DDU",
            "GOST": "180205",
        }
        card = gbc.generate_card(sample_row, ["2RS"], equiv, "KB-RU-000032")
        assert "SKF" in card
        assert "FAG" in card

    def test_ball_angular_type(self):
        row = {
            "designation": "7205",
            "type": "ball_angular",
            "series": "72",
            "d_mm": "25",
            "D_mm": "52",
            "B_mm": "15",
            "C_kN": "14.0",
            "C0_kN": "8.0",
            "rpm_grease": "11000",
            "rpm_oil": "15000",
            "mass_kg": "0.12",
        }
        card = gbc.generate_card(row, ["B"], None, "KB-RU-000033")
        assert "радиально-упорный" in card

    def test_roller_cylindrical_type(self):
        row = {
            "designation": "N205",
            "type": "roller_cylindrical",
            "series": "N2",
            "d_mm": "25",
            "D_mm": "52",
            "B_mm": "15",
            "C_kN": "20.0",
            "C0_kN": "14.0",
            "rpm_grease": "10000",
            "rpm_oil": "14000",
            "mass_kg": "0.15",
        }
        card = gbc.generate_card(row, [], None, "KB-RU-000034")
        assert "цилиндрический" in card

    def test_roller_tapered_type(self):
        row = {
            "designation": "30205",
            "type": "roller_tapered",
            "series": "302",
            "d_mm": "25",
            "D_mm": "52",
            "B_mm": "16.25",
            "C_kN": "28.0",
            "C0_kN": "25.0",
            "rpm_grease": "7500",
            "rpm_oil": "10000",
            "mass_kg": "0.17",
        }
        card = gbc.generate_card(row, [], None, "KB-RU-000035")
        assert "конический" in card
