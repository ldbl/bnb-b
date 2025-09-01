"""Report generation for historical testing."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from bnb_trading.core.exceptions import AnalysisError
from bnb_trading.core.models import TestResult

logger = logging.getLogger(__name__)


def generate_test_report(
    results: list[TestResult],
    analysis: dict[str, Any],
    feature_name: str = "system_test",
) -> str:
    """
    Generate comprehensive test report.

    Args:
        results: Test results from different periods
        analysis: Analysis of test results
        feature_name: Name of feature being tested

    Returns:
        Formatted test report as string
    """
    try:
        report_lines = []

        # Header
        report_lines.append(f"🧪 Historical Test Report: {feature_name}")
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("=" * 60)

        # Summary
        summary = analysis.get("summary", {})
        report_lines.append("\n📊 SUMMARY")
        report_lines.append(f"Total Signals: {summary.get('total_signals', 0)}")
        report_lines.append(
            f"Overall Accuracy: {summary.get('overall_accuracy', 0):.1f}%"
        )
        report_lines.append(f"LONG Accuracy: {summary.get('long_accuracy', 0):.1f}%")
        report_lines.append(f"SHORT Accuracy: {summary.get('short_accuracy', 0):.1f}%")
        report_lines.append(f"Total P&L: {summary.get('total_pnl', 0):.2f}%")

        # Baseline comparison
        baseline_comp = analysis.get("baseline_comparison", {})
        if baseline_comp:
            report_lines.append("\n📈 BASELINE COMPARISON")
            long_vs_baseline = baseline_comp.get("long_vs_baseline", 0)
            short_vs_baseline = baseline_comp.get("short_vs_baseline", 0)

            report_lines.append(f"LONG vs Baseline: {long_vs_baseline:+.1f}%")
            report_lines.append(f"SHORT vs Baseline: {short_vs_baseline:+.1f}%")

        # Period breakdown
        period_analysis = analysis.get("period_analysis", {})
        if period_analysis:
            report_lines.append("\n📅 PERIOD BREAKDOWN")
            for period_name, period_data in period_analysis.items():
                accuracy = period_data.get("accuracy", 0)
                assessment = period_data.get("assessment", "UNKNOWN")
                report_lines.append(f"{period_name}: {accuracy:.1f}% ({assessment})")

        # Quality assessment
        quality = analysis.get("quality_assessment", {})
        report_lines.append(
            f"\n✅ QUALITY ASSESSMENT: {quality.get('overall_grade', 'UNKNOWN')}"
        )

        quality_issues = quality.get("quality_issues", [])
        if quality_issues:
            report_lines.append("⚠️  Issues found:")
            for issue in quality_issues:
                report_lines.append(f"   - {issue}")

        recommendations = quality.get("recommendations", [])
        if recommendations:
            report_lines.append("💡 Recommendations:")
            for rec in recommendations:
                report_lines.append(f"   - {rec}")

        return "\n".join(report_lines)

    except Exception as e:
        logger.exception(f"Error generating test report: {e}")
        raise AnalysisError(f"Test report generation failed: {e}") from e


def export_results_to_json(
    results: list[TestResult],
    analysis: dict[str, Any],
    output_path: str = "data/test_results.json",
) -> bool:
    """
    Export test results to JSON file.

    Args:
        results: Test results
        analysis: Analysis results
        output_path: Path to output JSON file

    Returns:
        True if export successful, False otherwise
    """
    try:
        # Prepare data for export
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "results": [_test_result_to_dict(r) for r in results],
            "analysis": analysis,
        }

        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Test results exported to {output_path}")
        return True

    except Exception as e:
        logger.exception(f"Error exporting results: {e}")
        return False


def _test_result_to_dict(result: TestResult) -> dict[str, Any]:
    """Convert TestResult to dictionary for JSON export."""
    return {
        "period_name": result.period_name,
        "start_date": result.start_date,
        "end_date": result.end_date,
        "total_signals": result.total_signals,
        "long_signals": result.long_signals,
        "short_signals": result.short_signals,
        "long_accuracy": result.long_accuracy,
        "short_accuracy": result.short_accuracy,
        "overall_accuracy": result.overall_accuracy,
        "total_pnl": result.total_pnl,
        "max_drawdown": result.max_drawdown,
        "sharpe_ratio": result.sharpe_ratio,
        "avg_trade_duration": result.avg_trade_duration,
        "baseline_comparison": result.baseline_comparison,
    }
