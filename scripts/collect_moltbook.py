#!/usr/bin/env python3
"""Collect simple Lightning adoption signals from Moltbook.

This is intentionally heuristic-based: count keyword mentions in recent posts/comments.

Env:
- MOLTBOOK_API_KEY (required)
- WINDOW_HOURS (default 24)
- LIMIT_POSTS (default 50)
- OUT_PATH (default projects/lightning/adoption-tracker/data/adoption.json)

Note: Moltbook API surface can change; adjust endpoints as needed.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

API_BASE = "https://www.moltbook.com/api/v1"

WINDOW_HOURS = int(os.environ.get("WINDOW_HOURS", "24"))
LIMIT_POSTS = int(os.environ.get("LIMIT_POSTS", "50"))
OUT_PATH = os.environ.get(
    "OUT_PATH",
    "projects/lightning/adoption-tracker/data/adoption.json",
)

BOLT11_RE = re.compile(r"\bln(?:bc|tb|bcrt)[0-9a-z]+\b", re.IGNORECASE)
LNURL_RE = re.compile(r"\blnurl[0-9a-z]+\b", re.IGNORECASE)

KEYWORDS = {
    "lightning": re.compile(r"\blightning\b", re.IGNORECASE),
    "phoenixd": re.compile(r"\bphoenixd\b|\bphoenix-cli\b", re.IGNORECASE),
    "tipjar": re.compile(r"/\.well-known/lightning\.json", re.IGNORECASE),
}


def mb_get(path: str):
    api_key = os.environ["MOLTBOOK_API_KEY"]
    req = Request(API_BASE + path, headers={"Authorization": f"Bearer {api_key}"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def count_text(text: str, counts: dict):
    t = text or ""
    if KEYWORDS["lightning"].search(t):
        counts["lightning_mentions"] += 1
    if BOLT11_RE.search(t):
        counts["bolt11_mentions"] += 1
    if LNURL_RE.search(t):
        counts["lnurl_mentions"] += 1
    if KEYWORDS["phoenixd"].search(t):
        counts["phoenixd_mentions"] += 1
    if KEYWORDS["tipjar"].search(t):
        counts["tipjar_wellknown_mentions"] += 1


def main():
    since_ts = int(time.time()) - WINDOW_HOURS * 3600

    counts = {
        "posts_scanned": 0,
        "comments_scanned": 0,
        "lightning_mentions": 0,
        "bolt11_mentions": 0,
        "lnurl_mentions": 0,
        "phoenixd_mentions": 0,
        "tipjar_wellknown_mentions": 0,
    }
    highlights = []

    # Best-effort: fetch latest posts.
    # Moltbook currently supports /posts; if it changes, adjust here.
    posts_resp = mb_get(f"/posts?sort=new&limit={LIMIT_POSTS}")
    posts = posts_resp.get("posts") or posts_resp.get("data") or []

    for p in posts:
        counts["posts_scanned"] += 1
        content = (p.get("content") or "") + "\n" + (p.get("title") or "")
        count_text(content, counts)

        created = p.get("created_at") or p.get("createdAt")
        # If no timestamps are available, still count mentions.
        if created:
            # accept ISO strings
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if int(dt.timestamp()) < since_ts:
                    continue
            except Exception:
                pass

        url = p.get("url") or (f"https://www.moltbook.com/posts/{p.get('id')}" if p.get("id") else None)
        if url and (BOLT11_RE.search(content) or KEYWORDS["tipjar"].search(content)):
            highlights.append({"url": url, "reason": "post mentions bolt11 or tipjar"})

    out = {
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": {
            "moltbook": {
                "window_hours": WINDOW_HOURS,
                "counts": counts,
                "highlights": highlights[:20],
            }
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    if "MOLTBOOK_API_KEY" not in os.environ:
        raise SystemExit("Missing MOLTBOOK_API_KEY")
    main()
