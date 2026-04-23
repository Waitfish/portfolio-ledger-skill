from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from portfolio_ledger.schemas import AppendTradesRequest, ReplacePositionsRequest
from portfolio_ledger.storage import PortfolioLedgerStore


class AppendTradesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "portfolio.db"
        self.store = PortfolioLedgerStore(db_path=self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _replace(self, payload: dict) -> dict:
        request = ReplacePositionsRequest.from_dict(payload)
        return self.store.replace_positions(request, payload)

    def _append(self, payload: dict) -> dict:
        request = AppendTradesRequest.from_dict(payload)
        return self.store.append_trades(request, payload)

    def test_late_trade_does_not_change_current_positions(self) -> None:
        self._replace(
            {
                "portfolio_id": "main",
                "as_of_time": "2026-04-22T15:30:00+08:00",
                "positions": [{"symbol": "AAPL", "quantity": 10}],
            }
        )
        result = self._append(
            {
                "portfolio_id": "main",
                "trades": [
                    {
                        "trade_time": "2026-04-20T09:35:22+08:00",
                        "symbol": "AAPL",
                        "side": "BUY",
                        "quantity": 2,
                        "price": 100,
                    }
                ],
            }
        )
        positions = self.store.get_positions(portfolio_id="main")
        self.assertEqual(result["inserted_count"], 1)
        self.assertEqual(positions[0]["quantity"], 10.0)


if __name__ == "__main__":
    unittest.main()
