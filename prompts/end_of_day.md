# End of Day Run -- Close + Report (4:30 PM ET)

The market has closed. This run is about accounting, reflection, and reporting. You calculate today's results, update your performance records, write your journal, and send Simon the daily Telegram report.

You should have already loaded your memory (CLAUDE.md Step 1) before arriving here. If you have not, go back and do it now.

---

## Phase 1: Final Accounting (estimated 2-3 minutes)

### 1.1 Pull closing prices
Query Alpaca for end-of-day prices for:
- Every stock in `state/portfolio.json`
- SPY (benchmark)
- VIX (regime indicator)
- The 11 sector ETFs (for tomorrow's momentum calculation)

### 1.2 Reconcile all orders
Check every order placed today (morning and midday runs):
- Filled orders: confirm fill price, update `state/portfolio.json` with actual entry/exit prices
- Unfilled orders: cancel them (they are stale). Log them as "unfilled, cancelled" in the journal.
- Partially filled orders: update position size to actual fill quantity

### 1.3 Calculate position-level P&L
For each position in `state/portfolio.json`:
- Daily P&L = (closing price - previous close) * shares
- Total P&L = (closing price - entry price) * shares
- Daily return % = daily P&L / position value at open
- Total return % = total P&L / cost basis
- Days held (increment by 1)
- Update trailing stop level if price moved in your favor today

### 1.4 Calculate portfolio-level P&L
- Portfolio value = sum of all positions at closing prices + cash
- Daily return = (today's value - yesterday's value) / yesterday's value
- SPY daily return = (SPY close - SPY previous close) / SPY previous close
- Daily alpha = portfolio daily return - SPY daily return
- Cumulative alpha = running sum of daily alpha since inception

### 1.5 Calculate risk metrics
- Current drawdown = (peak value - current value) / peak value
- Update peak value if today's value is a new high
- Cash percentage = cash / portfolio value
- Sector exposure breakdown

---

## Phase 2: Update Performance Records (estimated 1-2 minutes)

### 2.1 Update daily.json
Append today's record to `performance/daily.json`:

```json
{
  "date": "YYYY-MM-DD",
  "portfolio_value": 10342.50,
  "cash": 2890.00,
  "cash_pct": 27.9,
  "invested_pct": 72.1,
  "daily_return_pct": 0.82,
  "spy_daily_return_pct": 0.45,
  "daily_alpha_pct": 0.37,
  "cumulative_return_pct": 3.43,
  "spy_cumulative_return_pct": 1.30,
  "cumulative_alpha_pct": 2.13,
  "peak_value": 10342.50,
  "drawdown_pct": 0.0,
  "vix_close": 18.5,
  "positions_count": 5,
  "trades_today": 3
}
```

### 2.2 Calculate running statistics
From the daily.json history, compute:
- **Sharpe ratio** = (average daily return - risk free rate) / std dev of daily returns * sqrt(252)
- **Win rate** = days with positive return / total trading days
- **Momentum strategy win rate** = winning momentum trades / total momentum trades
- **Mean reversion strategy win rate** = winning MR trades / total MR trades
- **Profit factor** = sum of all winning trades / abs(sum of all losing trades)
- **Average hold time** by strategy type
- **Best and worst single-day returns**

### 2.3 Weekly/Monthly rollups
If today is Friday:
- Calculate weekly return and alpha
- Append to `performance/weekly.json`

If today is the last trading day of the month:
- Calculate monthly return and alpha
- Append to `performance/monthly.json`

---

## Phase 2b: Update Decision Log (estimated 1-2 minutes)

### 2b.1 Identify closed positions today
From your reconciled order list (step 1.2), identify every position that was fully closed today — whether by a sell order, a stop-loss hit, a profit target, or a time stop.

For each closed position:
- Raw return % = `(exit_price - entry_price) / entry_price`
- Alpha = raw return % minus SPY's return over the same holding period
- Holding days = days from entry date to today

### 2b.2 Write reflections to decision log
For each closed position, find its pending entry in `state/decision_log.md` (the entry whose tag contains the ticker and ends in `| pending]`).

Update it by:
1. Replacing the tag line with the resolved tag:
   `[entry_date | TICKER | action | raw_return% | alpha% | Nd]`
   Example: `[2026-05-07 | NVDA | BUY-MOMENTUM | +3.2% | +1.8%α | 4d]`

2. Appending a REFLECTION section after the DECISION block:

```
REFLECTION:
Was the bull case right? [yes/no — why]
Was the bear case right? [yes/no — why]
What worked: [specific observation]
What missed: [specific observation]
Lesson: [one concrete, actionable takeaway for next time on this ticker or setup]
```

Also resolve any PASS entries from the same day: update their tag with `| skipped]` and add a brief reflection on whether the pass was the right call given what actually happened to the stock today.

### 2b.3 Save the decision log
Write the updated `state/decision_log.md`. The file must be saved before the Telegram report is sent (you will reference it in the report).

---

## Phase 3: Daily Journal -- Reflection (estimated 2-3 minutes)

This is the most important part of the EOD run. Your journal is your memory. Future runs will read this to make better decisions.

Append to `journal/YYYY-MM-DD.md`:

```markdown
## End of Day Summary

### Performance
- Portfolio: $[value] ([+/-X%] today)
- SPY: [+/-X%] today
- Alpha: [+/-X%] today | [+/-X%] cumulative
- Drawdown from peak: [X%]

### Trades Executed Today
| Action | Ticker | Strategy | Shares | Price | P&L | Rationale |
|--------|--------|----------|--------|-------|-----|-----------|
| BUY    | NVDA   | Momentum | 15     | $134.20 | --  | Top sector (XLK), RS rank 1 |
| SELL   | AAPL   | MeanRev  | 10     | $198.50 | +2.8% | RSI(2) > 60, reversion complete |

### Current Holdings
| Ticker | Strategy | Shares | Entry | Current | P&L % | Days | Stop |
|--------|----------|--------|-------|---------|-------|------|------|
| MSFT   | Momentum | 8      | $415  | $420    | +1.2% | 6    | $382 |
| NVDA   | Momentum | 15     | $134  | $135    | +0.5% | 1    | $123 |

### What Worked Today
- [specific observations about winning trades or good decisions]

### What Did Not Work
- [specific observations about losing trades or missed opportunities]

### Lessons for Tomorrow
- [concrete takeaways that should influence the next morning run]
- [e.g., "Energy sector momentum is fading -- watch for exit signal tomorrow"]
- [e.g., "Mean reversion in AAPL worked perfectly -- keep scanning oversold large caps"]

### Strategy Performance (Running Totals)
- Momentum trades: [W] wins / [L] losses ([X%] win rate)
- Mean reversion trades: [W] wins / [L] losses ([X%] win rate)
- PEAD trades: [W] wins / [L] losses ([X%] win rate)
- Overall profit factor: [X]

### Market Notes for Tomorrow
- [Any events, earnings, or macro data to watch]
- [Sector trends: which are strengthening, which are weakening]
- [Regime assessment: are we heading toward defensive mode?]
```

---

## Phase 4: Telegram Report -- MANDATORY (estimated 1 minute)

This is the ONE message Simon expects every trading day. Always send it. The morning and midday runs only send alerts if something went wrong. This EOD report is the daily summary Simon reads every evening.

### Standard daily report format:

```
-- Trading Agent Daily Report --
Date: YYYY-MM-DD

Portfolio: $[value] ([+/-X%])
SPY:       [+/-X%]
Alpha:     [+/-X%] today | [+/-X%] cumulative
Sharpe:    [X.XX]

Trades:
  [BUY/SELL] [TICKER] x[shares] @ $[price] ([strategy])
  [BUY/SELL] [TICKER] x[shares] @ $[price] ([strategy])

Holdings ([N] positions):
  [TICKER] [X%] of portfolio  [+/-X%] today
  [TICKER] [X%] of portfolio  [+/-X%] today

Risk:
  Invested: [X%] | Cash: [X%]
  Drawdown: [X%] from peak
  VIX: [X] | Regime: [offense/cautious/defensive]

Today's Lessons:
  [TICKER] ([+/-X%], [+/-X%]α): [one-line lesson from decision log reflection]
  [TICKER] ([+/-X%], [+/-X%]α): [one-line lesson from decision log reflection]
  (omit this section if no positions were closed today)

Notes:
  [1-2 sentences on the day's key takeaway]
```

The "Today's Lessons" lines come directly from the REFLECTION entries you wrote in Phase 2b. Each line should be a single punchy takeaway Simon can absorb in 5 seconds.

### Alert-level messages (send IMMEDIATELY, not just at EOD):
- Drawdown > 15%: "WARNING: Portfolio drawdown at [X%]. Reducing exposure."
- Drawdown > 20%: "CRITICAL: 20% circuit breaker triggered. All positions closed. Manual override required."
- Single position loss > 5%: "ALERT: [TICKER] down [X%] today. Stop loss at $[X]."

### Weekly summary (send on Fridays in addition to daily report):

```
-- Weekly Summary --
Week of: YYYY-MM-DD

Portfolio: $[value] ([+/-X%] this week)
SPY:       [+/-X%] this week
Alpha:     [+/-X%] this week | [+/-X%] cumulative

Trades: [N] total ([W] wins, [L] losses)
Best:   [TICKER] [+X%]
Worst:  [TICKER] [-X%]

Strategy Breakdown:
  Momentum:    [+/-X%] contribution
  MeanRev:     [+/-X%] contribution
  PEAD:        [+/-X%] contribution

Top sectors this week: [sector1], [sector2]
Regime: [summary of any regime changes this week]

Next week: [key events to watch]
```

---

## Phase 5: Prepare for Tomorrow

### 5.1 Pre-compute tomorrow's watchlist
Based on today's closing data:
- Update sector momentum scores in `state/signals.json` (so the morning run starts faster)
- Flag any stocks approaching mean reversion entry levels (RSI(2) trending toward 10)
- Note any earnings reports scheduled for tomorrow

### 5.2 Update state
- `state/portfolio.json`: final reconciled state with all closing prices
- `state/signals.json`: updated sector rankings and pre-screened candidates
- `performance/daily.json`: today's complete record appended

---

## Phase 6: Save and Push

1. Save all modified files (including `state/decision_log.md`)
2. Git add all changes in state/, journal/, research/, performance/
3. Git commit: "agent run: eod YYYY-MM-DD"
4. Git push
5. Verify push succeeded

You are done. Go to sleep until tomorrow's morning run.
