"""Custom exceptions for BNB Trading System."""


class BNBTradingError(Exception):
    """Base exception for BNB Trading System."""


class DataError(BNBTradingError):
    """Data fetching or validation errors."""


class AnalysisError(BNBTradingError):
    """Analysis calculation errors."""


class ValidationError(BNBTradingError):
    """Signal validation errors."""


class ConfigurationError(BNBTradingError):
    """Configuration validation errors."""


class NetworkError(BNBTradingError):
    """Network connectivity errors."""


class InsufficientDataError(DataError):
    """Not enough data for analysis."""


class InvalidSignalError(ValidationError):
    """Invalid trading signal generated."""


class MarketRegimeError(AnalysisError):
    """Market regime detection errors."""
