"""
Telemetry output for LONG decision transparency
Simple but clear console output showing decision breakdown
"""

import logging

from ..core.models import DecisionResult

logger = logging.getLogger(__name__)


def display_decision_telemetry(result: DecisionResult) -> None:
    """
    Display decision telemetry table for transparency

    Args:
        result: DecisionResult from unified decision logic
    """
    try:
        print("\n" + "═" * 60)
        print("🎯 LONG Decision Telemetry")
        print("═" * 60)

        # Data Health Check
        metrics = result.metrics
        data_health = "✓ 500d/100w closed" if metrics else "⚠ No metrics"
        print(f"Data: {data_health}")

        # Core Metrics
        if "tail_strength" in metrics:
            tail_strength = metrics["tail_strength"]
            status = "[PASS]" if tail_strength >= 2.5 else "[FAIL]"
            print(f"Tails: {tail_strength:.2f} strength {status}")

        if "fibonacci_confidence" in metrics:
            fib_conf = metrics["fibonacci_confidence"]
            proximity = "0.015" if fib_conf > 0.6 else "N/A"  # Placeholder
            status = "[PASS]" if fib_conf > 0.5 else "[FAIL]"
            print(f"Fib: {proximity} proximity {status}")

        if "volume_confidence" in metrics:
            vol_conf = metrics["volume_confidence"]
            ratio = f"{vol_conf * 2:.2f}x" if vol_conf > 0.5 else "N/A"  # Approx
            status = "[PASS]" if vol_conf > 0.5 else "[FAIL]"
            print(f"Volume: {ratio} MA20 {status}")

        # Final Decision
        confidence_status = "✓" if result.confidence >= 0.88 else "✗"
        print(f"Confidence: {result.confidence:.3f} {confidence_status}")

        # Signal & Price
        signal_icon = (
            "🟢"
            if result.signal == "LONG"
            else ("🔴" if result.signal == "SHORT" else "⚪")
        )
        print(f"Signal: {signal_icon} {result.signal} @ ${result.price_level:.2f}")

        # Reason
        reason = result.reasons[0] if result.reasons else "No reason provided"
        print(f"Reason: {reason}")

        print("═" * 60)

        # Weights breakdown (if available)
        if "weights_used" in metrics:
            weights = metrics["weights_used"]
            print("⚖️  Weights:")
            print(f"   Tails: {weights.get('weekly_tails', 0):.2f}")
            print(f"   Fib: {weights.get('fibonacci', 0):.2f}")
            print(f"   Trend: {weights.get('trend', 0):.2f}")
            print(f"   Volume: {weights.get('volume', 0):.2f}")
            print("═" * 60)

        print()  # Final newline

    except Exception as e:
        logger.exception(f"Error displaying decision telemetry: {e}")
        # Fallback simple display
        print(f"\n🎯 Decision: {result.signal} (confidence: {result.confidence:.3f})")
        print(f"💰 Price: ${result.price_level:.2f}")
        if result.reasons:
            print(f"📝 Reason: {result.reasons[0]}")
        print()


def format_decision_summary(result: DecisionResult) -> str:
    """
    Format decision as a simple text summary

    Args:
        result: DecisionResult from unified decision logic

    Returns:
        Formatted summary string
    """
    try:
        signal_icon = (
            "🟢"
            if result.signal == "LONG"
            else ("🔴" if result.signal == "SHORT" else "⚪")
        )
        reason = result.reasons[0] if result.reasons else "No reason"

        return (
            f"{signal_icon} {result.signal} "
            f"(confidence: {result.confidence:.3f}, "
            f"price: ${result.price_level:.2f}) - {reason}"
        )

    except Exception as e:
        logger.exception(f"Error formatting decision summary: {e}")
        return f"Decision: {result.signal} (error formatting)"
