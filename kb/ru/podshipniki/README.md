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

- [Как подобрать сальник или манжету по размерам   Подшипники в Беларуси   Aprom](./kak-podobrat-salnik-ili-manzhetu-po-razmeram-podsh/README.md)

- [Каталог подшипников NKE.](./katalog-podshipnikov-nke/README.md)

- [CONTENTS .......................................................................](./contents/README.md)

- [Sealed Spherical Roller Bearings](./sealed-spherical-roller-bearings/README.md)

- [Needle Roller Cages for Big End  dup2](./needle-roller-cages-for-big-end-dup2/README.md)

- [Каталог подшипников SNFA.](./katalog-podshipnikov-snfa/README.md)

- [Automotive Catalog 2011](./automotive-catalog-2011/README.md)

- [CRAFT BEARINGS QUALITY CONTROL](./craft-bearings-quality-control/README.md)

- [Обгонные муфты INA - HF, HFL.](./obgonnye-mufty-ina-hf-hfl/README.md)

- [Сферические роликоподшипники FAG](./sfericheskie-rolikopodshipniki-fag/README.md)

- [Needle Roller Bearings  dup2](./needle-roller-bearings-dup2/README.md)

- [Catalogue 2013](./catalogue-2013/README.md)

- [Каталог подшипников IBB.](./katalog-podshipnikov-ibb/README.md)

- [TIMKEN PRODUCTS CATALOG D1  dup2](./timken-products-catalog-d1-dup2/README.md)

- [brands (2)  dup2](./brands-2-dup2/README.md)

- [Каталог подшипников IBC.](./katalog-podshipnikov-ibc/README.md)

- [Каталог подшипников APB для станкостроения.](./katalog-podshipnikov-apb-dlya-stankostroeniya/README.md)

- [Каталог подшипников NMB.](./katalog-podshipnikov-nmb/README.md)

- [Каталог зубчатых шестерен без ступицы  dup2](./katalog-zubchatyh-shesteren-bez-stupitsy-dup2/README.md)

- [Каталог подшипников SNH](./katalog-podshipnikov-snh/README.md)

- [Общий каталог подшипников STC-STEYR](./obschiy-katalog-podshipnikov-stc-steyr/README.md)

- [Каталог подшипников ЕПК - ОАО "Завод авиационных подшипников"](./katalog-podshipnikov-epk-oao-zavod-aviatsionnyh-po/README.md)

- [Ball and Roller Bearings](./ball-and-roller-bearings/README.md)

- [Автомобильные комплекты подшипников SKF, FAG, SNR, TIMKEN, FERSA A&S, QH   Подшипники в Беларуси](./avtomobilnye-komplekty-podshipnikov-skf-fag-snr-ti/README.md)

- [Игольчатые роликоподшипники NTN  dup2](./igolchatye-rolikopodshipniki-ntn-dup2/README.md)

- [High precision ball bearings](./high-precision-ball-bearings/README.md)

- [Крестовины карданного вала и крестовины вала рулевого управления   Подшипники в Беларуси](./krestoviny-kardannogo-vala-i-krestoviny-vala-rulev/README.md)

- [Caged Roller Bearings  dup2](./caged-roller-bearings-dup2/README.md)

- [Каталог сверхточных подшипников NSK.](./katalog-sverhtochnyh-podshipnikov-nsk/README.md)

- [Deep Groove Ball Bearings](./deep-groove-ball-bearings/README.md)

- [Каталог десятого подшипникового завода](./katalog-desyatogo-podshipnikovogo-zavoda/README.md)

- [CYLINDRICAL ROLLER BEARING CATALOG  dup2](./cylindrical-roller-bearing-catalog-dup2/README.md)

- [Каталог подшипников LSA GROUP INC для грузовой автотехники.](./katalog-podshipnikov-lsa-group-inc-dlya-gruzovoy-a/README.md)

- [Подшипники качения](./podshipniki-kacheniya/README.md)

