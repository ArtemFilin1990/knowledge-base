---
id: KB-RU-000020
title: "Таблица-схема для поиска аналогов подшипников"
topic: "bearings-datasets"
tags: ["подшипники", "данные", "схема", "аналоги", "ИИ"]
status: draft
source: "kb/ru/bearings/datasets/analog-search-schema.md"
created: 2026-02-05
updated: 2026-02-05
---

# Таблица-схема для поиска аналогов подшипников

Документ описывает целевую схему данных для поиска аналогов подшипников. Схема опирается на текущие датасеты репозитория:

- `catalog.csv` — техпараметры типоразмеров.
- `equivalents.csv` — быстрые эквиваленты между брендами.
- `nomenclature.csv` — длинный кросс-справочник ГОСТ ↔ международные аналоги с трассировкой источника.

Схема разделена на две таблицы:

1. **`bearings_catalog`** — техкарточка подшипника.
2. **`bearings_crossref`** — связи аналогов между системами/брендами.

## 1. Таблица техпараметров `bearings_catalog`

| Группа | Колонка (RU) | Переменная (var_key) | Тип | Ед. | Роль | Правило заполнения |
|---|---|---|---|---|---|---|
| Идентификация | Базовое обозначение | `designation_base` | string | — | фильтр | Нормализуем до «базы» (например, `6205`). |
| Идентификация | Полное обозначение | `designation_full` | string | — | контекст | Как пришло из источника (`6205-2RS1/C3`). |
| Идентификация | Система обозначений | `designation_system` | enum | — | фильтр | `ISO` / `GOST` / `ABMA` (если известно). |
| Идентификация | Производитель/бренд | `manufacturer` | string | — | фильтр | Например: SKF/FAG/NSK/… |
| Классификация | Тип подшипника | `bearing_type` | enum | — | фильтр | Нормализованный тип (шариковый радиальный / конический / …). |
| Геометрия | Внутренний диаметр d | `d_mm` | number | мм | фильтр | Из каталога/карточки/стандарта. |
| Геометрия | Наружный диаметр D | `D_mm` | number | мм | фильтр | Из каталога/карточки/стандарта. |
| Геометрия | Ширина/высота B (или T) | `B_mm` | number | мм | фильтр | Для разных типов может быть B/T/H — фиксируем как `B_mm` + уточняем ниже. |
| Геометрия | Тип ширины (B/T/H) | `width_dim_code` | enum | — | контекст | `B` для радиальных, `T` для конических, `H` для упорных. |
| Нагрузки | Динамическая грузоподъёмность C | `dynamic_C_kN` | number | кН | ранжирование | Если есть в источнике (каталоги производителей). |
| Нагрузки | Статическая грузоподъёмность C0 | `static_C0_kN` | number | кН | ранжирование | Если есть в источнике. |
| Нагрузки | Предел усталостной нагрузки Pu | `fatigue_Pu_kN` | number | кН | ранжирование | Опционально; встречается в каталогах. |
| Скорость | Скорость reference | `reference_speed_rpm` | number | об/мин | ранжирование | Опционально; если источник даёт reference+limiting. |
| Скорость | Скорость limiting | `limiting_speed_rpm` | number | об/мин | фильтр/риск | Опционально; механический предел. |
| Скорость | Единый лимит оборотов | `rpm_limit` | number | об/мин | фильтр/риск | Если в источнике один лимит — пишем сюда (как в `catalog.csv`). |
| Масса | Масса | `mass_kg` | number | кг | ранжирование | Если есть. |
| Исполнение | Суффиксы (как строка) | `suffixes_raw` | string | — | контекст | Храним для трассы и перепроверки. |
| Исполнение | Суффиксы (нормализ.) | `suffixes_norm` | array[string] | — | фильтр | Разбиваем и приводим к единому виду. |
| Исполнение | Уплотнения/щитки (код) | `seal_code` | string | — | фильтр | 2RS/2RS1/2Z/… по справочнику суффиксов. |
| Исполнение | Уплотнения (тип) | `seal_type` | enum | — | фильтр | `open` / `contact_seal` / `non_contact_shield` / … (из `seal_code`). |
| Исполнение | Радиальный зазор | `clearance_class` | enum | — | фильтр | CN/C2/C3/C4… |
| Исполнение | Класс точности | `precision_class` | enum | — | фильтр | P0/P6/P5/P4/P2… |
| Исполнение | Сепаратор (код) | `cage_code` | string | — | ранжирование | J/M/TN9/… |
| Исполнение | Сепаратор (материал) | `cage_material` | enum | — | ранжирование | steel/brass/polyamide/… |
| Смазка | Смазка (код) | `lubricant_code` | string | — | ранжирование | LHT23/NS7/… |
| Смазка | Tmin | `temp_min_c` | number | °C | риск | Если выводим из кода смазки/исполнения. |
| Смазка | Tmax | `temp_max_c` | number | °C | риск | Аналогично. |
| Источники | URL источника | `source_url` | string | — | трасса | Из `nomenclature.csv`/парсеров; трассировка обязательна. |
| Источники | Файл источника | `source_file` | string | — | трасса | Из inbox/processed/… |
| Качество | Дата обновления записи | `updated_at` | date | — | контроль | Когда обновили/перепарсили. |
| Качество | Флаги качества | `dq_flags` | array[string] | — | контроль | Например: `missing_load`, `suffix_ambiguous`, `dim_conflict`. |

## 2. Таблица связей `bearings_crossref`

