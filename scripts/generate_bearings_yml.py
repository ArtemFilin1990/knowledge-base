"""Build a YML (Yandex Market Language) catalog from the bearing nomenclature.

Reads:
- kb/ru/bearings/datasets/manufacturers.csv  (manufacturer → country)
- kb/ru/bearings/datasets/catalog.csv        (technical specs for ~70 generic models)
- kb/ru/bearings/datasets/equivalents.csv    (cross-brand equivalents)
- kb/ru/bearings/datasets/nomenclature.csv   (every catalog row across all brands)

Writes:
- kb/ru/bearings/export.xml — a YML catalog where each (designation, manufacturer)
  pair from nomenclature.csv becomes one <offer> element. Categories are organised
  hierarchically: country → manufacturer.

The format mirrors https://api.llmagent.ru/static/export.xml.
"""

from __future__ import annotations

import csv
import datetime as _dt
import re
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "kb" / "ru" / "bearings" / "datasets"
OUTPUT_PATH = REPO_ROOT / "kb" / "ru" / "bearings" / "export.xml"

SHOP_NAME = "knowledge-base.bearings"
SHOP_COMPANY = "Knowledge Base — Подшипники"
SHOP_URL = "https://github.com/ArtemFilin1990/knowledge-base"
PLATFORM = "knowledge-base/bearings-yml"
VERSION = "1.0.0"

# Default fallback price (used when no price data is available).
DEFAULT_PRICE = "0"

