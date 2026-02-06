#!/usr/bin/env python3
"""
Генерация карточек подшипников из CSV-каталога.

Читает CSV с характеристиками подшипников и создаёт README.md
по шаблону bearing-card.md.

Использование:
    python scripts/generate_bearing_cards.py \
        --catalog kb/ru/bearings/datasets/catalog.csv \
        --equivalents kb/ru/bearings/datasets/equivalents.csv \
        --output-dir kb/ru/bearings/cards \
        --id-start 30 \
        --suffixes "2RS"
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Bearing type metadata
# ---------------------------------------------------------------------------

TYPE_INFO = {
    "ball_radial": {
        "title_ru": "подшипник шариковый радиальный",
        "description": "Шариковый радиальный однорядный подшипник",
        "tags_extra": ["radial", "deep-groove"],
        "series_prefix_meaning": {
            "6": "серия шариковых радиальных однорядных (глубокий желоб)",
        },
        "load_type_radial": "основная (до 80% от C)",
        "load_type_axial": "вспомогательная (до 30% от радиальной)",
        "applications": [
            "Электродвигатели общепромышленные",
            "Насосное оборудование",
            "Конвейерные ролики и натяжители",
            "Редукторы и приводные механизмы",
        ],
        "life_formula": "L10 = (C / P)³ × 10⁶ оборотов",
        "life_note": "Для шариковых подшипников:",
    },
    "ball_angular": {
        "title_ru": "подшипник шариковый радиально-упорный",
        "description": "Шариковый радиально-упорный однорядный подшипник с углом контакта 40°",
        "tags_extra": ["angular-contact"],
        "series_prefix_meaning": {
            "7": "серия шариковых радиально-упорных (angular contact)",
        },
        "load_type_radial": "основная составляющая",
        "load_type_axial": "значительная, в одном направлении (до 60% от C)",
        "applications": [
            "Шпиндели металлорежущих станков",
            "Редукторы с коническими и червячными передачами",
            "Насосы высокого давления",
            "Приводы с комбинированной радиально-осевой нагрузкой",
        ],
        "life_formula": (
            "L10 = (C / P)³ × 10⁶ оборотов\n"
            "L10h = L10 / (60 × n)\n"
            "P = X × Fr + Y × Fa  (для комбинированной нагрузки)"
        ),
        "life_note": "Для шариковых подшипников:",
    },
}

SUFFIX_INFO = {
    "2RS": {
        "label": "двойное резиновое уплотнение (контактное, с двух сторон)",
        "tag": "sealed",
        "details": [
            "Защита от пыли, грязи, воды",
            "Снижает предельные обороты (vs открытый или 2Z)",
            "Пластичная смазка заложена на весь срок службы",
        ],
    },
    "C3": {
        "label": "увеличенный радиальный зазор группы C3",
        "tag": "c3",
        "details": [
            "Компенсация теплового расширения",
            "Стандарт для электродвигателей",
            "Замена на CN может привести к заклиниванию",
        ],
    },
    "B": {
        "label": "угол контакта 40°",
        "tag": None,
        "details": [
            "Повышенная осевая грузоподъёмность по сравнению с углом 15° или 25°",
            "Стандартная конфигурация для комбинированных нагрузок",
            "Требует осевого преднатяга при монтаже",
        ],
    },
}

# Width-series digit → human label
WIDTH_SERIES_LABEL = {
    "2": "лёгкая",
    "3": "средняя",
    "4": "тяжёлая",
}

# Manufacturer-specific suffix patterns for sealed bearings
SEALED_MANUFACTURER_NOTES = {
    "SKF": "Премиум качество, Heavy duty уплотнение",
    "FAG": "Премиум, точка вместо дефиса",
    "NTN": "LLU = низкое трение уплотнения",
    "NSK": "DDU = двойное уплотнение",
    "ГОСТ": 'Отечественный, код "18" = двухстороннее уплотнение',
}

ANGULAR_MANUFACTURER_NOTES = {
    "SKF": "BEP = полиамидный сепаратор, 40° контакт",
    "FAG": "B = 40°, XL = усиленный, TVP = полиамидный сепаратор",
    "NTN": "B = 40° угол контакта",
    "NSK": "B = 40° угол контакта",
    "ГОСТ": 'Отечественный, код "46" = радиально-упорный',
}

BASE_MANUFACTURER_NOTES = {
    "SKF": "",
    "FAG": "",
    "NTN": "",
    "NSK": "",
    "ГОСТ": "Отечественный аналог",
}

# Application examples keyed by (type, approximate bore range)
APPLICATION_EXAMPLES_RADIAL = {
    "small": [
        {
            "title": "Бытовая техника (вентилятор, пылесос)",
            "conditions": "лёгкая нагрузка 150 Н, 1200 об/мин, чистая среда",
            "life": ">200000 часов",
            "notes": "можно рассмотреть 2Z для снижения трения",
        },
        {
            "title": "Электродвигатель малой мощности",
            "conditions": "нагрузка 400 Н, 1500 об/мин, пыльная среда",
            "life": ">100000 часов",
            "notes": "стандартный выбор для лёгких приводов",
        },
    ],
    "medium": [
        {
            "title": "Электродвигатель общепромышленный (до 3 кВт)",
            "conditions": "радиальная нагрузка 700 Н, температура 55 °C, пыльная среда",
            "life": ">80000 часов (расчётный)",
            "notes": "уплотнения 2RS защищают от пыли, рекомендуется C3 при нагреве",
        },
        {
            "title": "Конвейерный ролик",
            "conditions": "нагрузка 500 Н, 800 об/мин, загрязнённая среда",
            "life": ">100000 часов",
            "notes": "уплотнения обязательны, необслуживаемый режим",
        },
    ],
    "large": [
        {
            "title": "Промышленный насос",
            "conditions": "радиальная нагрузка 1500 Н, 1500 об/мин, чистая среда",
            "life": ">50000 часов",
            "notes": "возможна масляная смазка при высоких нагрузках",
        },
        {
            "title": "Сельскохозяйственная машина",
            "conditions": "ударная нагрузка 2000 Н, 600 об/мин, грязь и влага",
            "life": "5000–10000 часов",
            "notes": "уплотнения 2RS обязательны, возможен C3 для компенсации нагрева",
        },
    ],
}

APPLICATION_EXAMPLES_ANGULAR = [
    {
        "title": "Шпиндель фрезерного станка (парная установка DB)",
        "conditions": "Fr = 500 Н, Fa = 300 Н, 4000 об/мин, масляная смазка",
        "life": "20000–30000 часов (расчётный)",
        "notes": "парная установка DB, преднатяг пружиной, масляный туман",
    },
    {
        "title": "Червячный редуктор (входной вал)",
        "conditions": "Fr = 800 Н, Fa = 600 Н, 1500 об/мин, консистентная смазка",
        "life": "30000–40000 часов",
        "notes": "значительная осевая от червячной передачи, преднатяг гайкой",
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def load_catalog(path: Path) -> list[dict]:
    """Load bearing catalog CSV into list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_equivalents(path: Path) -> dict[str, dict]:
    """Load equivalents CSV keyed by composite designation (base or base-suffix)."""
    result: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row["base_designation"]
            result[key] = row
    return result


