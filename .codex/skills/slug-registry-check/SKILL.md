---
name: slug-registry-check
description: Check slug stability, folder naming, registry alignment, and internal links before or after structural knowledge-base changes.
---

# slug-registry-check

Use this skill when a task touches slugs, folder names, section maps, registries, or article moves.

## Use when
- The user wants to rename or shorten slugs.
- A section map or page registry changed.
- Articles are being moved between topics.
- You suspect broken links after taxonomy work.

## What to check
1. Slugs remain stable unless there is a real reason to change them.
2. Folder names stay ASCII kebab-case.
3. The registry / section map and actual article paths do not drift apart.
4. `kb/ru/INDEX.md` still points to the right canonical locations.
5. Internal links and related-article references still resolve.
6. No duplicate topic is created under different slugs.

## Repository-specific checks
- One article = one folder = one `README.md`.
- Registry changes should not silently invalidate links.
- English semantic slugs should remain consistent inside the same subtree.
- Avoid mixing old transliterated and new semantic slug styles within one branch of the KB.

## Validation commands
Run when relevant:
```bash
python tests/check_kb_links.py
python scripts/kb_quality_gate.py
```

## Output format
1. Slug decision: keep / rename / merge / archive
2. Affected paths
3. Links or index entries that must be updated
4. Duplicate-risk notes
5. Smallest safe migration plan

## Hard rules
- Do not mass-rename slugs for aesthetics alone.
- Do not rename slugs without checking links and index references.
- Do not leave both old and new canonical slugs active for the same topic without explicit intent.
- Prefer minimal churn.
