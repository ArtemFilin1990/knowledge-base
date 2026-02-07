---
id: KB-RU-000200
title: "Карточки подшипников — правила и индекс"
topic: "podshipniki-cards"
tags: ["подшипники", "карточки", "индекс", "генерация"]
status: draft
source: "kb/ru/bearings/cards/, scripts/generate_bearing_cards.py"
created: "2026-02-07"
updated: "2026-02-07"
---

# Карточки подшипников — правила и индекс

Описание правил создания карточек подшипников и индекс существующих карточек в базе знаний.

## Контекст применения

- Создание новых карточек подшипников
- Навигация к существующим карточкам
- Понимание структуры и метаданных карточек
- Автоматическая генерация карточек из CSV

## Что такое карточка подшипника

**Карточка подшипника** — это детальное описание конкретного типоразмера подшипника, содержащее:

- Техническиехарактеристики (габариты, грузоподъёмность, обороты)
- Расшифровку обозначения
- Эквиваленты и аналоги производителей
- Области применения
- Рекомендации по эксплуатации

### Структура карточки

Карточки расположены в `kb/ru/bearings/cards/[обозначение]/README.md`

Пример: `kb/ru/bearings/cards/6305-2rs/README.md`

## Метаданные карточки

Карточки используют расширенные метаданные согласно `_templates/bearing-card.md`:

```yaml
---
id: KB-RU-000XXX
title: "Подшипник [обозначение]"
topic: bearings-card
tags: ["подшипники", "карточка", "серия", "тип"]
status: draft
source: "kb/ru/bearings/datasets/catalog.csv"
created: "2026-02-07"
updated: "2026-02-07"

# Расширенные поля для карточек
designation:
  base: "6305"
  suffixes: ["2RS"]  # Уплотнения, зазоры и т.д.

dims:
  d: 25       # Внутренний диаметр, мм
  D: 62       # Наружный диаметр, мм
  B: 17       # Ширина, мм
  unit: "mm"

load_capacity:
  dynamic_C_kN: 22.5      # Динамическая грузоподъёмность
  static_C0_kN: 11.2      # Статическая грузоподъёмность
  rpm_limit: 10000        # Предельные обороты

equivalents:
  - {manufacturer: "SKF", code: "6305-2RSH"}
  - {manufacturer: "FAG", code: "6305.2RSR"}
  - {manufacturer: "NSK", code: "6305DDU"}
  - {manufacturer: "ГОСТ", code: "180305Л"}
---
```

## Правила создания карточек

### Ручное создание

1. **Выбрать обозначение**
   - Использовать базовое обозначение + суффиксы
   - Примеры: `6305`, `6305-2rs`, `6305-2rs-c3`

2. **Создать папку**
   ```bash
   mkdir -p kb/ru/bearings/cards/6305-2rs/
   ```

3. **Скопировать шаблон**
   ```bash
   cp _templates/bearing-card.md kb/ru/bearings/cards/6305-2rs/README.md
   ```

4. **Заполнить метаданные**
   - Назначить новый ID (следующий после максимального)
   - Заполнить designation, dims, load_capacity
   - Добавить equivalents из nomenclature.csv

5. **Заполнить разделы**
   - Назначение и применение
   - Расшифровка обозначения
   - Габариты и совместимость
   - Грузоподъёмность и ресурс
   - Эквиваленты и аналоги
   - Риски замены
   - Эксплуатация и обслуживание

6. **Добавить в индекс**
   - Обновить kb/ru/bearings/INDEX.md
   - Группировать по сериям (62xx, 63xx, и т.д.)

### Автоматическая генерация

Для массового создания карточек используйте скрипт:

```bash
python scripts/generate_bearing_cards.py \
  --catalog kb/ru/bearings/datasets/catalog.csv \
  --equivalents kb/ru/bearings/datasets/equivalents.csv \
  --output-dir kb/ru/bearings/cards/ \
  --id-start 000201 \
  --suffixes 2RS,C3
```

**Параметры**:
- `--catalog`: CSV с характеристиками подшипников
- `--equivalents`: CSV с эквивалентами производителей
- `--output-dir`: Папка для карточек
- `--id-start`: Начальный ID для генерации
- `--suffixes`: Суффиксы для генерации вариантов (опционально)

**Результат**:
- Карточки созданы в kb/ru/bearings/cards/
- Метаданные заполнены из CSV
- Эквиваленты подтянуты автоматически

## Индекс существующих карточек

