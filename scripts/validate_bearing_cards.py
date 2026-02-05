#!/usr/bin/env python3
"""
Валидация метаданных карточек подшипников.

Проверяет специфичные для подшипников поля в YAML front-matter:
- designation (базовое обозначение и суффиксы)
- dims (размеры d, D, B)
- load_capacity (грузоподъёмность C, C0)
- equivalents (эквиваленты производителей)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict

# Путь к карточкам подшипников
BEARING_CARDS_ROOT = Path("kb/ru/bearings/cards")

YAML_START = re.compile(r"^---\s*$")


def parse_yaml_value(value: str) -> Any:
    """Простой парсер YAML значений."""
    value = value.strip()
    
    # Списки
    if value.startswith("[") and value.endswith("]"):
        content = value[1:-1].strip()
        if not content:
            return []
        # Простой парсинг списка (без вложенных структур)
        items = []
        for item in content.split(","):
            item = item.strip().strip('"').strip("'")
            items.append(item)
        return items
    
    # Словари (упрощённо)
    if value.startswith("{") and value.endswith("}"):
        return value  # Возвращаем как строку для дальнейшего разбора
    
    # Числа
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Строки
    return value.strip('"').strip("'")


def parse_front_matter(text: str) -> Dict[str, Any]:
    """Извлекает YAML front-matter из текста."""
    lines = text.splitlines()
    if not lines or not YAML_START.match(lines[0]):
        return {}

    end = None
    for i in range(1, min(len(lines), 200)):
        if YAML_START.match(lines[i]):
            end = i
            break
    if end is None:
        return {}

    fm_lines = lines[1:end]
    fm: Dict[str, Any] = {}
    current_key = None
    
    for ln in fm_lines:
        # Пропускаем пустые строки и комментарии
        if not ln.strip() or ln.strip().startswith("#"):
            continue
            
        # Ключ-значение
        if ":" in ln and not ln.startswith(" "):
            key, _, value = ln.partition(":")
            key = key.strip()
            value = value.strip()
            current_key = key
            
            if value:
                fm[key] = parse_yaml_value(value)
            else:
                fm[key] = None
        # Продолжение значения (например, в списках)
        elif ln.startswith(" ") and current_key:
            if ln.strip().startswith("-"):
                # Элемент списка
                if fm[current_key] is None:
                    fm[current_key] = []
                item = ln.strip()[1:].strip()
                if item.startswith("{"):
                    fm[current_key].append(item)
                else:
                    fm[current_key].append(parse_yaml_value(item))
    
    return fm


def validate_bearing_card(path: Path) -> list[str]:
    """Валидация карточки подшипника. Возвращает список ошибок."""
    errors = []
    
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_front_matter(text)
    
    if not fm:
        return [f"{path}: отсутствует YAML front-matter"]
    
    # Проверка обязательных полей для карточек подшипников
    if fm.get("topic") == "bearings-card":
        # designation
        if "designation" not in fm:
            errors.append(f"{path}: отсутствует поле 'designation'")
        else:
            desig = fm["designation"]
            if isinstance(desig, str):
                errors.append(f"{path}: 'designation' должен быть словарём с 'base' и 'suffixes'")
        
        # dims
        if "dims" not in fm:
            errors.append(f"{path}: отсутствует поле 'dims' (размеры)")
        else:
            dims = fm["dims"]
            if isinstance(dims, str) and "{" in dims:
                # Простая проверка наличия d, D, B
                if "d:" not in dims or "D:" not in dims or "B:" not in dims:
                    errors.append(f"{path}: 'dims' должен содержать d, D, B")
        
        # load_capacity
        if "load_capacity" in fm:
            lc = fm["load_capacity"]
            if isinstance(lc, str) and "{" in lc:
                # Проверка наличия динамической грузоподъёмности
                if "dynamic_C_kN" not in lc and "C_kN" not in lc:
                    errors.append(f"{path}: 'load_capacity' должен содержать dynamic_C_kN")
        
        # equivalents
        if "equivalents" in fm:
            equivs = fm["equivalents"]
            if not isinstance(equivs, list):
                errors.append(f"{path}: 'equivalents' должен быть списком")
            elif len(equivs) == 0:
                errors.append(f"{path}: 'equivalents' пуст, добавьте хотя бы один эквивалент")
    
    return errors


def main() -> None:
    """Основная функция валидации."""
    if not BEARING_CARDS_ROOT.exists():
        print(f"WARN: папка {BEARING_CARDS_ROOT} не существует, пропускаем валидацию карточек")
        return
    
    all_errors = []
    card_count = 0
    
    # Находим все README.md в cards/
    for readme in BEARING_CARDS_ROOT.rglob("README.md"):
        card_count += 1
        errors = validate_bearing_card(readme)
        all_errors.extend(errors)
    
    if all_errors:
        print(f"BEARING VALIDATION ERRORS ({len(all_errors)}):")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"OK: validated {card_count} bearing card(s), no errors")


if __name__ == "__main__":
    main()
