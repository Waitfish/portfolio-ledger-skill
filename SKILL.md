---
name: portfolio-ledger
description: Store and query stock positions and trade records in a local SQLite ledger by calling a Python CLI in the skill directory. Use after screenshots or documents have already been turned into structured JSON.
triggers:
  - User wants to save stock positions to a local ledger
  - User wants to save trade records to SQLite
  - User provides structured holdings or trade JSON
  - User asks to query current positions or trade history from the ledger
---

# Portfolio Ledger Skill

This skill does not parse screenshots.

Use it only after the model has already extracted structured JSON from screenshots, PDFs, spreadsheets, or user text.

## Rules

1. Do not invent missing fields.
2. Keep datetime values in ISO 8601 with timezone.
3. Use `replace_positions` only for full current holdings snapshots.
4. Use `append_trades` only for trade history.
5. If the user asks what the tool can do, run `python3 skill.py manifest`.

## Commands

### Manifest

```bash
python3 skill.py manifest
```

### Save positions

```bash
python3 skill.py <<'EOF'
{
  "tool": "replace_positions",
  "input": {
    "portfolio_id": "main",
    "as_of_time": "2026-04-22T15:30:00+08:00",
    "positions": [
      {"symbol": "AAPL", "quantity": 10}
    ]
  }
}
EOF
```

### Save trades

```bash
python3 skill.py <<'EOF'
{
  "tool": "append_trades",
  "input": {
    "portfolio_id": "main",
    "trades": [
      {
        "trade_time": "2026-04-23T09:35:22+08:00",
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 2,
        "price": 100
      }
    ]
  }
}
EOF
```

### Query positions

```bash
printf '%s' '{"tool":"get_positions","input":{"portfolio_id":"main"}}' | python3 skill.py
```

### Query trades

```bash
printf '%s' '{"tool":"get_trades","input":{"portfolio_id":"main"}}' | python3 skill.py
```
