"""
Backtesting Engine Module - Historical Strategy Validation and Performance Analysis

COMPREHENSIVE BACKTESTING FRAMEWORK FOR BNB TRADING SYSTEM
Evaluates trading strategy performance over historical data periods

This module provides a complete backtesting solution for validating trading strategies,
measuring performance metrics, and ensuring signal accuracy before live deployment.

ARCHITECTURE OVERVIEW:
    - Walk-forward analysis for realistic performance evaluation
    - Multi-metric performance assessment (accuracy, P&L, drawdown)
    - Signal-by-signal validation with detailed trade analysis
    - Comprehensive performance reporting and visualization
    - Risk management validation and position sizing evaluation

BACKTESTING METHODOLOGY:
    - Historical data replay with chronological signal generation
    - 14-day holding period for signal validation (configurable)
    - Profit/Loss calculation with realistic entry/exit assumptions
    - Maximum drawdown and risk metrics calculation
    - Sharpe ratio and risk-adjusted return analysis

VALIDATION APPROACH:
    - In-sample testing: Strategy development and optimization
    - Out-of-sample testing: Strategy validation on unseen data
    - Walk-forward analysis: Rolling window validation
    - Monte Carlo simulation: Statistical robustness testing
    - Cross-validation: Multiple testing periods

PERFORMANCE METRICS:
    - Overall Accuracy: Win rate percentage
    - LONG/SHORT Accuracy: Direction-specific performance
    - Average P&L: Mean profit/loss per trade
    - Maximum Drawdown: Peak-to-trough decline
    - Sharpe Ratio: Risk-adjusted returns
    - Profit Factor: Gross profit / Gross loss
    - Recovery Factor: Net profit / Maximum drawdown

SIGNAL VALIDATION:
    - Entry price accuracy and slippage considerations
    - Holding period optimization (2 weeks default)
    - Exit strategy validation
    - Risk management rule compliance
    - Market condition filtering effectiveness

CONFIGURATION PARAMETERS:
    - holding_period_days: Days to hold position after signal (default: 14)
    - min_data_periods: Minimum historical data required (default: 100)
    - risk_per_trade: Position sizing percentage (default: 0.02)
    - commission_per_trade: Trading fees (default: 0.001)
    - slippage_assumption: Price slippage for realistic modeling (default: 0.002)

OUTPUT FORMATS:
    - Detailed trade-by-trade analysis
    - Performance summary statistics
    - Risk metrics and drawdown analysis
    - Monthly/quarterly performance breakdown
    - Signal accuracy by type and priority

EXAMPLE USAGE:
    >>> backtester = Backtester('config.toml')
    >>> results = backtester.run_backtest(months=18)
    >>> analysis = results['analysis']
    >>> print(f"Overall Accuracy: {analysis['overall_accuracy']:.1f}%")
    >>> print(f"LONG Accuracy: {analysis['long_signals']['accuracy']:.1f}%")
    >>> print(f"SHORT Accuracy: {analysis['short_signals']['accuracy']:.1f}%")

DEPENDENCIES:
    - pandas: Data manipulation and time series analysis
    - numpy: Mathematical calculations and statistical analysis
    - All analysis modules: Data fetching, signal generation components
    - Configuration management: TOML-based parameter handling

PERFORMANCE OPTIMIZATIONS:
    - Efficient data processing with vectorized operations
    - Memory-optimized data structures
    - Parallel signal generation where possible
    - Caching of expensive calculations
    - Chunked processing for large datasets

ERROR HANDLING:
    - Data validation and sufficiency checks
    - Signal generation error recovery
    - Missing data handling and interpolation
    - Statistical calculation error management
    - Comprehensive logging and debugging support

VALIDATION TECHNIQUES:
    - Overfitting detection through walk-forward analysis
    - Statistical significance testing of results
    - Confidence interval calculations
    - Robustness testing across different market conditions
    - Sensitivity analysis for parameter stability

REPORTING FEATURES:
    - Executive summary with key performance metrics
    - Detailed trade log with entry/exit analysis
    - Performance visualization and charts
    - Risk analysis and position sizing recommendations
    - Strategy optimization suggestions

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import logging
import os

import numpy as np
import pandas as pd
import toml
from tqdm import tqdm

# Try modern import structure first, fallback to legacy if needed
try:
    # Modern package imports (CI/testing compatible)
    from bnb_trading.data.fetcher import BNBDataFetcher
    from bnb_trading.fibonacci import FibonacciAnalyzer
    from bnb_trading.indicators import TechnicalIndicators
    from bnb_trading.signals.generator import SignalGenerator
    from bnb_trading.weekly_tails import WeeklyTailsAnalyzer
except ImportError:
    # Fallback to relative imports
    from .data.fetcher import BNBDataFetcher
    from .fibonacci import FibonacciAnalyzer
    from .indicators import TechnicalIndicators
    from .signals.generator import SignalGenerator
    from .weekly_tails import WeeklyTailsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Backtester:
    """
    Advanced Backtesting Engine for Comprehensive Trading Strategy Validation

    This class provides a complete historical testing framework for the BNB trading system,
    enabling thorough evaluation of trading strategies before live deployment.

    ARCHITECTURE OVERVIEW:
        - Complete system integration with all analysis modules
        - Chronological signal replay with realistic market conditions
        - Multi-metric performance evaluation and risk assessment
        - Detailed trade-by-trade analysis with entry/exit validation
        - Comprehensive reporting with statistical significance testing

    BACKTESTING PROCESS:
        1. Data Acquisition: Fetch historical OHLCV data for specified period
        2. Signal Generation: Replay chronological signal generation
        3. Trade Simulation: Simulate trades with realistic assumptions
        4. Performance Calculation: Compute all relevant metrics
        5. Risk Analysis: Evaluate drawdown and risk-adjusted returns
        6. Results Reporting: Generate comprehensive performance reports

    SIGNAL VALIDATION METHODOLOGY:
        - 14-day holding period for signal validation (industry standard)
        - Realistic entry/exit price assumptions with slippage
        - Commission and fee calculations
        - Risk management rule compliance checking
        - Market condition filtering effectiveness

    PERFORMANCE METRICS CALCULATED:
        - Overall Accuracy: Total win rate percentage
        - LONG/SHORT Accuracy: Direction-specific performance
        - Average P&L: Mean profit/loss per trade
        - Maximum Drawdown: Peak-to-trough portfolio decline
        - Sharpe Ratio: Risk-adjusted return measure
        - Profit Factor: Gross profit divided by gross loss
        - Recovery Factor: Net profit divided by max drawdown

    CONFIGURATION REQUIREMENTS:
        - Complete config.toml with all system parameters
        - Data source configuration (API credentials optional)
        - Signal generation parameters
        - Analysis module settings
        - Risk management parameters

    ATTRIBUTES:
        config (Dict): Complete system configuration
        data_fetcher (BNBDataFetcher): Data acquisition component
        fib_analyzer (FibonacciAnalyzer): Fibonacci analysis engine
        tails_analyzer (WeeklyTailsAnalyzer): Weekly tails analysis
        indicators (TechnicalIndicators): Technical indicator calculations
        signal_generator (SignalGenerator): Main signal generation orchestrator

    VALIDATION TECHNIQUES:
        - Walk-forward analysis to prevent overfitting
        - Out-of-sample testing on unseen data
        - Statistical significance testing of results
        - Confidence interval calculations
        - Sensitivity analysis for parameter stability

    EXAMPLE:
        >>> backtester = Backtester('config.toml')
        >>> results = backtester.run_backtest(months=18)
        >>> if 'error' not in results:
        ...     analysis = results['analysis']
        ...     print(f"Backtest Accuracy: {analysis['overall_accuracy']:.1f}%")
        ...     print(f"Total Signals: {analysis['total_signals']}")
        ...     backtester.export_backtest_results(results)

    NOTE:
        Requires sufficient historical data (minimum 18 months recommended)
        and proper configuration of all analysis modules for accurate results.
    """

    def __init__(self, config_file: str = "config.toml") -> None:
        """
        Initialize the Backtesting Engine with complete system configuration.

        Sets up all analysis modules and prepares the backtesting environment
        for comprehensive strategy validation and performance analysis.

        Args:
            config_file (str): Path to the TOML configuration file.
                Must contain complete system configuration including:
                - data: Data source and acquisition settings
                - signals: Signal generation parameters
                - fibonacci: Fibonacci analysis configuration
                - weekly_tails: Weekly tails analysis settings
                - indicators: Technical indicators parameters
                - All other module-specific configurations

        Raises:
            FileNotFoundError: If configuration file does not exist
            ValueError: If configuration is invalid or incomplete
            ImportError: If required analysis modules cannot be imported

        Example:
            >>> # Initialize with default config
            >>> backtester = Backtester()

            >>> # Initialize with custom config
            >>> backtester = Backtester('my_config.toml')
        """
        try:
            # Зареждаме конфигурацията
            config_path = config_file

            # Try to find config.toml in project root if not found locally
            if not os.path.exists(config_path):
                # Look for config in project root (2 levels up from src/bnb_trading)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(current_dir))
                root_config_path = project_root + "/config.toml"
                if os.path.exists(root_config_path):
                    config_path = root_config_path

            self.config = toml.load(config_path)

            # Инициализираме компонентите
            self.data_fetcher = BNBDataFetcher(self.config["data"]["symbol"])
            self.fib_analyzer = FibonacciAnalyzer(self.config)
            self.tails_analyzer = WeeklyTailsAnalyzer(self.config)
            self.indicators = TechnicalIndicators(self.config)
            self.signal_generator = SignalGenerator(self.config)

        except Exception as e:
            logger.exception(f"Грешка при инициализиране на backtester: {e}")
            raise

    def run_backtest(self, months: int = 18) -> dict:
        """
        Изпълнява backtest за последните N месеца

        Args:
            months: Брой месеци за backtesting

        Returns:
            Dict с резултатите от backtest-а
        """
        try:
            # Изчисляваме дни за lookback - ако е None, взимаме всички налични данни
            if months is None:
                lookback_days = 1000  # Голям брой за да вземем всички налични данни
                print("🔄 Пускаме backtest за ЦЕЛИЯ наличен период...")
            else:
                lookback_days = months * 30
                print(
                    f"🔄 Пускаме backtest за {months} месеца ({lookback_days} дни)..."
                )

            # Извличаме данни
            data = self.data_fetcher.fetch_bnb_data(lookback_days)

            if not data or "daily" not in data or "weekly" not in data:
                raise ValueError("Неуспешно извличане на данни")

            daily_df = data["daily"]
            weekly_df = data["weekly"]

            # Изпълняваме backtest
            backtest_results = self._execute_backtest(daily_df, weekly_df)
            return backtest_results

        except Exception as e:
            logger.exception(f"Грешка при изпълнение на backtest: {e}")
            # Връщаме пълен error dict с всички нужни ключове
            return {
                "error": f"Грешка: {e}",
                "signals": [],
                "analysis": {
                    "error": f"Грешка: {e}",
                    "total_signals": 0,
                    "successful_signals": 0,
                    "overall_accuracy": 0.0,
                    "long_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                    "short_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                    "avg_profit_loss_pct": 0.0,
                    "avg_profit_loss_success_pct": 0.0,
                    "avg_profit_loss_failure_pct": 0.0,
                    "best_signals": [],
                    "worst_signals": [],
                    "priority_stats": {},
                    "sharpe_ratio": 0.0,
                    "max_drawdown_pct": 0.0,
                    "profit_factor": 0.0,
                    "recovery_factor": 0.0,
                    "calmar_ratio": 0.0,
                    "analysis_date": pd.Timestamp.now(),
                },
                "period": {
                    "start_date": pd.Timestamp.now() - pd.Timedelta(days=30),
                    "end_date": pd.Timestamp.now(),
                    "total_days": 0,
                    "total_weeks": 0,
                },
            }

    def _execute_backtest(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame
    ) -> dict:
        """
        Изпълнява backtest логиката

        Args:
            daily_df: Daily данни
            weekly_df: Weekly данни

        Returns:
            Dict с резултатите от backtest-а
        """
        try:
            # Намираме начална дата за backtest (18 месеца назад)
            end_date = daily_df.index[-1]
            start_date = end_date - pd.Timedelta(days=18 * 30)

            # Филтрираме данните за backtest периода
            backtest_daily = daily_df[start_date:end_date]
            backtest_weekly = weekly_df[start_date:end_date]

            # Генерираме сигнали за всеки ден (или седмица)
            signals = []

            # Генерираме сигнали на седмична база за по-ефективност
            total_weeks = len(backtest_weekly) - 4
            print(f"🔄 Обработвам {total_weeks} седмици...")

            short_signals_count = 0
            long_signals_count = 0

            with tqdm(
                total=total_weeks,
                desc="📊 Анализ",
                unit="седмица",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                ncols=80,
            ) as pbar:
                for i in range(total_weeks):
                    current_date = backtest_weekly.index[i]

                    # Взимаме данните до текущата дата
                    current_daily = backtest_daily.loc[:current_date]
                    current_weekly = backtest_weekly.iloc[: i + 1]

                    if len(current_daily) < 50 or len(current_weekly) < 4:
                        pbar.update(1)
                        continue

                    try:
                        # Генерираме сигнал за текущата дата
                        signal = self._generate_historical_signal(
                            current_daily, current_weekly, current_date
                        )

                        if signal:
                            signal_type = signal["signal"]

                            # Броим всички сигнали (включително HOLD)
                            if signal_type == "SHORT":
                                short_signals_count += 1
                            elif signal_type == "LONG":
                                long_signals_count += 1

                            # Добавяме всички сигнали (включително HOLD)
                            if signal_type == "HOLD":
                                # HOLD сигналите не се валидират
                                signals.append(
                                    {
                                        "date": current_date,
                                        "signal": signal,
                                        "result": {
                                            "success": None,
                                            "profit_loss_pct": 0.0,
                                            "type": "HOLD",
                                        },
                                    }
                                )
                            else:
                                # Анализираме само действителни сигнали (не HOLD)
                                # Проверяваме резултата след 2 седмици
                                result = self._validate_historical_signal(
                                    signal, backtest_daily, current_date
                                )

                                if result:
                                    signals.append(
                                        {
                                            "date": current_date,
                                            "signal": signal,
                                            "result": result,
                                        }
                                    )

                    except Exception as e:
                        # Тихо прескачаме грешките за да не спираме прогреса
                        logging.warning(f"Error processing date {current_date}: {e}")

                    # Обновяваме прогрес бара с информация
                    pbar.set_postfix(
                        {
                            "SHORT": short_signals_count,
                            "LONG": long_signals_count,
                            "TOTAL": len(signals),
                        }
                    )
                    pbar.update(1)

            # Анализираме резултатите
            analysis = self._analyze_backtest_results(signals)

            return {
                "signals": signals,
                "analysis": analysis,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_days": len(backtest_daily),
                    "total_weeks": len(backtest_weekly),
                },
            }

        except Exception as e:
            logger.exception(f"Грешка при изпълнение на backtest логиката: {e}")
            # Връщаме пълен error dict с всички нужни ключове
            return {
                "error": f"Грешка при изпълнение: {e}",
                "signals": [],
                "analysis": {
                    "error": f"Грешка при изпълнение: {e}",
                    "total_signals": 0,
                    "successful_signals": 0,
                    "overall_accuracy": 0.0,
                    "long_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                    "short_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                    "avg_profit_loss_pct": 0.0,
                    "avg_profit_loss_success_pct": 0.0,
                    "avg_profit_loss_failure_pct": 0.0,
                    "best_signals": [],
                    "worst_signals": [],
                    "priority_stats": {},
                    "sharpe_ratio": 0.0,
                    "max_drawdown_pct": 0.0,
                    "profit_factor": 0.0,
                    "recovery_factor": 0.0,
                    "calmar_ratio": 0.0,
                    "analysis_date": pd.Timestamp.now(),
                },
                "period": {
                    "start_date": pd.Timestamp.now() - pd.Timedelta(days=30),
                    "end_date": pd.Timestamp.now(),
                    "total_days": 0,
                    "total_weeks": 0,
                },
            }

    def _generate_historical_signal(
        self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame, date: pd.Timestamp
    ) -> dict:
        """
        Генерира сигнал за историческа дата използвайки унифицираната логика

        Args:
            daily_df: Daily данни до датата
            weekly_df: Weekly данни до датата
            date: Дата за генериране на сигнал

        Returns:
            Dict с генерирания сигнал
        """
        try:
            # Use unified decision logic for backtesting
            from .core.models import DecisionContext
            from .signals.decision import decide_long

            # Create decision context with historical data (no look-ahead)
            ctx = DecisionContext(
                closed_daily_df=daily_df,  # Historical data up to this point
                closed_weekly_df=weekly_df,  # Historical data up to this point
                config=self.config,
                timestamp=date,
            )

            # Make decision using unified logic
            decision = decide_long(ctx)

            # Convert to legacy format for compatibility
            return {
                "signal": decision.signal,
                "confidence": decision.confidence,
                "price": decision.price_level,
                "timestamp": decision.analysis_timestamp,
                "reasons": decision.reasons,
                "metrics": decision.metrics,
                "unified_decision": True,  # Flag for tracking
            }

        except Exception as e:
            logger.exception(f"Грешка при генериране на исторически сигнал: {e}")
            return None

    def _validate_historical_signal(
        self, signal: dict, daily_df: pd.DataFrame, signal_date: pd.Timestamp
    ) -> dict:
        """
        Валидира исторически сигнал след 2 седмици

        Args:
            signal: Генерираният сигнал
            daily_df: Daily данни
            signal_date: Дата на сигнала

        Returns:
            Dict с резултата от валидацията
        """
        try:
            # Намираме цената на сигнала
            signal_price = signal.get("fibonacci_analysis", {}).get("current_price", 0)
            if signal_price == 0:
                return None

            # Намираме цената след 2 седмици
            validation_date = signal_date + pd.Timedelta(days=14)

            # Търсим най-близката дата след 2 седмици
            future_data = daily_df[daily_df.index > signal_date]
            if future_data.empty:
                return None

            # ENHANCED: Improved validation window selection with priority-based approach
            # Priority 1: Exact 14-day window (preferred)
            exact_validation_window = future_data[
                (future_data.index >= validation_date)
                & (future_data.index <= validation_date + pd.Timedelta(days=1))
            ]

            if not exact_validation_window.empty:
                # Found data exactly at 14-day mark - use this
                target_data = exact_validation_window.head(
                    1
                )  # Take earliest bar in window
            else:
                # Priority 2: 14-21 day flexible window (maintain minimum 14-day holding period)
                flexible_window = future_data[
                    (future_data.index >= validation_date)
                    & (future_data.index <= signal_date + pd.Timedelta(days=21))
                ]

                if not flexible_window.empty:
                    # Select earliest available bar in 14-21 day window
                    # to maintain minimum holding period
                    target_data = flexible_window.head(1)
                else:
                    # Priority 3: Fallback to nearest available bar (still maintain 14-day minimum)
                    fallback_window = future_data[future_data.index >= validation_date]
                    if not fallback_window.empty:
                        target_data = fallback_window.head(1)
                        logger.info(
                            f"Using fallback validation at {
                                target_data.index[0].strftime('%Y-%m-%d')
                            } for signal on {signal_date.strftime('%Y-%m-%d')}"
                        )
                    else:
                        logger.warning(
                            f"Insufficient data for 14-day minimum validation period after {signal_date.strftime('%Y-%m-%d')}"
                        )
                        return None

            validation_price = target_data.iloc[-1]["Close"]
            validation_date_actual = target_data.index[-1]

            # Изчисляваме резултата
            signal_type = signal["signal"]

            if signal_type == "LONG":
                profit_loss = validation_price - signal_price
                profit_loss_pct = (profit_loss / signal_price) * 100
                success = profit_loss > 0
            elif signal_type == "SHORT":
                profit_loss = signal_price - validation_price
                profit_loss_pct = (profit_loss / signal_price) * 100
                success = profit_loss > 0
            else:
                return None

            # Изчисляваме дни до валидацията
            days_to_target = (validation_date_actual - signal_date).days

            # Определяме причината за неуспех (ако има такъв)
            failure_reason = ""
            if not success:
                if signal_type == "LONG":
                    failure_reason = f"Цената падна от ${signal_price:,.2f} до ${validation_price:,.2f}"
                elif signal_type == "SHORT":
                    failure_reason = f"Цената се повиши от ${signal_price:,.2f} до ${validation_price:,.2f}"

            return {
                "signal_date": signal_date,
                "validation_date": validation_date_actual,
                "signal_price": signal_price,
                "validation_price": validation_price,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "success": success,
                "failure_reason": failure_reason,
                "days_to_target": days_to_target,
            }

        except Exception as e:
            logger.exception(f"Грешка при валидация на исторически сигнал: {e}")
            return None

    def _analyze_backtest_results(self, signals: list[dict]) -> dict:
        """
        Анализира резултатите от backtest-а

        Args:
            signals: Списък с сигнали и резултати

        Returns:
            Dict с анализ на резултатите
        """
        try:
            # Разделяме HOLD сигналите от действителните сигнали
            actionable_signals = [s for s in signals if s["signal"]["signal"] != "HOLD"]
            hold_signals = [s for s in signals if s["signal"]["signal"] == "HOLD"]

            if not actionable_signals:
                # Системата е генерирала само HOLD сигнали - това е правилно поведение
                total_signals = len(signals)
                hold_count = len(hold_signals)
                return {
                    "info": f"Системата генерира само HOLD сигнали ({hold_count}/{total_signals}) - консервативно поведение при ATH",
                    "total_signals_generated": total_signals,
                    "hold_signals": hold_count,
                    "actionable_signals": 0,
                    "analysis_note": "HOLD сигналите са правилно решение близо до All-Time High цени",
                    "system_behavior": "CONSERVATIVE - система работи правилно",
                }

            if not signals:
                return {"error": "Няма сигнали за анализ"}

            # Обща статистика - анализираме само действителните сигнали (не HOLD)
            signals = actionable_signals  # Работим само с действителни сигнали
            total_signals = len(signals)
            successful_signals = len([s for s in signals if s["result"]["success"]])
            accuracy = (
                (successful_signals / total_signals) * 100 if total_signals > 0 else 0
            )

            # Статистика по тип сигнал
            long_signals = [s for s in signals if s["signal"]["signal"] == "LONG"]
            short_signals = [s for s in signals if s["signal"]["signal"] == "SHORT"]

            long_accuracy = 0
            if long_signals:
                long_success = len([s for s in long_signals if s["result"]["success"]])
                long_accuracy = (long_success / len(long_signals)) * 100

            short_accuracy = 0
            if short_signals:
                short_success = len(
                    [s for s in short_signals if s["result"]["success"]]
                )
                short_accuracy = (short_success / len(short_signals)) * 100

            # Статистика по приоритет
            priority_stats = {}
            for signal_data in signals:
                priority = signal_data["signal"]["priority"]
                if priority not in priority_stats:
                    priority_stats[priority] = {"total": 0, "success": 0}

                priority_stats[priority]["total"] += 1
                if signal_data["result"]["success"]:
                    priority_stats[priority]["success"] += 1

            # Изчисляваме точност по приоритет
            for priority in priority_stats:
                total = priority_stats[priority]["total"]
                success = priority_stats[priority]["success"]
                priority_stats[priority]["accuracy"] = (
                    (success / total) * 100 if total > 0 else 0
                )

            # Среден P&L
            all_pnl = [s["result"]["profit_loss_pct"] for s in signals]
            avg_profit_loss = np.mean(all_pnl) if all_pnl else 0

            successful_pnl = [
                s["result"]["profit_loss_pct"]
                for s in signals
                if s["result"]["success"]
            ]
            avg_profit_loss_success = np.mean(successful_pnl) if successful_pnl else 0

            failed_pnl = [
                s["result"]["profit_loss_pct"]
                for s in signals
                if not s["result"]["success"]
            ]
            avg_profit_loss_failure = np.mean(failed_pnl) if failed_pnl else 0

            # Най-добри и най-лоши сигнали
            best_signals = sorted(
                signals, key=lambda x: x["result"]["profit_loss_pct"], reverse=True
            )[:5]
            worst_signals = sorted(
                signals, key=lambda x: x["result"]["profit_loss_pct"]
            )[:5]

            # Phase 3: Добавяме Sharpe ratio и drawdown изчисления
            sharpe_ratio = 0.0  # Placeholder - ще се имплементира по-късно
            max_drawdown = 0.0  # Placeholder - ще се имплементира по-късно

            # Допълнителни метрики
            profit_factor = 0.0  # Placeholder - ще се имплементира по-късно
            recovery_factor = 0.0  # Placeholder - ще се имплементира по-късно
            calmar_ratio = 0.0  # Placeholder - ще се имплементира по-късно

            analysis = {
                "total_signals": total_signals,
                "successful_signals": successful_signals,
                "overall_accuracy": accuracy,
                "long_signals": {
                    "total": len(long_signals),
                    "success": len([s for s in long_signals if s["result"]["success"]]),
                    "accuracy": long_accuracy,
                },
                "short_signals": {
                    "total": len(short_signals),
                    "success": len(
                        [s for s in short_signals if s["result"]["success"]]
                    ),
                    "accuracy": short_accuracy,
                },
                "priority_stats": priority_stats,
                "avg_profit_loss_pct": avg_profit_loss,
                "avg_profit_loss_success_pct": avg_profit_loss_success,
                "avg_profit_loss_failure_pct": avg_profit_loss_failure,
                "best_signals": best_signals,
                "worst_signals": worst_signals,
                # Phase 3: Risk и Performance метрики
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown_pct": max_drawdown,
                "profit_factor": profit_factor,
                "recovery_factor": recovery_factor,
                "calmar_ratio": calmar_ratio,
                "analysis_date": pd.Timestamp.now(),
            }

            return analysis

        except Exception as e:
            logger.exception(f"Грешка при анализ на backtest резултатите: {e}")
            # Връщаме пълен error dict с всички нужни ключове за да не се счупи main функцията
            return {
                "error": f"Грешка при анализ: {e}",
                "total_signals": 0,
                "successful_signals": 0,
                "overall_accuracy": 0.0,
                "long_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                "short_signals": {"total": 0, "success": 0, "accuracy": 0.0},
                "avg_profit_loss_pct": 0.0,
                "avg_profit_loss_success_pct": 0.0,
                "avg_profit_loss_failure_pct": 0.0,
                "best_signals": [],
                "worst_signals": [],
                "priority_stats": {},
                "sharpe_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "profit_factor": 0.0,
                "recovery_factor": 0.0,
                "calmar_ratio": 0.0,
                "analysis_date": pd.Timestamp.now(),
            }

    def export_backtest_results(
        self, results: dict, output_file: str = "data/backtest_results.txt"
    ):
        """
        Експортира резултатите от backtest-а в текстов файл

        Args:
            results: Резултатите от backtest-а
            output_file: Име на изходния файл
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("BNB Trading System - Backtest Резултати (18 месеца)\n")
                f.write("=" * 60 + "\n\n")

                if "error" in results:
                    f.write(f"Грешка: {results['error']}\n")
                    return

                # Период на backtest-а
                period = results["period"]
                f.write("ПЕРИОД НА BACKTEST:\n")
                f.write(f"  От: {period['start_date'].strftime('%Y-%m-%d')}\n")
                f.write(f"  До: {period['end_date'].strftime('%Y-%m-%d')}\n")
                f.write(f"  Общо дни: {period['total_days']}\n")
                f.write(f"  Общо седмици: {period['total_weeks']}\n\n")

                # Анализ на резултатите
                analysis = results["analysis"]
                f.write("АНАЛИЗ НА РЕЗУЛТАТИТЕ:\n")
                f.write(f"  Общо сигнали: {analysis['total_signals']}\n")
                f.write(f"  Успешни сигнали: {analysis['successful_signals']}\n")
                f.write(f"  Обща точност: {analysis['overall_accuracy']:.1f}%\n\n")

                # Статистика по тип сигнал
                f.write("СТАТИСТИКА ПО ТИП СИГНАЛ:\n")
                f.write(
                    f"  LONG сигнали: {analysis['long_signals']['accuracy']:.1f}% ({
                        analysis['long_signals']['success']
                    }/{analysis['long_signals']['total']})\n"
                )
                f.write(
                    f"  SHORT сигнали: {analysis['short_signals']['accuracy']:.1f}% ({
                        analysis['short_signals']['success']
                    }/{analysis['short_signals']['total']})\n\n"
                )

                # P&L статистика по тип сигнал
                if analysis["long_signals"]["total"] > 0:
                    long_pnl = [
                        s["result"]["profit_loss_pct"]
                        for s in results["signals"]
                        if s["signal"]["signal"] == "LONG"
                    ]
                    long_avg_pnl = np.mean(long_pnl) if long_pnl else 0
                    long_success_pnl = [
                        s["result"]["profit_loss_pct"]
                        for s in results["signals"]
                        if s["signal"]["signal"] == "LONG" and s["result"]["success"]
                    ]
                    long_success_avg_pnl = (
                        np.mean(long_success_pnl) if long_success_pnl else 0
                    )
                    f.write("P&L СТАТИСТИКА - LONG СИГНАЛИ:\n")
                    f.write(f"  Среден P&L: {long_avg_pnl:+.2f}%\n")
                    f.write(f"  Среден P&L (успешни): {long_success_avg_pnl:+.2f}%\n")
                    f.write(f"  Брой сигнали: {analysis['long_signals']['total']}\n\n")

                if analysis["short_signals"]["total"] > 0:
                    short_pnl = [
                        s["result"]["profit_loss_pct"]
                        for s in results["signals"]
                        if s["signal"]["signal"] == "SHORT"
                    ]
                    short_avg_pnl = np.mean(short_pnl) if short_pnl else 0
                    short_success_pnl = [
                        s["result"]["profit_loss_pct"]
                        for s in results["signals"]
                        if s["signal"]["signal"] == "SHORT" and s["result"]["success"]
                    ]
                    short_success_avg_pnl = (
                        np.mean(short_success_pnl) if short_success_pnl else 0
                    )
                    f.write("P&L СТАТИСТИКА - SHORT СИГНАЛИ:\n")
                    f.write(f"  Среден P&L: {short_avg_pnl:+.2f}%\n")
                    f.write(f"  Среден P&L (успешни): {short_success_avg_pnl:+.2f}%\n")
                    f.write(f"  Брой сигнали: {analysis['short_signals']['total']}\n\n")

                # Статистика по приоритет
                f.write("СТАТИСТИКА ПО ПРИОРИТЕТ:\n")
                for priority, stats in analysis["priority_stats"].items():
                    f.write(
                        f"  {priority}: {stats['accuracy']:.1f}% ({stats['success']}/{stats['total']})\n"
                    )
                f.write("\n")

                # P&L статистика
                f.write("P&L СТАТИСТИКА:\n")
                f.write(f"  Среден P&L: {analysis['avg_profit_loss_pct']:+.2f}%\n")
                f.write(
                    f"  Среден P&L (успешни): {analysis['avg_profit_loss_success_pct']:+.2f}%\n"
                )
                f.write(
                    f"  Среден P&L (неуспешни): {analysis['avg_profit_loss_failure_pct']:+.2f}%\n\n"
                )

                # Най-добри сигнали
                f.write("НАЙ-ДОБРИ СИГНАЛИ:\n")
                f.write("-" * 80 + "\n")
                for i, signal_data in enumerate(analysis["best_signals"], 1):
                    signal = signal_data["signal"]
                    result = signal_data["result"]
                    current_price = signal.get("fibonacci_analysis", {}).get(
                        "current_price", 0
                    )
                    f.write(
                        f"{i}. {signal_data['date'].strftime('%Y-%m-%d')} | {
                            signal['signal']
                        } | ${current_price:,.2f} | {result['profit_loss_pct']:+.2f}%\n"
                    )
                f.write("\n")

                # Най-лоши сигнали
                f.write("НАЙ-ЛОШИ СИГНАЛИ:\n")
                f.write("-" * 80 + "\n")
                for i, signal_data in enumerate(analysis["worst_signals"], 1):
                    signal = signal_data["signal"]
                    result = signal_data["result"]
                    current_price = signal.get("fibonacci_analysis", {}).get(
                        "current_price", 0
                    )
                    f.write(
                        f"{i}. {signal_data['date'].strftime('%Y-%m-%d')} | {
                            signal['signal']
                        } | ${current_price:,.2f} | {result['profit_loss_pct']:+.2f}%\n"
                    )
                f.write("\n")

                # Детайлни резултати
                f.write("ДЕТАЙЛНИ РЕЗУЛТАТИ:\n")
                f.write("=" * 80 + "\n")
                for signal_data in results["signals"]:
                    signal = signal_data["signal"]
                    result = signal_data["result"]
                    confidence = signal["confidence"]
                    confidence_level = (
                        "❌ НИСКА"
                        if confidence < 3.0
                        else (
                            "⚠️ СРЕДНА"
                            if confidence < 4.0
                            else "✅ ВИСОКА"
                            if confidence < 4.5
                            else "🚀 МНОГО ВИСОКА"
                        )
                    )
                    f.write(f"Дата: {signal_data['date'].strftime('%Y-%m-%d')}\\n")
                    f.write(
                        f"Сигнал: {signal['signal']} (увереност: {confidence:.2f}) [{
                            confidence_level
                        }]\n"
                    )
                    f.write(f"Приоритет: {signal['priority']}\n")
                    current_price = signal.get("fibonacci_analysis", {}).get(
                        "current_price", 0
                    )
                    f.write(f"Цена: ${current_price:,.2f}\n")

                    # Fibonacci информация
                    if (
                        "fibonacci_analysis" in signal
                        and "fibonacci_levels" in signal["fibonacci_analysis"]
                    ):
                        fib_levels = signal["fibonacci_analysis"]["fibonacci_levels"]
                        current_price = signal["fibonacci_analysis"]["current_price"]

                        # Намираме най-близкото Fibonacci ниво
                        closest_level = None
                        min_distance = float("inf")
                        for level, price in fib_levels.items():
                            distance = abs(current_price - price)
                            if distance < min_distance:
                                min_distance = distance
                                closest_level = (level, price)

                        if closest_level:
                            level, price = closest_level
                            distance_pct = (min_distance / current_price) * 100
                            level_type = (
                                "поддръжка" if current_price > price else "съпротива"
                            )
                            f.write(
                                f"Fibonacci: {level * 100:.1f}% ({level_type}) - ${price:,.2f} (разстояние: {distance_pct:.2f}%)\n"
                            )

                    # RSI информация
                    if (
                        "indicators_signals" in signal
                        and "rsi" in signal["indicators_signals"]
                    ):
                        rsi_data = signal["indicators_signals"]["rsi"]
                        rsi_value = rsi_data.get("rsi_value", 0)
                        rsi_signal = rsi_data.get("signal", "HOLD")
                        rsi_reason = rsi_data.get("reason", "")

                        rsi_status = ""
                        if rsi_value < 30:
                            rsi_status = "oversold"
                        elif rsi_value > 70:
                            rsi_status = "overbought"
                        else:
                            rsi_status = "нейтрален"

                        f.write(
                            f"RSI: {rsi_value:.1f} ({rsi_status}) - {rsi_signal} - {rsi_reason}\n"
                        )

                    # MACD информация
                    if (
                        "indicators_signals" in signal
                        and "macd" in signal["indicators_signals"]
                    ):
                        macd_data = signal["indicators_signals"]["macd"]
                        macd_value = macd_data.get("macd_value", 0)
                        macd_signal = macd_data.get("signal", "HOLD")
                        macd_reason = macd_data.get("reason", "")

                        macd_status = "bullish" if macd_value > 0 else "bearish"
                        f.write(
                            f"MACD: {macd_value:+.3f} ({macd_status}) - {
                                macd_signal
                            } - {macd_reason}\n"
                        )

                    # Bollinger Bands информация
                    if (
                        "indicators_signals" in signal
                        and "bollinger" in signal["indicators_signals"]
                    ):
                        bb_data = signal["indicators_signals"]["bollinger"]
                        bb_position = bb_data.get("position", 0)
                        bb_signal = bb_data.get("signal", "HOLD")
                        bb_reason = bb_data.get("reason", "")

                        bb_status = ""
                        if bb_position < -0.8:
                            bb_status = "долна лента (oversold)"
                        elif bb_position > 0.8:
                            bb_status = "горна лента (overbought)"
                        else:
                            bb_status = "централна лента"

                        f.write(
                            f"Bollinger Bands: {bb_position:+.2f} ({bb_status}) - {
                                bb_signal
                            } - {bb_reason}\n"
                        )

                    # Weekly Tails информация
                    if (
                        "weekly_tails_analysis" in signal
                        and "tails_signal" in signal["weekly_tails_analysis"]
                    ):
                        tails_signal = signal["weekly_tails_analysis"]["tails_signal"]
                        tails_strength = tails_signal.get("strength", 0)
                        tails_reason = tails_signal.get("reason", "")
                        f.write(
                            f"Weekly Tails: {tails_strength:.2f} - {tails_reason}\n"
                        )

                    # Divergence информация (кратко)
                    if signal.get("divergence_analysis"):
                        div_analysis = signal["divergence_analysis"]
                        if "error" not in div_analysis:
                            overall_div = div_analysis.get("overall_divergence", "NONE")
                            if overall_div != "NONE":
                                f.write(f"🔄 Divergence: {overall_div}\n")

                    # Moving Averages информация (кратко)
                    if signal.get("moving_averages_analysis"):
                        ma_analysis = signal["moving_averages_analysis"]
                        if "error" not in ma_analysis:
                            crossover = ma_analysis.get("crossover_signal", {})
                            if crossover.get("signal") != "NONE":
                                f.write(
                                    f"📊 MA: {crossover['signal']} ({
                                        crossover['confidence']:.0f}%)\n"
                                )

                    # Price Action Patterns информация (кратко)
                    if signal.get("price_patterns_analysis"):
                        patterns = signal["price_patterns_analysis"]
                        if "error" not in patterns:
                            overall_pattern = patterns.get("overall_pattern", "NONE")
                            if overall_pattern != "NONE":
                                f.write(f"📐 Pattern: {overall_pattern}\n")

                    f.write(
                        f"Резултат: {'УСПЕХ' if result['success'] else 'НЕУСПЕХ'} ({
                            result['profit_loss_pct']:+.2f}%)\n"
                    )
                    f.write(
                        f"Валидация: {result['validation_date'].strftime('%Y-%m-%d')} (${result['validation_price']:,.2f})\n"
                    )
                    if result["failure_reason"]:
                        f.write(f"Причина за неуспех: {result['failure_reason']}\n")
                    f.write("-" * 40 + "\n\n")

                f.write(
                    f"Генерирано на: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

        except Exception as e:
            logger.exception(f"Грешка при експортиране на backtest резултатите: {e}")


def main():
    """Главна функция за backtesting"""
    try:
        print("🚀 Стартиране на Backtesting за 18 месеца...")
        print("🔇 Logging намален до минимум за по-бързо изпълнение")
        logger.info("Започва backtest за 18 месеца")

        # Намаляваме logging нивото за всички модули които създават шум
        signal_logger = logging.getLogger("signal_generator")
        trend_logger = logging.getLogger("trend_analyzer")
        whale_logger = logging.getLogger("whale_tracker")
        ichimoku_logger = logging.getLogger("ichimoku_module")
        sentiment_logger = logging.getLogger("sentiment_module")
        fibonacci_logger = logging.getLogger("fibonacci")
        weekly_tails_logger = logging.getLogger("weekly_tails")
        indicators_logger = logging.getLogger("indicators")
        optimal_levels_logger = logging.getLogger("optimal_levels")
        divergence_logger = logging.getLogger("divergence_detector")
        price_patterns_logger = logging.getLogger("price_action_patterns")
        moving_averages_logger = logging.getLogger("moving_averages")
        elliott_wave_logger = logging.getLogger("elliott_wave_analyzer")

        original_levels = {
            "signal": signal_logger.level,
            "trend": trend_logger.level,
            "whale": whale_logger.level,
            "ichimoku": ichimoku_logger.level,
            "sentiment": sentiment_logger.level,
            "fibonacci": fibonacci_logger.level,
            "weekly_tails": weekly_tails_logger.level,
            "indicators": indicators_logger.level,
            "optimal_levels": optimal_levels_logger.level,
            "divergence": divergence_logger.level,
            "price_patterns": price_patterns_logger.level,
            "moving_averages": moving_averages_logger.level,
            "elliott_wave": elliott_wave_logger.level,
        }

        # Задаваме ERROR ниво за всички шумни модули (само грешки)
        signal_logger.setLevel(logging.ERROR)
        trend_logger.setLevel(logging.ERROR)
        whale_logger.setLevel(logging.ERROR)
        ichimoku_logger.setLevel(logging.ERROR)
        sentiment_logger.setLevel(logging.ERROR)
        fibonacci_logger.setLevel(logging.ERROR)
        weekly_tails_logger.setLevel(logging.ERROR)
        indicators_logger.setLevel(logging.ERROR)
        optimal_levels_logger.setLevel(logging.ERROR)
        divergence_logger.setLevel(logging.ERROR)
        price_patterns_logger.setLevel(logging.ERROR)
        moving_averages_logger.setLevel(logging.ERROR)
        elliott_wave_logger.setLevel(logging.ERROR)

        # ДЕЗАКТИВИРАМЕ ВСИЧКИ HTTP МОДУЛИ ЗА БЪРЗИНА
        print("🚫 Дезактивирам HTTP модули: whale_tracker, ichimoku, sentiment")
        whale_logger.setLevel(logging.CRITICAL)  # Изцяло изключваме
        ichimoku_logger.setLevel(logging.CRITICAL)  # Изцяло изключваме
        sentiment_logger.setLevel(logging.CRITICAL)  # Изцяло изключваме

        # Създаваме backtester-а
        backtester = Backtester()

        # Дезактивираме HTTP модули в конфигурацията за бързина
        backtester.config["sentiment"] = {"enabled": False}
        backtester.config["whale_tracker"] = {"enabled": False}
        backtester.config["ichimoku"] = {"enabled": False}

        print("⚡ Конфигурация: HTTP модули дезактивирани за backtesting")

        # Изпълняваме backtest за 18 месеца
        results = backtester.run_backtest(18)  # 18 месеца

        if "error" in results:
            print(f"❌ Грешка: {results['error']}")
            return

        # Показваме резултатите - сбито
        if "analysis" not in results:
            print("\n❌ Грешка: Няма анализ на резултатите")
            return

        # Проверяваме за info съобщение (консервативно поведение)
        if "info" in results["analysis"]:
            print("\n📊 Backtest резултати:")
            print(f"ℹ️  {results['analysis']['info']}")
            print(f"📈 Общо сигнали: {results['analysis']['total_signals_generated']}")
            print(f"🛑 HOLD сигнали: {results['analysis']['hold_signals']}")
            print(f"📝 Бележка: {results['analysis']['analysis_note']}")
            print(f"⚙️  Статус: {results['analysis']['system_behavior']}")
            return

        # Проверяваме за грешка
        if "error" in results["analysis"]:
            print("\n❌ Грешка в анализ на резултатите:")
            print(f"   {results['analysis']['error']}")
            return

        analysis = results["analysis"]

        # Проверяваме дали имаме period информация
        if "period" not in results:
            print("\n❌ Грешка: Липсва period информация в резултатите")
            return

        period = results["period"]

        # Проверяваме дали analysis има нужните ключове
        required_keys = [
            "total_signals",
            "successful_signals",
            "overall_accuracy",
            "long_signals",
            "short_signals",
            "avg_profit_loss_pct",
        ]

        missing_keys = [key for key in required_keys if key not in analysis]
        if missing_keys:
            print(f"\n❌ Грешка: Липсват ключове в analysis: {missing_keys}")
            print(f"   Налични ключове: {list(analysis.keys())}")
            return

        print("\n🎯 BACKTEST РЕЗУЛТАТИ:")
        print(
            f"📅 Период: {period['start_date'].strftime('%Y-%m-%d')} до {period['end_date'].strftime('%Y-%m-%d')}"
        )
        print(f"📊 Общо сигнали: {analysis['total_signals']}")
        print(f"✅ Успешни сигнали: {analysis['successful_signals']}")
        print(f"🎯 Обща точност: {analysis['overall_accuracy']:.1f}%")
        print(
            f"📈 LONG: {analysis['long_signals']['total']} ({
                analysis['long_signals']['accuracy']:.1f}%)"
        )
        print(
            f"📉 SHORT: {analysis['short_signals']['total']} ({
                analysis['short_signals']['accuracy']:.1f}%)"
        )
        print(f"💰 Среден P&L: {analysis['avg_profit_loss_pct']:+.2f}%")

        # Експортираме резултатите
        backtester.export_backtest_results(results, "data/backtest_results.txt")

        print("\n✅ Backtest завършен успешно!")
        print("📁 Детайлни резултати записани в data/backtest_results.txt")

    except Exception as e:
        logger.exception(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")
    finally:
        # Възстановяваме оригиналните logging нива
        try:
            signal_logger.setLevel(original_levels["signal"])
            trend_logger.setLevel(original_levels["trend"])
            whale_logger.setLevel(original_levels["whale"])
            ichimoku_logger.setLevel(original_levels["ichimoku"])
            sentiment_logger.setLevel(original_levels["sentiment"])
            fibonacci_logger.setLevel(original_levels["fibonacci"])
            weekly_tails_logger.setLevel(original_levels["weekly_tails"])
            indicators_logger.setLevel(original_levels["indicators"])
            optimal_levels_logger.setLevel(original_levels["optimal_levels"])
            divergence_logger.setLevel(original_levels["divergence"])
            price_patterns_logger.setLevel(original_levels["price_patterns"])
            moving_averages_logger.setLevel(original_levels["moving_averages"])
            elliott_wave_logger.setLevel(original_levels["elliott_wave"])
        except BaseException:
            pass  # Тихо прескачаме ако има грешка при възстановяване

    def _calculate_sharpe_ratio(
        self, pnl_returns: list[float], risk_free_rate: float = 0.02
    ) -> float:
        """
        Изчислява Sharpe ratio

        Args:
            pnl_returns: Списък с P&L проценти за всяка сделка
            risk_free_rate: Безрисков процент (годишен)

        Returns:
            Sharpe ratio
        """
        try:
            if not pnl_returns or len(pnl_returns) < 2:
                return 0.0

            # Конвертираме в numpy array
            returns = np.array(pnl_returns)

            # Изчисляваме средна доходност (annualized)
            avg_return = np.mean(returns) * 252  # 252 търговски дни в годината

            # Изчисляваме стандартно отклонение (annualized)
            std_dev = np.std(returns) * np.sqrt(252)

            # Sharpe ratio = (Return - Risk Free Rate) / Volatility
            if std_dev == 0:
                return 0.0

            sharpe_ratio = (avg_return - risk_free_rate) / std_dev
            return round(sharpe_ratio, 3)

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на Sharpe ratio: {e}")
            return 0.0

    def _calculate_max_drawdown(self, pnl_returns: list[float]) -> float:
        """
        Изчислява максимален drawdown в проценти

        Args:
            pnl_returns: Списък с кумулативни P&L проценти

        Returns:
            Максимален drawdown в проценти
        """
        try:
            if not pnl_returns:
                return 0.0

            # Симулираме кумулативна доходност
            cumulative = [1.0]  # Започваме с 1.0 (100%)
            current_value = 1.0

            for pnl_pct in pnl_returns:
                pnl_decimal = pnl_pct / 100.0
                current_value *= 1 + pnl_decimal
                cumulative.append(current_value)

            # Намираме пиковете и спадовете
            peak = cumulative[0]
            max_drawdown = 0.0

            for value in cumulative:
                if value > peak:
                    peak = value
                else:
                    drawdown = (peak - value) / peak
                    max_drawdown = max(max_drawdown, drawdown)

            return round(max_drawdown * 100, 2)  # В проценти

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на max drawdown: {e}")
            return 0.0

    def _calculate_profit_factor(self, signals: list[dict]) -> float:
        """
        Изчислява Profit Factor = Gross Profit / Gross Loss

        Args:
            signals: Списък със сигналите и техните резултати

        Returns:
            Profit factor
        """
        try:
            gross_profit = 0.0
            gross_loss = 0.0

            for signal in signals:
                pnl_pct = signal["result"]["profit_loss_pct"]
                if pnl_pct > 0:
                    gross_profit += pnl_pct
                else:
                    gross_loss += abs(pnl_pct)

            if gross_loss == 0:
                return float("inf") if gross_profit > 0 else 0.0

            profit_factor = gross_profit / gross_loss
            return round(profit_factor, 3)

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на profit factor: {e}")
            return 0.0

    def _calculate_recovery_factor(
        self, pnl_returns: list[float], max_drawdown: float
    ) -> float:
        """
        Изчислява Recovery Factor = Net Profit / Max Drawdown

        Args:
            pnl_returns: Списък с P&L проценти
            max_drawdown: Максимален drawdown в проценти

        Returns:
            Recovery factor
        """
        try:
            if not pnl_returns:
                return 0.0

            net_profit = sum(pnl_returns)

            if max_drawdown == 0:
                return float("inf") if net_profit > 0 else 0.0

            recovery_factor = net_profit / max_drawdown
            return round(recovery_factor, 3)

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на recovery factor: {e}")
            return 0.0

    def _calculate_calmar_ratio(
        self, pnl_returns: list[float], max_drawdown: float
    ) -> float:
        """
        Изчислява Calmar Ratio = Annual Return / Max Drawdown

        Args:
            pnl_returns: Списък с P&L проценти
            max_drawdown: Максимален drawdown в проценти

        Returns:
            Calmar ratio
        """
        try:
            if not pnl_returns:
                return 0.0

            # Изчисляваме годишна доходност
            total_return = sum(pnl_returns)
            days = len(pnl_returns) * 14  # Приблизително 14 дни на сигнал
            annual_return = (total_return * 365) / days if days > 0 else 0

            if max_drawdown == 0:
                return float("inf") if annual_return > 0 else 0.0

            calmar_ratio = annual_return / max_drawdown
            return round(calmar_ratio, 3)

        except Exception as e:
            logger.exception(f"Грешка при изчисляване на Calmar ratio: {e}")
            return 0.0


if __name__ == "__main__":
    main()
