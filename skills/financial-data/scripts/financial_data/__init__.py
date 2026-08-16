"""financial-data core package and reusable handbook utilities."""

from .cn_futures_official import fetch_cn_futures_daily
from .contracts import DataPoint, DataRequest, DataResult, ErrorCode, FinancialDataError, QualityFlag
from .eastmoney import EastmoneyClient
from .facade import get_data, result_dict
from .futures_positioning import (
    aggregate_standard_windows,
    aggregate_top_n,
    fetch_cn_futures_positions,
    position_denominators_from_daily,
)

__all__ = [
    "DataPoint",
    "DataRequest",
    "DataResult",
    "ErrorCode",
    "FinancialDataError",
    "QualityFlag",
    "EastmoneyClient",
    "fetch_cn_futures_daily",
    "fetch_cn_futures_positions",
    "aggregate_top_n",
    "aggregate_standard_windows",
    "position_denominators_from_daily",
    "get_data",
    "result_dict",
]