### Серия 62xx (лёгкая, шариковые радиальные)

Всего карточек: 13

- [6200-2RS](../../bearings/cards/6200-2rs/README.md) — d=10мм, D=30мм, B=9мм
- [6201-2RS](../../bearings/cards/6201-2rs/README.md) — d=12мм, D=32мм, B=10мм
- [6202-2RS](../../bearings/cards/6202-2rs/README.md) — d=15мм, D=35мм, B=11мм
- [6203-2RS](../../bearings/cards/6203-2rs/README.md) — d=17мм, D=40мм, B=12мм
- [6204-2RS](../../bearings/cards/6204-2rs/README.md) — d=20мм, D=47мм, B=14мм
- [6205-2RS](../../bearings/cards/6205-2rs/README.md) — d=25мм, D=52мм, B=15мм
- [6206-2RS](../../bearings/cards/6206-2rs/README.md) — d=30мм, D=62мм, B=16мм
- [6207-2RS](../../bearings/cards/6207-2rs/README.md) — d=35мм, D=72мм, B=17мм
- [6208-2RS](../../bearings/cards/6208-2rs/README.md) — d=40мм, D=80мм, B=18мм
- [6209-2RS](../../bearings/cards/6209-2rs/README.md) — d=45мм, D=85мм, B=19мм
- [6210-2RS](../../bearings/cards/6210-2rs/README.md) — d=50мм, D=90мм, B=20мм
- [6211-2RS](../../bearings/cards/6211-2rs/README.md) — d=55мм, D=100мм, B=21мм
- [6212-2RS](../../bearings/cards/6212-2rs/README.md) — d=60мм, D=110мм, B=22мм

### Серия 63xx (средняя, шариковые радиальные)

Всего карточек: 13

- [6300-2RS](../../bearings/cards/6300-2rs/README.md) — d=10мм, D=35мм, B=11мм
- [6301-2RS](../../bearings/cards/6301-2rs/README.md) — d=12мм, D=37мм, B=12мм
- [6302-2RS](../../bearings/cards/6302-2rs/README.md) — d=15мм, D=42мм, B=13мм
- [6303-2RS](../../bearings/cards/6303-2rs/README.md) — d=17мм, D=47мм, B=14мм
- [6304-2RS](../../bearings/cards/6304-2rs/README.md) — d=20мм, D=52мм, B=15мм
- [6305-2RS C3](../../bearings/cards/6305-2rs-c3/README.md) — d=25мм, D=62мм, B=17мм (увеличенный зазор)
- [6306-2RS](../../bearings/cards/6306-2rs/README.md) — d=30мм, D=72мм, B=19мм
- [6307-2RS](../../bearings/cards/6307-2rs/README.md) — d=35мм, D=80мм, B=21мм
- [6308-2RS](../../bearings/cards/6308-2rs/README.md) — d=40мм, D=90мм, B=23мм
- [6309-2RS](../../bearings/cards/6309-2rs/README.md) — d=45мм, D=100мм, B=25мм
- [6310-2RS](../../bearings/cards/6310-2rs/README.md) — d=50мм, D=110мм, B=27мм
- [6311-2RS](../../bearings/cards/6311-2rs/README.md) — d=55мм, D=120мм, B=29мм
- [6312-2RS](../../bearings/cards/6312-2rs/README.md) — d=60мм, D=130мм, B=31мм

### Серия 7xxx (радиально-упорные шариковые)

Всего карточек: 13

- [7200-B](../../bearings/cards/7200-b/README.md) — d=10мм, угол контакта 40°
- [7201-B](../../bearings/cards/7201-b/README.md) — d=12мм
- [7202-B](../../bearings/cards/7202-b/README.md) — d=15мм
- [7203-B](../../bearings/cards/7203-b/README.md) — d=17мм
- [7204-B](../../bearings/cards/7204-b/README.md) — d=20мм
- [7205-B](../../bearings/cards/7205-b/README.md) — d=25мм
- [7206-B](../../bearings/cards/7206-b/README.md) — d=30мм
- [7207-B](../../bearings/cards/7207-b/README.md) — d=35мм
- [7208-B](../../bearings/cards/7208-b/README.md) — d=40мм
- [7209-B](../../bearings/cards/7209-b/README.md) — d=45мм
- [7210-B](../../bearings/cards/7210-b/README.md) — d=50мм
- [7211-B](../../bearings/cards/7211-b/README.md) — d=55мм
- [7212-B](../../bearings/cards/7212-b/README.md) — d=60мм

