# Morning Run -- Pre-Market (7:00 AM ET)

This is the most important run of the day. You research, generate signals, make decisions, and place orders before the 9:30 AM market open.

You should have already loaded your memory (CLAUDE.md Step 1) before arriving here. If you have not, go back and do it now.

---

## Phase 0: First Run Bootstrap (SKIP if not your first run)

Check `state/portfolio.json`. If `last_updated` is null, this is the very first run. Execute this bootstrap sequence before proceeding to Phase 1:

### 0.1 Verify API connections
- Call Alpaca API: get account info. Confirm cash balance matches starting capital ($10,000).
- Run a web search: "US stock market overview today". Confirm results come back.
- Call Telegram API: send a test message ("Trading agent online. First run starting."). Confirm delivery.

If Alpaca or Telegram fails, STOP. Log the error. Do not proceed until both are working.
(Web search is built into Claude -- it does not require a separate API connection.)

### 0.2 Initialize baseline data
- Pull current SPY price. This is your benchmark starting point.
- Pull current VIX level.
- Pull closing prices for all 11 sector ETFs.
- Calculate initial momentum scores (use available historical data from Alpaca).

### 0.3 Set baseline state
Update `state/portfolio.json`:
```json
{
  "last_updated": "YYYY-MM-DD HH:MM ET",
  "last_run": "morning",
  "trading_days_completed": 0,
  "account": {
    "starting_capital": 10000.00,
    "cash": 10000.00,
    "portfolio_value": 10000.00,
    "peak_value": 10000.00,
    "drawdown_pct": 0.0
  },
  "positions": [],
  "open_orders": [],
  "paused_until": null,
  "launch_week": true
}
```

Initialize `performance/daily.json` with day zero:
```json
[{
  "date": "YYYY-MM-DD",
  "portfolio_value": 10000.00,
  "spy_price": [current SPY price],
  "spy_baseline": [current SPY price],
  "cumulative_return_pct": 0.0,
  "spy_cumulative_return_pct": 0.0,
  "cumulative_alpha_pct": 0.0,
  "peak_value": 10000.00,
  "drawdown_pct": 0.0,
  "note": "Day zero baseline"
}]
```

### 0.4 Write first journal entry
Create `journal/YYYY-MM-DD.md`:
```markdown
# Trading Journal -- YYYY-MM-DD

## First Run -- Bootstrap

Agent is live. APIs verified. Baseline set.
- Starting capital: $10,000
- SPY baseline: $[price]
- VIX: [level]
- Launch week mode: ON (1% risk per trade, max 1 entry/day, max 50% invested)

Proceeding to first research and signal generation.
```

### 0.5 Read strategy documents
Since this is your first run, read both:
- `STRATEGY.md` -- your trading rules
- `HOW_TO_BEAT_THE_SPY.md` -- your investment thesis

Now proceed to Phase 1 as normal.

---

## Phase 1: Research (estimated 5-8 minutes)

Use Claude's built-in web search to research the market. This is your edge -- be thorough. Do not rush this phase. Run multiple searches per topic, cross-reference what you find, and read into articles when a headline looks relevant. Shallow research leads to bad trades.

### 1.1 Check current holdings (one search per holding)
For each stock in `state/portfolio.json`:
- Search: "[TICKER] stock news today [date]"
- Search: "[TICKER] earnings analyst upgrade downgrade [date]" (if results from first search are thin)
- What you are looking for: anything that changes the thesis. Downgrades, lawsuits, earnings misses, CEO departures, FDA rejections, lost contracts, guidance cuts.
- If you find a material negative catalyst on a holding, mark it for immediate exit.
- If you find a material positive catalyst (upgrade, earnings beat, new contract), note it -- this may be a reason to hold longer or add.

### 1.2 Check macro environment (3-4 searches)
- Search: "US stock market news today premarket [date]"
- Search: "economic calendar this week jobs CPI Fed [date]"
- Search: "VIX today market volatility [date]"
- Search: "geopolitical risks market impact today" (only if prior results hint at something)
- What you are looking for: scheduled events that move markets (FOMC, CPI, jobs report, trade policy), overnight futures direction, any surprise geopolitical events.

### 1.3 Check target sectors (one search per top sector)
Read `state/signals.json` for yesterday's top 3 sectors. For each:
- Search: "[SECTOR NAME] sector stocks news outlook [date]"
- Search: "[SECTOR ETF] performance trend [date]" (if first search is thin)
- What you are looking for: confirmation the trend is intact, or early signs of reversal (negative news, rotation signals, analyst warnings).

### 1.4 Scan for earnings plays (1-2 searches)
- Search: "S&P 500 earnings results this week beat miss surprise [date]"
- Search: "biggest earnings surprises this week stock reaction [date]"
- What you are looking for: stocks that reported strong earnings with positive price reaction in the last 5 days. These are PEAD candidates.

