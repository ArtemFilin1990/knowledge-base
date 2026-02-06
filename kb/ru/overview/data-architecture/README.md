---
id: KB-RU-000179
title: "Архитектура данных и энциклопедии: подшипники, РТИ, узлы, смазки"
topic: "data-architecture"
tags: ["данные", "схема", "подшипники", "рти", "узлы", "смазки"]
status: draft
source: "kb/ru/overview/data-architecture/README.md"
created: 2026-02-06
updated: 2026-02-06
---

# Архитектура данных и энциклопедии: подшипники, РТИ, узлы, смазки

Цель: единая схема БД + структура энциклопедии для инженерного подбора, закупки и обслуживания.

## Контекст применения
- Инженеры, закупка, сервис, продажи B2B
- Покрытие: подшипники качения/скольжения, РТИ (манжеты, O-/V-Ring, сальники), корпуса/узлы, смазки, материалы, стандарты
- Основа для подбора аналогов, расчётов и кросс-ссылок между БД и статьями

## ER-логика (текстово)
- bearings (PK) ↔ bearing_analogs (1:N) ↔ manufacturers (N:1)
- bearings ↔ standards (M:N через bearing_standards)
- bearings ↔ seals_rti / housings (совместимость, M:N через joint tables)
- seals_rti ↔ materials (N:1), greases (опция)
- o_rings, v_rings — частные таблицы для геометрии/профиля, связаны с materials
- housings ↔ bearings (M:N), housings ↔ standards
- greases ↔ materials (загуститель/база) ↔ standards (NLGI, ISO)
- materials ↔ standards (ISO, DIN, ГОСТ) для классов сталь/эластомер
- deprecations: любое изделие имеет поля is_active, superseded_by (FK)

## Таблицы (ядро)

### bearings
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Уникальный ключ |
| iso_designation | text | да | Базовое обозначение по ISO |
| type | enum | да | радиальный/упорный/конический/цилиндрический/игольчатый/скольжения |
| series | text | да | 62xx/63xx/NU/NJ/302xx и т.п. |
| inner_diameter_mm | numeric(6,2) | да | d |
| outer_diameter_mm | numeric(6,2) | да | D |
| width_mm | numeric(6,2) | да | B/T |
| load_dynamic_c_kN | numeric(8,2) | да | C |
| load_static_c0_kN | numeric(8,2) | да | C0 |
| speed_grease_rpm | int | да | Предельные обороты (смазка) |
| speed_oil_rpm | int | да | Предельные обороты (масло) |
| clearance | text | нет | CN/C3/C4 |
| accuracy_class | text | нет | P0/P6/P5/P4 |
| sealing_type | text | нет | open/2RS/2Z |
| material | fk materials | нет | Материал колец/тел |
| lubrication_type | text | нет | заложенная смазка/без смазки |
| operating_temp_min/ max | int | нет | Диапазон °C |
| mass_kg | numeric(8,3) | нет | Справочная масса |
| is_active | bool | да | Актуален? |
| superseded_by | fk bearings | нет | Снят, заменён на |
| notes | text | нет | Особенности |

### bearing_analogs
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| bearing_id | fk bearings | да | Базовое ISO |
| manufacturer_id | fk manufacturers | да | Бренд |
| code | text | да | Обозначение производителя |
| equivalence_type | enum | да | exact/functional |
| notes | text | нет | Отличия (зазор, уплотнение) |
| is_active | bool | да | Доступность |

### seals_rti (манжеты/сальники)
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| type | enum | да | манжета/сальник/V-ring |
| profile | text | да | Профиль (TC, SC, VA и т.д.) |
| inner_diameter_mm | numeric(6,2) | да | d |
| outer_diameter_mm | numeric(6,2) | да | D |
| thickness_mm | numeric(6,2) | да | B |
| pressure_limit_mpa | numeric(6,2) | нет | До 0.05/0.2 и т.д. |
| speed_limit_rpm | int | нет | Предельная скорость |
| temp_min/max_c | int | нет | Диапазон |
| material_id | fk materials | да | Эластомер |
| medium | text | нет | Масла/вода/агрессивные среды |
| is_active | bool | да | Актуален |
| superseded_by | fk seals_rti | нет | Замена |

### o_rings
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| standard | text | да | ISO 3601/ГОСТ |
| d_inner_mm | numeric(6,3) | да | Внутренний диаметр |
| cross_section_mm | numeric(6,3) | да | Сечение |
| hardness_shA | int | нет | Твёрдость |
| material_id | fk materials | да | Эластомер |
| temp_min/max_c | int | нет | Диапазон |
| medium | text | нет | Среда |
| is_active | bool | да | Актуален |
| superseded_by | fk o_rings | нет | Замена |

### housings
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| type | enum | да | UC/SAF/FL/PL/т.п. |
| bore_mm | numeric(6,2) | да | Под вал |
| bolt_pattern | text | да | Отверстия/шаг |
| material_id | fk materials | да | Чугун/сталь/пластик |
| sealing_option | text | нет | Без/сальники/лабиринт |
| grease_fitting | bool | нет | Наличие пресс-маслёнки |
| is_active | bool | да | Актуален |
| superseded_by | fk housings | нет | Замена |

### greases
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| name | text | да | Торговое имя |
| nlgi_class | int | да | NLGI 000–6 |
| base_oil | text | да | Минеральное/синтетика |
| thickener | text | да | Li-complex/Ca-sulfonate/PTFE |
| base_oil_visc_40/100_cst | numeric(6,1) | нет | Вязкость |
| temp_min/max_c | int | да | Диапазон |
| speed_factor_n_dm | int | нет | Предельный n·dm |
| water_resistance | text | нет | IPx/EMCOR |
| food_grade | bool | нет | NSF H1? |
| is_active | bool | да | Актуален |
| superseded_by | fk greases | нет | Замена |

