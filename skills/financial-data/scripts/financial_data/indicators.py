from __future__ import annotations

import math
import statistics
from typing import Iterable, Optional, Union


ALGORITHM_VERSION = "financial-data-indicators/0.1.0"


def _floats(values: Iterable[float]) -> list[float]:
    return [float(v) for v in values]


def sma(values: Iterable[float], period: int) -> list[Optional[float]]:
    xs = _floats(values)
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[Optional[float]] = []
    for i in range(len(xs)):
        if i + 1 < period:
            out.append(None)
        else:
            out.append(sum(xs[i - period + 1 : i + 1]) / period)
    return out


def ema(values: Iterable[float], period: int) -> list[float]:
    xs = _floats(values)
    if period <= 0:
        raise ValueError("period must be positive")
    if not xs:
        return []
    alpha = 2.0 / (period + 1.0)
    out = [xs[0]]
    for x in xs[1:]:
        out.append(alpha * x + (1.0 - alpha) * out[-1])
    return out


def returns(prices: Iterable[float], *, log: bool = False) -> list[Optional[float]]:
    xs = _floats(prices)
    if not xs:
        return []
    out: list[Optional[float]] = [None]
    for prev, cur in zip(xs, xs[1:]):
        if prev <= 0 or (log and cur <= 0):
            raise ValueError("prices must be positive for return calculation")
        out.append(math.log(cur / prev) if log else cur / prev - 1.0)
    return out


def rsi(values: Iterable[float], period: int = 14) -> list[Optional[float]]:
    xs = _floats(values)
    if period <= 0:
        raise ValueError("period must be positive")
    if not xs:
        return []
    out: list[Optional[float]] = [None] * len(xs)
    if len(xs) <= period:
        return out
    changes = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
    gains = [max(c, 0.0) for c in changes]
    losses = [max(-c, 0.0) for c in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    def calc(g: float, l: float) -> float:
        if l == 0:
            return 100.0 if g > 0 else 50.0
        rs = g / l
        return 100.0 - 100.0 / (1.0 + rs)

    out[period] = calc(avg_gain, avg_loss)
    for idx in range(period + 1, len(xs)):
        gain = gains[idx - 1]
        loss = losses[idx - 1]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[idx] = calc(avg_gain, avg_loss)
    return out


def macd(values: Iterable[float], *, fast: int = 12, slow: int = 26, signal: int = 9) -> dict[str, list[float]]:
    xs = _floats(values)
    if not (0 < fast < slow and signal > 0):
        raise ValueError("require 0 < fast < slow and signal > 0")
    fast_e = ema(xs, fast)
    slow_e = ema(xs, slow)
    line = [a - b for a, b in zip(fast_e, slow_e)]
    sig = ema(line, signal)
    hist = [a - b for a, b in zip(line, sig)]
    return {"macd": line, "signal": sig, "histogram": hist}


def bollinger(values: Iterable[float], *, period: int = 20, num_std: float = 2.0) -> dict[str, list[Optional[float]]]:
    xs = _floats(values)
    if period <= 0:
        raise ValueError("period must be positive")
    middle: list[Optional[float]] = []
    upper: list[Optional[float]] = []
    lower: list[Optional[float]] = []
    for i in range(len(xs)):
        if i + 1 < period:
            middle.append(None); upper.append(None); lower.append(None)
            continue
        window = xs[i - period + 1 : i + 1]
        mean = sum(window) / period
        variance = sum((x - mean) ** 2 for x in window) / period
        std = math.sqrt(variance)
        middle.append(mean)
        upper.append(mean + num_std * std)
        lower.append(mean - num_std * std)
    return {"middle": middle, "upper": upper, "lower": lower}


def volatility(prices: Iterable[float], *, periods_per_year: int = 252, log_returns: bool = True) -> float:
    rs = [r for r in returns(prices, log=log_returns)[1:] if r is not None]
    if len(rs) < 2:
        raise ValueError("at least three prices are required")
    return statistics.stdev(rs) * math.sqrt(periods_per_year)


def drawdown(prices: Iterable[float]) -> list[float]:
    xs = _floats(prices)
    if not xs:
        return []
    peak = xs[0]
    out: list[float] = []
    for x in xs:
        peak = max(peak, x)
        out.append(x / peak - 1.0 if peak else 0.0)
    return out


def historical_percentile(history: Iterable[float], value: float) -> float:
    xs = _floats(history)
    if not xs:
        raise ValueError("history cannot be empty")
    return sum(x <= float(value) for x in xs) / len(xs)


def turnover_rate(volume_shares: float, free_float_shares: float) -> float:
    if free_float_shares <= 0:
        raise ValueError("free_float_shares must be positive")
    if volume_shares < 0:
        raise ValueError("volume_shares cannot be negative")
    return float(volume_shares) / float(free_float_shares)


def turnover_concentration(turnovers: Iterable[float], *, top_n: int = 20) -> float:
    xs = [float(x) for x in turnovers]
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    if any(x < 0 for x in xs):
        raise ValueError("turnover values cannot be negative")
    total = sum(xs)
    if total == 0:
        return 0.0
    return sum(sorted(xs, reverse=True)[:top_n]) / total


def market_breadth(changes: Iterable[float]) -> dict[str, Union[float, int]]:
    xs = _floats(changes)
    adv = sum(x > 0 for x in xs)
    dec = sum(x < 0 for x in xs)
    unchanged = len(xs) - adv - dec
    return {
        "advancers": adv,
        "decliners": dec,
        "unchanged": unchanged,
        "advance_ratio": adv / len(xs) if xs else 0.0,
    }


def kdj(bars: list[dict[str, float]], *, period: int = 9, k_smooth: int = 3, d_smooth: int = 3) -> list[dict[str, Optional[float]]]:
    if period <= 0 or k_smooth <= 0 or d_smooth <= 0:
        raise ValueError("period and smoothing parameters must be positive")
    k_value = 50.0
    d_value = 50.0
    out: list[dict[str, Optional[float]]] = []
    for i, bar in enumerate(bars):
        if i + 1 < period:
            out.append({"k": None, "d": None, "j": None})
            continue
        window = bars[i - period + 1 : i + 1]
        highest = max(float(x["high"]) for x in window)
        lowest = min(float(x["low"]) for x in window)
        close = float(bar["close"])
        rsv = 50.0 if highest == lowest else (close - lowest) / (highest - lowest) * 100.0
        k_value = (1.0 / k_smooth) * rsv + (1.0 - 1.0 / k_smooth) * k_value
        d_value = (1.0 / d_smooth) * k_value + (1.0 - 1.0 / d_smooth) * d_value
        j_value = 3.0 * k_value - 2.0 * d_value
        out.append({"k": k_value, "d": d_value, "j": j_value})
    return out