- [Каталог тонких подшипников подшипников Kaydon высокоточной серии Reali-Slim.](./katalog-tonkih-podshipnikov-podshipnikov-kaydon-vy/README.md)

- [Общий каталог подшипников  бренда Самарский Подшипник](./obschiy-katalog-podshipnikov-brenda-samarskiy-pods/README.md)

- [Каталог подшипников ЕПК - ОАО "Завод авиационных подшипников"](./katalog-podshipnikov-epk-oao-zavod-aviatsionnyh-po/README.md)

- [КИТАЙСКИЕ ПОДШИПНИКИ  Подшипники в Беларуси   Aprom](./kitayskie-podshipniki-podshipniki-v-belarusi-aprom/README.md)

- [Каталог цилиндрических бессепараторных подшипников APB - серия SL.](./katalog-tsilindricheskih-besseparatornyh-podshipni/README.md)

- [Гибридные подшипники](./gibridnye-podshipniki/README.md)

- [Каталог высокоточных и специальных подшипников качения AKE.](./katalog-vysokotochnyh-i-spetsialnyh-podshipnikov-k/README.md)

- [Радиальные роликовые подшипники с цилиндрическими роликами](./radialnye-rolikovye-podshipniki-s-tsilindricheskim/README.md)

- [Как выбрать подшипник   Подшипники в Беларуси](./kak-vybrat-podshipnik-podshipniki-v-belarusi/README.md)

- [Каталог игольчатых подшипников NBS.](./katalog-igolchatyh-podshipnikov-nbs/README.md)

- [Из чего состоит подшипник   Подшипники в Беларуси](./iz-chego-sostoit-podshipnik-podshipniki-v-belarusi/README.md)

- [High precision ball bearings  dup2](./high-precision-ball-bearings-dup2/README.md)

- [Общий каталог подшипников Kaydon.](./obschiy-katalog-podshipnikov-kaydon/README.md)

- [Каталог подшипников для экстремальных температур BECO.](./katalog-podshipnikov-dlya-ekstremalnyh-temperatur/README.md)

- [Каталог подшипников DAS LAGER.](./katalog-podshipnikov-das-lager/README.md)

- [Каталог зубчатых шестерен с каленом зубом и со ступицей  dup3](./katalog-zubchatyh-shesteren-s-kalenom-zubom-i-so-s/README.md)

- [Каталог подшипников LSA GROUP INC для легковых автомобилей.](./katalog-podshipnikov-lsa-group-inc-dlya-legkovyh-a/README.md)

- [Каталог подшипников LSA GROUP INC для легковых автомобилей.](./katalog-podshipnikov-lsa-group-inc-dlya-legkovyh-a/README.md)

- [ПОДШИПНИКИ СЕРИИ](./podshipniki-serii/README.md)

- [Каталог цилиндрических бессепараторных подшипников APB - серия SL.](./katalog-tsilindricheskih-besseparatornyh-podshipni/README.md)

- [Каталог подшипников качения NSK](./katalog-podshipnikov-kacheniya-nsk/README.md)

- [Deep groove Ball Bearings  dup2](./deep-groove-ball-bearings-dup2/README.md)

- [Шарнирные подшипников INA. Шарнирные головки INA.](./sharnirnye-podshipnikov-ina-sharnirnye-golovki-ina/README.md)

- [Каталог подшипников Fersa.](./katalog-podshipnikov-fersa/README.md)

- [Каталог подшипников IBC.](./katalog-podshipnikov-ibc/README.md)

- [Каталог подшипников TSС.](./katalog-podshipnikov-tss/README.md)

- [aligning bearings is on pages 41 42.](./aligning-bearings-is-on-pages-41-42/README.md)

- [Коды ТН ВЭД на подшипники](./kody-tn-ved-na-podshipniki/README.md)

- [Каталог  сверхпрецизионных подшипников Myonic.](./katalog-sverhpretsizionnyh-podshipnikov-myonic/README.md)

- [www.craft bearings.com  dup2](./wwwcraft-bearingscom-dup2/README.md)