### materials
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| class | enum | да | сталь/чугун/бронза/элaстомер/пластик |
| grade | text | да | 100Cr6, AISI 440C, NBR, FKM |
| hardness | text | нет | HRC/ShA |
| temp_min/max_c | int | нет | Диапазон применения |
| corrosion_resistance | text | нет | Да/по стандарту |
| notes | text | нет | Особенности |

### standards
| Поле | Тип | Обяз. | Описание |
|---|---|---|---|
| id (PK) | UUID | да | Ключ |
| code | text | да | ISO/DIN/ГОСТ номер |
| title | text | да | Название |
| scope | text | да | Размеры/допуски/материалы |
| status | enum | да | active/withdrawn |
| replaces | fk standards | нет | Чем заменён |
| replaced_by | fk standards | нет | Чем заменяет |

### junction tables (ключевые)
- bearing_standards(bearing_id, standard_id)
- bearing_housings(bearing_id, housing_id, fit, seal_kit)
- bearing_seals(bearing_id, seal_id, config) — для комплектов уплотнений
- housing_standards(housing_id, standard_id)
- grease_standards(grease_id, standard_id)

## Энциклопедия (статьи и связь с БД)
- Статья «Радиальный шариковый подшипник» → ссылка на таблицу `bearings`, поля: серия, зазор, допуск; связки: смазки, корпуса, уплотнения.
- Статья «Роликовый конический подшипник» → `bearings` (type=tapered), `bearing_analogs`.
- Статья «Манжета радиальная (TC)» → `seals_rti`, `materials`, совместимость с `bearings`.
- Статья «O-Ring по ISO 3601» → `o_rings`, `materials`, температура/среда.
- Статья «Подшипниковый узел UCFL» → `housings`, `bearing_housings`, `greases`.
- Статья «Смазка Li-Complex NLGI-2» → `greases`, `grease_standards`, применимость к скоростям/температурам.
- Статья «Материал 100Cr6» → `materials`, связанные `bearings`.
- Статья «Стандарты ISO 15 / ISO 281 / ГОСТ 520» → `standards`, применимость к `bearings`.

## Ключевые параметры (как хранить)
- Размеры: d/D/B мм (numeric), допуски — по ISO 492/PJ, r_min при необходимости.
- Нагрузки: C, C0 кН; для скольжения — p·v.
- Скорость: grease/oil rpm или n·dm (для смазок).
- Температура: мин/макс °C, при ссылке на материал/смазку.
- Среда: классификатор (масла, вода, агрессивные, пищевые).
- Герметизация: типы уплотнений (2RS/2Z/TC/VA) и совместимость.

## Подбор и логика (алгоритмы)
1. **По размерам**: фильтр по d, D, B; проверка r_min; исключить снятые (is_active=false).
2. **По нагрузке**: расчёт P = X·Fr + Y·Fa; сравнить с C/C0; для роликов — (C/P)^(10/3), для шариков — (C/P)^3.
3. **По температуре/среде**: пересечение диапазонов материала и смазки; исключить материалы несовместимые с средой.
4. **По скорости**: проверить rpm против grease/oil; для смазок — n·dm ≤ предел.
5. **Замена на аналог**: через `bearing_analogs` exact → прямой; functional → проверить зазор/уплотнение/скорость.
6. **При конфликте параметров**: безопасность/ресурс > температура > скорость > цена; фиксировать отклонения в notes.

## Типовые ошибки подбора
- Игнорирование clearance/accuracy при замене.
- Подбор манжеты без учёта среды/давления.
- Установка узла без проверки посадки корпуса/вала.
- Выбор смазки без учёта n·dm и температуры.

## Как выходит из строя
- Подшипники: выкрашивание дорожек, перегрев из-за смазки, износ при загрязнении.
- РТИ: термо-старение, разрыв кромки, задир при недостатке смазки.
- Узлы: проворачивание кольца, трещины корпуса.

## Правила качества
- Единые единицы: мм, кН, °C, rpm.
- Стандартизированные enums и справочники (series, materials, clearance, accuracy).
- Отсутствие данных → поле NULL + пояснение в notes.
- Статусы активностей и замены обязательны.

## Примеры
- Подбор: d=35/D=72 → 6207 или 6307; проверка C и r_min по стандарту.
- Замена: 6305-2RS SKF → functional аналог 180305 (ГОСТ) при совпадении зазора.
- РТИ: вал 50 мм, среда масло 120 °C → манжета FKM TC, совместима с 6210.

## См. также
- [База знаний по подшипникам](../bearings/INDEX.md)
- [Наборы данных](../bearings/datasets/README.md)
- [Процессы генерации базы](../bearings-knowledge-base/README.md)
- [ISO 15 — Габаритные размеры](../bearings/standards/iso-15/README.md)
- [ISO 281 — Грузоподъёмность и ресурс](../bearings/standards/iso-281/README.md)

## Источники и примечания
- Опорные стандарты: ISO 15, ISO 281, ISO 492, ISO 3601, ГОСТ 520-2011, NLGI.
- Конвенции датасетов: см. `kb/ru/bearings/datasets/README.md`.

## Контроль качества
- [x] Есть метаданные (id/topic/status/source)
- [x] Понятно без внешнего контекста
- [x] Есть примеры
- [x] Нет противоречий
- [x] Есть 3–7 ссылок «См. также»
- [ ] Для `status: verified` нет `[[TBD]]`
