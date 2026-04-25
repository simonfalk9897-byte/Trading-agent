# Midday Run -- Market Check (12:00 PM ET)

This is a lighter run. You are monitoring, not making big decisions. The market is open. Your job is to check that everything is on track, manage risk, and adjust if needed.

You should have already loaded your memory (CLAUDE.md Step 1) before arriving here. If you have not, go back and do it now.

---

## Phase 1: Sync with Reality (estimated 1-2 minutes)

### 1.1 Check order fills
Query Alpaca for all orders placed during the morning run.
For each order:
- Did it fill? At what price?
- Did it partially fill?
- Is it still open/pending?

Update `state/portfolio.json` with actual fill prices and quantities. This is critical. Your state must reflect reality, not what you hoped would happen.

### 1.2 Snapshot current positions
For each position in `state/portfolio.json`:
- Pull current market price from Alpaca
- Calculate unrealized P&L (current price vs entry price)
- Calculate distance to stop loss
- Note intraday high and low

### 1.3 Check market conditions
- Pull current VIX level
- Pull current SPY price and compare to 50-day and 200-day MAs
- Has the regime changed since morning? (e.g., VIX spiked above 30, SPY broke below a key MA)

---

## Phase 2: Risk Assessment (estimated 1-2 minutes)

Work through each check. If any trigger fires, take the corresponding action.

### 2.1 Portfolio drawdown
Calculate current portfolio value (sum of all positions at current prices + cash).
Compare to peak portfolio value in `performance/daily.json`.

- Drawdown > 10% from peak? --> Halve all remaining position sizes. Tighten stops.
- Drawdown > 15%? --> Close enough positions to reach 50% cash. No new entries for 2 days.
- Drawdown > 20%? --> Close ALL positions. Go 100% cash. Send Telegram alert to Simon:
  ```
  ALERT: 20% drawdown circuit breaker triggered.
  Portfolio: $[value] | Peak: $[peak] | Drawdown: [X%]
  All positions closed. Manual override required.
  ```

### 2.2 Individual position checks
For each position:

**Has the stop loss been hit or nearly hit (within 0.5%)?**
- If the stop order on Alpaca has already triggered: confirm it executed, update state
- If price is within 0.5% of stop but has not triggered: monitor closely, do not move the stop further away

**Has a position moved significantly in our favor (> 3% gain since entry)?**
- Momentum positions: tighten the trailing stop. Move it up so the new risk is max 5% from current price (locking in some profit)
- Mean reversion positions: if it has hit the 3% profit target, exit now

**Has a mean reversion position been held for 5 days?**
- Time stop. Exit now regardless of P&L.

### 2.3 Sector exposure check
Calculate current allocation by sector. If any sector exceeds 30%, plan a trim for the EOD or next morning run.

### 2.4 Cash floor check
Calculate current cash percentage. If it has fallen below 20% due to fills, flag this. You may need to trim a position to restore the cash buffer.

---

## Phase 3: Adjustments (only if needed)

If Phase 2 identified any issues, act on them now:

### Exits / Trims
- Submit sell orders for any positions that need to be closed (stops hit, time stops, profit targets)
- Use limit orders near the current bid
- Update `state/portfolio.json` after submitting

### Stop adjustments
- For positions that have moved in your favor, update the trailing stop:
  - Cancel the old stop order on Alpaca
  - Submit a new stop order at the tightened level
  - Update the stop level in `state/portfolio.json`

### No new entries at midday
Do NOT open new positions during the midday run. Save new entries for the morning run when you have full research context. The only exception: a mean reversion candidate that triggers intraday AND you have already identified it in the morning's signals.

---

## Phase 4: Journal Update

Append to today's `journal/YYYY-MM-DD.md`:

```markdown
## Midday Check

### Order Status
- [TICKER] morning [BUY/SELL]: [filled at $XX / still open / cancelled]

### Position Updates
- [TICKER]: Current $XX | Entry $XX | P&L: [+/-X%] | Stop: $XX | Days held: [N]

### Risk Status
- Portfolio value: $XX | Cash: XX% | Drawdown from peak: X%
- VIX: XX | SPY vs MAs: [status]
- Regime: [same as morning / changed to X]

### Actions Taken
- [list any stop adjustments, exits, or trims]
- [or "No adjustments needed"]

### Concerns
- [anything to watch for the EOD run]
```

---

## Phase 5: Telegram (ONLY if something important happened)

You do NOT send a Telegram message every midday. Simon expects one daily summary at end of day.

Send a Telegram message ONLY if one or more of these are true:
- A drawdown circuit breaker triggered (10%, 15%, or 20%)
- A position lost more than 5% intraday
- A regime change happened since morning (VIX crossed above 30, SPY broke below key MA)
- You had to make an emergency exit or significant trim

If none of these apply, skip Telegram entirely.

Format for midday alerts:

```
-- Midday Alert --
Date: YYYY-MM-DD

[REASON]: [concise description]
Action taken: [what you did about it]
Portfolio: $[value] | Cash: [X%] | Drawdown: [X%]
```

---

## Phase 6: Save and Push

1. Save all modified files: `state/portfolio.json`, `journal/YYYY-MM-DD.md`
2. Git add, commit ("agent run: midday YYYY-MM-DD"), push
3. Verify push succeeded

You are done. Go to sleep until the end-of-day run.
