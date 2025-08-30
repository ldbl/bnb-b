"""Main smart SHORT signal generator (refactored thin layer)."""

import logging
from typing import Any

import pandas as pd

from ...core.models import ShortSignalCandidate
from .confluence import validate_short_confluence
from .market_regime import MarketRegimeDetector
from .risk_filters import apply_risk_filters

logger = logging.getLogger(__name__)


class SmartShortSignalGenerator:
    """
    Основен клас за интелигентна SHORT сигнал генерация (refactored)
    """

    trend_analyzer: Any  # TrendAnalyzer or None

    def __init__(self, config: dict[str, Any]):
        """
        Инициализация на Smart SHORT Generator

        Args:
            config: Конфигурация от config.toml
        """
        self.config = config
        self.market_detector = MarketRegimeDetector()

        # НОВИ: Интеграция с Enhanced Trend Analyzer
        try:
            from ...trend_analyzer import TrendAnalyzer

            self.trend_analyzer = TrendAnalyzer(config)
            self.use_enhanced_regime_detection = True
            logger.info("✅ Enhanced TrendAnalyzer интегриран успешно")
        except ImportError as e:
            logger.warning(f"⚠️ Enhanced TrendAnalyzer не може да се зареди: {e}")
            self.trend_analyzer = None
            self.use_enhanced_regime_detection = False

        # SHORT specific thresholds from config
        short_config = config.get("smart_short", {})
        self.short_thresholds = {
            "min_ath_distance_pct": short_config.get("min_ath_distance_pct", 5.0),
            "max_ath_distance_pct": short_config.get("max_ath_distance_pct", 25.0),
            "min_confluence_score": short_config.get("min_confluence_score", 3),
            "min_risk_reward_ratio": short_config.get("min_risk_reward_ratio", 1.5),
            "max_stop_loss_pct": short_config.get("max_stop_loss_pct", 5.0),
            "bull_market_block": short_config.get("bull_market_block", True),
        }

    def generate_smart_short_signal(
        self,
        daily_df: pd.DataFrame,
        weekly_df: pd.DataFrame | None = None,
        analyses: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Main method for generating smart SHORT signals (thin orchestration layer).

        Args:
            daily_df: Daily OHLCV data
            weekly_df: Weekly OHLCV data (optional)
            analyses: Pre-computed analyses from other modules

        Returns:
            Dict with SHORT signal or HOLD recommendation
        """
        try:
            # Step 1: Detect market regime
            if weekly_df is None:
                # Use daily_df as fallback if weekly not available
                market_regime = self.market_detector.detect_market_regime(
                    daily_df, daily_df
                )
            else:
                market_regime = self.market_detector.detect_market_regime(
                    daily_df, weekly_df
                )

            # Step 2: Early exit if SHORT signals blocked
            if not market_regime.get("short_signals_allowed", False):
                return {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": f"SHORT signals blocked in {market_regime.get('regime')} market",
                    "market_regime": market_regime["regime"],
                }

            # Step 3: Find SHORT setup opportunities
            candidates = self._find_short_setups(daily_df, weekly_df, market_regime)

            if not candidates:
                return {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": "No valid SHORT setups found",
                    "market_regime": market_regime["regime"],
                }

            # Step 4: Select best candidate
            best_candidate = max(
                candidates, key=lambda x: (x.confidence, x.confluence_score)
            )

            # Step 5: Apply final risk filters
            signal_dict = {
                "timestamp": best_candidate.timestamp,
                "price": best_candidate.price,
                "confidence": best_candidate.confidence,
                "reasons": best_candidate.reasons,
                "confluence_score": best_candidate.confluence_score,
                "risk_reward_ratio": best_candidate.risk_reward_ratio,
                "stop_loss_price": best_candidate.stop_loss_price,
                "take_profit_price": best_candidate.take_profit_price,
                "market_regime": best_candidate.market_regime,
                "ath_distance_pct": best_candidate.ath_distance_pct,
            }
            market_data = {"market_regime": market_regime}
            filtered_signal = apply_risk_filters(signal_dict, market_data, self.config)

            if filtered_signal.get("blocked", False):
                return {
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": filtered_signal.get(
                        "block_reason", "Risk filter blocked signal"
                    ),
                    "market_regime": market_regime["regime"],
                }

            # Return validated SHORT signal
            return {
                "signal": "SHORT",
                "confidence": best_candidate.confidence,
                "price": best_candidate.price,
                "stop_loss": best_candidate.stop_loss_price,
                "take_profit": best_candidate.take_profit_price,
                "reasons": best_candidate.reasons,
                "risk_reward_ratio": best_candidate.risk_reward_ratio,
                "market_regime": market_regime["regime"],
                "confluence_score": best_candidate.confluence_score,
            }

        except Exception as e:
            logger.exception(f"Грешка при smart SHORT generation: {e}")
            return {
                "signal": "HOLD",
                "confidence": 0.0,
                "reason": f"Error: {e!s}",
                "error": True,
            }

    def _find_short_setups(
        self,
        daily_df: pd.DataFrame,
        weekly_df: pd.DataFrame | None,
        market_regime: dict[str, Any],
    ) -> list[ShortSignalCandidate]:
        """Find potential SHORT setup opportunities."""
        candidates = []

        try:
            # Look for SHORT setups in last 5 days
            for i in range(max(0, len(daily_df) - 5), len(daily_df)):
                setup = {
                    "index": i,
                    "timestamp": daily_df.index[i],
                    "price": daily_df["Close"].iloc[i],
                }

                # Validate confluence for this setup
                candidate = validate_short_confluence(
                    setup, daily_df, weekly_df, market_regime
                )

                if (
                    candidate
                    and candidate.confluence_score
                    >= self.short_thresholds["min_confluence_score"]
                ):
                    candidates.append(candidate)

        except Exception as e:
            logger.exception(f"Грешка при търсене на SHORT setups: {e}")

        return candidates