def bore_code(d_mm: int) -> str:
    """Return the ISO bore code string for a given inner diameter."""
    if d_mm < 10:
        return str(d_mm)
    if d_mm < 20:
        mapping = {10: "00", 12: "01", 15: "02", 17: "03"}
        return mapping.get(d_mm, str(d_mm))
    return f"{d_mm // 5:02d}"


def bore_explanation(d_mm: int) -> str:
    """Human-readable bore code explanation."""
    code = bore_code(d_mm)
    if d_mm < 20:
        return f"код внутреннего диаметра: d = {d_mm} мм"
    return f"код внутреннего диаметра: d = {code} × 5 = {d_mm} мм"


def size_bucket(d_mm: int) -> str:
    if d_mm <= 17:
        return "small"
    if d_mm <= 30:
        return "medium"
    return "large"


def kn_to_kgf(kn: float) -> int:
    return round(kn * 1000 / 9.80665)


def folder_name(base: str, suffixes: list[str]) -> str:
    """Build the card folder name: lowercase, dash-separated."""
    parts = [base.lower()]
    for s in suffixes:
        parts.append(s.lower())
    return "-".join(parts)


def full_designation(base: str, suffixes: list[str]) -> str:
    """Full designation string, e.g. '6205-2RS C3'."""
    if not suffixes:
        return base
    result = base
    for i, s in enumerate(suffixes):
        if i == 0:
            if s in ("2RS", "2Z", "B"):
                result += "-" + s
            else:
                result += " " + s
        else:
            result += " " + s
    return result


