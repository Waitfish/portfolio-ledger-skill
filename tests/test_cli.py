from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill.py"


class CliTests(unittest.TestCase):
    def test_manifest_returns_tools(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "manifest"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])

    def test_empty_stdin_returns_clear_error(self) -> None:
        proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        data = json.loads(proc.stdout)
        self.assertIn("missing input", data["error"])

    def test_tool_envelope_invokes_replace_positions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["PORTFOLIO_LEDGER_DB"] = str(Path(tmpdir) / "portfolio.db")
            payload = {
                "tool": "replace_positions",
                "input": {
                    "portfolio_id": "main",
                    "as_of_time": "2026-04-22T15:30:00+08:00",
                    "positions": [{"symbol": "AAPL", "quantity": 10}],
                },
            }
            proc = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=ROOT,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                env=env,
                check=True,
            )
            data = json.loads(proc.stdout)
            self.assertTrue(data["ok"])


if __name__ == "__main__":
    unittest.main()
