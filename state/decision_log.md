# Decision Log

Append-only log of every trade decision. Each entry is written as `pending` at the morning run and updated with realized returns and a reflection at EOD.

Entry format:
- Pending:  `[YYYY-MM-DD | TICKER | ACTION | pending]`
- Resolved: `[YYYY-MM-DD | TICKER | ACTION | +X.X% | +X.Xα | Nd]`
- Skipped:  `[YYYY-MM-DD | TICKER | ACTION | skipped]`

---
