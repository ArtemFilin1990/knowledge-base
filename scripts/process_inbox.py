#!/usr/bin/env python3
"""
Автоматический обработчик файлов из inbox.

Сканирует inbox/, извлекает контент, создаёт структурированные статьи в kb/ru/,
обновляет индексы и перемещает обработанные файлы в inbox/processed/YYYY-MM/.

Использование:
    python scripts/process_inbox.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Константы
INBOX_DIR = Path("inbox")
PROCESSED_DIR = INBOX_DIR / "processed"
KB_ROOT = Path("kb/ru")
META_DIR = Path("_meta")
TEMPLATE = Path("_templates/article.md")
ID_REGISTRY = META_DIR / "id_registry.json"
DEDUP_INDEX = META_DIR / "dedup_index.json"
DEDUP_LOG = META_DIR / "dedup_log.md"
TOPICS_JSON = META_DIR / "topics.json"

# Регулярные выражения
CYRILLIC_ONLY = re.compile(r"[А-Яа-яЁё]+")
YAML_FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL | re.MULTILINE)


def die(msg: str) -> None:
    """Печатает ошибку и завершает программу."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def info(msg: str) -> None:
    """Печатает информационное сообщение."""
    print(f"INFO: {msg}")


def warn(msg: str) -> None:
    """Печатает предупреждение."""
    print(f"WARN: {msg}")


def ensure_meta_files() -> None:
    """Создаёт мета-файлы, если они не существуют."""
    META_DIR.mkdir(parents=True, exist_ok=True)
    
    if not ID_REGISTRY.exists():
        ID_REGISTRY.write_text(json.dumps({
            "next_id": 202,
            "prefix": "KB-RU-",
            "pad": 6
        }, indent=2, ensure_ascii=False))
    
    if not DEDUP_INDEX.exists():
        DEDUP_INDEX.write_text(json.dumps({}, indent=2, ensure_ascii=False))
    
    if not DEDUP_LOG.exists():
        DEDUP_LOG.write_text("# Dedup log\n\nФормат:\n- YYYY-MM-DD: inbox/<file> -> <canonical-article-path> (reason: sha256 match)\n\n")
    
    if not TOPICS_JSON.exists():
        TOPICS_JSON.write_text(json.dumps({}, indent=2, ensure_ascii=False))


def load_id_registry() -> Dict:
    """Загружает реестр ID."""
    if not ID_REGISTRY.exists():
        return {"next_id": 202, "prefix": "KB-RU-", "pad": 6}
    return json.loads(ID_REGISTRY.read_text())


def save_id_registry(registry: Dict) -> None:
    """Сохраняет реестр ID."""
    ID_REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False))


def allocate_id() -> str:
    """Выделяет новый уникальный ID для статьи."""
    registry = load_id_registry()
    next_id = registry["next_id"]
    prefix = registry["prefix"]
    pad = registry["pad"]
    
    article_id = f"{prefix}{str(next_id).zfill(pad)}"
    registry["next_id"] = next_id + 1
    save_id_registry(registry)
    
    return article_id


def load_dedup_index() -> Dict[str, str]:
    """Загружает индекс дедупликации."""
    if not DEDUP_INDEX.exists():
        return {}
    return json.loads(DEDUP_INDEX.read_text())


def save_dedup_index(index: Dict[str, str]) -> None:
    """Сохраняет индекс дедупликации."""
    DEDUP_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False))


