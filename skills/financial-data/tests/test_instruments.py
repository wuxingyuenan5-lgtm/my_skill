import pytest

from financial_data.contracts import ErrorCode, FinancialDataError
from financial_data.instruments import InstrumentMaster, normalize_symbol


def test_resolve_a_share_suffixes():
    master = InstrumentMaster()
    assert master.resolve("600519").ticker == "600519.SH"
    assert master.resolve("000001").ticker == "000001.SZ"
    assert master.resolve("300750").ticker == "300750.SZ"


def test_resolve_known_cn_index_before_equity_default():
    inst = InstrumentMaster().resolve("000300")
    assert inst.ticker == "000300.SH"
    assert inst.asset_class == "index"


def test_resolve_bse_current_920_series():
    inst = InstrumentMaster().resolve("920982")
    assert inst.ticker == "920982.BJ"
    assert inst.exchange == "BSE"


def test_bare_legacy_bse_code_is_not_silently_accepted():
    with pytest.raises(FinancialDataError) as exc:
        InstrumentMaster().resolve("832982")
    assert exc.value.code == ErrorCode.INSTRUMENT_NOT_FOUND
    assert "920" in exc.value.message


def test_resolve_hk_padding():
    master = InstrumentMaster()
    assert master.resolve("700.HK").ticker == "0700.HK"
    assert master.resolve("0700.HK").currency == "HKD"


def test_resolve_us_ticker_and_class_share():
    master = InstrumentMaster()
    assert master.resolve("AAPL").ticker == "AAPL.US"
    assert master.resolve("BRK.B").ticker == "BRK.B.US"


def test_common_index_aliases():
    master = InstrumentMaster()
    assert master.resolve("SPX").asset_class == "index"
    assert master.resolve("HSI").ticker == "HSI.HK"


def test_invalid_symbol_raises_explicit_error():
    with pytest.raises(FinancialDataError) as exc:
        normalize_symbol("茅台")
    assert exc.value.code == ErrorCode.INSTRUMENT_NOT_FOUND
