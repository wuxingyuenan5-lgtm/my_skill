import math
import pytest

from financial_data.indicators import (
    bollinger,
    drawdown,
    ema,
    historical_percentile,
    kdj,
    macd,
    market_breadth,
    returns,
    rsi,
    sma,
    turnover_concentration,
    turnover_rate,
    volatility,
)


def test_sma():
    assert sma([1, 2, 3, 4, 5], 3) == [None, None, 2.0, 3.0, 4.0]


def test_ema_uses_standard_alpha_and_first_value_seed():
    out = ema([1, 2, 3, 4], 3)
    assert out == pytest.approx([1.0, 1.5, 2.25, 3.125])


def test_returns_simple_and_log():
    prices = [100, 110, 99]
    assert returns(prices) == pytest.approx([None, 0.1, -0.1])
    logs = returns(prices, log=True)
    assert logs[1] == pytest.approx(math.log(1.1))


def test_rsi_wilder_reaches_100_on_monotonic_series():
    values = list(range(1, 20))
    out = rsi(values, 14)
    assert out[13] is None
    assert out[14] == 100.0
    assert out[-1] == 100.0


def test_macd_shapes_and_histogram_identity():
    out = macd(list(range(1, 40)), fast=12, slow=26, signal=9)
    assert len(out["macd"]) == 39
    i = -1
    assert out["histogram"][i] == pytest.approx(out["macd"][i] - out["signal"][i])


def test_bollinger_population_std():
    out = bollinger([1, 2, 3, 4, 5], period=5, num_std=2)
    assert out["middle"][-1] == 3.0
    assert out["upper"][-1] == pytest.approx(3 + 2 * math.sqrt(2))
    assert out["lower"][-1] == pytest.approx(3 - 2 * math.sqrt(2))


def test_drawdown_uses_running_peak():
    assert drawdown([100, 120, 90, 108]) == pytest.approx([0.0, 0.0, -0.25, -0.1])


def test_turnover_rate_uses_shares_not_value():
    assert turnover_rate(volume_shares=10_000_000, free_float_shares=1_000_000_000) == 0.01
    with pytest.raises(ValueError):
        turnover_rate(10, 0)


def test_turnover_concentration():
    assert turnover_concentration([100, 50, 25, 25], top_n=2) == pytest.approx(0.75)


def test_historical_percentile_is_empirical_cdf():
    assert historical_percentile([1, 2, 3, 4], 3) == 0.75


def test_market_breadth():
    out = market_breadth([0.01, -0.02, 0.0, 0.03])
    assert out == {"advancers": 2, "decliners": 1, "unchanged": 1, "advance_ratio": 0.5}


def test_volatility_annualizes_sample_std_of_returns():
    prices = [100, 101, 100, 102, 101]
    v = volatility(prices, periods_per_year=252, log_returns=False)
    assert v > 0


def test_kdj_returns_k_d_j_after_window():
    bars = [
        {"high": 10+i, "low": 8+i, "close": 9+i} for i in range(12)
    ]
    out = kdj(bars, period=9)
    assert out[7]["k"] is None
    assert out[8]["k"] is not None
    assert out[8]["j"] == pytest.approx(3*out[8]["k"] - 2*out[8]["d"])
