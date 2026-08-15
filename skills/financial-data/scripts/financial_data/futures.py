from __future__ import annotations

from typing import Any, Iterable, Mapping


def _number(row: Mapping[str, Any], field: str) -> float:
    if field not in row or row[field] is None:
        raise KeyError(f"missing futures field: {field}")
    return float(row[field])


def select_dominant_contract(rows: Iterable[Mapping[str, Any]], metric: str = "open_interest") -> dict[str, Any]:
    """Select a dominant contract using an explicit OI/volume methodology."""
    items = [dict(row) for row in rows]
    if not items:
        raise ValueError("cannot select dominant contract from empty rows")
    if metric not in {"open_interest", "volume"}:
        raise ValueError("metric must be 'open_interest' or 'volume'")
    return max(items, key=lambda row: _number(row, metric))


def term_structure(rows: Iterable[Mapping[str, Any]], price_field: str = "settlement") -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if not row.get("delivery_month") or not row.get("contract_id"):
            raise KeyError("term-structure row requires delivery_month and contract_id")
        point = dict(row)
        point["price"] = _number(row, price_field)
        point["price_field"] = price_field
        out.append(point)
    out.sort(key=lambda row: str(row["delivery_month"]))
    return out


def calendar_spread(near: Mapping[str, Any], far: Mapping[str, Any], price_field: str = "settlement", definition: str = "near_minus_far") -> dict[str, Any]:
    near_price, far_price = _number(near, price_field), _number(far, price_field)
    if definition == "near_minus_far": value = near_price - far_price
    elif definition == "far_minus_near": value = far_price - near_price
    else: raise ValueError("unsupported calendar spread definition")
    return {"near_contract":near.get("contract_id"),"far_contract":far.get("contract_id"),"price_field":price_field,"definition":definition,"value":value}


def basis(spot_price: float, futures_price: float, definition: str = "spot_minus_futures") -> dict[str, Any]:
    spot, future = float(spot_price), float(futures_price)
    if definition == "spot_minus_futures": value = spot - future
    elif definition == "futures_minus_spot": value = future - spot
    else: raise ValueError("unsupported basis definition")
    return {"definition":definition,"spot":spot,"futures":future,"value":value}


def roll_adjustment(old_price: float, new_price: float, method: str = "difference") -> dict[str, Any]:
    old, new = float(old_price), float(new_price)
    if method == "difference": value = new - old
    elif method == "ratio":
        if old == 0: raise ZeroDivisionError("old_price must be non-zero for ratio adjustment")
        value = new / old
    else: raise ValueError("method must be 'difference' or 'ratio'")
    return {"method":method,"value":value}
