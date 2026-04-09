---
name: bearing-article-verify
description: Verify a bearing-related article for factual accuracy, metadata integrity, analog safety, and canonical knowledge-base readiness before marking it as ready or verified.
---

# bearing-article-verify

Use this skill when the task is about checking a single bearing article or a small batch of articles before publication.

## Use when
- The user asks to verify a page about designations, standards, analogs, fits, clearances, or bearing types.
- A page is moving from `draft` toward `verified` or `ready`.
- You suspect unsafe claims about GOST/ISO mappings, suffix meanings, or analogs.

## What to verify
1. The article matches the repository article contract from `_templates/article.md`.
2. Metadata is present and honest: `id`, `title`, `topic`, `tags`, `status`, `source`, `created`, `updated`.
3. Bearing facts are not invented.
4. Base designation, prefixes, suffixes, and execution details are not mixed up.
5. No analog is stated unless the technical match is explicit and defensible.
6. Links in `See also` / related sections are real and relevant.
7. A page marked `verified` has no unresolved placeholders.

## Bearing-specific hard checks
Always check these where relevant:
- type;
- geometry;
- series;
- execution;
- clearance;
- precision class;
- sealing;
- cage;
- suffixes/prefixes;
- standards references.

## Validation commands
Run when relevant:
```bash
python scripts/kb_quality_gate.py
python tests/check_kb_links.py
python scripts/validate_bearing_cards.py
```

## Output format
1. Publish decision: `ready`, `draft`, or `needs rewrite`
2. Factual issues
3. Metadata issues
4. Link / structure issues
5. Smallest safe edit set

## Hard rules
- Never approve guessed GOST ⇄ ISO analogs.
- Never treat matching base numbers as enough proof.
- Never mark an article `verified` if `[[TBD]]` remains.
- Prefer one precise correction over broad rewriting.
