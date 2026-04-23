from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from portfolio_ledger.schemas import ReplacePositionsRequest
from portfolio_ledger.storage import PortfolioLedgerStore


class ReplacePositionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "portfolio.db"
        self.store = PortfolioLedgerStore(db_path=self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _replace(self, payload: dict) -> dict:
        request = ReplacePositionsRequest.from_dict(payload)
        return self.store.replace_positions(request, payload)

    def test_replace_positions_reports_only_truly_removed_symbols(self) -> None:
        self._replace(
            {
                "portfolio_id": "main",
                "as_of_time": "2026-04-22T15:30:00+08:00",
                "positions": [{"symbol": "AAPL", "quantity": 10}, {"symbol": "TSLA", "quantity": 5}],
            }
        )
        result = self._replace(
            {
                "portfolio_id": "main",
                "as_of_time": "2026-04-23T15:30:00+08:00",
                "positions": [{"symbol": "AAPL", "quantity": 12}, {"symbol": "MSFT", "quantity": 7}],
            }
        )
        self.assertEqual(result["removed_symbols"], ["TSLA"])


if __name__ == "__main__":
    unittest.main()
