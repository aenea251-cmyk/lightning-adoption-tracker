#!/usr/bin/env python3
"""Collect Lightning adoption signals from Moltx by scraping public pages.

Fallback when API access is not available.

Env:
- WINDOW_HOURS (default 24) [best-effort; scrape doesn't provide reliable timestamps]
- LIMIT_PAGES (default 2)
- OUT_PATH (default projects/lightning/adoption-tracker/data/adoption.json)

This script is intentionally conservative and read-only.
"""

import json
import os
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

BASE = "https://moltx.io"

LIMIT_PAGES = int(os.environ.get("LIMIT_PAGES", "2"))
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


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OpenClaw-adoption-tracker/0.1)"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


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
    counts = {
        "pages_scanned": 0,
        "lightning_mentions": 0,
        "bolt11_mentions": 0,
        "lnurl_mentions": 0,
        "phoenixd_mentions": 0,
        "tipjar_wellknown_mentions": 0,
    }
    highlights = []

    # Best-effort: scrape the home/feed pages (Moltx is dynamic; this may be incomplete).
    urls = [f"{BASE}/"]
    for i in range(2, LIMIT_PAGES + 1):
        urls.append(f"{BASE}/?page={i}")

    for url in urls:
        html = fetch(url)
        counts["pages_scanned"] += 1
        count_text(html, counts)
        if BOLT11_RE.search(html) or KEYWORDS["tipjar"].search(html):
            highlights.append({"url": url, "reason": "page contains bolt11 or tipjar marker"})

    out = {
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": {
            "moltx": {
                "mode": "scrape",
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
    main()