- [Каталог подшипников KRW](./katalog-podshipnikov-krw/README.md)

- [Radial insert ball bearings](./radial-insert-ball-bearings/README.md)

- [Каталог подшипников NACHI.](./katalog-podshipnikov-nachi/README.md)

- [Каталог сверхточных подшипников NSK.](./katalog-sverhtochnyh-podshipnikov-nsk/README.md)

- [Machined Type Caged Needle Roller Bearings  dup2](./machined-type-caged-needle-roller-bearings-dup2/README.md)

- [Корпусные подшипниковые узлы Nke  dup2](./korpusnye-podshipnikovye-uzly-nke-dup2/README.md)

- [Каталог MARKES. Ролики конвейерные.](./katalog-markes-roliki-konveyernye/README.md)

- [CYLINDRICAL ROLLER BEARING CATALOG 1](./cylindrical-roller-bearing-catalog-1/README.md)

- [Как выбрать подшипник](./kak-vybrat-podshipnik/README.md)

- [Slewing bearings](./slewing-bearings/README.md)

- [TIMKEN PRODUCTS CATALOG D1](./timken-products-catalog-d1/README.md)

- [Каталог подшипников SLF Германия.](./katalog-podshipnikov-slf-germaniya/README.md)

- [Из чего состоит подшипник](./iz-chego-sostoit-podshipnik/README.md)

- [Гибридные подшипники   Подшипники в Беларуси   Aprom](./gibridnye-podshipniki-podshipniki-v-belarusi-aprom/README.md)

- [TIMKEN ENGINEERING MANUAL  dup2](./timken-engineering-manual-dup2/README.md)

- [TIMKEN ANGULAR CONTACT BALL BEARING CATALOG  dup2](./timken-angular-contact-ball-bearing-catalog-dup2/README.md)

- [Каталог подшипников IBB.](./katalog-podshipnikov-ibb/README.md)

- [Каталог подшипников HARP.](./katalog-podshipnikov-harp/README.md)

- [Precision Rolling Bearings  dup2](./precision-rolling-bearings-dup2/README.md)

- [Каталог игольчатых роликовых подшипников IKO.](./katalog-igolchatyh-rolikovyh-podshipnikov-iko/README.md)

- [Каталог  сверхпрецизионных подшипников Myonic.](./katalog-sverhpretsizionnyh-podshipnikov-myonic/README.md)

- [Общий каталог подшипников MONTON](./obschiy-katalog-podshipnikov-monton/README.md)

- [LARGE BEARINGS](./large-bearings/README.md)

- [Ball Bearings  dup2](./ball-bearings-dup2/README.md)

- [Machined Type Caged Needle Roller Bearings](./machined-type-caged-needle-roller-bearings/README.md)

- [Каталог подшипников DAS LAGER.](./katalog-podshipnikov-das-lager/README.md)

- [APTM Bearings for Industrial Applications](./aptm-bearings-for-industrial-applications/README.md)

- [Общий каталог подшипников Kaydon.](./obschiy-katalog-podshipnikov-kaydon/README.md)

- [THRUST BEARING CATALOG 1](./thrust-bearing-catalog-1/README.md)

- [Классификация подшипников   Подшипники в Беларуси](./klassifikatsiya-podshipnikov-podshipniki-v-belarus/README.md)

- [ПОДШИПНИКИ КАЧЕНИЯ](./podshipniki-kacheniya/README.md)

- [Каталог подшипников SLF Германия.](./katalog-podshipnikov-slf-germaniya/README.md)

- [JHS 3i подшипниковые корпусные](./jhs-3i-podshipnikovye-korpusnye/README.md)

- [Классификация подшипников](./klassifikatsiya-podshipnikov/README.md)

- [Needle Roller Bearings with Thrust Ball Bearing  dup2](./needle-roller-bearings-with-thrust-ball-bearing-du/README.md)

- [brands (2)  dup3](./brands-2-dup3/README.md)

- [Каталог подшипников Fersa для легковых автомобилей](./katalog-podshipnikov-fersa-dlya-legkovyh-avtomobil/README.md)

