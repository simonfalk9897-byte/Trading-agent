# Trading Agent Strategy

## Mission

Build an autonomous trading agent that runs on Claude Code via scheduled tasks (Mon-Fri), trades US equities and options on Alpaca, and consistently beats the S&P 500 on a risk-adjusted basis. The agent researches via web search, trades via Alpaca, reports via Telegram, and persists all state to a Git repo so every run has full context of what came before.

---

## Account Parameters

- Starting capital: $10,000
- Broker: Alpaca (paper trading first, then live)
- Asset classes: US equities + options (covered calls, protective puts)
- Trading style: Swing trading (2-10 day holds)
- Risk profile: Moderate (2-3% risk per trade, max 20% drawdown)
- Benchmark: SPY (S&P 500 ETF)

---

## Core Strategy: Multi-Factor Momentum + Mean Reversion Hybrid

The agent runs two complementary strategies that together cover more market regimes than either alone.

### Strategy 1: Sector Momentum Rotation (60% of capital)

This is the primary alpha driver. Research shows sector momentum rotation has delivered ~21% annualized returns with a Sharpe ratio of 1.6 and max drawdown of -7.5%, outperforming the S&P 500 by roughly 6% annually.

**How it works:**

1. Every morning, the agent ranks the 11 SPDR sector ETFs (XLK, XLF, XLV, XLE, XLI, XLC, XLY, XLP, XLU, XLRE, XLB) plus a few thematic ETFs by their 1-month, 3-month, and 6-month momentum scores.
2. It allocates to the top 3 sectors with the strongest composite momentum.
3. Within each winning sector, it picks the 2-3 individual stocks showing the best relative strength (price above 20-day and 50-day moving averages, strong volume, positive earnings revisions).
4. Positions are held for 2-4 weeks and rotated when momentum shifts.

**Entry criteria:**
- Sector ETF must be above its 50-day moving average
- Sector must rank in top 3 by composite momentum score
- Individual stock must have RSI(14) between 40 and 70 (trending but not overbought)
- Volume must be above 20-day average volume

**Exit criteria:**
- Sector drops out of top 3 ranking
- Stock breaks below 50-day moving average
- 8% trailing stop hit
- Time-based exit after 20 trading days with no meaningful gain

### Strategy 2: Mean Reversion on Oversold S&P 500 Stocks (40% of capital)

This captures short-term bounces when quality stocks get temporarily oversold. RSI-based mean reversion on S&P 500 components has shown 85%+ win rates with profit factors above 2.0 in backtests.

**How it works:**

1. The agent screens all S&P 500 stocks daily for oversold conditions.
2. When a high-quality stock drops sharply on no fundamental catalyst (just market noise or sector rotation), the agent buys the dip.
3. Positions are held 2-5 days until the stock reverts to its mean.

**Entry criteria:**
- RSI(2) below 10 (deeply oversold on a short timeframe)
- Stock is above its 200-day moving average (long-term uptrend intact)
- The IBS (Internal Bar Strength) is below 0.3 for the day
- No negative earnings surprise or major news catalyst (web search check)

**Exit criteria:**
- RSI(2) rises above 60 (reversion complete)
- 3% profit target hit
- 5-day time stop (exit regardless)
- 4% hard stop loss

---

## Options Overlay: Income + Protection (Phase 2)

At $10,000 starting capital, traditional covered calls are impractical -- a single 100-share lot of a $150 stock would consume the entire account. Options will be introduced in Phase 2 once the portfolio has grown or if trading lower-priced stocks where 100-share lots are feasible (e.g., stocks under $30).

**Phase 1 (launch):** Equities only. No options.

**Phase 2 (when portfolio > $25,000 or opportunistic):**

*Covered calls (income generation):*
- On momentum positions where you hold 100+ shares, sell covered calls 15-20% out of the money with 2-3 weeks to expiration
- Only write calls when implied volatility is elevated (IV rank above 30)

*Protective puts (downside protection):*
- Buy SPY put spreads (cheaper than outright puts) when portfolio exposure exceeds 80%
- Budget: no more than 0.5% of portfolio per month on protection

**Implementation note:** Alpaca supports Level 1-3 options with no minimum balance, and paper accounts have Level 3 enabled by default. Test the options overlay thoroughly in paper trading before adding to live.

---

## Risk Management Rules

These rules are non-negotiable. The agent must follow them before any trade logic.

### Position Sizing
- Maximum 2-3% of portfolio risked per trade (distance to stop loss x shares = risk amount)
- Maximum 10% of portfolio in any single stock
- Maximum 30% in any single sector
- Always keep 15-20% cash reserve for mean reversion opportunities

### Portfolio-Level Controls
- Maximum 80% invested at any time (20% cash floor)
- If portfolio drawdown exceeds 10% from peak, reduce all position sizes by 50%
- If portfolio drawdown exceeds 15%, move to 50% cash and pause new entries for 2 days
- If portfolio drawdown exceeds 20%, go to 100% cash and send an alert. Wait for manual override.

