# CLAUDE.md

Guidance for Claude (and other AI assistants) working inside this repository.

## Repository purpose

This is a curated Russian-language knowledge base (`kb/ru/`) with a controlled
pipeline: `inbox/` → classify → write article → update indexes → dedup. The
primary subject domain is rolling bearings (подшипники), but the structure is
general enough to host other topics.

Core principles (treat these as hard rules):

1. **One article = one folder = one `README.md`.**
2. **All folder names are ASCII kebab-case.** No spaces, no Cyrillic, no
   snake_case, no camelCase.
3. **Every article `README.md` in `kb/` must begin with YAML front-matter**
   containing `id`, `title`, `topic`, `tags`, `status`, `source`, `created`,
   `updated`.
4. **`status: verified`** requires zero `[[TBD]]` placeholders and real sources.
   Default `status: draft`.
5. **`kb/ru/` is the canonical content layer.** Do not stash drafts, prompts,
   or scratch files there.
6. **`inbox/` is the only user-facing entry point for new raw material.**
   Never hand-sort files inside it — the processor does that.
7. **Dedup by SHA256 of article body.** Do not publish a new article if the
   content already exists; log the duplicate instead.

## Top-level layout

```
/knowledge-base
  kb/ru/               # canonical knowledge base (Russian)
    INDEX.md           # main index; update whenever topics/articles change
    <topic>/README.md  # topic landing page
    <topic>/<article>/README.md  # article
  inbox/               # raw material drop zone (single entry point)
    processed/YYYY-MM/ # archived after processing
    README.md
  _templates/          # article.md, bearing-card.md — use these as skeletons
  _meta/               # id_registry.json, dedup_index.json, dedup_log.md,
                       # topics.json, repository-audit.md, ingestion/
  prompts/             # operational prompts for the ingestion agent
  scripts/             # Python automation (no package, run from repo root)
  tests/               # link checker and similar lightweight checks
  docs/                # human-facing docs (e.g. inbox-processor.md)
  .github/workflows/   # CI: kb-quality.yml, inbox-processor.yml
```

## Article contract

Every article is a folder containing exactly one `README.md`. The front-matter
shape (see `_templates/article.md`):

```yaml
---
id: KB-RU-000000          # allocated by scripts/process_inbox.py via _meta/id_registry.json
title: "<Russian title>"
topic: <kebab-case slug>  # must match the parent topic folder
tags: []
status: draft             # draft | verified | deprecated
source: inbox/<filename>  # or external citation
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Body blocks (keep the order and headings from `_templates/article.md`):
Кому и зачем → Контекст применения → Ключевые пункты → Алгоритм / шаги →
Примеры → Частые ошибки → См. также → Источники и примечания → Контроль
качества.

Bearing spec cards use the richer `_templates/bearing-card.md` and live under
`kb/ru/bearings/cards/`. They add `designation`, `dims`, `standards`,
`equivalents`, `load_capacity` front-matter keys, validated by
`scripts/validate_bearing_cards.py`.

## ID allocation

- IDs are strings like `KB-RU-000123`, padded to 6 digits.
- The next free ID lives in `_meta/id_registry.json` (`next_id`, `prefix`,
  `pad`). At the time of writing `next_id = 471`.
- Do **not** hand-edit `next_id` unless you are reconciling a collision. Let
  `scripts/process_inbox.py` allocate IDs via `allocate_id()`.
- IDs must be unique across the whole `kb/` tree — `kb_quality_gate.py`
  enforces this.

## Ingestion workflow (inbox → article)

The canonical path is `scripts/process_inbox.py`; the agent prompt
`prompts/agent_v2.md` describes the same contract in natural language.

1. Drop files into `inbox/` (currently only `.md` is auto-processed — PDF,
   DOCX, etc. need manual extraction first).
2. Run `python scripts/process_inbox.py` (add `--dry-run` to preview).
3. The script will:
   - Strip any existing YAML front-matter, compute SHA256, check
     `_meta/dedup_index.json`.
   - Classify the topic via keyword matching in `classify_topic()` (bearings,
     lubrication-seals, drive-systems, standards, general).
   - Allocate a new ID, slugify the title with `to_kebab_case()` (length
     capped at 50 chars), and write
     `kb/ru/<topic>/<slug>/README.md` from the template.
   - Update the topic `README.md` by inserting a link under `## Статьи`
     (create the topic folder + landing page if missing).
   - Record the new hash in `_meta/dedup_index.json`, append duplicates to
     `_meta/dedup_log.md`.
   - Move the original file to `inbox/processed/YYYY-MM/`, appending a numeric
     suffix if a name collision occurs.

Duplicates are not rewritten — only logged and moved to `processed/`.

The GitHub Action `.github/workflows/inbox-processor.yml` runs the same
script on `push` to `main` when `inbox/**` changes and opens a PR on the
`auto-process-inbox` branch. Do not commit directly to that branch.

## Quality gates (must pass before merge)

`scripts/kb_quality_gate.py` — invoked by `.github/workflows/kb-quality.yml`
on PRs touching `kb/**`, `_templates/**`, `_meta/**`, or `scripts/**`. It:

- Requires `kb/ru/INDEX.md` to exist.
- Walks every `kb/**/README.md`, parses YAML front-matter, enforces:
  - presence of all `REQUIRED_KEYS`
    (`id`, `title`, `topic`, `tags`, `status`, `source`, `created`, `updated`);
  - `status ∈ {draft, verified, deprecated}`;
  - unique `id` across the tree;
  - `topic` is either `[[TBD]]` or kebab-case ASCII;
  - `verified` articles contain no `[[TBD]]`;
- Enforces that every folder segment under `kb/` is ASCII kebab-case, no
  spaces.

