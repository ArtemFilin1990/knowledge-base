---
name: bitrix-export-prep
description: Prepare canonical knowledge-base structure and article content for safe export or transfer into Bitrix24 Knowledge Base without mixing drafts, broken links, or non-canonical sources.
---

# bitrix-export-prep

Use this skill when the task is about preparing repository content for Bitrix24 Knowledge Base import, manual transfer, or CMS-oriented publication.

## Use when
- The user asks to prepare a batch of articles for Bitrix24.
- A section map, registry, or page tree needs to be converted into publishable KB pages.
- You need to separate what is ready for Bitrix24 from what is still draft or intake-only.
- You need to review links, slugs, statuses, and page types before transfer.

## Goals
1. Export only canonical content from `kb/ru/`.
2. Exclude raw intake, duplicate topics, and unsafe drafts.
3. Preserve stable slugs, page hierarchy, and navigation logic.
4. Ensure article content is portable to Bitrix24 without relying on unverified CMS assumptions.

## What to check
- Only canonical content from `kb/ru/` is included.
- Draft and verified status are handled honestly.
- Pages selected for Bitrix24 have valid metadata and stable slugs.
- `kb/ru/INDEX.md` and related navigation reflect the same canonical tree.
- Internal links point to real canonical pages.
- No duplicate topic is exported under multiple active paths.
- Bitrix-ready batches keep L1/L2 short and L3 detailed.

## Repository-specific rules
- Never export directly from `inbox/`.
- Never treat raw source files as publishable KB pages.
- Prefer repository article structure over CMS-specific formatting tricks.
- Keep content portable: headings, tables, lists, related links, and metadata should survive transfer cleanly.
- If Bitrix24-specific URL or UI behavior is not defined in the repo, do not invent it.

## Suggested workflow
1. Identify the target section or batch in `kb/ru/`.
2. Check metadata completeness and article status.
3. Run link and quality checks.
4. Build the minimal export set: pages, order, slugs, related links.
5. Flag pages that require rewrite, manual review, or holdback.

## Validation commands
Run when relevant:
```bash
python scripts/kb_quality_gate.py
python tests/check_kb_links.py
```

## Output format
1. Export decision: ready / partial / blocked
2. Pages safe for Bitrix24 transfer
3. Pages to hold back
4. Link, metadata, or slug issues
5. Minimal safe export plan

## Hard rules
- Do not export drafts as if they were verified.
- Do not invent final Bitrix24 URLs.
- Do not collapse canonical hierarchy just to simplify transfer.
- Do not include duplicate or stale pages in the export set.
- Prefer a smaller clean export over a larger noisy one.