def compute_sha256(text: str) -> str:
    """Вычисляет SHA256 хеш текста."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def log_duplicate(inbox_file: str, canonical_path: str, reason: str) -> None:
    """Логирует дубликат в dedup_log.md."""
    log_entry = f"- {date.today()}: {inbox_file} -> {canonical_path} ({reason})\n"
    with open(DEDUP_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)


def to_kebab_case(text: str) -> str:
    """
    Преобразует текст в kebab-case ASCII.
    Транслитерирует кириллицу, удаляет спецсимволы.
    """
    # Простая транслитерация (можно расширить)
    translit = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        '_': '-', ' ': '-', '(': '', ')': '', '[': '', ']': '', '{': '', '}': '',
        '.': '', ',': '', '!': '', '?': '', ':': '', ';': '', '"': '', "'": '',
        '/': '-', '\\': '-', '—': '-', '–': '-',
    }
    
    result = text.lower()
    for cyr, lat in translit.items():
        result = result.replace(cyr, lat)
    
    # Удаляем всё, кроме букв, цифр и дефисов
    result = re.sub(r'[^a-z0-9-]', '', result)
    # Убираем множественные дефисы
    result = re.sub(r'-+', '-', result)
    # Убираем дефисы в начале и конце
    result = result.strip('-')
    
    return result or "article"


def extract_text_from_md(file_path: Path) -> str:
    """Извлекает текст из markdown файла, убирая YAML front-matter."""
    text = file_path.read_text(encoding="utf-8", errors="replace")
    # Убираем существующий front-matter, если есть
    text = YAML_FRONTMATTER.sub("", text).strip()
    return text


def get_unprocessed_files() -> List[Path]:
    """Возвращает список необработанных файлов в inbox."""
    if not INBOX_DIR.exists():
        return []
    
    files = []
    for item in INBOX_DIR.iterdir():
        if item.is_file() and item.name != "README.md":
            files.append(item)
    
    return files


def classify_topic(text: str, title: str) -> str:
    """
    Классифицирует контент по теме.
    Возвращает topic slug (kebab-case).
    """
    # Простая классификация по ключевым словам
    text_lower = text.lower()
    title_lower = title.lower()
    
    # Подшипники
    bearing_keywords = [
        "подшипник", "bearing", "шариковый", "роликовый", "радиальный",
        "упорный", "конический", "цилиндрический", "сферический",
        "skf", "fag", "nsk", "koyo", "timken", "гост", "iso", "маркировка",
        "обозначение", "аналог", "эквивалент", "ступиц", "нагрузк",
    ]
    
    # Смазка и уплотнения
    lubrication_keywords = ["смазк", "масл", "консистент", "сальник", "манжет", "уплотнени"]
    
    # Цепи и ремни
    drive_keywords = ["ремень", "цепь", "звездочк", "привод", "шкив"]
    
    # Стандарты и документация
    standards_keywords = ["гост", "стандарт", "iso", "din", "термин", "определени", "classification"]
    
    # Монтаж и обслуживание
    maintenance_keywords = ["монтаж", "демонтаж", "установк", "ревизи", "обслуживан", "ремонт"]
    
    combined = title_lower + " " + text_lower[:1000]
    
    if any(kw in combined for kw in bearing_keywords):
        # Дополнительная детализация
        if any(kw in combined for kw in standards_keywords):
            return "podshipniki-standards"
        elif any(kw in combined for kw in maintenance_keywords):
            return "podshipniki-maintenance"
        elif "аналог" in combined or "эквивалент" in combined or "equivalent" in combined:
            return "podshipniki-equivalents"
        elif "маркировка" in combined or "обозначение" in combined or "designation" in combined:
            return "podshipniki-designation"
        else:
            return "podshipniki"
    
    elif any(kw in combined for kw in lubrication_keywords):
        return "lubrication-seals"
    
    elif any(kw in combined for kw in drive_keywords):
        return "drive-systems"
    
    elif any(kw in combined for kw in standards_keywords):
        return "standards"
    
    else:
        return "general"


def extract_title_from_content(text: str, filename: str) -> str:
    """Извлекает заголовок из содержимого или имени файла."""
    # Ищем первый H1
    lines = text.split("\n")
    for line in lines:
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    
    # Используем имя файла
    title = filename.replace("_", " ").replace("-", " ")
    if title.endswith(".md"):
        title = title[:-3]
    
    return title


def create_article_from_content(
    content: str,
    title: str,
    topic: str,
    source_file: str,
    article_id: str,
) -> str:
    """Создаёт README.md с YAML front-matter и контентом."""
    today = date.today().isoformat()
    
    # Генерируем теги на основе темы
    tags = ["imported-from-inbox"]
    if "podshipniki" in topic or "bearing" in topic:
        tags.append("bearings")
    if "standards" in topic or "гост" in topic.lower():
        tags.append("standards")
    if "designation" in topic or "маркировка" in topic.lower():
        tags.append("designation")
    
    tags_str = json.dumps(tags, ensure_ascii=False)
    
    # Формируем front-matter
    frontmatter = f"""---
id: {article_id}
title: {title}
topic: {topic}
tags: {tags_str}
status: draft
source: inbox/{source_file}
created: {today}
updated: {today}
---

"""
    
    # Убираем лишние пустые строки в начале контента
    content = content.lstrip("\n")
    
    # Добавляем H1 если его нет
    if not content.startswith("# "):
        content = f"# {title}\n\n{content}"
    
    return frontmatter + content


def move_to_processed(file_path: Path, dry_run: bool = False) -> Path:
    """Перемещает файл в inbox/processed/YYYY-MM/."""
    year_month = date.today().strftime("%Y-%m")
    target_dir = PROCESSED_DIR / year_month
    
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_path.name
        
        # Если файл уже существует, добавляем суффикс
        counter = 1
        while target_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            target_path = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        shutil.move(str(file_path), str(target_path))
        return target_path
    else:
        return target_dir / file_path.name


def update_topic_readme(topic: str, article_path: Path, article_title: str, dry_run: bool = False) -> None:
    """Обновляет README.md темы, добавляя ссылку на новую статью."""
    topic_dir = KB_ROOT / topic
    topic_readme = topic_dir / "README.md"
    
    if not dry_run:
        topic_dir.mkdir(parents=True, exist_ok=True)
        
        if not topic_readme.exists():
            # Создаём новый README для темы
            topic_title = topic.replace("-", " ").title()
            content = f"""---
