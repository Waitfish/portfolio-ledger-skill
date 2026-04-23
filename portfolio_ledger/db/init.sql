PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS import_batches (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL,
  action TEXT NOT NULL,
  source_kind TEXT,
  source_ref TEXT,
  requested_at TEXT NOT NULL,
  processed_at TEXT,
  status TEXT NOT NULL,
  raw_payload_json TEXT NOT NULL,
  records_total INTEGER NOT NULL DEFAULT 0,
  records_written INTEGER NOT NULL DEFAULT 0,
  records_skipped INTEGER NOT NULL DEFAULT 0,
  warnings_json TEXT NOT NULL DEFAULT '[]',
  errors_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS positions (
  id INTEGER PRIMARY KEY,
  portfolio_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  name TEXT,
  market TEXT,
  quantity REAL NOT NULL,
  available_quantity REAL,
  avg_cost REAL,
  cost_currency TEXT,
  last_price REAL,
  market_value REAL,
  pnl_amount REAL,
  pnl_percent REAL,
  as_of_time TEXT NOT NULL,
  anchor_kind TEXT NOT NULL,
  source_batch_id TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(portfolio_id, symbol),
  FOREIGN KEY(source_batch_id) REFERENCES import_batches(id)
);

CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY,
  portfolio_id TEXT NOT NULL,
  trade_time TEXT NOT NULL,
  symbol TEXT NOT NULL,
  name TEXT,
  side TEXT NOT NULL,
  trade_type TEXT,
  quantity REAL NOT NULL,
  price REAL NOT NULL,
  amount REAL,
  fee REAL,
  tax REAL,
  currency TEXT,
  content_fingerprint TEXT NOT NULL,
  batch_id TEXT NOT NULL,
  raw_row_index INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(portfolio_id, content_fingerprint),
  FOREIGN KEY(batch_id) REFERENCES import_batches(id)
);

CREATE INDEX IF NOT EXISTS idx_positions_portfolio_symbol
  ON positions(portfolio_id, symbol);

CREATE INDEX IF NOT EXISTS idx_trades_portfolio_trade_time
  ON trades(portfolio_id, trade_time);

CREATE INDEX IF NOT EXISTS idx_trades_portfolio_fingerprint
  ON trades(portfolio_id, content_fingerprint);

CREATE INDEX IF NOT EXISTS idx_import_batches_portfolio_requested
  ON import_batches(portfolio_id, requested_at);