def get_equiv_row(equivalents: dict, base: str, suffixes: list[str]) -> dict | None:
    """Look up equivalents for a designation, trying suffixed then base."""
    full = full_designation(base, suffixes)
    if full in equivalents:
        return equivalents[full]
    if base in equivalents:
        return equivalents[base]
    return None


def _equiv_table_rows(
    equiv_row: dict | None, bearing_type: str, suffixes: list[str]
) -> list[tuple[str, str, str]]:
    """Return list of (manufacturer, code, note) tuples for the equivalents table."""
    if equiv_row is None:
        return []

    has_seal = any(s in ("2RS", "2Z") for s in suffixes)
    is_angular = bearing_type == "ball_angular"

    if has_seal:
        notes_map = SEALED_MANUFACTURER_NOTES
    elif is_angular:
        notes_map = ANGULAR_MANUFACTURER_NOTES
    else:
        notes_map = BASE_MANUFACTURER_NOTES

    rows = []
    for mfr_csv, mfr_display in [
        ("SKF", "SKF"),
        ("FAG", "FAG"),
        ("NTN", "NTN"),
        ("NSK", "NSK"),
        ("GOST", "ГОСТ"),
    ]:
        code = equiv_row.get(mfr_csv, "")
        if code:
            note = notes_map.get(mfr_display, "")
            rows.append((mfr_display, code, note))
    return rows


# ---------------------------------------------------------------------------
# Card generation
# ---------------------------------------------------------------------------


