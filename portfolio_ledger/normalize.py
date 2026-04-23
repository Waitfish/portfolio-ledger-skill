from __future__ import annotations

from datetime import datetime, timezone


VALID_SIDES = {"BUY", "SELL"}
POSITIVE_TRADE_TYPES = {"BUY", "BONUS", "TRANSFER_IN", "DIVIDEND_STOCK", "RED_STOCK"}
NEGATIVE_TRADE_TYPES = {"SELL", "TRANSFER_OUT"}


def normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("text fields must be strings")
    stripped = value.strip()
    return stripped or None


def normalize_symbol(value: object) -> str:
    symbol = normalize_optional_text(value)
    if not symbol:
        raise ValueError("symbol is required")
    return symbol.upper()


def normalize_market(value: object) -> str | None:
    market = normalize_optional_text(value)
    return market.upper() if market else None


def normalize_number(value: object, *, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")
    return float(value)


def normalize_timestamp(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO 8601 string")
    raw = value.strip()
    if not raw:
        raise ValueError(f"{field_name} is required")
    normalized = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO 8601 datetime") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{field_name} must include timezone information")
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def normalize_side(value: object) -> str:
    side = normalize_optional_text(value)
    if not side:
        raise ValueError("side is required")
    normalized = side.upper()
    if normalized not in VALID_SIDES:
        raise ValueError(f"unsupported side: {side}")
    return normalized


def normalize_trade_type(value: object, *, side: str) -> str:
    trade_type = normalize_optional_text(value)
    if trade_type is None:
        return side
    normalized = trade_type.upper()
    if normalized not in POSITIVE_TRADE_TYPES | NEGATIVE_TRADE_TYPES:
        raise ValueError(f"unsupported trade_type: {trade_type}")
    return normalized


def signed_quantity(*, side: str, trade_type: str, quantity: float) -> float:
    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    if trade_type in POSITIVE_TRADE_TYPES:
        return quantity
    if trade_type in NEGATIVE_TRADE_TYPES:
        return -quantity
    if side == "BUY":
        return quantity
    if side == "SELL":
        return -quantity
    raise ValueError(f"cannot determine signed quantity for trade_type={trade_type}")