id: TBD
title: {topic_title}
topic: {topic}
tags: ["topic-index"]
status: draft
source: auto-generated
created: {date.today().isoformat()}
updated: {date.today().isoformat()}
---

# {topic_title}

## Статьи

- [{article_title}](./{article_path.parent.name}/README.md)

"""
            topic_readme.write_text(content, encoding="utf-8")
        else:
            # Добавляем ссылку в существующий README
            content = topic_readme.read_text(encoding="utf-8")
            
            # Ищем секцию со статьями
            if "## Статьи" in content:
                # Добавляем после заголовка "## Статьи"
                article_link = f"- [{article_title}](./{article_path.parent.name}/README.md)\n"
                content = content.replace(
                    "## Статьи\n",
                    f"## Статьи\n\n{article_link}"
                )
            else:
                # Добавляем секцию в конец
                article_link = f"\n## Статьи\n\n- [{article_title}](./{article_path.parent.name}/README.md)\n"
                content += article_link
            
            topic_readme.write_text(content, encoding="utf-8")


def process_file(file_path: Path, dry_run: bool = False) -> Optional[Dict]:
    """
    Обрабатывает один файл из inbox.
    
    Returns:
        Dict с информацией о созданной статье или None, если файл был пропущен.
    """
    info(f"Обработка: {file_path.name}")
    
    # Извлекаем текст
    if file_path.suffix.lower() == ".md":
        text = extract_text_from_md(file_path)
    else:
        warn(f"Пропуск {file_path.name}: неподдерживаемый формат (пока поддерживаются только .md)")
        return None
    
    # Проверка на дубликат
    text_hash = compute_sha256(text)
    dedup_index = load_dedup_index()
    
    if text_hash in dedup_index:
        canonical_path = dedup_index[text_hash]
        warn(f"Дубликат обнаружен: {file_path.name} -> {canonical_path}")
        log_duplicate(file_path.name, canonical_path, f"sha256={text_hash[:8]}...")
        
        if not dry_run:
            move_to_processed(file_path)
        
        return None
    
    # Извлекаем заголовок
    title = extract_title_from_content(text, file_path.name)
    
    # Классифицируем тему
    topic = classify_topic(text, title)
    info(f"  Тема: {topic}")
    info(f"  Заголовок: {title}")
    
    # Выделяем ID
    article_id = allocate_id()
    info(f"  ID: {article_id}")
    
    # Создаём путь для статьи
    article_slug = to_kebab_case(title)[:50]  # Ограничиваем длину
    article_dir = KB_ROOT / topic / article_slug
    article_readme = article_dir / "README.md"
    
    # Создаём статью
    article_content = create_article_from_content(
        text, title, topic, file_path.name, article_id
    )
    
    if not dry_run:
        article_dir.mkdir(parents=True, exist_ok=True)
        article_readme.write_text(article_content, encoding="utf-8")
        info(f"  Создано: {article_readme}")
        
        # Обновляем индекс дедупликации
        dedup_index[text_hash] = str(article_readme)
        save_dedup_index(dedup_index)
        
        # Обновляем README темы
        update_topic_readme(topic, article_readme, title)
        
        # Перемещаем в processed
        processed_path = move_to_processed(file_path)
        info(f"  Перемещено в: {processed_path}")
    
    return {
        "id": article_id,
        "title": title,
        "topic": topic,
        "path": str(article_readme),
        "source": file_path.name,
    }


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Автоматический обработчик файлов из inbox"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что будет сделано, без изменений"
    )
    args = parser.parse_args()
    
    info("=== Обработчик inbox ===")
    if args.dry_run:
        info("РЕЖИМ: dry-run (без изменений)")
    
    # Проверяем и создаём мета-файлы
    ensure_meta_files()
    
    # Получаем необработанные файлы
    files = get_unprocessed_files()
    info(f"Найдено файлов для обработки: {len(files)}")
    
    if not files:
        info("Нет файлов для обработки")
        return
    
    # Обрабатываем файлы
    processed_articles = []
    for file_path in files:
        result = process_file(file_path, dry_run=args.dry_run)
        if result:
            processed_articles.append(result)
    
    # Итоговый отчёт
    info("\n=== Итоги ===")
    info(f"Обработано файлов: {len(files)}")
    info(f"Создано статей: {len(processed_articles)}")
    
    if processed_articles:
        info("\nСозданные статьи:")
        for article in processed_articles:
            info(f"  - {article['id']}: {article['title']}")
            info(f"    Путь: {article['path']}")
            info(f"    Источник: {article['source']}")


if __name__ == "__main__":
    main()