### Market Regime Detection
- Track VIX daily. If VIX > 30, reduce position sizes by 50% and tighten all stops
- Track SPY's 50-day moving average. If SPY is below its 50-day MA, shift allocation: reduce momentum to 40%, increase cash to 40%, keep mean reversion at 20%
- If SPY is below its 200-day MA, go defensive: 30% in positions max, 70% cash

### Stop Losses
- Every position MUST have a stop loss set at order entry
- Momentum trades: 8% trailing stop
- Mean reversion trades: 4% hard stop
- Options: close if underlying moves 3% against the position

---

## Daily Schedule (3 Runs)

### Run 1: Pre-Market (7:00 AM ET, before 9:30 open)

This is the main decision-making run.

**Step 1 - Load state**
- Read `state/portfolio.json` for current holdings, cash, open orders
- Read `state/signals.json` for yesterday's signal scores
- Read `journal/` for recent trade journal entries
- Read `performance/daily.json` for running P&L and benchmark comparison

**Step 2 - Research via web search**
- Search the web for overnight news on current holdings
- Query for macro events (Fed, economic data releases, geopolitical)
- Query for earnings reports due today and this week
- Query for sector-specific news on the sectors we are targeting
- Summarize findings in `research/YYYY-MM-DD.md`

**Step 3 - Generate signals**
- Pull price data from Alpaca for all watchlist stocks and sector ETFs
- Calculate momentum scores for sector rotation
- Screen S&P 500 for mean reversion setups
- Score and rank all candidates
- Write to `state/signals.json`

**Step 4 - Make decisions**
- Compare new signals against current holdings
- Decide: new entries, exits, hold, adjust stops
- Run position sizing through risk rules
- Generate order list

**Step 5 - Execute**
- Submit orders to Alpaca API
- Log all orders in `journal/YYYY-MM-DD.md`
- Update `state/portfolio.json`
- Git commit + push

### Run 2: Midday Check (12:00 PM ET)

Lighter run focused on monitoring and risk.

**Step 1 - Load state + check fills**
- Read current state files
- Check which morning orders filled on Alpaca
- Update portfolio state with actual fills and current prices

**Step 2 - Risk check**
- Calculate current drawdown from portfolio peak
- Check if any positions hit stop losses
- Check sector exposure limits
- Assess if VIX or SPY have moved significantly since morning

**Step 3 - Adjust if needed**
- Tighten trailing stops if positions have moved in our favor
- Close positions if stops were hit
- Reduce exposure if risk limits are being approached
- Log any adjustments

**Step 4 - Persist**
- Update state files
- Git commit + push

### Run 3: End of Day (4:30 PM ET, after 4:00 close)

Summary and reporting run.

**Step 1 - Final position snapshot**
- Pull end-of-day prices from Alpaca
- Calculate daily P&L for each position and portfolio total
- Compare against SPY's daily return

**Step 2 - Update performance tracking**
- Append to `performance/daily.json`: date, portfolio value, SPY value, daily return, cumulative return, alpha, max drawdown
- Update `performance/weekly.json` if it's Friday
- Calculate running Sharpe ratio, win rate, average win/loss

**Step 3 - Generate daily journal**
- Write `journal/YYYY-MM-DD.md` with: trades executed, P&L, rationale for each decision, what went right/wrong, lessons learned
- This is the critical feedback loop: the agent reads past journals to improve

**Step 4 - Telegram report**
- Send a concise daily summary to Telegram:
  - Portfolio value and daily change
  - Performance vs SPY (daily and cumulative)
  - Top winner and loser
  - Key positions and their status
  - Any alerts or concerns

**Step 5 - Git push**
- Commit all state files, journal, performance data, research notes
- Push to GitHub

---

## Repo Structure

```
trading-agent/
  README.md
  STRATEGY.md                    # This file
  CLAUDE.md                      # Agent instructions for Claude Code

  src/
    agent.py                     # Main agent orchestrator
    alpaca_client.py             # Alpaca API wrapper
    research_client.py           # Web search research wrapper
    telegram_client.py           # Telegram bot wrapper
    signals/
      momentum.py                # Sector momentum scoring
      mean_reversion.py          # RSI/IBS mean reversion signals
      options_overlay.py         # Covered call + put logic
    risk/
      position_sizing.py         # Position size calculator
      portfolio_risk.py          # Portfolio-level risk checks
      market_regime.py           # VIX and trend regime detection
    utils/
      state_manager.py           # Read/write state files
      git_manager.py             # Commit + push to GitHub
      performance_tracker.py     # P&L and benchmark tracking

  state/
    portfolio.json               # Current holdings, cash, orders
    signals.json                 # Latest signal scores
    watchlist.json               # Stock universe and sector ETFs
    config.json                  # API keys, risk params, thresholds

  journal/
    YYYY-MM-DD.md                # Daily trade journal with rationale

  research/
    YYYY-MM-DD.md                # Daily research summaries (via web search)

  performance/
    daily.json                   # Daily performance vs SPY
    weekly.json                  # Weekly rollups
    monthly.json                 # Monthly rollups

  prompts/
    pre_market.md                # Prompt template for morning run
    midday.md                    # Prompt template for midday run
    end_of_day.md                # Prompt template for EOD run

  .env                           # API keys (gitignored)
  .gitignore
  requirements.txt
```

