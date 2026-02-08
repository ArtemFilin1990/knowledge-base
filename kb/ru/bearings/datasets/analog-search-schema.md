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
| Идентификация | Обозначение | `designation` | string | — | фильтр | Как в `catalog.csv` (например, `6305-2RS`). |
| Классификация | Тип подшипника | `type` | enum | — | фильтр | Значение из `catalog.csv` (например, `ball_radial`). |
| Классификация | Серия | `series` | string | — | фильтр | Серийный код из `catalog.csv` (например, `62xx`). |
| Геометрия | Внутренний диаметр d | `d_mm` | number | мм | фильтр | Поле `d_mm` из `catalog.csv`. |
| Геометрия | Наружный диаметр D | `D_mm` | number | мм | фильтр | Поле `D_mm` из `catalog.csv`. |
| Геометрия | Ширина B | `B_mm` | number | мм | фильтр | Поле `B_mm` из `catalog.csv`. |
| Нагрузки | Динамическая грузоподъёмность C | `C_kN` | number | кН | ранжирование | Поле `C_kN` из `catalog.csv`. |
| Нагрузки | Статическая грузоподъёмность C0 | `C0_kN` | number | кН | ранжирование | Поле `C0_kN` из `catalog.csv`. |
| Масса | Масса | `mass_kg` | number | кг | ранжирование | Поле `mass_kg` из `catalog.csv`. |
| Скорость | Предельная скорость (смазка) | `rpm_grease` | number | об/мин | фильтр/риск | Поле `rpm_grease` из `catalog.csv`. |
| Скорость | Предельная скорость (масло) | `rpm_oil` | number | об/мин | фильтр/риск | Поле `rpm_oil` из `catalog.csv`. |
| Идентификация | Производитель/бренд | `manufacturer` | string | — | фильтр | Поле `manufacturer` из `catalog.csv`. |
| Источники | Источник записи | `source` | string | — | трасса | Поле `source` из `catalog.csv` (например, `ISO_catalog`). |

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

| designation | type | series | d_mm | D_mm | B_mm | C_kN | C0_kN | mass_kg | rpm_grease | rpm_oil | manufacturer | source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6200 | ball_radial | 62xx | 10 | 30 | 9 | 5.07 | 2.36 | 0.032 | 26000 | 34000 | generic | ISO_catalog |
| 6201 | ball_radial | 62xx | 12 | 32 | 10 | 6.89 | 3.10 | 0.037 | 22000 | 28000 | generic | ISO_catalog |

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

1. **Тип подшипника** — соответствие `type` обязательно.
2. **Габариты** — совпадение `d_mm`/`D_mm`/`B_mm`.
3. **Ключевые суффиксы** — уплотнения, класс точности, радиальный зазор (если суффиксы есть в запросе).

### Ранжирование (если кандидатов несколько)

- `C_kN` и `C0_kN` — приоритет выше при равных размерах.
- `rpm_grease` и `rpm_oil` — приоритет для высокооборотных узлов.
- При равных параметрах учитываем предпочтения по производителю.

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

1. Нормализовать обозначение и выделить суффиксы из `designation`.
2. Привести суффиксы к нормализованному виду через справочник.
3. Применить жёсткие фильтры по типу и размерам.
4. Использовать `bearings_crossref` для связывания брендов.
5. Отсортировать кандидатов по нагрузкам и скоростям.
6. Выставить риски/ограничения в `dq_flags` и `match_notes`.
