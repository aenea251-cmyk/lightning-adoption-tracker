# Adoption data schema (draft)

`data/adoption.json`

```json
{
  "updated_at": "2026-02-01T13:00:00Z",
  "sources": {
    "moltbook": {
      "window_hours": 24,
      "counts": {
        "posts_scanned": 0,
        "comments_scanned": 0,
        "lightning_mentions": 0,
        "bolt11_mentions": 0,
        "lnurl_mentions": 0,
        "phoenixd_mentions": 0,
        "tipjar_wellknown_mentions": 0
      },
      "highlights": [
        { "url": "https://...", "reason": "new tip jar protocol mention" }
      ]
    },
    "moltx": { "note": "pending connector" }
  }
}
```

Keyword heuristics:
- bolt11: `lnbc`, `lntb`, `lnbcrt`
- lnurl: `lnurl`
- phoenixd: `phoenixd`, `phoenix-cli`
- tipjar: `/.well-known/lightning.json`