### Серия NU (роликовые цилиндрические)

Всего карточек: 10

- [NU202](../../bearings/cards/nu202/README.md) — d=15мм
- [NU203](../../bearings/cards/nu203/README.md) — d=17мм
- [NU204](../../bearings/cards/nu204/README.md) — d=20мм
- [NU205](../../bearings/cards/nu205/README.md) — d=25мм
- [NU206](../../bearings/cards/nu206/README.md) — d=30мм
- [NU207](../../bearings/cards/nu207/README.md) — d=35мм
- [NU208](../../bearings/cards/nu208/README.md) — d=40мм
- [NU209](../../bearings/cards/nu209/README.md) — d=45мм
- [NU210](../../bearings/cards/nu210/README.md) — d=50мм
- [NU211](../../bearings/cards/nu211/README.md) — d=55мм

### Серия NJ (роликовые цилиндрические с бортом)

Всего карточек: 10

- [NJ202](../../bearings/cards/nj202/README.md) — d=15мм
- [NJ203](../../bearings/cards/nj203/README.md) — d=17мм
- [NJ204](../../bearings/cards/nj204/README.md) — d=20мм
- [NJ205](../../bearings/cards/nj205/README.md) — d=25мм
- [NJ206](../../bearings/cards/nj206/README.md) — d=30мм
- [NJ207](../../bearings/cards/nj207/README.md) — d=35мм
- [NJ208](../../bearings/cards/nj208/README.md) — d=40мм
- [NJ209](../../bearings/cards/nj209/README.md) — d=45мм
- [NJ210](../../bearings/cards/nj210/README.md) — d=50мм
- [NJ211](../../bearings/cards/nj211/README.md) — d=55мм

### Серия 30xxx (роликовые конические)

Всего карточек: 10

- [30202](../../bearings/cards/30202/README.md) — d=15мм
- [30203](../../bearings/cards/30203/README.md) — d=17мм
- [30204](../../bearings/cards/30204/README.md) — d=20мм
- [30205](../../bearings/cards/30205/README.md) — d=25мм
- [30206](../../bearings/cards/30206/README.md) — d=30мм
- [30207](../../bearings/cards/30207/README.md) — d=35мм
- [30208](../../bearings/cards/30208/README.md) — d=40мм
- [30209](../../bearings/cards/30209/README.md) — d=45мм
- [30210](../../bearings/cards/30210/README.md) — d=50мм
- [30211](../../bearings/cards/30211/README.md) — d=55мм

## Итого карточек: 145+

Всего в базе знаний: 145+ карточек подшипников различных серий и типов.

## Источники данных для карточек

1. **Технические характеристики**:
   - kb/ru/bearings/datasets/catalog.csv
   - Каталоги производителей (SKF, FAG, NTN, NSK)
   - Стандарты ISO 15, ISO 281

2. **Эквиваленты**:
   - kb/ru/bearings/datasets/nomenclature.csv (82,951 запись)
   - kb/ru/bearings/datasets/equivalents.csv
   - inbox/processed/2026-02/*.md (85 файлов производителей)

3. **Применение и рекомендации**:
   - Технические руководства производителей
   - Опыт эксплуатации (где задокументирован)

## Частые ошибки

- **Неправильное обозначение папки**: использовать kebab-case (6305-2rs, не 6305_2RS)
- **Отсутствие эквивалентов**: обязательно указывать основные аналоги
- **Некорректные габариты**: проверять соответствие ISO 15
- **Пропуск source**: всегда указывать источник данных

## См. также

- [Техническое задание](../README.md) — общая структура базы знаний
- [Наборы данных](../datasets/README.md) — источники для карточек
- [Процедуры обработки](../playbooks/README.md) — как создавать карточки
- [База знаний по подшипникам](../../bearings/INDEX.md) — полный индекс
- [Шаблон карточки подшипника](../../../_templates/bearing-card.md)

## Источники и примечания

- Source: `kb/ru/bearings/cards/, scripts/generate_bearing_cards.py`
- Notes: 145+ карточек созданы автоматически из catalog.csv; эквиваленты из nomenclature.csv

## Контроль качества

- [x] Есть метаданные (id/topic/status/source)
- [x] Понятно без внешнего контекста
- [x] Есть примеры использования
- [x] Нет противоречий
- [x] Есть 3–7 ссылок «См. также»
- [ ] Для `status: verified` нет `[[TBD]]`