| Группа | Колонка (RU) | Переменная (var_key) | Тип | Роль | Правило заполнения |
|---|---|---|---|---|---|
| Откуда | Обозначение исходное | `from_designation` | string | вход | Как пришло (ГОСТ или ISO). |
| Откуда | Система исходная | `from_system` | enum | вход | `GOST`/`ISO`/… |
| Куда | Производитель назначения | `to_manufacturer` | string | выход | SKU-бренд назначения. |
| Куда | Обозначение аналога | `to_designation` | string | выход | Код у производителя. |
| Семантика | Тип соответствия | `match_grade` | enum | фильтр | `exact` / `functional` / `unknown` (из notes/правил). |
| Семантика | Примечание | `match_notes` | string | контекст | Например: «отличия в уплотнениях» (как в `equivalents.csv`). |
| Источники | URL источника | `source_url` | string | трасса | Как у `nomenclature.csv`. |
| Источники | Файл источника | `source_file` | string | трасса | Как у `nomenclature.csv`. |
| Качество | Уверенность | `confidence` | number | ранжирование | 0–1: правило/источник/повторяемость. |
| Качество | Дата обновления | `updated_at` | date | контроль | Когда перепроверили связь. |

## Пример заполнения из текущих датасетов

Ниже приведены строки, заполненные значениями из `catalog.csv`, `equivalents.csv` и `nomenclature.csv`. Поля, отсутствующие в источнике, оставлены пустыми.

### Пример: `bearings_catalog` (источник `catalog.csv`)

| designation_base | designation_full | designation_system | manufacturer | bearing_type | d_mm | D_mm | B_mm | width_dim_code | dynamic_C_kN | static_C0_kN | mass_kg | reference_speed_rpm | limiting_speed_rpm | rpm_limit | suffixes_raw | suffixes_norm | seal_code | seal_type | clearance_class | precision_class | cage_code | cage_material | lubricant_code | temp_min_c | temp_max_c | source_url | source_file | updated_at | dq_flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6200 | 6200 |  | generic | ball_radial | 10 | 30 | 9 | B | 5.07 | 2.36 | 0.032 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | catalog.csv |  |  |
| 6201 | 6201 |  | generic | ball_radial | 12 | 32 | 10 | B | 6.89 | 3.10 | 0.037 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | catalog.csv |  |  |

### Пример: `bearings_crossref` (источник `equivalents.csv`)

| from_designation | from_system | to_manufacturer | to_designation | match_grade | match_notes | source_url | source_file | confidence | updated_at |
|---|---|---|---|---|---|---|---|---|---|
| 6200 |  | SKF | 6200 | exact |  |  | equivalents.csv |  |  |
| 6200 |  | FAG | 6200 | exact |  |  | equivalents.csv |  |  |

### Пример: `bearings_crossref` (источник `nomenclature.csv`)

| from_designation | from_system | to_manufacturer | to_designation | match_grade | match_notes | source_url | source_file | confidence | updated_at |
|---|---|---|---|---|---|---|---|---|---|
| 2206 | GOST | 10-ГПЗ | N206 |  |  | https://aprom.by/cgi-bin/nomenclature.pl?brand=10-ГПЗ | 10-ГПЗ.md |  |  |

## Правила сопоставления

### Жёсткие фильтры (MVP)

1. **Тип подшипника** — соответствие `bearing_type` обязательно.
2. **Габариты** — совпадение `d_mm`/`D_mm`/`B_mm`.
3. **Ключевые суффиксы** — уплотнения, класс точности, радиальный зазор.

### Ранжирование (если кандидатов несколько)

- `dynamic_C_kN` и `static_C0_kN` — приоритет выше при равных размерах.
- `reference_speed_rpm` и `limiting_speed_rpm` — приоритет для высокооборотных узлов.
- Дополнительные признаки исполнения (`cage_material`, `lubricant_code`).

### Риски и ограничения

- Замена открытого исполнения на 2RS уменьшает допустимые обороты — фиксируем как риск.
- Отличия по зазору (CN↔C3) допустимы только при учёте посадок и температуры — фиксируем в `match_notes` и `dq_flags`.
- Суффиксы разных производителей могут обозначать одинаковые признаки, поэтому нормализация суффиксов — отдельный слой.

## Минимальный контракт данных для ИИ

Для интеграции с ИИ полезно фиксировать единый JSON-контракт.

```json
{
  "query": {
    "designation_raw": "{{designation_raw}}",
    "manufacturer": "{{manufacturer}}",
    "designation_system": "{{designation_system}}",
    "d_mm": "{{d_mm}}",
    "D_mm": "{{D_mm}}",
    "B_mm": "{{B_mm}}",
    "suffixes_raw": "{{suffixes_raw}}"
  },
  "candidate": {
    "to_manufacturer": "{{to_manufacturer}}",
    "to_designation": "{{to_designation}}",
    "match_grade": "{{match_grade}}",
    "match_notes": "{{match_notes}}"
  },
  "data_lineage": {
    "source_url": "{{source_url}}",
    "source_file": "{{source_file}}",
    "updated_at": "{{updated_at}}"
  }
}
```

## Рекомендуемая последовательность обработки

1. Нормализовать обозначение в `designation_base` и `suffixes_raw`.
2. Привести суффиксы к `suffixes_norm` через справочник.
3. Применить жёсткие фильтры по типу и размерам.
4. Использовать `bearings_crossref` для связывания брендов.
5. Отсортировать кандидатов по нагрузкам и скоростям.
6. Выставить риски/ограничения в `dq_flags` и `match_notes`.