- [Experts in Bearing Solutions](./experts-in-bearing-solutions/README.md)

- [Precision Rolling Bearings](./precision-rolling-bearings/README.md)

- [Шариковые и роликовые подшипники NTN  dup2](./sharikovye-i-rolikovye-podshipniki-ntn-dup2/README.md)

- [Шарнирные подшипников INA. Шарнирные головки INA.](./sharnirnye-podshipnikov-ina-sharnirnye-golovki-ina/README.md)

- [Каталог подшипниковых узлов ASAHI.](./katalog-podshipnikovyh-uzlov-asahi/README.md)

- [Каталог зубчатых шестерен со ступицей  dup3](./katalog-zubchatyh-shesteren-so-stupitsey-dup3/README.md)

- [Каталог подшипников для экстремальных температур BECO.](./katalog-podshipnikov-dlya-ekstremalnyh-temperatur/README.md)

- [Bearings for  dup2](./bearings-for-dup2/README.md)

- [Ball Bearings](./ball-bearings/README.md)

- [SKF spherical plain](./skf-spherical-plain/README.md)

- [SKF composite  dup2](./skf-composite-dup2/README.md)

- [Фильтра   Подшипники в Беларуси](./filtra-podshipniki-v-belarusi/README.md)

- [Bearings for](./bearings-for/README.md)

- [Deep groove Ball Bearings](./deep-groove-ball-bearings/README.md)

- [Каталог зубчатых шестерен со ступицей  dup2](./katalog-zubchatyh-shesteren-so-stupitsey-dup2/README.md)

- [Каталог части номенклатуры подшипников FAG, INA.](./katalog-chasti-nomenklatury-podshipnikov-fag-ina/README.md)

- [Каталог подшипников CRAFT.](./katalog-podshipnikov-craft/README.md)

- [Каталог подшипников NACHI.](./katalog-podshipnikov-nachi/README.md)

- [GENERAL CATALOGUE](./general-catalogue/README.md)

- [Fersa Bearings use only clean raw materials](./fersa-bearings-use-only-clean-raw-materials/README.md)

- [Угол контакта - подшипники шариковые радиально-упорные однорядные.](./ugol-kontakta-podshipniki-sharikovye-radialno-upor/README.md)

- [CRAFT BEARINGS QUALITY CONTROL  dup2](./craft-bearings-quality-control-dup2/README.md)

- [Хранение и упаковка подшипников   Подшипники в Беларуси](./hranenie-i-upakovka-podshipnikov-podshipniki-v-bel/README.md)

- [Каталог MARKES. Ролики конвейерные.](./katalog-markes-roliki-konveyernye/README.md)

- [Каталог подшипников KDF.](./katalog-podshipnikov-kdf/README.md)

- [Нагрузка на подшипники   Подшипники в Беларуси](./nagruzka-na-podshipniki-podshipniki-v-belarusi/README.md)

- [Каталог подшипников NMB.](./katalog-podshipnikov-nmb/README.md)

- [Высокотемпературные подшипники skf  dup2](./vysokotemperaturnye-podshipniki-skf-dup2/README.md)

- [Каталог систем линейного перемещения ABBA](./katalog-sistem-lineynogo-peremescheniya-abba/README.md)

- [Коды ТН ВЭД на подшипники   Aprom](./kody-tn-ved-na-podshipniki-aprom/README.md)

- [Needle Roller Bearings](./needle-roller-bearings/README.md)

- [ПОДШИПНИКИ  dup2](./podshipniki-dup2/README.md)

- [Каталог подшипников KDF.](./katalog-podshipnikov-kdf/README.md)

- [Каталог подшипников FKL Сербия.](./katalog-podshipnikov-fkl-serbiya/README.md)

- [High Rigidity Type Crossed Roller Bearings V](./high-rigidity-type-crossed-roller-bearings-v/README.md)

- [Каталог подшипников CRAFT.](./katalog-podshipnikov-craft/README.md)

