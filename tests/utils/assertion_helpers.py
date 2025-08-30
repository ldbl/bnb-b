"""
Custom assertion helpers for BNB Trading System tests.

This module provides specialized assertion functions that validate
the specific business logic and constraints of the trading system.
"""

from typing import Any

import pandas as pd

from bnb_trading.core.models import DecisionResult, ModuleResult


def assert_decision_result_valid(result: DecisionResult) -> None:
    """
    Validates DecisionResult structure and constraints.

    This is a critical assertion that ensures all decision results
    follow the established business rules and data contracts.

    Args:
        result: The DecisionResult to validate

    Raises:
        AssertionError: If the result violates any constraints
    """
    # Type validation
    assert isinstance(result, DecisionResult), (
        f"Expected DecisionResult, got {type(result)}"
    )

    # Signal validation
    assert result.signal in ["LONG", "HOLD"], (
        f"Invalid signal: {result.signal}. Must be LONG or HOLD"
    )

    # Confidence validation
    assert isinstance(result.confidence, (int, float)), (
        f"Confidence must be numeric, got {type(result.confidence)}"
    )
    assert 0.0 <= result.confidence <= 1.0, (
        f"Confidence must be between 0.0 and 1.0, got {result.confidence}"
    )

    # LONG signal specific validation
    if result.signal == "LONG":
        assert result.confidence >= 0.85, (
            f"LONG signal must have confidence >= 0.85, got {result.confidence:.3f}"
        )

    # Reasons validation
    assert result.reasons is not None, "Reasons cannot be None"
    assert isinstance(result.reasons, list), (
        f"Reasons must be list, got {type(result.reasons)}"
    )
    assert len(result.reasons) > 0, "Reasons list cannot be empty"
    assert all(isinstance(reason, str) for reason in result.reasons), (
        "All reasons must be strings"
    )
    assert all(len(reason.strip()) > 0 for reason in result.reasons), (
        "No reason can be empty"
    )

    # Metrics validation
    assert result.metrics is not None, "Metrics cannot be None"
    assert isinstance(result.metrics, dict), (
        f"Metrics must be dict, got {type(result.metrics)}"
    )

    # Timestamp validation
    assert result.analysis_timestamp is not None, "Timestamp cannot be None"
    assert isinstance(result.analysis_timestamp, pd.Timestamp), (
        f"Timestamp must be pd.Timestamp, got {type(result.analysis_timestamp)}"
    )

    # Price level validation
    assert isinstance(result.price_level, (int, float)), (
        f"Price level must be numeric, got {type(result.price_level)}"
    )
    assert result.price_level >= 0.0, (
        f"Price level must be non-negative, got {result.price_level}"
    )


def assert_signals_identical(
    result1: DecisionResult,
    result2: DecisionResult,
    tolerance: float = 0.001,
    ignore_timestamp: bool = True,
) -> None:
    """
    Ensures two DecisionResults are identical (for parity testing).

    This is crucial for regression testing to ensure that main.py
    and backtester.py produce identical results.

    Args:
        result1: First DecisionResult
        result2: Second DecisionResult
        tolerance: Numerical tolerance for float comparisons
        ignore_timestamp: Whether to ignore timestamp differences

    Raises:
        AssertionError: If results are not identical
    """
    # Signal must be exactly the same
    assert result1.signal == result2.signal, (
        f"Signal mismatch: '{result1.signal}' != '{result2.signal}'"
    )

    # Confidence must be within tolerance
    confidence_diff = abs(result1.confidence - result2.confidence)
    assert confidence_diff < tolerance, (
        f"Confidence mismatch: {result1.confidence:.6f} vs {result2.confidence:.6f} (diff: {confidence_diff:.6f})"
    )

    # Reasons should be identical
    assert len(result1.reasons) == len(result2.reasons), (
        f"Different number of reasons: {len(result1.reasons)} vs {len(result2.reasons)}"
    )

    for i, (reason1, reason2) in enumerate(
        zip(result1.reasons, result2.reasons, strict=False)
    ):
        assert reason1 == reason2, f"Reason {i} mismatch: '{reason1}' != '{reason2}'"

    # Key metrics should be identical
    key_metrics = ["total_confidence", "threshold"]
    for key in key_metrics:
        if key in result1.metrics and key in result2.metrics:
            val1, val2 = result1.metrics[key], result2.metrics[key]
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                diff = abs(val1 - val2)
                assert diff < tolerance, (
                    f"Metric '{key}' mismatch: {val1:.6f} vs {val2:.6f} (diff: {diff:.6f})"
                )
            else:
                assert val1 == val2, f"Metric '{key}' mismatch: {val1} != {val2}"

    # Price level should be within tolerance (if both are set)
    if result1.price_level > 0 and result2.price_level > 0:
        price_diff = abs(result1.price_level - result2.price_level)
        assert price_diff < tolerance, (
            f"Price level mismatch: {result1.price_level:.6f} vs {result2.price_level:.6f}"
        )

    # Timestamp comparison (optional)
    if not ignore_timestamp:
        assert result1.analysis_timestamp == result2.analysis_timestamp, (
            f"Timestamp mismatch: {result1.analysis_timestamp} != {result2.analysis_timestamp}"
        )


