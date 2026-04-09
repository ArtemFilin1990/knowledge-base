---
name: index-maintainer
description: Maintain kb/ru/INDEX.md and related navigation layers so the canonical knowledge base stays discoverable, consistent, and aligned with actual article paths.
---

# index-maintainer

Use this skill when the task affects `kb/ru/INDEX.md`, topic navigation, article discoverability, or large content additions that should appear in the canonical index.

## Use when
- New canonical articles were added to `kb/ru/`.
- Articles were moved, archived, merged, or renamed.
- The user asks to clean up or rebuild the central index.
- The repository structure changed and navigation may be stale.

## Goals
1. Keep `kb/ru/INDEX.md` as the central entry point.
2. Make sure index links match actual canonical article locations.
3. Keep navigation compact, readable, and scalable.
4. Avoid duplicate listings for the same topic.

## What to check
- Every indexed article path exists.
- The index reflects canonical content in `kb/ru/`, not raw intake from `inbox/`.
- Moved or archived pages are not still listed as active canon.
- Section labels, topic names, and paths are internally consistent.
- Navigation does not mix old and new canonical paths for the same topic.

## Repository-specific rules
- `kb/ru/INDEX.md` is a navigation layer, not a full article dump.
- Prefer concise index entries over long editorial text.
- Preserve existing structure unless there is a real navigation problem.
- Keep article ordering stable unless there is a clear reason to change it.

## Validation commands
Run when relevant:
```bash
python tests/check_kb_links.py
python scripts/kb_quality_gate.py
```

## Output format
1. Index decision: keep / update / rebuild section / archive stale links
2. Paths added or corrected
3. Stale or broken entries found
4. Minimal safe edit plan

## Hard rules
- Do not rewrite the whole index for cosmetic reasons.
- Do not index raw files from `inbox/` as canonical content.
- Do not leave stale paths after moving canonical content.
- Prefer minimal navigation edits.
