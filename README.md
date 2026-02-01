# Lightning adoption tracker (agent social networks)

Goal: track Lightning usage/adoption signals across agent social networks (starting with Moltbook/Moltx), e.g.:
- number of posts/comments mentioning Lightning (bolt11 / lnurl / phoenixd / invoices)
- number of “tip jar” discovery endpoints seen
- notable new projects/skills

Outputs:
- `data/adoption.json` (time series)
- a tiny static dashboard (site/) that renders the data

Non-goals:
- no custody, no payments
- no deanonymization or cross-linking identities across platforms

Next: implement collectors per network under `scripts/collect_*.py` and run them on heartbeat/cron.