- [Каталог подшипников LSA GROUP INC для грузовой автотехники.](./katalog-podshipnikov-lsa-group-inc-dlya-gruzovoy-a/README.md)

- [CYLINDRICAL ROLLER BEARING CATALOG](./cylindrical-roller-bearing-catalog/README.md)

- [Общий каталог подшипников STC-STEYR](./obschiy-katalog-podshipnikov-stc-steyr/README.md)

- [Каталог подшипников APB для станкостроения.](./katalog-podshipnikov-apb-dlya-stankostroeniya/README.md)

- [Separable Roller Followers](./separable-roller-followers/README.md)

- [Needle Roller Bearings with Thrust Ball Bearing](./needle-roller-bearings-with-thrust-ball-bearing/README.md)

- [Separable Roller Followers  dup2](./separable-roller-followers-dup2/README.md)

- [10-32](./10-32/README.md)

- [Каталог систем линейного перемещения ABBA](./katalog-sistem-lineynogo-peremescheniya-abba/README.md)

- [Каталог подшипников HARP.](./katalog-podshipnikov-harp/README.md)

- [Needle Roller Cages for Big End](./needle-roller-cages-for-big-end/README.md)

- [Каталог подшипников качения NSK](./katalog-podshipnikov-kacheniya-nsk/README.md)

- [Нагрузка на подшипники](./nagruzka-na-podshipniki/README.md)

- [High Rigidity Type Crossed Roller Bearings V  dup2](./high-rigidity-type-crossed-roller-bearings-v-dup2/README.md)

- [Хранение и упаковка подшипников](./hranenie-i-upakovka-podshipnikov/README.md)

- [Каталог подшипников FKL Сербия.](./katalog-podshipnikov-fkl-serbiya/README.md)

- [Каталог подшипников TSС.](./katalog-podshipnikov-tss/README.md)

- [Каталог подшипников Fersa для легковых автомобилей](./katalog-podshipnikov-fersa-dlya-legkovyh-avtomobil/README.md)

- [Общий каталог подшипников  бренда Самарский Подшипник](./obschiy-katalog-podshipnikov-brenda-samarskiy-pods/README.md)

- [Каталог подшипников NKE.](./katalog-podshipnikov-nke/README.md)

- [ROlling Bearings  dup2](./rolling-bearings-dup2/README.md)

- [SKF spherical plain  dup2](./skf-spherical-plain-dup2/README.md)

- [Radial insert ball bearings  dup2](./radial-insert-ball-bearings-dup2/README.md)

- [Каталог подшипников SNH](./katalog-podshipnikov-snh/README.md)

- [Каталог высокоточных и специальных подшипников качения AKE.](./katalog-vysokotochnyh-i-spetsialnyh-podshipnikov-k/README.md)

- [10-32](./10-32/README.md)

- [ПОДШИПНИКИ ДЛЯ](./podshipniki-dlya/README.md)

- [Каталог подшипниковых узлов ASAHI.](./katalog-podshipnikovyh-uzlov-asahi/README.md)

- [Подшипники SKF  dup2](./podshipniki-skf-dup2/README.md)

- [NSK high performance bearings help to maximize uptime](./nsk-high-performance-bearings-help-to-maximize-upt/README.md)

- [TIMKEN ENGINEERING MANUAL](./timken-engineering-manual/README.md)

- [RHP ВЫСОКОНАДЕЖНЫЕ ПОДШИПНИКИ](./rhp-vysokonadezhnye-podshipniki/README.md)

- [КИТАЙСКИЕ ПОДШИПНИКИ](./kitayskie-podshipniki/README.md)

- [APTM Bearings for Industrial Applications  dup2](./aptm-bearings-for-industrial-applications-dup2/README.md)

- [Experts in Bearing Solutions  dup2](./experts-in-bearing-solutions-dup2/README.md)

- [Автомобильные комплекты подшипников SKF, FAG, SNR, TIMKEN, FERSA A&S, QH](./avtomobilnye-komplekty-podshipnikov-skf-fag-snr-ti/README.md)

