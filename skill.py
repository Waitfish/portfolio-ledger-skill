from __future__ import annotations

import json
import os
import sys

from portfolio_ledger.schemas import (
    AppendTradesRequest,
    GetImportBatchRequest,
    GetPositionsRequest,
    GetTradesRequest,
    ReplacePositionsRequest,
)
from portfolio_ledger.storage import PortfolioLedgerStore


def load_payload() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("stdin must contain valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return payload


def resolve_action(argv: list[str], payload: dict) -> tuple[str, dict]:
    if len(argv) == 1 and argv[0] in HANDLERS:
        return argv[0], payload
    if len(argv) == 0:
        if not payload:
            raise ValueError(
                "missing input: pass an action argument or stdin {\"tool\": ..., \"input\": ...}"
            )
        tool = payload.get("tool")
        tool_input = payload.get("input")
        if tool not in HANDLERS:
            raise ValueError(f"unknown tool: {tool}")
        if not isinstance(tool_input, dict):
            raise ValueError("input must be an object")
        return tool, tool_input
    raise ValueError(f"usage: skill.py [{'|'.join(HANDLERS)}] or stdin {{\"tool\": ..., \"input\": ...}}")


def build_store() -> PortfolioLedgerStore:
    db_path = os.environ.get("PORTFOLIO_LEDGER_DB")
    return PortfolioLedgerStore(db_path=db_path)


def handle_replace_positions(store: PortfolioLedgerStore, payload: dict) -> dict:
    request = ReplacePositionsRequest.from_dict(payload)
    return store.replace_positions(request, payload)


def handle_append_trades(store: PortfolioLedgerStore, payload: dict) -> dict:
    request = AppendTradesRequest.from_dict(payload)
    return store.append_trades(request, payload)


def handle_get_positions(store: PortfolioLedgerStore, payload: dict) -> dict:
    request = GetPositionsRequest.from_dict(payload)
    return {"ok": True, "positions": store.get_positions(portfolio_id=request.portfolio_id)}


def handle_get_trades(store: PortfolioLedgerStore, payload: dict) -> dict:
    request = GetTradesRequest.from_dict(payload)
    return {
        "ok": True,
        "trades": store.get_trades(
            portfolio_id=request.portfolio_id,
            start_time=request.start_time,
            end_time=request.end_time,
        ),
    }


def handle_get_import_batch(store: PortfolioLedgerStore, payload: dict) -> dict:
    request = GetImportBatchRequest.from_dict(payload)
    batch = store.get_import_batch(batch_id=request.batch_id)
    if batch is None:
        return {"ok": False, "error": "batch not found", "batch_id": request.batch_id}
    return {"ok": True, "batch": batch}


HANDLERS = {
    "replace_positions": handle_replace_positions,
    "append_trades": handle_append_trades,
    "get_positions": handle_get_positions,
    "get_trades": handle_get_trades,
    "get_import_batch": handle_get_import_batch,
}


def tool_manifest() -> dict:
    return {
        "ok": True,
        "tools": [
            {
                "name": "replace_positions",
                "description": "Replace current positions for a portfolio with a full snapshot.",
                "input_schema": {
                    "type": "object",
                    "required": ["portfolio_id", "as_of_time", "positions"],
                    "properties": {
                        "portfolio_id": {"type": "string"},
                        "as_of_time": {"type": "string", "format": "date-time"},
                        "source_kind": {"type": ["string", "null"]},
                        "source_ref": {"type": ["string", "null"]},
                        "positions": {"type": "array"},
                    },
                },
            },
            {
                "name": "append_trades",
                "description": "Append trades and update current positions only for newer trades.",
                "input_schema": {
                    "type": "object",
                    "required": ["portfolio_id", "trades"],
                    "properties": {
                        "portfolio_id": {"type": "string"},
                        "source_kind": {"type": ["string", "null"]},
                        "source_ref": {"type": ["string", "null"]},
                        "trades": {"type": "array"},
                    },
                },
            },
            {
                "name": "get_positions",
                "description": "Return current positions for a portfolio.",
                "input_schema": {
                    "type": "object",
                    "required": ["portfolio_id"],
                    "properties": {"portfolio_id": {"type": "string"}},
                },
            },
            {
                "name": "get_trades",
                "description": "Return trades for a portfolio, optionally filtered by time range.",
                "input_schema": {
                    "type": "object",
                    "required": ["portfolio_id"],
                    "properties": {
                        "portfolio_id": {"type": "string"},
                        "start_time": {"type": ["string", "null"], "format": "date-time"},
                        "end_time": {"type": ["string", "null"], "format": "date-time"},
                    },
                },
            },
            {
                "name": "get_import_batch",
                "description": "Return the stored batch payload and summary for one import run.",
                "input_schema": {
                    "type": "object",
                    "required": ["batch_id"],
                    "properties": {"batch_id": {"type": "string"}},
                },
            },
        ],
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    try:
        payload = load_payload()
        if len(argv) == 1 and argv[0] == "manifest":
            print(json.dumps(tool_manifest(), ensure_ascii=False, indent=2))
            return 0
        action, action_payload = resolve_action(argv, payload)
        store = build_store()
        result = HANDLERS[action](store, action_payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
