"""Mirror kb/ru/ overview articles into a Bitrix24 knowledge base.

Walks every README.md / *.md inside kb/ru/ (excluding bearings/cards/) and
publishes it as a separate landing page in the target Bitrix24 knowledge base.
Folders are mirrored as Bitrix24 site folders. The article body is converted
from Markdown to HTML and pushed into a single text block per landing — no
content truncation.

Usage:
    BITRIX24_WEBHOOK=https://<portal>/rest/<uid>/<token>/ \
    BITRIX24_SITE_ID=67 \
    python scripts/push_kb_to_bitrix24.py [--dry-run]

The state file scripts/.bitrix24_kb_state.json caches mappings from local
paths to remote folder/landing IDs so the script can be re-run incrementally
without recreating items that already exist.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

import markdown  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = REPO_ROOT / "kb" / "ru"
EXCLUDE_DIR_PARTS = {"cards"}
STATE_FILE = REPO_ROOT / "scripts" / ".bitrix24_kb_state.json"

BLOCK_CODE = "08.3.one_col_fix_title_and_text"
SLEEP_BETWEEN_CALLS = 0.25  # Bitrix24 REST throttling
MAX_TITLE = 240
MAX_CODE = 240
NODE_TITLE = ".landing-block-node-title"
NODE_SUBTITLE = ".landing-block-node-subtitle"
NODE_TEXT = ".landing-block-node-text"


# ---------- Bitrix24 REST helpers ----------------------------------------------------


class Bitrix24Client:
    def __init__(self, webhook: str, scope: str = "KNOWLEDGE", verbose: bool = True):
        self.webhook = webhook.rstrip("/") + "/"
        self.scope = scope
        self.verbose = verbose

    def call(self, method: str, payload: dict | None = None) -> dict:
        url = self.webhook + method + ".json"
        flat: list[tuple[str, str]] = []
        if self.scope:
            flat.append(("scope", self.scope))
        if payload:
            _flatten("", payload, flat)
        body = urllib.parse.urlencode(flat).encode("utf-8")
        req = urllib.request.Request(url, data=body)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                payload_str = exc.read().decode("utf-8", "replace")
                if exc.code == 503 or exc.code == 429:
                    wait = 2 ** attempt
                    print(f"  ! HTTP {exc.code}; retry in {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"HTTP {exc.code} on {method}: {payload_str}")
            except urllib.error.URLError as exc:
                wait = 2 ** attempt
                print(f"  ! network error {exc}; retry in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            time.sleep(SLEEP_BETWEEN_CALLS)
            if "error" in data:
                raise RuntimeError(
                    f"Bitrix24 error on {method}: {data.get('error')} — "
                    f"{data.get('error_description')}"
                )
            return data
        raise RuntimeError(f"giving up on {method} after retries")


def _flatten(prefix: str, value, out: list[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            key = f"{prefix}[{k}]" if prefix else str(k)
            _flatten(key, v, out)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _flatten(f"{prefix}[{i}]", v, out)
    else:
        out.append((prefix, "" if value is None else str(value)))


# ---------- File walking + parsing ---------------------------------------------------


FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_article(path: Path) -> tuple[str, str, str]:
    """Return (title, breadcrumb, html_body) for a markdown article."""
    text = path.read_text(encoding="utf-8")
    front_title = ""
    match = FRONT_MATTER_RE.match(text)
    if match:
        for line in match.group(1).splitlines():
            if line.startswith("title:"):
                front_title = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        text = text[match.end():]

    # Extract first heading (# Title) as the title if no front-matter title.
    title = front_title
    body_lines: list[str] = []
    seen_first_h1 = False
    for line in text.splitlines():
        if not seen_first_h1 and line.lstrip().startswith("# "):
            heading = line.lstrip()[2:].strip()
            if not title:
                title = heading
            seen_first_h1 = True
            continue
        body_lines.append(line)
    if not title:
        title = path.parent.name or path.stem

    body_md = "\n".join(body_lines).strip()
    html = markdown.markdown(
        body_md,
        extensions=["extra", "tables", "fenced_code", "sane_lists"],
    )
    breadcrumb = " / ".join(path.relative_to(KB_ROOT).parent.parts) or "kb/ru"
    return title.strip()[:MAX_TITLE], breadcrumb[:MAX_TITLE], html


def collect_articles() -> list[Path]:
    files: list[Path] = []
    for p in sorted(KB_ROOT.rglob("*.md")):
        if any(part in EXCLUDE_DIR_PARTS for part in p.relative_to(KB_ROOT).parts):
            continue
        files.append(p)
    return files


# ---------- Slug helpers -------------------------------------------------------------


_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str, fallback: str = "page") -> str:
    text = text.strip().lower()
    out_chars: list[str] = []
    for ch in text:
        if ch in _TRANSLIT:
            out_chars.append(_TRANSLIT[ch])
        elif ch.isascii() and (ch.isalnum() or ch in "-_"):
            out_chars.append(ch)
        elif ch.isspace() or ch in "/\\.":
            out_chars.append("-")
    slug = "".join(out_chars)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return (slug or fallback)[:MAX_CODE]


# ---------- State management ---------------------------------------------------------


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"folders": {}, "articles": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- Main upload routine ------------------------------------------------------


def ensure_folder(
    client: Bitrix24Client,
    state: dict,
    site_id: int,
    rel_dir: tuple[str, ...],
    dry_run: bool,
) -> int | None:
    """Create the folder chain rel_dir under site_id; return final folder id (or None if root)."""
    if not rel_dir:
        return None
    parent_id = 0
    key_chain: list[str] = []
    for part in rel_dir:
        key_chain.append(part)
        key = "/".join(key_chain)
        if key in state["folders"]:
            parent_id = int(state["folders"][key])
            continue
        title = part.replace("-", " ").replace("_", " ").strip().capitalize() or part
        code = slugify(part, fallback="folder")
        print(f"  + folder {key} (parent={parent_id}) → '{title}'")
        if dry_run:
            parent_id = -1
            state["folders"][key] = parent_id
            continue
        result = client.call(
            "landing.site.addfolder",
            {
                "siteId": site_id,
                "fields": {
                    "TITLE": title[:MAX_TITLE],
                    "CODE": code,
                    "PARENT_ID": parent_id or 0,
                    "ACTIVE": "Y",
                },
            },
        )
        parent_id = int(result["result"])
        state["folders"][key] = parent_id
        save_state(state)
    return parent_id


def push_article(
    client: Bitrix24Client,
    state: dict,
    site_id: int,
    path: Path,
    folder_id: int | None,
    dry_run: bool,
) -> None:
    rel = str(path.relative_to(KB_ROOT))
    if rel in state["articles"]:
        print(f"  ✓ skip (already pushed) {rel}")
        return
    title, breadcrumb, html = parse_article(path)
    code = slugify("-".join(path.relative_to(KB_ROOT).with_suffix("").parts), "page")
    print(f"  → {rel}  →  «{title}»  ({len(html)} bytes html)")
    if dry_run:
        state["articles"][rel] = {"landing_id": -1, "block_id": -1}
        return
    add_payload = {
        "fields": {
            "SITE_ID": site_id,
            "TITLE": title[:MAX_TITLE],
            "CODE": code[:MAX_CODE],
            "ACTIVE": "Y",
        }
    }
    if folder_id and folder_id > 0:
        add_payload["fields"]["FOLDER_ID"] = folder_id
    landing = client.call("landing.landing.add", add_payload)
    landing_id = int(landing["result"])

    block = client.call(
        "landing.landing.addblock",
        {"lid": landing_id, "fields": {"CODE": BLOCK_CODE, "ACTIVE": "Y"}},
    )
    block_id = int(block["result"])

    client.call(
        "landing.block.updatenodes",
        {
            "lid": landing_id,
            "block": block_id,
            "data": {
                NODE_SUBTITLE: breadcrumb,
                NODE_TITLE: title,
                NODE_TEXT: html or "<p></p>",
            },
        },
    )
    client.call("landing.landing.publication", {"lid": landing_id})
    state["articles"][rel] = {"landing_id": landing_id, "block_id": block_id}
    save_state(state)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="upload at most N articles (0 = all)")
    args = ap.parse_args()

    webhook = os.environ.get("BITRIX24_WEBHOOK")
    site_id = int(os.environ.get("BITRIX24_SITE_ID", "0"))
    if not webhook or not site_id:
        sys.exit("Set BITRIX24_WEBHOOK and BITRIX24_SITE_ID environment variables")

    client = Bitrix24Client(webhook)
    state = load_state()

    files = collect_articles()
    print(f"discovered {len(files)} articles in {KB_ROOT}")
    if args.limit:
        files = files[: args.limit]
        print(f"limiting to first {len(files)} for this run")

    for path in files:
        rel_parts = path.relative_to(KB_ROOT).parent.parts
        folder_id = ensure_folder(client, state, site_id, rel_parts, args.dry_run)
        try:
            push_article(client, state, site_id, path, folder_id, args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! FAILED {path}: {exc}", file=sys.stderr)
            save_state(state)
    save_state(state)
    print(f"done. state → {STATE_FILE}")


if __name__ == "__main__":
    main()
