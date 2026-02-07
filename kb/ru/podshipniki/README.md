---
id: KB-RU-000180
title: "Техническое задание: база знаний «Подшипники»"
topic: "podshipniki"
tags: ["подшипники", "структура", "пайплайн", "метаданные"]
status: draft
source: "kb/ru/overview/data-architecture/README.md"
created: "2026-02-06"
updated: "2026-02-06"
---

# Техническое задание: база знаний «Подшипники»

Кому и зачем: владельцам базы и авторам статей, чтобы вести единый раздел «Подшипники» с чёткой структурой, метаданными и трассировкой источников от сырья до индексов.

## Контекст применения
- Пользователи: инженеры, закупка, сервис, продажи B2B.
- Покрытие: подшипники качения/скольжения, РТИ (манжеты, O-/V-Ring), корпуса/узлы, смазки, материалы, стандарты.
- Вход: сырьё в `inbox/`, каталоги производителей, прайсы, стандарты; выход: статьи `kb/ru/podshipniki` + связанные карточки/датасеты.

## Ключевые пункты
- Целевая структура раздела:
  ```
  kb/ru/podshipniki/
  ├── README.md            # этот ТЗ + индекс раздела
  ├── concepts/            # объяснения и классификация (ссылки на bearings/)
  ├── datasets/            # описание CSV/структур (синхронизировано с kb/ru/bearings/datasets)
  ├── playbooks/           # процедуры ingest/очистки/публикации
  └── cards/               # ссылки и правила для карточек подшипников
  ```
- Метаданные: единый YAML front-matter (id/title/topic/tags/status/source/created/updated); для карточек — расширение `designation`, `dims`, `equivalents`, `load_capacity` по `_templates/bearing-card.md`.
- Пайплайн: intake → дедупликация → разбор → статьи/карточки/датасеты → обновление индексов → валидация → архив сырья.
- Трассировка источников: поле `source` указывает исходный файл в `inbox/`; дубли фиксируются в `_meta/dedup_log.md` и `_meta/dedup_index.json`; индексы связывают статьи с датасетами и карточками.

## Алгоритм / шаги
1. **Intake**: положить сырьё в `inbox/` без ручной сортировки.
2. **Дедупликация**: посчитать sha256 содержимого, сверить с `_meta/dedup_index.json`; при дубле — записать в `_meta/dedup_log.md`, не публиковать новую статью.
3. **Разбор и декомпозиция**: разложить материал на статьи/карточки; выделить сущности (подшипники, уплотнения, корпуса, смазки) и привязать к существующим датасетам в `kb/ru/bearings/datasets/`.
4. **Создание/обновление статей**: по `_templates/article.md`, новые ID начиная с KB-RU-000180; `source` = имя файла в `inbox/` или путь к каталогу; `topic` = `podshipniki` или специализированный сабтопик.
5. **Карточки и датасеты**: карточки подшипников — по `_templates/bearing-card.md`; структурированные данные — обновлять CSV и паспорт в `kb/ru/bearings/datasets/README.md` с ссылкой на источник.
6. **Индексы и связи**: обновить `kb/ru/INDEX.md`, этот файл как локальный индекс, а также тематические листы (`kb/ru/bearings/INDEX.md`, `kb/ru/bearings-knowledge-base/README.md`) при добавлении новых материалов.
7. **Валидация**: запустить `python tests/check_kb_links.py` и при необходимости `python scripts/kb_quality_gate.py` / `python scripts/validate_bearing_cards.py`.
8. **Архивирование сырья**: переместить обработанные файлы в `inbox/processed/YYYY-MM/` с сохранением имени для трассировки.

## Примеры
- Трассировка: `inbox/SKF-6205-catalog.pdf` → статья `kb/ru/podshipniki/concepts/radial-ball/README.md` (source указывает PDF) → карточка `kb/ru/bearings/cards/6205/README.md` → ссылка в `kb/ru/bearings/INDEX.md`.
- Структура связки: прайс `inbox/price-2025.xlsx` → нормализованная таблица в `kb/ru/bearings/datasets/catalog.csv` + паспорт обновления в `kb/ru/bearings/datasets/README.md` → индексация ссылки в `kb/ru/podshipniki/README.md` и `kb/ru/bearings-price-list/README.md`.