`scripts/validate_bearing_cards.py` — validates bearing-card specific fields
under `kb/ru/bearings/cards/` (`designation` is a dict, `dims` has `d/D/B`,
`load_capacity.dynamic_C_kN`, non-empty `equivalents`).

`tests/check_kb_links.py` — verifies local links from `kb/ru/INDEX.md` and
`kb/ru/overview/README.md` resolve to real files. Run it after touching
either file.

Run everything locally before pushing:

```bash
python scripts/kb_quality_gate.py
python scripts/validate_bearing_cards.py
python tests/check_kb_links.py
```

All three are plain Python 3.11, no dependencies, run from the repo root so
relative paths (`kb/`, `_meta/`, etc.) resolve.

## Other scripts

- `scripts/generate_bearing_cards.py` — bulk-generate bearing cards from a
  CSV catalog using `_templates/bearing-card.md`. Reads
  `kb/ru/bearings/datasets/catalog.csv` + `equivalents.csv`, writes under
  `kb/ru/bearings/cards/`. CLI flags: `--catalog`, `--equivalents`,
  `--output-dir`, `--id-start`, `--suffixes`.
- `scripts/generate_bearings_yml.py` — builds a Yandex Market Language XML
  catalog (`kb/ru/bearings/export.xml`) from the bearing datasets.
- `scripts/push_kb_to_bitrix24.py` — mirrors `kb/ru/` into a Bitrix24
  knowledge base via REST. Needs `BITRIX24_WEBHOOK` and `BITRIX24_SITE_ID`
  env vars; caches remote IDs in `scripts/.bitrix24_kb_state.json`
  (gitignored). Requires the `markdown` Python package. Run with `--dry-run`
  before touching production.

## Metadata files (`_meta/`)

Do not overwrite these blindly — they are mutated by scripts:

- `id_registry.json` — ID allocator state. Only `process_inbox.py` should
  bump `next_id`.
- `dedup_index.json` — `{sha256: canonical_path}`. Keep in sync with what's
  actually on disk; if you move an article, update the value.
- `dedup_log.md` — append-only human-readable log of duplicates.
- `topics.json` — optional topic metadata (title, language, status). Not
  exhaustive today; add entries when you introduce a new topic.
- `repository-audit.md` — design notes and roadmap. Background reading.
- `ingestion/` — raw ingestion artefacts (`registry.jsonl`, `outputs/`).

## Conventions and style

- Russian for titles, body copy, and comments in `kb/`. ASCII kebab-case for
  paths. Scripts/comments can be bilingual — existing code mixes Russian
  docstrings with English identifiers; follow the file you are editing.
- No spaces in folder names anywhere under `kb/`.
- Prefer updating existing articles over creating near-duplicates.
- When referencing another article, use a relative link with the
  `./<slug>/README.md` form so the link checker can resolve it.
- `[[TBD]]` is the only allowed placeholder marker; never leave bare "TODO".
- Keep front-matter keys in the order used by `_templates/article.md` — the
  simple line-based parser in `kb_quality_gate.py` reads top-level `key: value`
  only, so do not introduce nested YAML in the required keys.
- Dates are ISO 8601 (`YYYY-MM-DD`).

## Adding a new topic

1. Pick a kebab-case slug that does not collide with existing folders under
   `kb/ru/`.
2. Create `kb/ru/<topic>/README.md` with front-matter (`tags: ["topic-index"]`
   is the convention used by `process_inbox.update_topic_readme`) and a
   `## Статьи` section.
3. Add a link to the new topic from `kb/ru/INDEX.md`.
4. Optionally register it in `_meta/topics.json`.
5. Run `python scripts/kb_quality_gate.py` and `python tests/check_kb_links.py`.

## Adding or modifying scripts

- Target Python 3.11 (the CI image). Keep scripts dependency-free where
  possible; only `push_kb_to_bitrix24.py` currently needs a third-party
  package (`markdown`).
- Run scripts from the repository root so `Path("kb/ru")` etc. resolve.
- When adding automation, wire it into `.github/workflows/kb-quality.yml` if
  it's a gate, or create a dedicated workflow if it mutates the tree.

## What not to do

- Do **not** write articles directly into `kb/ru/` from prose in `inbox/`
  without going through the template + front-matter contract.
- Do **not** rename or delete files under `inbox/processed/` — it's the
  historical archive that the dedup log references.
- Do **not** bypass `kb_quality_gate.py`; fix the underlying issue instead.
- Do **not** push to `main` directly; open a PR. The `inbox-processor`
  workflow expects to own the `auto-process-inbox` branch.
- Do **not** add Cyrillic or spaces to any path under `kb/`, `_templates/`,
  `_meta/`, `scripts/`, or `tests/`.
- Do **not** fabricate technical facts (standards numbers, load capacities,
  manufacturer equivalents). If the source material doesn't cover it,
  write `[[TBD]]` and keep `status: draft`.

## Quick command cheatsheet

```bash
# Process the inbox (preview then apply)
python scripts/process_inbox.py --dry-run
python scripts/process_inbox.py

# Validate the KB
python scripts/kb_quality_gate.py
python scripts/validate_bearing_cards.py
python tests/check_kb_links.py

# Generate bearing cards from the CSV catalog
python scripts/generate_bearing_cards.py \
    --catalog kb/ru/bearings/datasets/catalog.csv \
    --equivalents kb/ru/bearings/datasets/equivalents.csv \
    --output-dir kb/ru/bearings/cards \
    --id-start 30

# Rebuild the YML export
python scripts/generate_bearings_yml.py

# Mirror to Bitrix24 (requires env vars)
BITRIX24_WEBHOOK=... BITRIX24_SITE_ID=... \
    python scripts/push_kb_to_bitrix24.py --dry-run
```
