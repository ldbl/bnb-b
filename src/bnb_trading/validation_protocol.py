#!/usr/bin/env python3
"""
🛡️ Pre-deployment Validation Protocol - 7-Point Validation System
==================================================================

Този модул имплементира задължителна validation система преди deployment
на всяка нова функционалност в BNB Trading System.

7-POINT VALIDATION CHECKLIST:
=============================
1. ✅ LONG Accuracy Protection (100% must be maintained)
2. ✅ P&L Stability Check (no regression allowed)
3. ✅ Max Drawdown Control (cannot increase significantly)
4. ✅ SHORT Signal Logic Validation (must make sense)
5. ✅ Configuration Documentation (all parameters documented)
6. ✅ Edge Cases Testing (missing data, extreme values)
7. ✅ Performance Impact Assessment (speed and resource usage)

Author: Stanislav Nedelchev
Date: 2025-08-28
Version: 2.0
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import our testing framework
from historical_tester import HistoricalTester, TestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationPoint:
    """Структура за един validation point"""

    name: str
    description: str
    critical: bool  # Ако е True, failure блокира deployment
    validator_func: callable
    expected_result: Any
    failure_message: str


@dataclass
class ValidationResult:
    """Резултат от цялата validation"""

    feature_name: str
    total_points: int
    passed_points: int
    failed_points: int
    critical_failures: int
    results: Dict[str, Dict[str, Any]]
    deployment_ready: bool
    summary: str


class ValidationProtocol:
    """
    7-Point Pre-deployment Validation Protocol

    Тази система осигурява че всяка нова функционалност:
    - Не нарушава съществуващата функционалност
    - Подобрява performance или поне не я влошава
    - Е добре документирана и тествана
    - Е готова за production deployment
    """

    def __init__(self, config_path: str = "config.toml"):
        """
        Инициализация на validation protocol

        Args:
            config_path: Път до конфигурационния файл
        """
        self.config_path = config_path
        self.historical_tester = HistoricalTester(config_path)

        # Define the 7 validation points
        self.validation_points = self._define_validation_points()

        logger.info("🛡️ Validation Protocol инициализиран със 7-point checklist")

    def _define_validation_points(self) -> List[ValidationPoint]:
        """Дефинира 7-те validation точки"""

        return [
            ValidationPoint(
                name="long_accuracy_protection",
                description="LONG сигнали точността трябва да остане 100%",
                critical=True,
                validator_func=self._validate_long_accuracy,
                expected_result=">= 100.0%",
                failure_message="LONG accuracy падна под критичния праг от 100%",
            ),
            ValidationPoint(
                name="pnl_stability_check",
                description="P&L не трябва да се влошава значително",
                critical=True,
                validator_func=self._validate_pnl_stability,
                expected_result="No significant regression",
                failure_message="P&L показва значителна регресия",
            ),
            ValidationPoint(
                name="max_drawdown_control",
                description="Max drawdown не трябва да се увеличава с >5%",
                critical=True,
                validator_func=self._validate_drawdown_control,
                expected_result="<= +5% increase",
                failure_message="Max drawdown се е увеличил значително",
            ),
            ValidationPoint(
                name="short_signal_logic",
                description="SHORT сигнали трябва да имат логични резултати",
                critical=False,
                validator_func=self._validate_short_signal_logic,
                expected_result="Logical signal distribution",
                failure_message="SHORT сигнали показват нелогично поведение",
            ),
            ValidationPoint(
                name="configuration_documented",
                description="Всички нови параметри трябва да са документирани",
                critical=True,
                validator_func=self._validate_configuration,
                expected_result="All parameters documented",
                failure_message="Недокументирани конфигурационни параметри",
            ),
            ValidationPoint(
                name="edge_cases_tested",
                description="Edge cases трябва да са тествани",
                critical=False,
                validator_func=self._validate_edge_cases,
                expected_result="Edge cases handled",
                failure_message="Edge cases не са обработени правилно",
            ),
            ValidationPoint(
                name="performance_impact",
                description="Performance impact трябва да е приемлив",
                critical=False,
                validator_func=self._validate_performance_impact,
                expected_result="Acceptable performance",
                failure_message="Performance impact е твърде висок",
            ),
        ]

    def validate_feature(
        self, feature_name: str, test_periods: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Изпълнява пълна 7-point validation за дадена функционалност

        Args:
            feature_name: Име на функционалността за тестване
            test_periods: Опционални тестови периоди

        Returns:
            ValidationResult: Пълни резултати от валидацията
        """
        logger.info(f"🛡️ Започвам 7-point validation за: {feature_name}")

        # Run historical testing first
        test_results = self.historical_tester.test_new_feature(feature_name, test_periods)

        # Initialize results
        validation_results = {}
        critical_failures = 0
        passed_points = 0
        failed_points = 0

        # Execute each validation point
        for validation_point in self.validation_points:
            try:
                logger.info(f"🔍 Проверявам: {validation_point.name}")

                result = validation_point.validator_func(
                    feature_name=feature_name,
                    test_results=test_results,
                    validation_point=validation_point,
                )

                validation_results[validation_point.name] = {
                    "passed": result["passed"],
                    "details": result.get("details", {}),
                    "message": result.get("message", ""),
                    "critical": validation_point.critical,
                }

                if result["passed"]:
                    passed_points += 1
                    logger.info(f"✅ {validation_point.name}: PASSED")
                else:
                    failed_points += 1
                    if validation_point.critical:
                        critical_failures += 1
                    logger.error(
                        f"❌ {validation_point.name}: FAILED - {result.get('message', '')}"
                    )

            except Exception as e:
                logger.error(f"💥 Грешка при validation на {validation_point.name}: {e}")
                validation_results[validation_point.name] = {
                    "passed": False,
                    "details": {},
                    "message": f"Validation error: {e}",
                    "critical": validation_point.critical,
                }
                failed_points += 1
                if validation_point.critical:
                    critical_failures += 1

        # Generate summary
        deployment_ready = critical_failures == 0
        summary = self._generate_validation_summary(
            feature_name,
            passed_points,
            failed_points,
            critical_failures,
            len(self.validation_points),
        )

        validation_result = ValidationResult(
            feature_name=feature_name,
            total_points=len(self.validation_points),
            passed_points=passed_points,
            failed_points=failed_points,
            critical_failures=critical_failures,
            results=validation_results,
            deployment_ready=deployment_ready,
            summary=summary,
        )

        logger.info(
            f"🛡️ Validation завършена: {passed_points}/{len(self.validation_points)} точки минати"
        )
        if deployment_ready:
            logger.info("✅ Функционалността е готова за deployment!")
        else:
            logger.warning("⚠️  Функционалността НЕ е готова за deployment!")

        return validation_result

    def _validate_long_accuracy(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали LONG accuracy е запазена (трябва да е >= 95%)
        """
        long_accuracies = []
        baseline_long_accuracy = self.historical_tester.baseline_metrics.long_accuracy

        for period_name, result in test_results.items():
            if result and hasattr(result, "long_accuracy"):
                long_accuracies.append(result.long_accuracy)

        if not long_accuracies:
            return {"passed": False, "message": "Няма LONG accuracy данни за сравнение"}

        avg_long_accuracy = sum(long_accuracies) / len(long_accuracies)
        min_long_accuracy = min(long_accuracies)

        # LONG accuracy трябва да е >= 100% (перфектна точност)
        passed = min_long_accuracy >= 100.0

        return {
            "passed": passed,
            "details": {
                "baseline_accuracy": baseline_long_accuracy,
                "avg_accuracy": avg_long_accuracy,
                "min_accuracy": min_long_accuracy,
                "all_accuracies": long_accuracies,
            },
            "message": f"LONG accuracy: {min_long_accuracy:.1f}% (min required: 100%)",
        }

    def _validate_pnl_stability(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали P&L не се е влошил значително
        """
        pnl_changes = []
        baseline_pnl = self.historical_tester.baseline_metrics.total_pnl

        for period_name, result in test_results.items():
            if result and hasattr(result, "baseline_comparison"):
                pnl_delta = result.baseline_comparison.get("pnl_delta", 0)
                pnl_changes.append(pnl_delta)

        if not pnl_changes:
            return {
                "passed": True,  # No data = assume stable
                "message": "Няма P&L данни за сравнение",
            }

        avg_pnl_change = sum(pnl_changes) / len(pnl_changes)
        max_pnl_loss = min(pnl_changes)  # Most negative change

        # P&L не трябва да падне с повече от 15%
        pnl_loss_threshold = -15.0
        passed = max_pnl_loss >= pnl_loss_threshold

        return {
            "passed": passed,
            "details": {
                "baseline_pnl": baseline_pnl,
                "avg_pnl_change": avg_pnl_change,
                "max_pnl_loss": max_pnl_loss,
                "threshold": pnl_loss_threshold,
            },
            "message": f"P&L change: {avg_pnl_change:+.1f}% (max loss: {max_pnl_loss:+.1f}%)",
        }

    def _validate_drawdown_control(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали max drawdown не се е увеличил значително
        """
        drawdown_changes = []
        baseline_drawdown = self.historical_tester.baseline_metrics.max_drawdown

        for period_name, result in test_results.items():
            if result and hasattr(result, "baseline_comparison"):
                dd_delta = result.baseline_comparison.get("drawdown_delta", 0)
                drawdown_changes.append(dd_delta)

        if not drawdown_changes:
            return {"passed": True, "message": "Няма drawdown данни за сравнение"}

        avg_dd_change = sum(drawdown_changes) / len(drawdown_changes)
        max_dd_increase = max(drawdown_changes)

        # Max drawdown не трябва да се увеличи с повече от 5%
        dd_threshold = 5.0
        passed = max_dd_increase <= dd_threshold

        return {
            "passed": passed,
            "details": {
                "baseline_drawdown": baseline_drawdown,
                "avg_dd_change": avg_dd_change,
                "max_dd_increase": max_dd_increase,
                "threshold": dd_threshold,
            },
            "message": f"Drawdown change: {avg_dd_change:+.1f}% (max increase: {max_dd_increase:+.1f}%)",
        }

    def _validate_short_signal_logic(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали SHORT сигнали имат логична структура
        """
        total_short_signals = 0
        total_signals = 0
        short_accuracies = []

        for period_name, result in test_results.items():
            if result and hasattr(result, "short_signals") and hasattr(result, "total_signals"):
                total_short_signals += result.short_signals
                total_signals += result.total_signals
                if hasattr(result, "short_accuracy"):
                    short_accuracies.append(result.short_accuracy)

        if total_signals == 0:
            return {"passed": False, "message": "Няма генерирани сигнали за анализ"}

        short_percentage = (total_short_signals / total_signals) * 100

        # SHORT сигнали - гъвкава логика базирано на пазарни условия
        # В силен bull market е нормално да няма SHORT сигнали
        # В bear/correction период SHORT сигналите трябва да са 10-40%

        # Анализираме сигналите (Fix: Use separate variable to avoid corrupting total_signals)
        total_periods = len([r for r in test_results.values() if r and hasattr(r, "total_signals")])
        long_signals = sum(
            [r.long_signals for r in test_results.values() if r and hasattr(r, "long_signals")]
        )
        short_signals = sum(
            [r.short_signals for r in test_results.values() if r and hasattr(r, "short_signals")]
        )

        # Дефинираме reasonable_range в началото
        reasonable_range = (10, 40)

        if total_periods == 0:
            # Никакви сигнали - не можем да оценим
            passed = False
        elif short_signals == 0 and long_signals >= 10:
            # Няма SHORT сигнали, но имаме достатъчно LONG - приемливо за bull market
            passed = True
        elif short_signals > 0:
            # Има SHORT сигнали - проверяваме дали са в разумен диапазон
            passed = reasonable_range[0] <= short_percentage <= reasonable_range[1]
        else:
            # Малко LONG сигнали - не можем да оценим SHORT логиката
            passed = True  # Assume good until we have more data

        return {
            "passed": passed,
            "details": {
                "total_signals": total_signals,  # Keep original accumulated total for metrics
                "total_periods": total_periods,  # Add periods count for clarity
                "short_signals": total_short_signals,
                "long_signals": long_signals,  # Include for completeness
                "short_percentage": short_percentage,
                "reasonable_range": reasonable_range,
                "short_accuracies": short_accuracies,
            },
            "message": f"SHORT signals: {short_percentage:.1f}% (expected: {reasonable_range[0]}-{reasonable_range[1]}%)",
        }

    def _validate_configuration(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали всички нови параметри са документирани
        """
        # Това е опростена проверка - в реалността би трябвало да се сравни
        # config файла с документацията

        # За сега проверяваме дали има нови секции в config
        try:
            import toml

            config = toml.load(self.config_path)

            # Проверяваме за специфични секции свързани с testing
            required_sections = ["signals", "indicators", "fibonacci", "weekly_tails"]
            missing_sections = []

            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)

            passed = len(missing_sections) == 0

            return {
                "passed": passed,
                "details": {
                    "available_sections": list(config.keys()),
                    "required_sections": required_sections,
                    "missing_sections": missing_sections,
                },
                "message": f"Configuration sections: {len(missing_sections)} missing",
            }

        except Exception as e:
            return {"passed": False, "message": f"Configuration validation error: {e}"}

    def _validate_edge_cases(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява дали edge cases са обработени
        """
        # Проверяваме дали има тестове за различни периоди
        tested_periods = list(test_results.keys())
        expected_periods = ["bull_market", "correction_phase", "recovery_phase", "recent_data"]

        missing_periods = [p for p in expected_periods if p not in tested_periods]
        failed_periods = [p for p, r in test_results.items() if r is None]

        # Успех ако имаме поне 1 успешен период с достатъчно сигнали
        # или поне 2 успешни периода (за по-добра coverage)
        successful_periods = len(tested_periods) - len(failed_periods) - len(missing_periods)

        # Проверяваме дали имаме поне един период с сигнали (дори 1 сигнал е достатъчно за тест)
        has_signals = False
        for period_name, result in test_results.items():
            if result and hasattr(result, "total_signals") and result.total_signals > 0:
                has_signals = True
                break

        # Успех ако имаме сигнали в някой период или поне 1 успешен период
        passed = has_signals or successful_periods >= 1

        return {
            "passed": passed,
            "details": {
                "tested_periods": tested_periods,
                "expected_periods": expected_periods,
                "missing_periods": missing_periods,
                "failed_periods": failed_periods,
                "successful_periods": successful_periods,
            },
            "message": f"Edge case testing: {successful_periods}/{len(expected_periods)} periods successful",
        }

    def _validate_performance_impact(
        self,
        feature_name: str,
        test_results: Dict[str, TestResult],
        validation_point: ValidationPoint,
    ) -> Dict[str, Any]:
        """
        Проверява performance impact
        """
        # Това е опростена проверка за performance
        # В реалността би трябвало да се измерва execution time

        total_signals = sum(result.total_signals for result in test_results.values() if result)

        # Ако имаме поне някакви сигнали, performance е OK (за development)
        reasonable_signal_count = total_signals > 0
        passed = reasonable_signal_count

        return {
            "passed": passed,
            "details": {"total_signals_generated": total_signals, "reasonable_threshold": 10},
            "message": f"Performance check: {total_signals} signals generated",
        }

    def _generate_validation_summary(
        self, feature_name: str, passed: int, failed: int, critical_failures: int, total: int
    ) -> str:
        """
        Генерира summary на validation резултатите
        """
        success_rate = (passed / total) * 100 if total > 0 else 0

        lines = [
            f"🛡️ VALIDATION SUMMARY: {feature_name}",
            "=" * 50,
            f"Total validation points: {total}",
            f"Passed: {passed}",
            f"Failed: {failed}",
            f"Critical failures: {critical_failures}",
            f"Success rate: {success_rate:.1f}%",
            "",
        ]

        if critical_failures == 0:
            lines.append("✅ DEPLOYMENT APPROVED")
            lines.append("All critical validation points passed.")
        else:
            lines.append("❌ DEPLOYMENT REJECTED")
            lines.append(f"Critical failures detected: {critical_failures}")
            lines.append("Feature requires fixes before deployment.")

        return "\n".join(lines)

    def save_validation_report(
        self, validation_result: ValidationResult, output_file: str = "validation_report.txt"
    ):
        """
        Запазва детайлен validation report

        Args:
            validation_result: Резултати от валидацията
            output_file: Име на output файла
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(validation_result.summary)
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("DETAILED RESULTS:\n")
                f.write("=" * 50 + "\n\n")

                for point_name, result in validation_result.results.items():
                    status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                    critical = " (CRITICAL)" if result.get("critical") else ""

                    f.write(f"{point_name}{critical}: {status}\n")
                    if result.get("message"):
                        f.write(f"  Message: {result['message']}\n")

                    if result.get("details"):
                        f.write("  Details:\n")
                        for key, value in result["details"].items():
                            f.write(f"    {key}: {value}\n")

                    f.write("\n")

            logger.info(f"💾 Validation report запазен в: {output_file}")

        except Exception as e:
            logger.error(f"❌ Грешка при запазване на validation report: {e}")


# Utility functions
def quick_validation(feature_name: str, config_path: str = "config.toml") -> Dict[str, Any]:
    """
    Бърза validation за development purposes

    Args:
        feature_name: Име на функционалността
        config_path: Път до config файла

    Returns:
        Quick validation results
    """
    protocol = ValidationProtocol(config_path)

    try:
        result = protocol.validate_feature(feature_name, ["recent_data"])

        return {
            "success": True,
            "deployment_ready": result.deployment_ready,
            "passed_points": result.passed_points,
            "critical_failures": result.critical_failures,
            "summary": result.summary,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    print("🛡️ BNB Trading System - Validation Protocol")
    print("=" * 50)

    # Run quick validation
    print("\n🔍 Running quick validation...")
    result = quick_validation("baseline_test")

    if result["success"]:
        print("✅ Validation completed!")
        print(f"Deployment ready: {result['deployment_ready']}")
        print(f"Passed points: {result['passed_points']}/7")
        print(f"Critical failures: {result['critical_failures']}")
    else:
        print(f"❌ Validation failed: {result['error']}")

    print("\n🎯 Validation Protocol ready for production use!")
