from __future__ import annotations

from dataclasses import dataclass

from .normalize import (
    normalize_market,
    normalize_number,
    normalize_optional_text,
    normalize_side,
    normalize_symbol,
    normalize_timestamp,
    normalize_trade_type,
)


def _require_dict(value: object, *, field_name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _require_list(value: object, *, field_name: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    return value


@dataclass(frozen=True)
class PositionInput:
    symbol: str
    name: str | None
    market: str | None
    quantity: float
    available_quantity: float | None
    avg_cost: float | None
    cost_currency: str | None
    last_price: float | None
    market_value: float | None
    pnl_amount: float | None
    pnl_percent: float | None

    @classmethod
    def from_dict(cls, payload: object) -> "PositionInput":
        data = _require_dict(payload, field_name="position")
        quantity = normalize_number(data.get("quantity"), field_name="quantity")
        if quantity is None:
            raise ValueError("quantity is required")
        return cls(
            symbol=normalize_symbol(data.get("symbol")),
            name=normalize_optional_text(data.get("name")),
            market=normalize_market(data.get("market")),
            quantity=quantity,
            available_quantity=normalize_number(data.get("available_quantity"), field_name="available_quantity"),
            avg_cost=normalize_number(data.get("avg_cost"), field_name="avg_cost"),
            cost_currency=normalize_optional_text(data.get("cost_currency")),
            last_price=normalize_number(data.get("last_price"), field_name="last_price"),
            market_value=normalize_number(data.get("market_value"), field_name="market_value"),
            pnl_amount=normalize_number(data.get("pnl_amount"), field_name="pnl_amount"),
            pnl_percent=normalize_number(data.get("pnl_percent"), field_name="pnl_percent"),
        )


@dataclass(frozen=True)
class ReplacePositionsRequest:
    portfolio_id: str
    as_of_time: str
    source_kind: str | None
    source_ref: str | None
    positions: list[PositionInput]

    @classmethod
    def from_dict(cls, payload: object) -> "ReplacePositionsRequest":
        data = _require_dict(payload, field_name="payload")
        positions = [PositionInput.from_dict(item) for item in _require_list(data.get("positions", []), field_name="positions")]
        portfolio_id = normalize_optional_text(data.get("portfolio_id"))
        if not portfolio_id:
            raise ValueError("portfolio_id is required")
        return cls(
            portfolio_id=portfolio_id,
            as_of_time=normalize_timestamp(data.get("as_of_time"), field_name="as_of_time"),
            source_kind=normalize_optional_text(data.get("source_kind")),
            source_ref=normalize_optional_text(data.get("source_ref")),
            positions=positions,
        )


@dataclass(frozen=True)
class TradeInput:
    trade_time: str
    symbol: str
    name: str | None
    side: str
    trade_type: str
    quantity: float
    price: float
    amount: float | None
    fee: float | None
    tax: float | None
    currency: str | None

    @classmethod
    def from_dict(cls, payload: object) -> "TradeInput":
        data = _require_dict(payload, field_name="trade")
        side = normalize_side(data.get("side"))
        quantity = normalize_number(data.get("quantity"), field_name="quantity")
        price = normalize_number(data.get("price"), field_name="price")
        if quantity is None:
            raise ValueError("quantity is required")
        if price is None:
            raise ValueError("price is required")
        return cls(
            trade_time=normalize_timestamp(data.get("trade_time"), field_name="trade_time"),
            symbol=normalize_symbol(data.get("symbol")),
            name=normalize_optional_text(data.get("name")),
            side=side,
            trade_type=normalize_trade_type(data.get("trade_type"), side=side),
            quantity=quantity,
            price=price,
            amount=normalize_number(data.get("amount"), field_name="amount"),
            fee=normalize_number(data.get("fee"), field_name="fee"),
            tax=normalize_number(data.get("tax"), field_name="tax"),
            currency=normalize_optional_text(data.get("currency")),
        )


@dataclass(frozen=True)
class AppendTradesRequest:
    portfolio_id: str
    source_kind: str | None
    source_ref: str | None
    trades: list[TradeInput]

    @classmethod
    def from_dict(cls, payload: object) -> "AppendTradesRequest":
        data = _require_dict(payload, field_name="payload")
        trades = [TradeInput.from_dict(item) for item in _require_list(data.get("trades", []), field_name="trades")]
        portfolio_id = normalize_optional_text(data.get("portfolio_id"))
        if not portfolio_id:
            raise ValueError("portfolio_id is required")
        return cls(
            portfolio_id=portfolio_id,
            source_kind=normalize_optional_text(data.get("source_kind")),
            source_ref=normalize_optional_text(data.get("source_ref")),
            trades=trades,
        )


@dataclass(frozen=True)
class GetPositionsRequest:
    portfolio_id: str

    @classmethod
    def from_dict(cls, payload: object) -> "GetPositionsRequest":
        data = _require_dict(payload, field_name="payload")
        portfolio_id = normalize_optional_text(data.get("portfolio_id"))
        if not portfolio_id:
            raise ValueError("portfolio_id is required")
        return cls(portfolio_id=portfolio_id)


@dataclass(frozen=True)
class GetTradesRequest:
    portfolio_id: str
    start_time: str | None
    end_time: str | None

    @classmethod
    def from_dict(cls, payload: object) -> "GetTradesRequest":
        data = _require_dict(payload, field_name="payload")
        portfolio_id = normalize_optional_text(data.get("portfolio_id"))
        if not portfolio_id:
            raise ValueError("portfolio_id is required")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        return cls(
            portfolio_id=portfolio_id,
            start_time=normalize_timestamp(start_time, field_name="start_time") if start_time is not None else None,
            end_time=normalize_timestamp(end_time, field_name="end_time") if end_time is not None else None,
        )


@dataclass(frozen=True)
class GetImportBatchRequest:
    batch_id: str

    @classmethod
    def from_dict(cls, payload: object) -> "GetImportBatchRequest":
        data = _require_dict(payload, field_name="payload")
        batch_id = normalize_optional_text(data.get("batch_id"))
        if not batch_id:
            raise ValueError("batch_id is required")
        return cls(batch_id=batch_id)