### 1.5 Deep dive on any trade candidates (as needed)
Before committing to any new entry, do a targeted search on that specific stock:
- Search: "[TICKER] stock analysis bull bear case [date]"
- Search: "[TICKER] recent news catalyst [date]"
- This is especially critical for mean reversion candidates. You MUST verify the dip is noise, not a fundamental breakdown. If you cannot confirm this, do not buy the dip.

### 1.6 Save research
Write all findings to `research/YYYY-MM-DD.md` in this format:

```markdown
# Research -- YYYY-MM-DD

## Holdings Check
- [TICKER]: [one-line summary of news/status] | Action: [hold/exit/watch]

## Macro Environment
- Market sentiment: [bullish/neutral/bearish]
- Key events today/this week: [list]
- VIX: [level] | Futures: [direction]

## Sector Outlook
- [SECTOR 1]: [status -- strengthening/holding/weakening] | [key driver]
- [SECTOR 2]: [status] | [key driver]
- [SECTOR 3]: [status] | [key driver]

## Earnings Opportunities
- [TICKER]: beat by [X%], stock reacted [+/-X%] on [date] | PEAD candidate: [yes/no]

## Trade Candidate Deep Dives
- [TICKER]: [what you found, why it supports or kills the trade idea]

## Red Flags
- [anything concerning that requires immediate action or caution]

## Research Quality Note
[How confident are you in today's research? Were sources consistent? Any gaps you could not fill?]
```

### Research quality standard
Do not treat research as a checkbox. The purpose is to avoid putting money into a stock that is about to drop on news you could have found. If your research on a trade candidate is inconclusive, skip the trade. There will always be another setup tomorrow.

---

## Phase 2: Signal Generation (estimated 2-3 minutes)

### 2.1 Sector Momentum Scores
Pull price data from Alpaca for these ETFs: XLK, XLF, XLV, XLE, XLI, XLC, XLY, XLP, XLU, XLRE, XLB

For each ETF, calculate:
- 1-month return (weight: 0.33)
- 3-month return (weight: 0.33)
- 6-month return (weight: 0.34)
- Composite score = weighted sum
- Check: is it above its 50-day MA? (must be YES to qualify)

Rank all sectors by composite score. The top 3 that are above their 50-day MA are your target sectors.

### 2.2 Stock Selection within Top Sectors
For each top sector, pull the component stocks. For each stock, check:
- Price > 20-day MA? (YES required)
- Price > 50-day MA? (YES required)
- RSI(14) between 40 and 70? (YES required)
- Volume > 20-day average volume? (YES required)
- Any positive earnings surprise in last 30 days? (bonus points)

Score each stock. Pick the top 2-3 from each sector.

### 2.3 Mean Reversion Screen
Scan ALL S&P 500 stocks. For each, check:
- RSI(2) < 10? (must be YES)
- Price > 200-day MA? (must be YES)
- IBS < 0.3? (must be YES -- IBS = (Close - Low) / (High - Low))
- Research check: did your web search find a fundamental catalyst? (must be NO -- if you skipped the deep dive on this stock in Phase 1.5, go back and do it now)

Any stock passing all 4 filters is a mean reversion candidate.

### 2.4 Save signals
Write all scores and rankings to `state/signals.json`:

```json
{
  "date": "YYYY-MM-DD",
  "run": "morning",
  "regime": {
    "vix": 18.5,
    "vix_above_200ma": false,
    "spy_above_50ma": true,
    "spy_above_200ma": true,
    "mode": "full_offense"
  },
  "sector_rankings": [
    {"sector": "XLE", "score": 0.85, "above_50ma": true, "rank": 1},
    {"sector": "XLI", "score": 0.72, "above_50ma": true, "rank": 2}
  ],
  "momentum_candidates": [
    {"ticker": "CVX", "sector": "XLE", "score": 0.91, "entry_price": null},
    {"ticker": "CAT", "sector": "XLI", "score": 0.87, "entry_price": null}
  ],
  "mean_reversion_candidates": [
    {"ticker": "AAPL", "rsi2": 8.3, "ibs": 0.15, "above_200ma": true}
  ]
}
```

---

## Phase 3: Decision Making (estimated 2-3 minutes)

Work through this checklist in order. Do not skip steps.

### 3.1 Regime check (do this FIRST, before any trade decisions)
Read the regime data from signals. Apply the rules:

- If `vix_above_200ma` is true OR vix > 30: you are in DEFENSIVE mode
  - Reduce all position sizes by 50%
  - Tighten all trailing stops to 5% (from 8%)
  - Skip all new momentum entries
  - Mean reversion only with extra caution

- If `spy_above_50ma` is false:
  - Reduce momentum allocation from 60% to 40%
  - Increase cash target to 40%

