"""Unified decision logic for BNB Trading System - single source of truth for signal decisions."""

import logging
from dataclasses import dataclass
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DecisionContext:
    """Context data for making trading decisions."""

    daily_df: pd.DataFrame
    weekly_df: pd.DataFrame
    analyses: dict[str, Any]
    config: dict[str, Any]


@dataclass
class DecisionResult:
    """Result of a trading decision."""

    signal: str  # LONG/SHORT/HOLD
    confidence: float
    reasons: list[str]
    metadata: dict[str, Any]


def decide_signal(context: DecisionContext) -> DecisionResult:
    """
    Single source of truth for signal decisions.

    This function consolidates all decision logic that was previously scattered
    across main.py, backtester.py, and signal_generator.py.

    Args:
        context: All data needed to make a decision

    Returns:
        DecisionResult with final trading decision
    """
    try:
        # Step 1: Combine signals using weighted scoring
        logger.debug("[DECISION] Step 1: Combining signals...")

        from bnb_trading.signals.combiners import combine_signals

        # Get weights from config
        weights = _extract_weights(context.config)
        confidence_threshold = context.config.get("signals", {}).get(
            "confidence_threshold", 0.3
        )

        combined_signal = combine_signals(
            context.analyses, weights, confidence_threshold
        )

        # Step 2: Apply filters
        logger.debug("[DECISION] Step 2: Applying filters...")

        from bnb_trading.signals.filters import apply_signal_filters

        filtered_signal = apply_signal_filters(combined_signal, context.config)

        # Step 3: Calculate final confidence
        logger.debug("[DECISION] Step 3: Calculating final confidence...")

        from bnb_trading.signals.confidence import calculate_confidence

        final_confidence = calculate_confidence(filtered_signal, context.analyses)

        # Step 4: Validate decision
        logger.debug("[DECISION] Step 4: Validating decision...")

        final_signal = _validate_decision(filtered_signal, final_confidence, context)

        # Step 5: Build decision result
        decision_result = DecisionResult(
            signal=final_signal.get("signal", "HOLD"),
            confidence=final_confidence,
            reasons=final_signal.get("reasons", []),
            metadata={
                "analysis_modules": len(context.analyses),
                "weights_used": weights,
                "threshold": confidence_threshold,
                "price": context.daily_df["Close"].iloc[-1]
                if not context.daily_df.empty
                else 0.0,
                "timestamp": context.daily_df.index[-1]
                if not context.daily_df.empty
                else pd.Timestamp.now(),
                "long_score": combined_signal.get("long_score", 0),
                "short_score": combined_signal.get("short_score", 0),
                "total_weight": combined_signal.get("total_weight", 0),
            },
        )

        # Debug final decision
        logger.debug(
            f"[DECISION] Final: signal={decision_result.signal}, confidence={decision_result.confidence:.3f}, reasons={len(decision_result.reasons)}"
        )

        return decision_result

    except Exception as e:
        logger.exception(f"Error in unified decision logic: {e}")
        return DecisionResult(
            signal="HOLD",
            confidence=0.0,
            reasons=[f"Decision error: {e}"],
            metadata={"error": str(e)},
        )


def _extract_weights(config: dict[str, Any]) -> dict[str, float]:
    """Extract signal weights from configuration."""
    signals_config = config.get("signals", {})

    return {
        "fibonacci": signals_config.get("fibonacci_weight", 0.35),
        "weekly_tails": signals_config.get("weekly_tails_weight", 0.40),
        "ma": signals_config.get("ma_weight", 0.10),
        "rsi": signals_config.get("rsi_weight", 0.08),
        "macd": signals_config.get("macd_weight", 0.07),
        "bb": signals_config.get("bb_weight", 0.00),
    }


def _validate_decision(
    signal: dict[str, Any], confidence: float, context: DecisionContext
) -> dict[str, Any]:
    """Validate final trading decision against risk criteria."""
    try:
        # Basic validation
        if not signal:
            return {"signal": "HOLD", "reasons": ["No signal data"]}

        current_signal = signal.get("signal", "HOLD")

        # Risk management checks
        if current_signal != "HOLD":
            # Check if we're near ATH (All-Time High)
            if not context.daily_df.empty:
                current_price = context.daily_df["Close"].iloc[-1]
                recent_high = context.daily_df["Close"].tail(180).max()  # 180-day ATH
                distance_from_ath = (recent_high - current_price) / recent_high

                if distance_from_ath < 0.05:  # Within 5% of ATH
                    logger.info(
                        f"Near ATH filter: {distance_from_ath:.2%} from recent high"
                    )
                    if current_signal == "SHORT":
                        return {
                            "signal": "HOLD",
                            "reasons": [
                                f"Too close to ATH for SHORT ({distance_from_ath:.2%})"
                            ],
                        }

        # Confidence validation
        min_confidence = context.config.get("signals", {}).get(
            "confidence_threshold", 0.3
        )
        if confidence < min_confidence:
            return {
                "signal": "HOLD",
                "reasons": [
                    f"Confidence {confidence:.3f} below threshold {min_confidence}"
                ],
            }

        # All checks passed
        return signal

    except Exception as e:
        logger.exception(f"Error validating decision: {e}")
        return {"signal": "HOLD", "reasons": [f"Validation error: {e}"]}


# Convenience functions for backwards compatibility


def run_live_decision(context: DecisionContext) -> DecisionResult:
    """Run decision logic for live trading (main.py)."""
    return decide_signal(context)


def run_backtest_decision(context: DecisionContext) -> DecisionResult:
    """Run decision logic for backtesting (backtester.py)."""
    return decide_signal(context)