TYPE_LABELS = {
    "ball_radial": "Шариковый радиальный",
    "ball_angular": "Шариковый радиально-упорный",
    "ball_radial_thrust": "Шариковый радиально-упорный",
    "ball_thrust": "Шариковый упорный",
    "roller_radial": "Роликовый радиальный",
    "roller_tapered": "Роликовый конический",
    "roller_spherical": "Роликовый сферический",
    "roller_cylindrical": "Роликовый цилиндрический",
    "needle": "Игольчатый",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")


def _xml(text: object) -> str:
    return escape("" if text is None else str(text), {'"': "&quot;", "'": "&apos;"})


def build_categories(manufacturers: list[dict[str, str]]) -> tuple[list[str], dict[str, int]]:
    """Return (xml_lines, manufacturer_to_category_id)."""
    countries: dict[str, list[dict[str, str]]] = {}
    for row in manufacturers:
        countries.setdefault(row["country"] or "Прочие", []).append(row)

    lines: list[str] = []
    next_id = 1
    country_ids: dict[str, int] = {}
    for country in sorted(countries):
        cid = next_id
        next_id += 1
        country_ids[country] = cid
        lines.append(f'<category id="{cid}">{_xml(country)}</category>')

    mfr_ids: dict[str, int] = {}
    for country in sorted(countries):
        for row in sorted(countries[country], key=lambda r: r["manufacturer"]):
            mid = next_id
            next_id += 1
            mfr_ids[row["manufacturer"]] = mid
            lines.append(
                f'<category id="{mid}" parentId="{country_ids[country]}">'
                f"{_xml(row['manufacturer'])}</category>"
            )
    return lines, mfr_ids


def load_specs(catalog_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["designation"].strip(): row for row in catalog_rows if row.get("designation")}


def load_equivalents(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["base_designation"].strip(): row for row in rows if row.get("base_designation")}


def render_offer(
    offer_id: int,
    designation: str,
    manufacturer: str,
    analog: str,
    source_url: str,
    category_id: int,
    country: str,
    specs: dict[str, str] | None,
    equivalents: dict[str, str] | None,
) -> str:
    name_parts = ["Подшипник", designation]
    if manufacturer:
        name_parts.append(manufacturer)
    name = " ".join(p for p in name_parts if p)

    vendor_code = designation

    description_bits = [f"{name}, страна: {country}."]
    if specs:
        dims = (specs.get("d_mm"), specs.get("D_mm"), specs.get("B_mm"))
        if all(dims):
            description_bits.append(f"Размеры d×D×B: {dims[0]}×{dims[1]}×{dims[2]} мм.")
    if analog:
        description_bits.append(f"Аналог: {analog}.")
    description = " ".join(description_bits)

    lines: list[str] = []
    lines.append(f'<offer id="{offer_id}" available="true">')
    if source_url:
        lines.append(f"<url>{_xml(source_url)}</url>")
    lines.append(f"<price>{DEFAULT_PRICE}</price>")
    lines.append("<currencyId>RUR</currencyId>")
    lines.append(f"<categoryId>{category_id}</categoryId>")
    lines.append(f"<name>{_xml(name)}</name>")
    if manufacturer:
        lines.append(f"<vendor>{_xml(manufacturer)}</vendor>")
    lines.append(f"<model>{_xml(designation)}</model>")
    lines.append(f"<vendorCode>{_xml(vendor_code)}</vendorCode>")
    lines.append(f"<description>{_xml(description)}</description>")

    if analog:
        lines.append(f'<param name="Аналог">{_xml(analog)}</param>')
    lines.append(f'<param name="Страна">{_xml(country)}</param>')

    if specs:
        type_label = TYPE_LABELS.get(specs.get("type", ""), specs.get("type", ""))
        if type_label:
            lines.append(f'<param name="Тип">{_xml(type_label)}</param>')
        if specs.get("series"):
            lines.append(f'<param name="Серия">{_xml(specs["series"])}</param>')
        if specs.get("d_mm"):
            lines.append(f'<param name="d" unit="мм">{_xml(specs["d_mm"])}</param>')
        if specs.get("D_mm"):
            lines.append(f'<param name="D" unit="мм">{_xml(specs["D_mm"])}</param>')
        if specs.get("B_mm"):
            lines.append(f'<param name="B" unit="мм">{_xml(specs["B_mm"])}</param>')
        if specs.get("C_kN"):
            lines.append(f'<param name="C" unit="кН">{_xml(specs["C_kN"])}</param>')
        if specs.get("C0_kN"):
            lines.append(f'<param name="C0" unit="кН">{_xml(specs["C0_kN"])}</param>')
        if specs.get("mass_kg"):
            lines.append(f'<param name="Масса" unit="кг">{_xml(specs["mass_kg"])}</param>')
        if specs.get("rpm_grease"):
            lines.append(f'<param name="Обороты (смазка)" unit="об/мин">{_xml(specs["rpm_grease"])}</param>')
        if specs.get("rpm_oil"):
            lines.append(f'<param name="Обороты (масло)" unit="об/мин">{_xml(specs["rpm_oil"])}</param>')

    if equivalents:
        for brand in ("SKF", "FAG", "NTN", "NSK", "GOST"):
            value = (equivalents.get(brand) or "").strip()
            if value:
                lines.append(f'<param name="Эквивалент {brand}">{_xml(value)}</param>')

    if specs and specs.get("mass_kg"):
        try:
            lines.append(f"<weight>{float(specs['mass_kg'])}</weight>")
        except ValueError:
            pass

    lines.append("</offer>")
    return "".join(lines)


def main() -> None:
    manufacturers = _read_csv(DATA_DIR / "manufacturers.csv")
    catalog = _read_csv(DATA_DIR / "catalog.csv")
    equivalents = _read_csv(DATA_DIR / "equivalents.csv")
    nomenclature = _read_csv(DATA_DIR / "nomenclature.csv")

    specs_index = load_specs(catalog)
    equivalents_index = load_equivalents(equivalents)
    country_by_mfr = {row["manufacturer"]: (row["country"] or "Прочие") for row in manufacturers}

    category_lines, mfr_ids = build_categories(manufacturers)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")

    written = 0
    skipped = 0
    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(f'<yml_catalog date="{timestamp}">\n')
        out.write("<shop>\n")
        out.write(f"<name>{_xml(SHOP_NAME)}</name>\n")
        out.write(f"<company>{_xml(SHOP_COMPANY)}</company>\n")
        out.write(f"<url>{_xml(SHOP_URL)}</url>\n")
        out.write(f"<platform>{_xml(PLATFORM)}</platform>\n")
        out.write(f"<version>{_xml(VERSION)}</version>\n")
        out.write("<cpa>0</cpa>\n")
        out.write("<currencies>\n<currency id=\"RUR\" rate=\"1\"/>\n</currencies>\n")
        out.write("<categories>\n")
        for line in category_lines:
            out.write(line + "\n")
        out.write("</categories>\n")
        out.write("<offers>\n")

        offer_id = 100000
        for row in nomenclature:
            gost = (row.get("gost_designation") or "").strip()
            analog = (row.get("analog") or "").strip()
            manufacturer = (row.get("manufacturer") or "").strip()
            # Use GOST as primary, fall back to analog when GOST is absent.
            designation = gost or analog
            secondary = analog if gost else ""
            if not designation or manufacturer not in mfr_ids:
                skipped += 1
                continue
            offer_id += 1
            country = country_by_mfr.get(manufacturer, "Прочие")
            specs = specs_index.get(designation) or specs_index.get(analog) if analog else specs_index.get(designation)
            equivs = equivalents_index.get(designation) or (equivalents_index.get(analog) if analog else None)
            out.write(
                render_offer(
                    offer_id=offer_id,
                    designation=designation,
                    manufacturer=manufacturer,
                    analog=secondary,
                    source_url=(row.get("source_url") or "").strip(),
                    category_id=mfr_ids[manufacturer],
                    country=country,
                    specs=specs,
                    equivalents=equivs,
                )
                + "\n"
            )
            written += 1

        out.write("</offers>\n</shop>\n</yml_catalog>\n")

    size = OUTPUT_PATH.stat().st_size
    print(f"Wrote {written} offers ({skipped} skipped) to {OUTPUT_PATH}")
    print(f"File size: {size / 1024 / 1024:.2f} MB")
    print(f"Categories: {len(category_lines)} ({len(mfr_ids)} manufacturers)")


if __name__ == "__main__":
    main()
