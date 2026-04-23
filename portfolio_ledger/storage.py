from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .normalize import signed_quantity
from .schemas import AppendTradesRequest, ReplacePositionsRequest, TradeInput


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "portfolio.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "db" / "init.sql"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class PortfolioLedgerStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema)

    def _start_batch(self, *, portfolio_id: str, action: str, source_kind: str | None, source_ref: str | None, payload: dict, records_total: int) -> str:
        batch_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO import_batches (
                  id, portfolio_id, action, source_kind, source_ref, requested_at,
                  status, raw_payload_json, records_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    portfolio_id,
                    action,
                    source_kind,
                    source_ref,
                    utc_now(),
                    "processing",
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    records_total,
                ),
            )
        return batch_id

    def _finish_batch(
        self,
        *,
        batch_id: str,
        status: str,
        records_written: int,
        records_skipped: int,
        warnings: list[str],
        errors: list[str],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE import_batches
                   SET processed_at = ?,
                       status = ?,
                       records_written = ?,
                       records_skipped = ?,
                       warnings_json = ?,
                       errors_json = ?
                 WHERE id = ?
                """,
                (
                    utc_now(),
                    status,
                    records_written,
                    records_skipped,
                    json.dumps(warnings, ensure_ascii=False),
                    json.dumps(errors, ensure_ascii=False),
                    batch_id,
                ),
            )

    def replace_positions(self, request: ReplacePositionsRequest, raw_payload: dict) -> dict:
        batch_id = self._start_batch(
            portfolio_id=request.portfolio_id,
            action="replace_positions",
            source_kind=request.source_kind,
            source_ref=request.source_ref,
            payload=raw_payload,
            records_total=len(request.positions),
        )
        warnings: list[str] = []
        conn = self._connect()
        try:
            previous_symbols = {
                row["symbol"]
                for row in conn.execute(
                    "SELECT symbol FROM positions WHERE portfolio_id = ? ORDER BY symbol",
                    (request.portfolio_id,),
                ).fetchall()
            }
            new_symbols = {position.symbol for position in request.positions}
            removed_symbols = sorted(previous_symbols - new_symbols)
            now = utc_now()
            with conn:
                conn.execute("DELETE FROM positions WHERE portfolio_id = ?", (request.portfolio_id,))
                for position in request.positions:
                    conn.execute(
                        """
                        INSERT INTO positions (
                          portfolio_id, symbol, name, market, quantity, available_quantity,
                          avg_cost, cost_currency, last_price, market_value, pnl_amount,
                          pnl_percent, as_of_time, anchor_kind, source_batch_id, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            request.portfolio_id,
                            position.symbol,
                            position.name,
                            position.market,
                            position.quantity,
                            position.available_quantity,
                            position.avg_cost,
                            position.cost_currency,
                            position.last_price,
                            position.market_value,
                            position.pnl_amount,
                            position.pnl_percent,
                            request.as_of_time,
                            "snapshot",
                            batch_id,
                            now,
                        ),
                    )
            self._finish_batch(
                batch_id=batch_id,
                status="success",
                records_written=len(request.positions),
                records_skipped=0,
                warnings=warnings,
                errors=[],
            )
            return {
                "ok": True,
                "action": "replace_positions",
                "batch_id": batch_id,
                "portfolio_id": request.portfolio_id,
                "replaced_count": len(request.positions),
                "removed_symbols": removed_symbols,
                "warnings": warnings,
                "as_of_time": request.as_of_time,
            }
        except Exception as exc:
            conn.rollback()
            self._finish_batch(
                batch_id=batch_id,
                status="failed",
                records_written=0,
                records_skipped=0,
                warnings=warnings,
                errors=[str(exc)],
            )
            raise
        finally:
            conn.close()

    def append_trades(self, request: AppendTradesRequest, raw_payload: dict) -> dict:
        batch_id = self._start_batch(
            portfolio_id=request.portfolio_id,
            action="append_trades",
            source_kind=request.source_kind,
            source_ref=request.source_ref,
            payload=raw_payload,
            records_total=len(request.trades),
        )
        warnings: list[str] = []
        conn = self._connect()
        try:
            snapshot_anchor = self._latest_snapshot_anchor(conn, request.portfolio_id)
            inserted = 0
            skipped = 0
            positions_updated = 0
            now = utc_now()
            with conn:
                for index, trade in enumerate(request.trades):
                    fingerprint = self._trade_fingerprint(request.portfolio_id, trade)
                    try:
                        conn.execute(
                            """
                            INSERT INTO trades (
                              portfolio_id, trade_time, symbol, name, side, trade_type,
                              quantity, price, amount, fee, tax, currency,
                              content_fingerprint, batch_id, raw_row_index,
                              created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                request.portfolio_id,
                                trade.trade_time,
                                trade.symbol,
                                trade.name,
                                trade.side,
                                trade.trade_type,
                                trade.quantity,
                                trade.price,
                                trade.amount,
                                trade.fee,
                                trade.tax,
                                trade.currency,
                                fingerprint,
                                batch_id,
                                index,
                                now,
                                now,
                            ),
                        )
                    except sqlite3.IntegrityError:
                        skipped += 1
                        warnings.append(f"duplicate trade skipped at row {index}")
                        continue
                    inserted += 1
                    if snapshot_anchor is not None and trade.trade_time <= snapshot_anchor:
                        warnings.append(f"late trade kept in ledger only at row {index}")
                        continue
                    self._apply_trade_to_positions(conn, request.portfolio_id, trade, batch_id)
                    positions_updated += 1
            self._finish_batch(
                batch_id=batch_id,
                status="success",
                records_written=inserted,
                records_skipped=skipped,
                warnings=warnings,
                errors=[],
            )
            return {
                "ok": True,
                "action": "append_trades",
                "batch_id": batch_id,
                "portfolio_id": request.portfolio_id,
                "inserted_count": inserted,
                "skipped_duplicates": skipped,
                "positions_updated": positions_updated,
                "warnings": warnings,
            }
        except Exception as exc:
            conn.rollback()
            self._finish_batch(
                batch_id=batch_id,
                status="failed",
                records_written=0,
                records_skipped=0,
                warnings=warnings,
                errors=[str(exc)],
            )
            raise
        finally:
            conn.close()

    def get_positions(self, *, portfolio_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT portfolio_id, symbol, name, market, quantity, available_quantity,
                       avg_cost, cost_currency, last_price, market_value, pnl_amount,
                       pnl_percent, as_of_time, anchor_kind, source_batch_id, updated_at
                  FROM positions
                 WHERE portfolio_id = ?
                 ORDER BY symbol
                """,
                (portfolio_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_trades(self, *, portfolio_id: str, start_time: str | None = None, end_time: str | None = None) -> list[dict]:
        query = [
            "SELECT portfolio_id, trade_time, symbol, name, side, trade_type, quantity, price, amount, fee, tax, currency, content_fingerprint, batch_id, raw_row_index, created_at, updated_at",
            "FROM trades",
            "WHERE portfolio_id = ?",
        ]
        params: list[object] = [portfolio_id]
        if start_time is not None:
            query.append("AND trade_time >= ?")
            params.append(start_time)
        if end_time is not None:
            query.append("AND trade_time <= ?")
            params.append(end_time)
        query.append("ORDER BY trade_time, id")
        with self._connect() as conn:
            rows = conn.execute(" ".join(query), tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def get_import_batch(self, *, batch_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM import_batches WHERE id = ?", (batch_id,)).fetchone()
        if row is None:
            return None
        batch = dict(row)
        batch["warnings_json"] = json.loads(batch["warnings_json"])
        batch["errors_json"] = json.loads(batch["errors_json"])
        batch["raw_payload_json"] = json.loads(batch["raw_payload_json"])
        return batch

    def _latest_snapshot_anchor(self, conn: sqlite3.Connection, portfolio_id: str) -> str | None:
        row = conn.execute(
            "SELECT MAX(as_of_time) AS latest_snapshot FROM positions WHERE portfolio_id = ? AND anchor_kind = 'snapshot'",
            (portfolio_id,),
        ).fetchone()
        return row["latest_snapshot"] if row and row["latest_snapshot"] else None

    def _trade_fingerprint(self, portfolio_id: str, trade: TradeInput) -> str:
        payload = {
            "portfolio_id": portfolio_id,
            "trade_time": trade.trade_time,
            "symbol": trade.symbol,
            "side": trade.side,
            "trade_type": trade.trade_type,
            "quantity": trade.quantity,
            "price": trade.price,
            "amount": trade.amount,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _apply_trade_to_positions(self, conn: sqlite3.Connection, portfolio_id: str, trade: TradeInput, batch_id: str) -> None:
        delta = signed_quantity(side=trade.side, trade_type=trade.trade_type, quantity=trade.quantity)
        row = conn.execute(
            "SELECT * FROM positions WHERE portfolio_id = ? AND symbol = ?",
            (portfolio_id, trade.symbol),
        ).fetchone()
        now = utc_now()
        if row is None:
            if delta < 0:
                raise ValueError(f"cannot apply negative position update for {trade.symbol} without existing position")
            available_quantity = delta
            avg_cost = trade.price
            last_price = trade.price
            market_value = last_price * delta
            conn.execute(
                """
                INSERT INTO positions (
                  portfolio_id, symbol, name, market, quantity, available_quantity,
                  avg_cost, cost_currency, last_price, market_value, pnl_amount,
                  pnl_percent, as_of_time, anchor_kind, source_batch_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    portfolio_id,
                    trade.symbol,
                    trade.name,
                    None,
                    delta,
                    available_quantity,
                    avg_cost,
                    trade.currency,
                    last_price,
                    market_value,
                    None,
                    None,
                    trade.trade_time,
                    "trade_update",
                    batch_id,
                    now,
                ),
            )
            return
        current_quantity = float(row["quantity"])
        new_quantity = current_quantity + delta
        if new_quantity < 0:
            raise ValueError(f"trade would make position negative for {trade.symbol}")
        if abs(new_quantity) < 1e-9:
            conn.execute(
                "DELETE FROM positions WHERE portfolio_id = ? AND symbol = ?",
                (portfolio_id, trade.symbol),
            )
            return
        current_available = row["available_quantity"]
        if current_available is None:
            current_available = current_quantity
        new_available = float(current_available) + delta
        if delta > 0:
            existing_cost = (row["avg_cost"] or 0.0) * current_quantity
            added_cost = trade.price * delta
            new_avg_cost = (existing_cost + added_cost) / new_quantity
        else:
            new_avg_cost = row["avg_cost"]
        last_price = row["last_price"] if row["last_price"] is not None else trade.price
        market_value = float(last_price) * new_quantity if last_price is not None else None
        conn.execute(
            """
            UPDATE positions
               SET name = COALESCE(?, name),
                   quantity = ?,
                   available_quantity = ?,
                   avg_cost = ?,
                   cost_currency = COALESCE(?, cost_currency),
                   last_price = ?,
                   market_value = ?,
                   as_of_time = ?,
                   anchor_kind = ?,
                   source_batch_id = ?,
                   updated_at = ?
             WHERE portfolio_id = ? AND symbol = ?
            """,
            (
                trade.name,
                new_quantity,
                new_available,
                new_avg_cost,
                trade.currency,
                last_price,
                market_value,
                trade.trade_time,
                "trade_update",
                batch_id,
                now,
                portfolio_id,
                trade.symbol,
            ),
        )
