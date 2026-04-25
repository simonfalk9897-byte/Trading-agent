# Trading Agent

An autonomous swing trading agent that runs on Claude Code scheduled tasks, trades US equities on Alpaca, and aims to beat the S&P 500.

## How It Works

The agent wakes up 3 times per trading day (Mon-Fri):

- **7:00 AM ET** -- Research via web search, generate signals, place orders
- **12:00 PM ET** -- Monitor positions, check risk, adjust stops
- **4:30 PM ET** -- Calculate P&L, write journal, send Telegram report, push to Git

Every run reads its memory (state files, past journals, performance data) and writes back updated state. The agent is not stateless -- it learns from its own track record.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | The agent's brain. Entry point for every run. |
| `prompts/morning.md` | Step-by-step instructions for the pre-market run |
| `prompts/midday.md` | Step-by-step instructions for the midday check |
| `prompts/end_of_day.md` | Step-by-step instructions for the EOD run |
| `STRATEGY.md` | Full trading strategy: rules, sizing, risk management |
| `HOW_TO_BEAT_THE_SPY.md` | Investment thesis and academic evidence |
| `state/` | Live state: portfolio, signals, config, watchlist |
| `journal/` | Daily trade journals with decisions and outcomes |
| `research/` | Daily web search research summaries |
| `performance/` | P&L tracking vs SPY benchmark |

## Strategy

Two complementary strategies: sector momentum rotation (60% of capital) and short-term mean reversion on oversold S&P 500 stocks (40%). Protected by VIX regime filtering and hard drawdown circuit breakers.

Target: +4-8% annual alpha over SPY.

## Setup

1. Set up Alpaca account (live trading)
2. Create Telegram bot via @BotFather
3. Add API keys to `.env` (Alpaca + Telegram only -- research uses Claude's built-in web search)
4. Push repo to GitHub
5. Set up 3 Claude Code scheduled tasks (morning, midday, eod)

## Status

Planning complete. Ready to build in Claude Code. Going live from day one with launch week safety mode.