- [Каталог подшипников KRW](./katalog-podshipnikov-krw/README.md)

- [Caged Roller Bearings](./caged-roller-bearings/README.md)

- [Каталог десятого подшипникового завода](./katalog-desyatogo-podshipnikovogo-zavoda/README.md)

- [Каталог игольчатых роликовых подшипников IKO.](./katalog-igolchatyh-rolikovyh-podshipnikov-iko/README.md)

- [Общий каталог подшипников SKF](./obschiy-katalog-podshipnikov-skf/README.md)

- [Обгонные муфты INA - HF, HFL.](./obgonnye-mufty-ina-hf-hfl/README.md)

- [Каталог зубчатых шестерен без ступицы  dup3](./katalog-zubchatyh-shesteren-bez-stupitsy-dup3/README.md)

- [Игольчатые роликоподшипники NTN  dup3](./igolchatye-rolikopodshipniki-ntn-dup3/README.md)

- [BALL BEARING](./ball-bearing/README.md)

- [Catalogue](./catalogue/README.md)

- [Каталог части номенклатуры подшипников FAG, INA.](./katalog-chasti-nomenklatury-podshipnikov-fag-ina/README.md)

- [Каталог подшипников GAMET BEARINGS.](./katalog-podshipnikov-gamet-bearings/README.md)

- [Сферические роликоподшипники FAG](./sfericheskie-rolikopodshipniki-fag/README.md)

- [Шариковые и роликовые подшипники NTN  dup3](./sharikovye-i-rolikovye-podshipniki-ntn-dup3/README.md)

- [Каталог игольчатых подшипников NBS.](./katalog-igolchatyh-podshipnikov-nbs/README.md)

- [Хранение и упаковка подшипников .](./hranenie-i-upakovka-podshipnikov/README.md)

- [Общий каталог подшипников MONTON](./obschiy-katalog-podshipnikov-monton/README.md)

- [TIMKEN DEEP GROOVE BALL BEARING CATALOG  dup2](./timken-deep-groove-ball-bearing-catalog-dup2/README.md)

- [brands (2)](./brands-2/README.md)

- [Каталог подшипников GAMET BEARINGS.](./katalog-podshipnikov-gamet-bearings/README.md)

- [Slewing bearings  dup2](./slewing-bearings-dup2/README.md)

- [Каталог подшипников Fersa.](./katalog-podshipnikov-fersa/README.md)

- [Шариковая опора   Подшипники в Беларуси   Aprom](./sharikovaya-opora-podshipniki-v-belarusi-aprom/README.md)

- [ПОДШИПНИКОВ  dup2](./podshipnikov-dup2/README.md)

- [Каталог тонких подшипников подшипников Kaydon высокоточной серии Reali-Slim.](./katalog-tonkih-podshipnikov-podshipnikov-kaydon-vy/README.md)

- [SKF heavy duty  dup2](./skf-heavy-duty-dup2/README.md)

- [NSK high performance bearings help to maximize uptime  dup2](./nsk-high-performance-bearings-help-to-maximize-upt/README.md)

- [Sealed Spherical Roller Bearings  dup2](./sealed-spherical-roller-bearings-dup2/README.md)

- [Каталог зубчатых шестерен с каленом зубом и со ступицей  dup2](./katalog-zubchatyh-shesteren-s-kalenom-zubom-i-so-s/README.md)

- [LARGE BEARINGS  dup2](./large-bearings-dup2/README.md)

- [Общий каталог подшипников SKF](./obschiy-katalog-podshipnikov-skf/README.md)

- [Каталог подшипников SNFA.](./katalog-podshipnikov-snfa/README.md)

- [Cross Roller Ring Series](./cross-roller-ring-series/README.md)

- [ПОДШИПНИКОВЫЕ  dup2](./podshipnikovye-dup2/README.md)

- [Корпусные подшипники skf](./korpusnye-podshipniki-skf/README.md)

- [www.fersa.com  dup2](./wwwfersacom-dup2/README.md)

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
