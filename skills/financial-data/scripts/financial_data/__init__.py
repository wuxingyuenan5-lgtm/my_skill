"""financial-data core package."""

from .contracts import DataPoint, DataRequest, DataResult, ErrorCode, FinancialDataError, QualityFlag
from .facade import get_data, result_dict

__all__ = [
    "DataPoint",
    "DataRequest",
    "DataResult",
    "ErrorCode",
    "FinancialDataError",
    "QualityFlag",
    "get_data",
    "result_dict",
]
