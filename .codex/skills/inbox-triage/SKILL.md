---
name: inbox-triage
description: Triage raw files in inbox, decide what belongs in canonical knowledge, avoid duplicates, and route processing through the repository intake workflow.
---

# inbox-triage

Use this skill when the task starts from raw materials in `inbox/` or when the user asks to classify, route, or safely process new source files.

## Use when
- New files were added to `inbox/`.
- The user asks what should be processed, ignored, merged, or archived.
- You suspect duplicates, noisy files, or weak source quality.
- The task is about intake classification before canonical publication.

## Goals
1. Keep `inbox/` as the only raw intake zone.
2. Classify raw files before they contaminate canonical content.
3. Detect duplicates and low-value noise early.
4. Route good material into the standard processing workflow.

## What to check
- Which files in `inbox/` are new and relevant.
- Whether a file duplicates already processed or canonical content.
- Whether a file is raw source, transformed output, or noise.
- Which topic bucket the file likely belongs to.
- Whether the file should be processed now, deferred, merged, or ignored.

## Repository-specific rules
- Do not publish directly from `inbox/` into canon without respecting the existing pipeline.
- Prefer `scripts/process_inbox.py` over ad-hoc manual intake logic.
- Keep raw files and canonical articles strictly separate.
- Record limitations if classification is uncertain.

## Validation commands
Run when relevant:
```bash
python scripts/process_inbox.py --dry-run
python scripts/process_inbox.py
python scripts/kb_quality_gate.py
```

## Output format
1. Intake decision per file or group: process / merge / ignore / archive / manual review
2. Suspected duplicates
3. Target topic or section
4. Minimal safe next action

## Hard rules
- Do not move raw content into `kb/ru/` casually.
- Do not treat transformed noise as source of truth.
- Do not skip duplicate checks if intake scale is non-trivial.
- Prefer dry-run before broad intake processing.