## Частые ошибки
- Отсутствие ссылки на исходный файл в поле `source`.
- Пропуск обновления индексов (`kb/ru/INDEX.md`, тематические листы) после добавления статей.
- Использование новых ID без проверки на максимальный номер (текущий максимум: KB-RU-000179).

## См. также
- [Архитектура данных и энциклопедии](../overview/data-architecture/README.md)
- [База знаний по подшипникам](../bearings/INDEX.md)
- [Процессы генерации базы](../bearings-knowledge-base/README.md)
- [Шаблон статьи](../../../_templates/article.md)
- [Шаблон карточки подшипника](../../../_templates/bearing-card.md)

## Источники и примечания
- Source: `kb/ru/overview/data-architecture/README.md`
- Notes: использованы текущие правила из `_meta/repository-audit.md` и структуры `kb/ru/bearings/`.

## Контроль качества
- [x] Есть метаданные (id/topic/status/source)
- [x] Понятно без внешнего контекста
- [x] Есть примеры
- [x] Нет противоречий
- [x] Есть 3–7 ссылок «См. также»
- [ ] Для `status: verified` нет `[[TBD]]`

## Статьи

- [Подшипниковые заводы на территории СНГ](./podshipnikovye-zavody-na-territorii-sng/README.md)

- [Коды ТН ВЭД на подшипники.](./kody-tn-ved-na-podshipniki/README.md)

- [Нагрузка на подшипники.](./nagruzka-na-podshipniki/README.md)

- [Классификация подшипников](./klassifikatsiya-podshipnikov/README.md)

- [Предельная частота вращения подшипника.](./predelnaya-chastota-vrascheniya-podshipnika/README.md)

- [Слово ПОДШИПНИК на разных языках мира.](./slovo-podshipnik-na-raznyh-yazykah-mira/README.md)

- [Подшипники в электродвигателях и основные причины отказов.](./podshipniki-v-elektrodvigatelyah-i-osnovnye-prichi/README.md)

- [Как выбрать подшипник .](./kak-vybrat-podshipnik/README.md)

- [Из чего состоит подшипник](./iz-chego-sostoit-podshipnik/README.md)

- [Подшипниковые узлы. Корпусные подшипники.](./podshipnikovye-uzly-korpusnye-podshipniki/README.md)

- [Редукторы](./reduktory/README.md)

- [Втулки скольжения. Подшипники скольжения.](./vtulki-skolzheniya-podshipniki-skolzheniya/README.md)

- [Смазка для подшипников.](./smazka-dlya-podshipnikov/README.md)

- [Автомобильные комплекты подшипников SKF, FAG, SNR, TIMKEN, FERSA A&S, QH](./avtomobilnye-komplekty-podshipnikov-skf-fag-snr-ti/README.md)

- [Основные причины повреждения подшипников.](./osnovnye-prichiny-povrezhdeniya-podshipnikov/README.md)

- [Онлайн каталоги подшипников.](./onlayn-katalogi-podshipnikov/README.md)

- [Предварительный натяг подшипников. Преднатяг.](./predvaritelnyy-natyag-podshipnikov-prednatyag/README.md)

- [Гибридные подшипники.](./gibridnye-podshipniki/README.md)

- [С улыбкой о подшипниках :)](./s-ulybkoy-o-podshipnikah/README.md)

- [Советы SKF в выборе ступичного подшипника.](./sovety-skf-v-vybore-stupichnogo-podshipnika/README.md)

- [Симптомы неисправного подшипника ступицы колеса автомобиля.](./simptomy-neispravnogo-podshipnika-stupitsy-kolesa-/README.md)

- [Втулки тапербуш - TAPER BUSH.](./vtulki-taperbush-taper-bush/README.md)

- [Интересное о подшипниках](./interesnoe-o-podshipnikah/README.md)
