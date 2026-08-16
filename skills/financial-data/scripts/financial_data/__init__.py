"""financial-data core package and reusable handbook utilities."""

from .cn_futures_official import fetch_cn_futures_daily
from .contracts import DataPoint, DataRequest, DataResult, ErrorCode, FinancialDataError, QualityFlag
from .eastmoney import EastmoneyClient
from .facade import get_data, result_dict

__all__ = [
    "DataPoint",
    "DataRequest",
    "DataResult",
    "ErrorCode",
    "FinancialDataError",
    "QualityFlag",
    "EastmoneyClient",
    "fetch_cn_futures_daily",
    "get_data",
    "result_dict",
]
