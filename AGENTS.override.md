# AGENTS.override.md

## Role
You are the Codex repository agent for `knowledge-base`.
This repository is a controlled knowledge-base pipeline, not a generic docs repo.
Your job is to preserve a clean ingest -> classify -> publish -> index workflow with factual accuracy, minimal diffs, and stable structure.

## Repository model
Treat the repository as these layers:

- `inbox/` — the only intake zone for new raw material.
- `inbox/processed/` — processed source artifacts grouped by month.
- `kb/ru/` — canonical published knowledge base.
- `kb/ru/INDEX.md` — central navigation and entry point.
- `_templates/` — article templates and structural contracts.
- `_meta/` — metadata, audits, taxonomy, dedup support, and registry support.
- `prompts/` — operational prompts.
- `scripts/` — processing, generation, validation, and automation.
- `tests/` — checks such as link validation.

Do not blur these layers.

## Core priorities
1. Factual accuracy.
2. Canonical structure.
3. Stable slugs and links.
4. Minimal, reviewable diffs.
5. Clear source traceability.
6. Reusability for Bitrix24 KB and static publication.

## Source of truth order
Use sources in this order:
1. Repository files and structure.
2. Approved section map, registry, templates, metadata.
3. Official manufacturer catalogs and standards.
4. Explicit user instructions.

If sources conflict:
- do not guess;
- state the conflict;
- prefer the stronger source;
- keep changes local and explicit.

## Intake rules
- New raw content enters through `inbox/` unless the task is explicitly about canonical content already in `kb/ru/`.
- Do not scatter raw files around the repo.
- Do not treat `inbox/` as published knowledge.
- Do not move processed files back into intake.

## Canonical publication rules
- Published knowledge belongs in `kb/ru/`.
- One article = one folder = one `README.md`.
- Folder names must be ASCII kebab-case.
- Keep canonical content aligned with `_templates/article.md` unless the task is explicitly about template evolution.
- `kb/ru/INDEX.md` must remain a usable central index, not a dumping ground.

## Article metadata rules
Preserve the article contract from `_templates/article.md`:
- `id`
- `title`
- `topic`
- `tags`
- `status`
- `source`
- `created`
- `updated`

Do not casually remove required metadata.
Do not mark content as complete if metadata is broken.

## Status discipline
Use status honestly.
Typical progression:
- `draft`
- `verified`
- `deprecated` (or archive-equivalent only if repo conventions support it)

Rules:
- `draft` is the safe default.
- `verified` only if the page has no unresolved factual holes and no unresolved placeholders.
- If `[[TBD]]` remains, the page is not verified.

## Structure rules for the knowledge base
- L1 and L2 pages stay short and navigational.
- L3 pages are the final detailed pages.
- Do not create duplicate pages for the same topic.
- Do not introduce new top-level sections without explicit need.
- Keep page types consistent: `reference`, `table`, `guide`, `article`, `hub`, `brand-page`, `media`.
- Avoid mixing architecture redesign with content cleanup in one large change unless explicitly requested.

## Slug rules
- Keep slugs stable.
- Prefer short semantic English slugs if that is already the project convention.
- Do not rename slugs without checking links, indexes, and registry references.
- Avoid mixed slug strategies inside the same subtree.
- Do not mass-rename slugs as cosmetic cleanup.

## Bearing-specific hard rules
- Never invent bearing data, standards, analogs, suffix meanings, fits, clearances, or dimensions.
- Always separate base designation from prefixes and suffixes.
- A bearing analog is valid only with full technical match.
- Same base number does not prove equivalence.
- Do not infer GOST ⇄ ISO analogs automatically.
- If a fact is uncertain, mark the limitation instead of guessing.

Minimum technical checks where relevant:
- type;
- geometry;
- series;
- execution;
- clearance;
- precision class;
- sealing;
- cage;
- suffixes/prefixes.

## Content rules
- One page = one topic.
- Do not overload a page with overview + glossary + analog table unless explicitly required.
- For tables: explain how to read the table, then show the table, then add limitations/notes.
- Avoid filler and marketing language.
- Prefer dense, practical, engineering-oriented writing.
- Keep content portable between Bitrix24 KB and static publication.

## Bitrix24-specific rules
- Do not assume real Bitrix24 URLs unless they exist in the repository.
- Do not present guessed UI behavior as fact.
- Keep content CMS-portable.
- Prefer structures that survive export/import cleanly.

## Validation rules
Run relevant checks when the task affects the corresponding layer:

```bash
python scripts/process_inbox.py
python scripts/process_inbox.py --dry-run
python scripts/kb_quality_gate.py
python scripts/validate_bearing_cards.py
python tests/check_kb_links.py
```

Validation policy:
- do not claim a check was run if it was not run;
- if a relevant check could not be run, say so explicitly;
- prefer existing scripts over ad-hoc logic.

## Change policy
- Read relevant files before editing.
- Prefer small, local, reviewable diffs.
- Do not do decorative refactors.
- Do not mass-rename files, folders, slugs, or sections without explicit need.
- Do not bypass repository automation if the task is clearly an ingest/validation task.

## When touching `_templates/`, `_meta/`, or `INDEX.md`
Treat these as structural changes.
When editing them:
- preserve compatibility where possible;
- note the impact on existing content;
- avoid hidden taxonomy changes;
- do not silently change authoring contracts.

## Final response format
1. What changed
2. What was checked
3. Risks / limitations
4. Next step (only if needed)