- If `spy_above_200ma` is false:
  - Maximum 30% invested, 70% cash
  - Only take mean reversion setups with RSI(2) below 5

### 3.2 Drawdown check
Read `performance/daily.json`. Calculate drawdown from peak portfolio value.
- If drawdown > 10%: halve all position sizes
- If drawdown > 15%: go to 50% cash, no new entries for 2 days
- If drawdown > 20%: STOP. Go 100% cash. Alert Simon on Telegram. Do nothing else.

### 3.3 Review existing positions
For each position in `state/portfolio.json`:

**Momentum positions:**
- Has the sector dropped out of the top 3? If yes, begin exit (trailing stop, do not add)
- Has the stock broken below its 50-day MA? If yes, exit at market open
- Has the 8% trailing stop been hit? If yes, exit
- Has it been held for 20+ trading days with < 2% gain? If yes, exit
- Otherwise: hold, adjust trailing stop if price has moved in your favor

**Mean reversion positions:**
- Has RSI(2) risen above 60? If yes, exit (reversion complete)
- Has the 3% profit target been hit? If yes, exit
- Has it been held for 5+ trading days? If yes, exit (time stop)
- Has the 4% hard stop been hit? If yes, exit
- Otherwise: hold

### 3.4 Evaluate new entries
Only if you have capacity (cash > 20%, not in drawdown pause):

**Momentum entries:**
- Take the top-ranked momentum candidates that are not already in portfolio
- Position size: risk no more than 2-3% of portfolio (use 8% stop distance to calculate shares)
- Maximum 2 new momentum entries per day

**Mean reversion entries:**
- Take any candidates passing all 4 filters
- Position size: risk no more than 2% of portfolio (use 4% stop distance)
- Maximum 2 new mean reversion entries per day

**PEAD / Earnings drift entries (opportunistic):**
- If research flagged a strong earnings surprise with positive price reaction:
  - Buy if still within 5 days of the announcement
  - Position size: smaller (1-2% risk), shorter hold (5-10 days)
  - Maximum 1 PEAD entry per day

### 3.5 Write your reasoning
Before executing any trades, write to `journal/YYYY-MM-DD.md`:

```markdown
# Trading Journal -- YYYY-MM-DD

## Morning Run

### Market Regime
- VIX: [value] | SPY vs MAs: [above/below] | Mode: [full_offense/cautious/defensive]
- Drawdown from peak: [X%]

### Exits Planned
- [TICKER]: [reason for exit] | Expected order: [SELL X shares at market/limit $XX]

### New Entries Planned
- [TICKER]: [strategy type] | [why this stock, why now]
  Entry: ~$XX | Stop: $XX | Target: $XX or [exit criteria]
  Risk: $XX ([X%] of portfolio)

### Holds
- [TICKER]: Day [N] of hold | Current P&L: [X%] | Stop at: $XX | Notes: [any adjustment]

### Reasoning
[2-3 sentences on the overall thesis for today. What is the market doing? Why these trades?]
```

---

## Phase 4: Execution (estimated 1-2 minutes)

### 4.1 Check for stale orders
Query Alpaca for open orders. Cancel any that are more than 1 day old and unfilled.

### 4.2 Submit exit orders
Process all planned exits first (always reduce risk before adding risk):
- Use limit orders near the current bid for sells
- Set order to GTC (good till cancelled) or DAY depending on urgency

### 4.3 Submit entry orders
Process new entries:
- Use limit orders at or slightly below the current ask
- Immediately set a linked stop-loss order for each entry
- Log every order ID in `state/portfolio.json`

### 4.4 Update portfolio state
After all orders are submitted, update `state/portfolio.json`:
- Add new pending orders
- Update stop levels for adjusted positions
- Recalculate cash (accounting for pending orders)

---

## Phase 5: Telegram (ONLY if something important happened)

You do NOT send a Telegram message every morning. Simon expects one daily summary at end of day, not three.

Send a Telegram message ONLY if one or more of these are true:
- A drawdown circuit breaker triggered (10%, 15%, or 20%)
- A position hit its stop loss overnight or in premarket
- Research uncovered a major catalyst on a current holding (e.g., earnings miss, FDA rejection, downgrade)
- VIX spiked above 30 since yesterday
- SPY broke below a key moving average (50-day or 200-day) since yesterday

If none of these apply, skip Telegram entirely.

Format for morning alerts:

```
-- Morning Alert --
Date: YYYY-MM-DD

[REASON]: [concise description]
Action taken: [what you did about it]
```

---

## Phase 6: Save and Push

1. Save all modified files: `state/portfolio.json`, `state/signals.json`, `research/YYYY-MM-DD.md`, `journal/YYYY-MM-DD.md`
2. Git add, commit ("agent run: morning YYYY-MM-DD"), push
3. Verify push succeeded

You are done. Go to sleep until the midday run.
