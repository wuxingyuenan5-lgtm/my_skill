"""financial-data core package and reusable handbook utilities."""

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
    "get_data",
    "result_dict",
]
