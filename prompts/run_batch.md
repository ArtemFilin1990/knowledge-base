# Run one batch (inbox → kb)

1) Scan `inbox/` (ignore `inbox/processed/`).
2) For each new file: extract text, choose topic slug (ascii kebab-case), split into 1..N articles if needed.
3) Create/Update topic sheet: `kb/ru/<topic>/README.md`.
4) Create article folders: `kb/ru/<topic>/<article>/README.md` using `_templates/article.md`.
   - Fill YAML metadata (id, title, topic, tags, status=draft, source, created/updated).
   - Fill: context, key points, steps, examples, common mistakes, see-also links.
5) Update indexes: `kb/ru/INDEX.md` + topic README.
6) Dedup: if sha256 already in `_meta/dedup_index.json`, do NOT create duplicate; log in `_meta/dedup_log.md`.
7) Move processed files to `inbox/processed/YYYY-MM/`.
8) Run `python scripts/kb_quality_gate.py` and ensure it passes.
Deliver PR summary: created topics/articles, updated indexes, duplicates, TBD list.
