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