---

## State Management and Feedback Loop

This is the most important architectural decision. Every run reads the previous state and writes back its results. The agent is not stateless; it has memory.

### What the agent remembers between runs:
- **Portfolio state:** exact holdings, entry prices, stop levels, days held
- **Signal history:** what scored well yesterday, what is trending up or down
- **Trade journal:** why it made each decision, what worked, what did not
- **Performance data:** running track record vs SPY, drawdown from peak
- **Research notes:** what news or catalysts it identified

### How the feedback loop improves decisions:
- If a sector has been losing momentum for 3 consecutive days, the agent detects the pattern and exits earlier
- If mean reversion trades in a particular stock have a low win rate, the agent deprioritizes that stock
- If the portfolio's Sharpe ratio is declining, the agent reduces position sizes proactively
- The journal entries serve as in-context learning: the agent sees its own past reasoning and outcomes

---

## Telegram Message Format

Daily EOD message:

```
-- Trading Agent Daily Report --
Date: 2026-04-24

Portfolio: $10,342.50 (+0.82%)
SPY:       +0.45%
Alpha:     +0.37% (today) | +2.1% (cumulative)

Trades Today:
  BUY  NVDA  x15 @ $134.20 (momentum)
  SELL AAPL  x10 @ $198.50 (+2.8%, 4 days)

Top Holdings:
  MSFT   12% of portfolio  +1.2% today
  NVDA   10% of portfolio  +0.5% today
  XLK    8% of portfolio   +0.8% today

Risk:
  Invested: 72% | Cash: 28%
  Drawdown: -1.2% from peak
  VIX: 18.5

Notes:
  Rotated out of energy, into tech.
  3 mean reversion setups triggered.
```

---

## CLAUDE.md Agent Prompt (Summary)

The `CLAUDE.md` file in the repo will instruct Claude Code on how to behave during each scheduled run. Key points:

1. Always read `state/` files first before making any decisions
2. Follow the risk management rules exactly, no exceptions
3. Use web search for research (thorough, multi-query), Alpaca for trading, Telegram for reporting
4. Write your reasoning to the journal before executing trades
5. Never exceed position or portfolio limits
6. If uncertain, do nothing. Cash is a position.
7. Always commit and push state after every run
8. Compare every decision against the benchmark: "does this help beat SPY?"

---

## Known Gaps and Decisions to Make During Development

1. **IBS (Internal Bar Strength) calculation:** IBS = (Close - Low) / (High - Low). Simple to compute from Alpaca OHLC data, but must be implemented in the signals module.

2. **Earnings calendar integration:** The mean reversion filter "no negative earnings surprise" needs a data source. Options: Alpaca's corporate actions endpoint, a free API like Finnhub or Alpha Vantage, or a targeted web search for "does [stock] have earnings this week?"

3. **Sector rotation exit logic:** When a sector drops out of the top 3, the agent should not dump all positions immediately. Instead: stop entering new positions in that sector, and exit existing ones over 2-3 days using trailing stops, unless a stop is already close (within 2%), in which case exit at market.

4. **Research depth consideration:** The pre-market run does thorough web research (10-15 searches). If any search returns thin results, the agent should try rephrasing or broadening the query rather than moving on with incomplete information. Quality of research directly determines quality of trades.

---

## Paper Trading Phase

Before going live, run the agent in paper trading mode for at least 4-6 weeks to validate:

1. The Alpaca API integration works reliably (orders, fills, positions)
2. The web search research produces useful, actionable information
3. The signal generation produces sensible rankings
4. The risk management rules trigger correctly
5. The state management and Git push cycle is bulletproof
6. The Telegram messages are clear and informative
7. The options overlay does not introduce unexpected risk
8. Overall performance shows alpha over SPY in paper trading

Only move to live capital after the paper phase passes all checks.

---

## Key Metrics to Track

- **Daily/weekly/monthly return** vs SPY
- **Cumulative alpha** (portfolio return minus SPY return)
- **Sharpe ratio** (target > 1.0, ideally > 1.5)
- **Max drawdown** (must stay under 20%)
- **Win rate** (target > 55% for momentum, > 80% for mean reversion)
- **Profit factor** (total wins / total losses, target > 1.5)
- **Average hold time** per strategy
- **Number of trades per week**
- **Cash utilization** (how often is capital sitting idle)

---

## Technology Stack

- **Runtime:** Claude Code scheduled tasks (3x daily, Mon-Fri)
- **Language:** Python 3.11+
- **Broker API:** alpaca-py (official Python SDK)
- **Research:** Claude's built-in web search (no external API needed)
- **Notifications:** python-telegram-bot
- **Data:** Alpaca market data API (included with account)
- **State:** JSON files in Git repo
- **Version control:** GitHub
- **Technical indicators:** pandas-ta or ta-lib for RSI, moving averages, etc.
