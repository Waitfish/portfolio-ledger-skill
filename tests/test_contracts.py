from __future__ import annotations

import unittest

from portfolio_ledger.schemas import AppendTradesRequest, ReplacePositionsRequest


class ContractTests(unittest.TestCase):
    def test_replace_positions_accepts_valid_payload(self) -> None:
        request = ReplacePositionsRequest.from_dict(
            {
                "portfolio_id": "main",
                "as_of_time": "2026-04-22T15:30:00+08:00",
                "positions": [{"symbol": "aapl", "quantity": 10, "avg_cost": 100.5}],
            }
        )
        self.assertEqual(request.portfolio_id, "main")
        self.assertEqual(request.positions[0].symbol, "AAPL")
        self.assertEqual(request.as_of_time, "2026-04-22T07:30:00+00:00")

    def test_replace_positions_rejects_missing_timezone(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            ReplacePositionsRequest.from_dict(
                {"portfolio_id": "main", "as_of_time": "2026-04-22T15:30:00", "positions": []}
            )

    def test_append_trades_accepts_lowercase_side(self) -> None:
        request = AppendTradesRequest.from_dict(
            {
                "portfolio_id": "main",
                "trades": [
                    {
                        "trade_time": "2026-04-22T09:35:22+08:00",
                        "symbol": "aapl",
                        "side": "buy",
                        "quantity": 2,
                        "price": 123.4,
                    }
                ],
            }
        )
        self.assertEqual(request.trades[0].side, "BUY")


if __name__ == "__main__":
    unittest.main()