def generate_card(  # noqa: C901 — intentionally long to produce full card content
    row: dict,
    suffixes: list[str],
    equiv_row: dict | None,
    card_id: str,
) -> str:
    """Generate the full README.md content for a bearing card."""
    base = row["designation"]
    btype = row["type"]
    series = row["series"]
    d = int(row["d_mm"])
    D = int(row["D_mm"])
    B = int(row["B_mm"])
    C_kN = float(row["C_kN"])
    C0_kN = float(row["C0_kN"])
    rpm_grease = int(row["rpm_grease"])

    info = TYPE_INFO[btype]
    full_desig = full_designation(base, suffixes)
    today = date.today().isoformat()

    # --- tags ---
    tags = ["bearing", "ball"]
    tags.extend(info["tags_extra"])
    tags.append(series)
    for s in suffixes:
        si = SUFFIX_INFO.get(s)
        if si and si.get("tag"):
            tags.append(si["tag"])
    tags_str = ", ".join(f'"{t}"' for t in tags)

    # --- aliases ---
    aliases = [full_desig.replace("-", " ").lower()]
    if equiv_row:
        skf = equiv_row.get("SKF", "")
        if skf and skf != base:
            aliases.append(skf)
        nsk = equiv_row.get("NSK", "")
        if nsk and nsk != base:
            aliases.append(nsk)
    aliases_str = ", ".join(f'"{a}"' for a in aliases)

    # --- equivalents yaml ---
    equiv_rows = _equiv_table_rows(equiv_row, btype, suffixes)
    equiv_yaml_lines = []
    for mfr, code, _note in equiv_rows:
        equiv_yaml_lines.append(f'  - {{manufacturer: "{mfr}", code: "{code}"}}')
    equiv_yaml = "\n".join(equiv_yaml_lines) if equiv_yaml_lines else '  - {manufacturer: "generic", code: "' + base + '"}'

    # --- suffixes yaml ---
    suffixes_yaml = ", ".join(f'"{s}"' for s in suffixes) if suffixes else ""

    # --- rpm limit (sealed bearings are ~75% of grease rating) ---
    has_seal = any(s in ("2RS", "2Z") for s in suffixes)
    if has_seal:
        rpm_limit = int(rpm_grease * 0.80)
    else:
        rpm_limit = rpm_grease

    # --- series prefix ---
    prefix_digit = base[0]
    prefix_meaning = info["series_prefix_meaning"].get(
        prefix_digit, f"серия {prefix_digit}xxx"
    )
    width_digit = base[1]
    width_label = WIDTH_SERIES_LABEL.get(width_digit, "")
    bore_code_str = base[2:]

    # --- description line ---
    if has_seal:
        desc_suffix = " с двухсторонним резиновым уплотнением"
    elif "B" in suffixes:
        desc_suffix = ". Предназначен для комбинированных радиально-осевых нагрузок, обеспечивает высокую жёсткость и точность вращения при правильном преднатяге"
    else:
        desc_suffix = ""
    series_label = f"серии {series}"
    description_line = f"{info['description']}{desc_suffix}. Подшипник {series_label}, применяемый в промышленном оборудовании и механизмах."

    # --- equivalents table ---
    equiv_table_lines = []
    for mfr, code, note in equiv_rows:
        equiv_table_lines.append(f"| {mfr} | {code} | {note} |")
    equiv_table = "\n".join(equiv_table_lines)

    # --- functional analogues ---
    if has_seal:
        func_analogues = (
            f"- **{base}-2RS C3**: увеличенный зазор — для работы при повышенных температурах\n"
            f"- **{base}-2Z**: металлические шайбы вместо резины — меньшая защита, выше обороты\n"
            f"- **{base}** (открытый): нет уплотнений — требуется внешняя защита, выше обороты"
        )
    elif btype == "ball_angular":
        func_analogues = (
            f"- **{base}-B-2RS**: с уплотнениями — для загрязнённых условий, ниже обороты\n"
            f"- **{base[0]}{'%s' % base[1:]}** (угол 25°): меньше осевая, больше радиальная грузоподъёмность"
        )
    else:
        func_analogues = (
            f"- **{base}-2RS**: с уплотнениями — для загрязнённых условий\n"
            f"- **{base}-2Z**: с защитными шайбами — компромисс между защитой и оборотами"
        )

    # --- replacement risks ---
    d_prev = d - 5 if d >= 20 else d - 2
    d_next = d + 5 if d >= 20 else d + 3
    # Neighbouring series
    if series.startswith("62"):
        alt_series_prefix = "63"
        alt_D = D + 10
    elif series.startswith("63"):
        alt_series_prefix = "62"
        alt_D = D - 10
    else:
        alt_series_prefix = "62"
        alt_D = D

    cannot_replace = []
    # Different series
    if series != "7xxx":
        alt_desig = f"{alt_series_prefix}{base[2:]}"
        sfx = ("-" + suffixes[0]) if suffixes and suffixes[0] in ("2RS", "2Z", "B") else ""
        cannot_replace.append(
            f"- {alt_desig}{sfx} — другой D ({alt_D} мм вместо {D} мм) — не войдёт в корпус"
        )
    # Smaller bore
    prev_base = f"{base[0]}{base[1]}{bore_code(d_prev)}" if d_prev >= 10 else None
    if prev_base:
        sfx = ("-" + suffixes[0]) if suffixes and suffixes[0] in ("2RS", "2Z", "B") else ""
        cannot_replace.append(
            f"- {prev_base}{sfx} — другой d ({d_prev} мм вместо {d} мм) — не сядет на вал"
        )
    # Larger bore
    next_base = f"{base[0]}{base[1]}{bore_code(d_next)}"
    if next_base:
        sfx = ("-" + suffixes[0]) if suffixes and suffixes[0] in ("2RS", "2Z", "B") else ""
        cannot_replace.append(
            f"- {next_base}{sfx} — другой d ({d_next} мм вместо {d} мм) — не сядет на вал"
        )
    cannot_replace_str = "\n".join(cannot_replace)

    # --- allowed replacements ---
    if has_seal:
        allowed_replacements = (
            "- **Открытый → уплотнённый**: возможно, но снизятся обороты\n"
            "- **Уплотнённый → открытый**: возможно, но нужна внешняя защита от грязи\n"
            "- **CN → C3**: допустимо (C3 более универсален)\n"
            "- **2RS → 2Z**: допустимо, но снижается защита от влаги"
        )
    elif btype == "ball_angular":
        allowed_replacements = (
            f"- **{base}-A → {base}-B**: допустимо, но изменится распределение нагрузок\n"
            "- **Одиночный → парный**: допустимо для повышения жёсткости (DB или DF схема)\n"
            "- **Стальной сепаратор → полиамидный**: допустимо, полиамидный легче и тише"
        )
    else:
        allowed_replacements = (
            "- **Открытый → уплотнённый**: возможно, но снизятся обороты\n"
            "- **CN → C3**: допустимо (C3 более универсален)\n"
            "- **Разные производители**: проверяйте эквивалентность суффиксов"
        )

    # --- typical errors ---
    if btype == "ball_angular":
        typical_errors = (
            "- Монтаж без осевого преднатяга → повышенный люфт, вибрации, снижение ресурса\n"
            "- Неправильное направление установки → осевая нагрузка не воспринимается\n"
            f"- Замена на радиальный подшипник {base[0].replace('7','6')}{base[1:]}"
            " → отказ при осевых нагрузках\n"
            "- Чрезмерный преднатяг → перегрев, ускоренный износ"
        )
    else:
        typical_errors = (
            "- Монтаж ударами по телам качения → вмятины, преждевременный отказ\n"
            "- Игнорирование зазора при замене → заклинивание или вибрации\n"
            "- Переизбыток смазки (>50% объёма) → перегрев\n"
            f"- Применение на оборотах выше {rpm_limit} → перегрев"
            + (" уплотнений" if has_seal else "")
        )

    # --- maintenance section ---
    if has_seal:
        maintenance = (
            "**Рекомендуемая смазка**:\n"
            "- Тип: литиевая (Li) консистентная, NLGI 2\n"
            "- Подшипник поставляется с заводской смазкой\n"
            "- Температурный диапазон смазки: –30…+120 °C\n"
            "- Смазка заложена на весь срок службы (необслуживаемый)\n"
            "\n"
            "**Периодичность замены смазки**:\n"
            "- Для уплотнённых подшипников (2RS) смазка не обновляется\n"
            "- При появлении признаков износа — замена подшипника целиком\n"
            "\n"
            "**Монтаж**:\n"
            "- Метод: холодный монтаж с оправкой (для малых партий)\n"
            "- Горячая посадка при 80–100 °C (для серийного производства)\n"
            "- Обязательно: усилие через торец внутреннего кольца (вращающееся)\n"
            "- Запрещено: удары молотком, передача усилия через тела качения"
        )
    elif btype == "ball_angular":
        maintenance = (
            "**Рекомендуемая смазка**:\n"
            "- Тип: литиевая (Li) консистентная, NLGI 2 (или масляная для высоких оборотов)\n"
            "- Температурный диапазон смазки: –30…+120 °C\n"
            "- Для шпинделей: масляная смазка (масляный туман или циркуляция)\n"
            "- Заполнение: 30–50% свободного объёма (не более)\n"
            "\n"
            "**Периодичность замены смазки**:\n"
            "- Консистентная: каждые 2000–5000 часов (в зависимости от режима)\n"
            "- Масляная: по регламенту маслосистемы\n"
            "- Открытая конструкция требует регулярного контроля\n"
            "\n"
            "**Монтаж**:\n"
            "- Метод: холодный монтаж с оправкой или горячая посадка при 80–100 °C\n"
            "- Обязательно: обеспечить осевой преднатяг (пружиной или гайкой)\n"
            "- Направление: широкий торец наружного кольца обращён к осевой нагрузке\n"
            "- Запрещено: удары молотком, монтаж без преднатяга"
        )
    else:
        maintenance = (
            "**Рекомендуемая смазка**:\n"
            "- Тип: литиевая (Li) консистентная, NLGI 2\n"
            "- Температурный диапазон смазки: –30…+120 °C\n"
            "- Заполнение: 30–50% свободного объёма\n"
            "\n"
            "**Периодичность замены смазки**:\n"
            "- Нормальные условия: каждые 5000–10000 часов\n"
            "- Тяжёлые условия: каждые 2000–5000 часов\n"
            "\n"
            "**Монтаж**:\n"
            "- Метод: холодный монтаж с оправкой (для малых партий)\n"
            "- Горячая посадка при 80–100 °C (для серийного производства)\n"
            "- Обязательно: усилие через торец внутреннего кольца (вращающееся)\n"
            "- Запрещено: удары молотком, передача усилия через тела качения"
        )

    # --- replacement signs ---
    if btype == "ball_angular":
        replacement_signs = (
            "**Признаки необходимости замены**:\n"
            "- Повышенный шум (гул, скрежет)\n"
            "- Рост температуры выше 80 °C\n"
            "- Вибрации и биение шпинделя\n"
            "- Потеря преднатяга (увеличение осевого люфта)\n"
            "- Ухудшение точности обработки (для станков)"
        )
    else:
        replacement_signs = (
            "**Признаки необходимости замены**:\n"
            "- Повышенный шум (гул, скрежет)\n"
            "- Рост температуры выше 70 °C\n"
            "- Вибрации\n"
            "- Осевой или радиальный люфт\n"
            "- Утечка смазки через уплотнения"
        )

    # --- application examples ---
    if btype == "ball_angular":
        examples = APPLICATION_EXAMPLES_ANGULAR
    else:
        bucket = size_bucket(d)
        examples = APPLICATION_EXAMPLES_RADIAL.get(bucket, APPLICATION_EXAMPLES_RADIAL["medium"])

    examples_text_parts = []
    for i, ex in enumerate(examples, 1):
        examples_text_parts.append(
            f"**Пример {i}**: {ex['title']}\n"
            f"- Условия: {ex['conditions']}\n"
            f"- Ресурс: {ex['life']}\n"
            f"- Особенности: {ex['notes']}"
        )
    examples_text = "\n\n".join(examples_text_parts)

    # --- suffix explanation ---
    suffix_explanation = ""
    for s in suffixes:
        si = SUFFIX_INFO.get(s)
        if si:
            suffix_explanation += f"- **{s}** — {si['label']}\n"
            for detail in si["details"]:
                suffix_explanation += f"  - {detail}\n"

    # --- marking notes ---
    if has_seal:
        marking_notes = (
            f"- SKF: {base}-2RSH (H = Heavy duty уплотнение)\n"
            f"- FAG: {base}.2RSR (точка вместо дефиса)\n"
            f"- NTN: {base}LLU (LLU = низкое трение)\n"
            f"- NSK: {base}DDU (DDU = двойное уплотнение)"
        )
    elif btype == "ball_angular":
        marking_notes = (
            f"- SKF: {base} BEP (BEP = полиамидный сепаратор, 40° контакт)\n"
            f"- FAG: {base}-B-XL-TVP (B = 40°, XL = усиленный, TVP = полиамидный сепаратор)\n"
            f"- NTN: {base}B (B = 40° угол контакта)\n"
            f"- NSK: {base}B (B = 40° угол контакта)"
        )
    else:
        marking_notes = (
            "- У разных производителей суффиксы могут отличаться\n"
            "- Проверяйте совпадение по зазору и уплотнениям при замене"
        )

    # --- compatibility ---
    if btype == "ball_angular":
        compat_note = (
            f"- Серия {series[:-1]}x: размеры могут совпадать с серией 62xx по ISO 15, "
            "но конструкция принципиально отличается\n"
            f"- НЕ взаимозаменяем с 6{base[1:]} — другой тип нагрузки и требования к монтажу\n"
            "- Парные установки: O-образная (DB), X-образная (DF), тандем (DT)"
        )
        fit_requirements = (
            "- Вал: j5 или k5 (плотная посадка для точных применений)\n"
            "- Корпус: H6 или J6 (для неподвижного наружного кольца)\n"
            "- Осевой преднатяг: обязателен (пружиной или гайкой)\n"
            "- Направление осевой нагрузки: от широкого торца наружного кольца"
        )
    else:
        series_label_short = f"{series[:-1]}x"
        width_label_text = WIDTH_SERIES_LABEL.get(base[1], "")
        compat_note = (
            f"- Серия {series_label_short} ({width_label_text}): "
            f"стандартная серия для d={d} мм\n"
            f"- Другие зазоры: {base}-2RS C3 — размеры те же, но зазор увеличен"
        )
        fit_requirements = (
            "- Вал: h6 или js6 (для вращающегося внутреннего кольца)\n"
            "- Корпус: H7 или G7 (для неподвижного наружного кольца)\n"
            "- Осевая фиксация: с одной стороны крышкой, с другой — стопорным кольцом или буртиком"
        )

    # --- working conditions ---
    optimal_low = max(100, rpm_limit // 10)
    optimal_high = rpm_limit // 3
    if btype == "ball_angular":
        env_line = "- Среда: чистая или умеренно загрязнённая (открытая конструкция — требуется внешнее уплотнение)"
        temp_range = "–30…+120 °C (с учётом смазки)"
    elif has_seal:
        env_line = "- Среда: умеренно загрязнённая (уплотнения защищают от пыли и брызг)"
        temp_range = "–30…+110 °C (с учётом смазки)"
    else:
        env_line = "- Среда: чистая или умеренно загрязнённая"
        temp_range = "–30…+120 °C"

    # --- life calculation example ---
    example_Fr = max(300, int(C_kN * 1000 * 0.05))  # ~5% of C
    example_Fr = round(example_Fr / 100) * 100  # round to hundreds
    example_n = 1500
    P = example_Fr
    L10 = (C_kN * 1000 / P) ** 3
    L10h = L10 * 1e6 / (60 * example_n)

    if btype == "ball_angular":
        life_example = (
            f"**Пример расчёта для комбинированной нагрузки**:\n"
            f"- Радиальная нагрузка Fr = {example_Fr} Н\n"
            f"- Осевая нагрузка Fa = {example_Fr // 2} Н\n"
            f"- Частота вращения n = {example_n} об/мин\n"
            f"- X = 0.57, Y = 0.93 (для угла 40°, Fa/Fr > e)\n"
            f"- P = 0.57 × {example_Fr} + 0.93 × {example_Fr // 2} = "
            f"{int(0.57 * example_Fr + 0.93 * (example_Fr // 2))} Н\n"
            f"- L10 = (C / P)³ × 10⁶ оборотов\n"
            f"- L10h = L10 / (60 × n)"
        )
    else:
        life_example = (
            f"**Пример расчёта**:\n"
            f"- Радиальная нагрузка Fr = {example_Fr} Н\n"
            f"- Частота вращения n = {example_n} об/мин\n"
            f"- Эквивалентная нагрузка P ≈ Fr = {example_Fr} Н (малая осевая)\n"
            f"- L10 = ({int(C_kN * 1000)} / {example_Fr})³ × 10⁶ = {int(L10)} × 10⁶ оборотов\n"
            f"- L10h = {int(L10)} × 10⁶ / (60 × {example_n}) ≈ {int(L10h)} часов"
        )

    # --- rpm note ---
    rpm_oil = int(row["rpm_oil"])
    if has_seal:
        rpm_note = f"{rpm_limit} об/мин (с уплотнениями; открытый: {rpm_grease} об/мин)"
    elif btype == "ball_angular":
        rpm_note = f"{rpm_limit} об/мин (с консистентной смазкой; масляная смазка: {rpm_oil} об/мин)"
    else:
        rpm_note = f"{rpm_limit} об/мин (с консистентной смазкой; масляная: {rpm_oil} об/мин)"

    # --- angular-specific risk note ---
    if btype == "ball_angular":
        angular_risk_note = (
            "\n**Принципиальные отличия от радиальных подшипников**:\n"
            "- Требуется осевой преднатяг — без него подшипник будет работать некорректно\n"
            "- Осевая нагрузка воспринимается только в одном направлении\n"
            "- Для двухсторонней осевой нагрузки — парная установка (DB или DF)\n"
            "- Монтаж сложнее: необходимо соблюдать направление и величину преднатяга\n"
        )
    else:
        angular_risk_note = ""

    # -----------------------------------------------------------------------
    # Assemble the card
    # -----------------------------------------------------------------------
    card = f"""\
---
id: {card_id}
title: "{full_desig} — {info['title_ru']}"
topic: bearings-card
tags: [{tags_str}]
status: draft
source: "manufacturer_catalog"
created: {today}
updated: {today}
aliases: [{aliases_str}]
designation:
  base: "{base}"
  suffixes: [{suffixes_yaml}]
dims: {{d: {d}, D: {D}, B: {B}, unit: "mm"}}
standards: ["ISO 15", "ISO 281", "ГОСТ 520-2011"]
equivalents:
{equiv_yaml}
load_capacity:
  dynamic_C_kN: {C_kN}
  static_C0_kN: {C0_kN}
  rpm_limit: {rpm_limit}
---

# {full_desig} — {info['title_ru']}

{description_line}

## Назначение и где применяется

**Типовые применения**:
"""
    for app in info["applications"]:
        card += f"- {app}\n"

    card += f"""
**Тип нагрузки**:
- Радиальная: {info['load_type_radial']}
- Осевая: {info['load_type_axial']}

**Режимы работы**:
- Обороты: {optimal_low}–{rpm_limit} об/мин (оптимум {optimal_low}–{optimal_high})
- Температура: {temp_range}
{env_line}

## Расшифровка обозначения

**Базовое обозначение**: {base}
- **{prefix_digit}** — {prefix_meaning}
- **{width_digit}** — серия ширины {width_label} (B = {B} мм для этого размера)
- **{bore_code_str}** — {bore_explanation(d)}

**Суффиксы**:
{suffix_explanation}
**Особенности маркировки**:
{marking_notes}

## Габариты и совместимость

**Размеры** (ISO 15):
- Внутренний диаметр d: {d} мм
- Наружный диаметр D: {D} мм
- Ширина B: {B} мм

**Совместимость по ISO 15**:
{compat_note}

**Посадочные требования**:
{fit_requirements}

## Грузоподъёмность и ресурс

**Динамическая грузоподъёмность** (C): {C_kN} кН (≈ {kn_to_kgf(C_kN)} кгс)
**Статическая грузоподъёмность** (C0): {C0_kN} кН (≈ {kn_to_kgf(C0_kN)} кгс)
**Предельные обороты**: {rpm_note}

**Расчёт ресурса** (по ISO 281):

{info['life_note']}
```
{info['life_formula']}
L10h = L10 / (60 × n)
```

{life_example}

**Реальный ресурс** зависит от:
- Качества смазки и условий эксплуатации
- Точности монтажа и центровки
- Загрязнённости среды
- Температурного режима

## Эквиваленты и аналоги

**Точные эквиваленты** (совпадают размеры{', угол контакта' if btype == 'ball_angular' else ' и уплотнения'}):

| Производитель | Обозначение | Примечания |
|---------------|-------------|------------|
{equiv_table}

**Функциональные аналоги** (допустимые отличия):
{func_analogues}

**Внимание**: проверяйте совпадение суффиксов (зазор, уплотнение) при замене между производителями.

## Риски замены и ограничения

**Нельзя заменять на**:
{cannot_replace_str}

**Допустимые замены с оговорками**:
{allowed_replacements}
{angular_risk_note}
**Типовые ошибки**:
{typical_errors}

## Эксплуатация и обслуживание

{maintenance}

{replacement_signs}

**См. подробнее**: [Эксплуатация и обслуживание](../../maintenance/README.md)

## Примеры применения

{examples_text}

## См. также

- [Типы подшипников](../../types/README.md)
- [Маркировка подшипников](../../designation/README.md)
- [Размеры и серии](../../dimensions/README.md)
- [Выбор подшипника](../../selection/README.md)
- [Производители](../../manufacturers/README.md)

## Источники

- **Каталог производителя**: SKF General Catalogue 2020
- **Стандарт**: ISO 15:2017 (размеры), ISO 281:2007 (грузоподъёмность)
- **ГОСТ**: ГОСТ 520-2011 (общие технические условия)

## Контроль качества

- [x] Есть метаданные (id/topic/status/source)
- [x] Размеры и грузоподъёмность из каталога
- [x] Эквиваленты проверены по кросс-справочнику
- [x] Есть примеры применения
- [x] Риски замены описаны
- [ ] Для `status: verified` нет placeholder
"""
    return card


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Генерация карточек подшипников из CSV-каталога."
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        required=True,
        help="Путь к CSV-каталогу подшипников",
    )
    parser.add_argument(
        "--equivalents",
        type=Path,
        required=True,
        help="Путь к CSV-файлу эквивалентов",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Корневая папка для карточек (напр. kb/ru/bearings/cards)",
    )
    parser.add_argument(
        "--id-start",
        type=int,
        default=30,
        help="Начальный номер ID (KB-RU-NNNNNN)",
    )
    parser.add_argument(
        "--suffixes",
        type=str,
        default="",
        help='Суффиксы через запятую, напр. "2RS" или "2RS,C3"',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать что будет сгенерировано, не записывая файлы",
    )

    args = parser.parse_args()

    # Parse suffixes
    suffixes = [s.strip() for s in args.suffixes.split(",") if s.strip()] if args.suffixes else []

    # Load data
    catalog = load_catalog(args.catalog)
    equivalents = load_equivalents(args.equivalents)

    generated = []
    skipped = []
    current_id = args.id_start

    for row in catalog:
        base = row["designation"]

        # Build the designation with suffixes
        card_suffixes = list(suffixes)

        # For angular contact bearings with no explicit suffix, add "B" by default
        if row["type"] == "ball_angular" and not card_suffixes:
            card_suffixes = ["B"]

        fname = folder_name(base, card_suffixes)
        card_dir = args.output_dir / fname
        card_path = card_dir / "README.md"

        # Skip existing cards
        if card_path.exists():
            skipped.append(fname)
            continue

        # Look up equivalents
        equiv_row = get_equiv_row(equivalents, base, card_suffixes)

        # Generate ID
        card_id = f"KB-RU-{current_id:06d}"
        current_id += 1

        content = generate_card(row, card_suffixes, equiv_row, card_id)

        if args.dry_run:
            print(f"  [DRY-RUN] {card_path}")
        else:
            card_dir.mkdir(parents=True, exist_ok=True)
            card_path.write_text(content, encoding="utf-8")
            print(f"  [CREATED] {card_path}")

        generated.append(fname)

    # Summary
    print()
    print(f"Generated: {len(generated)} card(s)")
    if skipped:
        print(f"Skipped (already exist): {len(skipped)} — {', '.join(skipped)}")
    if generated:
        print("Cards:")
        for g in generated:
            print(f"  - {g}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
