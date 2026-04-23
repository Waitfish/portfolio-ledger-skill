# portfolio-ledger-skill

[![CI](https://github.com/Waitfish/portfolio-ledger-skill/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Waitfish/portfolio-ledger-skill/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Release](https://img.shields.io/github/v/release/Waitfish/portfolio-ledger-skill)](https://github.com/Waitfish/portfolio-ledger-skill/releases)

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

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

## Install in Hermes

```bash
hermes skills tap add Waitfish/portfolio-ledger-skill
hermes skills install Waitfish/portfolio-ledger-skill/portfolio-ledger
```

### One-command local installer

If you already cloned the repo locally, run:

```bash
bash install.sh
```

This installs `SKILL.md` to:

```text
~/.hermes/skills/productivity/portfolio-ledger/
```

Note: the Python implementation still runs from your local clone of this repository.

## Use in Hermes

```bash
hermes chat -s portfolio-ledger
```

Example prompt:

```text
Use the portfolio-ledger skill to query current positions for portfolio_id main and return the JSON result.
```
