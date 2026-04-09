---
name: kb-audit
description: Audit the repository knowledge base for structure, metadata, canonical content boundaries, link integrity, and scale risks before making broad changes.
---

# kb-audit

Use this skill when the task is about reviewing or stabilizing the repository as a knowledge-base system rather than editing one small article.

## Use when
- The user asks to audit the knowledge base.
- The user asks why the repository structure feels messy.
- A change may affect `inbox/`, `kb/ru/`, `_templates/`, `_meta/`, `scripts/`, or `kb/ru/INDEX.md`.
- You suspect duplicates, taxonomy drift, broken links, or mixed canonical/raw content.

## Goals
1. Confirm the repository still follows the intended pipeline: `inbox/` -> processing -> `kb/ru/`.
2. Detect structure drift, duplicate topics, metadata gaps, broken links, and scaling risks.
3. Recommend the smallest safe fix set.

## Repository-specific checks
- `inbox/` contains raw material only.
- `kb/ru/` contains canonical articles only.
- One article = one folder = one `README.md`.
- Front matter matches `_templates/article.md`.
- `kb/ru/INDEX.md` remains a usable central index.
- `_meta/` reflects current taxonomy and audit reality.
- Existing automation scripts are preferred over manual bulk edits.

## Run these checks when relevant
```bash
python scripts/process_inbox.py --dry-run
python scripts/kb_quality_gate.py
python tests/check_kb_links.py
```

## Audit output format
1. Decision
2. What is structurally correct
3. What is broken or drifting
4. Minimal fix plan
5. Risks if left unchanged

## Hard rules
- Do not mass-rewrite content during an audit unless explicitly asked.
- Do not move raw files into canonical content casually.
- Do not declare validation complete if checks were not run.
- Prefer local fixes over repository-wide churn.