def assert_long_accuracy_preserved(results: list[DecisionResult]) -> None:
    """
    Assert that LONG accuracy is preserved across a set of results.

    This is the critical regression test for the 21/21 LONG signals.

    Args:
        results: List of DecisionResults from historical data

    Raises:
        AssertionError: If LONG accuracy is not 100%
    """
    total_signals = len(results)
    long_signals = sum(1 for result in results if result.signal == "LONG")

    assert long_signals == total_signals, (
        f"LONG accuracy regression! Got {long_signals}/{total_signals} LONG signals ({long_signals / total_signals * 100:.1f}%)"
    )

    # Verify all LONG signals have sufficient confidence
    for i, result in enumerate(results):
        assert result.signal == "LONG", (
            f"Signal {i + 1} lost: expected LONG, got {result.signal}"
        )
        assert result.confidence >= 0.85, (
            f"Signal {i + 1} confidence too low: {result.confidence:.3f} < 0.85"
        )


def assert_module_contribution_valid(
    result: ModuleResult, expected_weight: float, tolerance: float = 0.001
) -> None:
    """
    Assert that module contribution is calculated correctly.

    Validates that contrib = score * weight as per the semantic rules.

    Args:
        result: ModuleResult to validate
        expected_weight: Expected weight from configuration
        tolerance: Numerical tolerance for float comparisons

    Raises:
        AssertionError: If contribution is not calculated correctly
    """
    expected_contrib = result.score * expected_weight
    actual_contrib = result.contrib

    contrib_diff = abs(actual_contrib - expected_contrib)
    assert contrib_diff < tolerance, (
        f"Contribution mismatch: expected {expected_contrib:.6f} (score={result.score:.3f} * weight={expected_weight:.3f}), got {actual_contrib:.6f}"
    )


def assert_performance_acceptable(
    execution_time: float,
    max_time: float = 2.0,
    memory_usage: float | None = None,
    max_memory: float | None = None,
) -> None:
    """
    Assert that performance metrics are within acceptable limits.

    Args:
        execution_time: Time taken in seconds
        max_time: Maximum acceptable time in seconds
        memory_usage: Memory usage in MB (optional)
        max_memory: Maximum acceptable memory in MB (optional)

    Raises:
        AssertionError: If performance is not acceptable
    """
    assert execution_time <= max_time, (
        f"Performance regression: execution took {execution_time:.3f}s > {max_time:.3f}s"
    )

    if memory_usage is not None and max_memory is not None:
        assert memory_usage <= max_memory, (
            f"Memory usage too high: {memory_usage:.1f}MB > {max_memory:.1f}MB"
        )


def assert_data_quality_valid(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Assert that test data has the required quality for reliable testing.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Raises:
        AssertionError: If data quality is insufficient
    """
    # Check DataFrame is not empty
    assert not df.empty, "DataFrame cannot be empty"

    # Check required columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    assert not missing_cols, f"Missing required columns: {missing_cols}"

    # Check for null values in required columns
    for col in required_columns:
        null_count = df[col].isnull().sum()
        assert null_count == 0, f"Column '{col}' has {null_count} null values"

    # Check numeric columns have reasonable values
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        if col in df.columns:
            assert (df[col] > 0).all(), f"Column '{col}' has non-positive values"

            # Check for reasonable price relationships
            if col in ["Open", "High", "Low", "Close"]:
                assert (df[col] < 1000000).all(), (
                    f"Column '{col}' has unrealistic high values"
                )

    # Check OHLC relationships
    ohlc_cols = ["Open", "High", "Low", "Close"]
    if all(col in df.columns for col in ohlc_cols):
        # High should be >= all other OHLC values
        assert (df["High"] >= df["Open"]).all(), "High < Open in some rows"
        assert (df["High"] >= df["Low"]).all(), "High < Low in some rows"
        assert (df["High"] >= df["Close"]).all(), "High < Close in some rows"

        # Low should be <= all other OHLC values
        assert (df["Low"] <= df["Open"]).all(), "Low > Open in some rows"
        assert (df["Low"] <= df["Close"]).all(), "Low > Close in some rows"


def assert_config_valid(config: dict[str, Any]) -> None:
    """
    Assert that test configuration is valid and complete.

    Args:
        config: Configuration dictionary to validate

    Raises:
        AssertionError: If configuration is invalid
    """
    # Check required top-level sections
    required_sections = ["signals"]
    for section in required_sections:
        assert section in config, f"Missing required config section: {section}"

    # Check signals section structure
    signals_config = config["signals"]
    assert "weights" in signals_config, "Missing signals.weights section"
    assert "thresholds" in signals_config, "Missing signals.thresholds section"

    # Check weights
    weights = signals_config["weights"]
    required_weights = ["weekly_tails", "fibonacci", "trend", "moving_avg"]
    for weight in required_weights:
        assert weight in weights, f"Missing weight: {weight}"
        assert 0.0 <= weights[weight] <= 1.0, (
            f"Invalid weight for {weight}: {weights[weight]}"
        )

    # Check thresholds
    thresholds = signals_config["thresholds"]
    assert "confidence_min" in thresholds, "Missing confidence_min threshold"
    assert 0.0 <= thresholds["confidence_min"] <= 1.0, (
        f"Invalid confidence_min: {thresholds['confidence_min']}"
    )
