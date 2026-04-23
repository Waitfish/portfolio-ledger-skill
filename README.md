# portfolio-ledger-skill

Hermes skill for storing stock positions and trade records in a local SQLite ledger.

This project does not parse screenshots.

The intended flow is:

1. Hermes or another LLM turns screenshots, documents, or user text into structured JSON.
2. This skill validates the JSON.
3. This skill writes positions and trades into a local SQLite database.

## Features

1. `replace_positions`
2. `append_trades`
3. `get_positions`
4. `get_trades`
5. `get_import_batch`
6. `manifest`

## Layout

```text
.
├── SKILL.md
├── skill.py
├── portfolio_ledger/
│   ├── normalize.py
│   ├── schemas.py
│   ├── storage.py
│   └── db/init.sql
├── examples/
└── tests/
```

## Requirements

- Python 3.11+
- No third-party Python packages required

## Quick start

Show manifest:

```bash
python3 skill.py manifest
```

Save a positions snapshot:

```bash
python3 skill.py < examples/tool_replace_positions.json
```

Append trades:

```bash
python3 skill.py < examples/tool_append_trades.json
```

Query positions:

```bash
printf '%s' '{"tool":"get_positions","input":{"portfolio_id":"main"}}' | python3 skill.py
```

## Database path

Default:

```text
data/portfolio.db
```

Override with:

```bash
PORTFOLIO_LEDGER_DB=/tmp/portfolio.db python3 skill.py manifest
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Hermes usage

If you install this as a local Hermes skill, the skill prompt can call:

```bash
python3 skill.py < examples/tool_replace_positions.json
```

Or construct its own envelope:

```json
{
  "tool": "append_trades",
  "input": {
    "portfolio_id": "main",
    "trades": []
  }
}
```

## Install in Hermes

If you want to use this skill through Hermes, add this repo as a skill source and install the skill:

```bash
hermes skills tap add Waitfish/portfolio-ledger-skill
hermes skills install Waitfish/portfolio-ledger-skill/portfolio-ledger
```

If Hermes asks for a category, use `productivity`.

Check that the skill is installed:

```bash
hermes skills list | grep portfolio-ledger
```

## Use in Hermes

Start a Hermes session with the skill preloaded:

```bash
hermes chat -s portfolio-ledger
```

Example prompts:

### Save positions

```text
Use the portfolio-ledger skill to save a full positions snapshot for portfolio_id main at 2026-04-22T15:30:00+08:00 with one holding: AAPL quantity 10, avg_cost 100, market US, cost_currency USD.
```

### Query positions

```text
Use the portfolio-ledger skill to query current positions for portfolio_id main and return the JSON result.
```

### Append trades

```text
Use the portfolio-ledger skill to append one trade for portfolio_id main: trade_time 2026-04-23T09:35:22+08:00, symbol AAPL, side BUY, quantity 2, price 100, amount 200.
```

### Query trades

```text
Use the portfolio-ledger skill to query trades for portfolio_id main.
```

## Recommended smoke test

After installation, test this order:

1. `python3 skill.py manifest`
2. `python3 skill.py < examples/tool_replace_positions.json`
3. `python3 skill.py < examples/tool_append_trades.json`
4. `python3 -m unittest discover -s tests -v`

Then test once through Hermes:

```bash
hermes chat -s portfolio-ledger
```
