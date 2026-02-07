# Автоматический обработчик inbox

Система автоматической обработки файлов из папки `inbox/` в структурированные статьи базы знаний.

## Быстрый старт

```bash
# Обработать все файлы из inbox
python scripts/process_inbox.py

# Предпросмотр без изменений
python scripts/process_inbox.py --dry-run
```

## Компоненты

1. **`scripts/process_inbox.py`** - скрипт обработки файлов
2. **`.github/workflows/inbox-processor.yml`** - автоматический workflow для GitHub Actions

## Что делает обработчик

1. Сканирует `inbox/` на наличие файлов
2. Извлекает контент и классифицирует по темам
3. Создаёт статьи с YAML front-matter и уникальными ID
4. Проверяет дубликаты (SHA256)
5. Перемещает обработанные файлы в `inbox/processed/YYYY-MM/`
6. Обновляет метаданные и индексы

## Результаты обработки

За один запуск были обработаны **99 файлов** из inbox:
- Создано 99 новых статей
- 7 новых тем: podshipniki, podshipniki-standards, podshipniki-designation, podshipniki-equivalents, podshipniki-maintenance, lubrication-seals, drive-systems, general
- Все файлы перемещены в `inbox/processed/2026-02/`
- ID реестр обновлён (следующий ID: 471)

## Автоматизация через GitHub Actions

При добавлении файлов в `inbox/` автоматически:
1. Запускается workflow
2. Обрабатываются новые файлы
3. Создаётся Pull Request с результатами

## Подробная документация

См. полную документацию в `docs/inbox-processor.md`
