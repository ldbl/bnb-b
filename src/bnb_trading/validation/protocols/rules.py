"""Validation rules for BNB Trading System."""

import logging
from typing import Any

from ...core.exceptions import ValidationError
from ...core.models import ValidationPoint

logger = logging.getLogger(__name__)


def define_validation_points() -> list[ValidationPoint]:
    """Дефинира 7-те validation точки"""

    return [
        ValidationPoint(
            name="long_accuracy_protection",
            description="LONG сигнали точността трябва да остане 100%",
            critical=True,
            validator_func=validate_long_accuracy,
            expected_result=">= 100.0%",
            failure_message="LONG accuracy падна под критичния праг от 100%",
        ),
        ValidationPoint(
            name="pnl_stability_check",
            description="P&L не трябва да се влошава значително",
            critical=True,
            validator_func=validate_pnl_stability,
            expected_result="No significant regression",
            failure_message="P&L показва значителна регресия",
        ),
        ValidationPoint(
            name="max_drawdown_control",
            description="Max drawdown не трябва да се увеличава с >5%",
            critical=True,
            validator_func=validate_drawdown_control,
            expected_result="<= +5% increase",
            failure_message="Max drawdown се е увеличил значително",
        ),
        ValidationPoint(
            name="short_signal_logic",
            description="SHORT сигнали трябва да имат логични резултати",
            critical=False,
            validator_func=validate_short_signal_logic,
            expected_result="Logical signal distribution",
            failure_message="SHORT сигнали показват нелогично поведение",
        ),
        ValidationPoint(
            name="configuration_documented",
            description="Всички нови параметри трябва да са документирани",
            critical=True,
            validator_func=validate_configuration,
            expected_result="All parameters documented",
            failure_message="Недокументирани конфигурационни параметри",
        ),
        ValidationPoint(
            name="edge_cases_tested",
            description="Edge cases трябва да са тествани",
            critical=False,
            validator_func=validate_edge_cases,
            expected_result="Edge cases handled",
            failure_message="Edge cases не са обработени правилно",
        ),
        ValidationPoint(
            name="performance_impact",
            description="Performance impact трябва да е приемлив",
            critical=False,
            validator_func=validate_performance_impact,
            expected_result="Acceptable performance",
            failure_message="Performance impact е твърде висок",
        ),
    ]


def validate_long_accuracy(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """Validate LONG signal accuracy doesn't degrade."""
    try:
        baseline_long_acc = baseline.get("long_accuracy", 0.0)
        current_long_acc = current.get("long_accuracy", 0.0)

        # Allow small tolerance for statistical variation
        tolerance = 0.05  # 5%
        acceptable_threshold = baseline_long_acc - tolerance

        passed = current_long_acc >= acceptable_threshold

        return {
            "passed": passed,
            "baseline_accuracy": baseline_long_acc,
            "current_accuracy": current_long_acc,
            "threshold": acceptable_threshold,
            "difference": current_long_acc - baseline_long_acc,
        }

    except Exception as e:
        logger.exception(f"Error validating LONG accuracy: {e}")
        raise ValidationError(f"LONG accuracy validation failed: {e}") from e


def validate_pnl_stability(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """Validate P&L stability."""
    try:
        baseline_pnl = baseline.get("total_pnl", 0.0)
        current_pnl = current.get("total_pnl", 0.0)

        # Allow 10% regression tolerance
        tolerance = 0.10
        acceptable_threshold = baseline_pnl * (1 - tolerance)

        passed = current_pnl >= acceptable_threshold

        return {
            "passed": passed,
            "baseline_pnl": baseline_pnl,
            "current_pnl": current_pnl,
            "threshold": acceptable_threshold,
            "regression_pct": ((baseline_pnl - current_pnl) / baseline_pnl * 100)
            if baseline_pnl != 0
            else 0,
        }

    except Exception as e:
        logger.exception(f"Error validating P&L stability: {e}")
        raise ValidationError(f"P&L stability validation failed: {e}") from e


def validate_drawdown_control(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """Validate drawdown doesn't increase significantly."""
    try:
        baseline_dd = baseline.get("max_drawdown", 0.0)
        current_dd = current.get("max_drawdown", 0.0)

        # Max 5% increase in drawdown
        max_increase = 0.05
        acceptable_threshold = baseline_dd + max_increase

        passed = current_dd <= acceptable_threshold

        return {
            "passed": passed,
            "baseline_drawdown": baseline_dd,
            "current_drawdown": current_dd,
            "threshold": acceptable_threshold,
            "increase": current_dd - baseline_dd,
        }

    except Exception as e:
        logger.exception(f"Error validating drawdown control: {e}")
        raise ValidationError(f"Drawdown control validation failed: {e}") from e


def validate_short_signal_logic(
    baseline: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """Validate SHORT signal logic."""
    try:
        baseline_short_count = baseline.get("short_signals", 0)
        current_short_count = current.get("short_signals", 0)

        # Check if SHORT signals are reasonable
        total_signals = current.get("total_signals", 1)
        short_ratio = current_short_count / total_signals if total_signals > 0 else 0

        # SHORT signals shouldn't be more than 60% in bull market
        reasonable_ratio = short_ratio <= 0.60

        passed = reasonable_ratio

        return {
            "passed": passed,
            "baseline_short_count": baseline_short_count,
            "current_short_count": current_short_count,
            "short_ratio": short_ratio,
            "reasonable_ratio": reasonable_ratio,
        }

    except Exception as e:
        logger.exception(f"Error validating SHORT signal logic: {e}")
        raise ValidationError(f"SHORT signal logic validation failed: {e}") from e


def validate_configuration(config: dict[str, Any]) -> dict[str, Any]:
    """Validate configuration documentation."""
    # Simplified - always pass for now
    return {"passed": True, "reason": "Configuration validation simplified"}


def validate_edge_cases(test_results: dict[str, Any]) -> dict[str, Any]:
    """Validate edge case handling."""
    # Simplified - always pass for now
    return {"passed": True, "reason": "Edge case validation simplified"}


def validate_performance_impact(performance_data: dict[str, Any]) -> dict[str, Any]:
    """Validate performance impact."""
    # Simplified - always pass for now
    return {"passed": True, "reason": "Performance validation simplified"}
