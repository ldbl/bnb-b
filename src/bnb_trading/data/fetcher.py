"""Main data fetching logic for BNB Trading System."""

import logging
import os
import sys

import ccxt
import pandas as pd

# For direct script execution - add src to path
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(os.path.dirname(current_dir))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from bnb_trading.core.exceptions import DataError, NetworkError

logger = logging.getLogger(__name__)


class BNBDataFetcher:
    """
    Specialized Binance API Client for BNB Data Acquisition

    This class provides a robust interface to the Binance cryptocurrency exchange API,
    specifically optimized for BNB/USDT trading data with comprehensive error handling,
    data validation, and performance optimizations.
    """

    def __init__(self, symbol: str = "BNB/USDT") -> None:
        """
        Initialize the Binance API client for BNB data fetching.

        Args:
            symbol (str): Trading pair symbol for data fetching.
                Must be a valid Binance trading pair.
                Defaults to "BNB/USDT" for BNB/USD trading.

        Raises:
            NetworkError: If internet connection is unavailable
            DataError: If symbol format is invalid
        """
        self.symbol = symbol
        try:
            self.exchange = ccxt.binance(
                {"enableRateLimit": True, "options": {"defaultType": "spot"}}
            )
            logger.info(f"Инициализиран Binance API за {symbol}")
        except Exception as e:
            raise NetworkError(f"Failed to initialize Binance API: {e}") from e

    def fetch_bnb_data(self, lookback_days: int = 500) -> dict[str, pd.DataFrame]:
        """
        Извлича BNB данни за daily и weekly timeframes

        Args:
            lookback_days: Брой дни за lookback (по подразбиране 500)

        Returns:
            Dict с daily и weekly DataFrames

        Raises:
            DataError: If data fetching fails
            NetworkError: If API connection fails
        """
        try:
            # Изчисляваме timestamps
            end_time = self.exchange.milliseconds()
            start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)

            logger.info(f"Извличане на {lookback_days} дни BNB данни...")

            # Извличаме daily данни (Binance limit е max 1000)
            daily_limit = min(lookback_days, 1000)
            daily_data = self.exchange.fetch_ohlcv(
                symbol=self.symbol, timeframe="1d", since=start_time, limit=daily_limit
            )

            # Извличаме weekly данни (Binance limit е max 1000)
            weekly_limit = min(lookback_days // 7, 1000)
            weekly_limit = max(weekly_limit, 1)

            weekly_data = self.exchange.fetch_ohlcv(
                symbol=self.symbol, timeframe="1w", since=start_time, limit=weekly_limit
            )

            # Конвертираме в DataFrames
            daily_df = self._convert_to_dataframe(daily_data, "1d")
            weekly_df = self._convert_to_dataframe(weekly_data, "1w")

            # Добавяме ATH анализ към daily данни
            from .validators import add_ath_analysis

            daily_df = add_ath_analysis(daily_df)

            logger.info(
                f"Успешно извлечени данни: Daily={len(daily_df)} редове, Weekly={
                    len(weekly_df)
                } редове"
            )

            return {"daily": daily_df, "weekly": weekly_df}

        except ccxt.NetworkError as e:
            raise NetworkError(f"Network error during data fetch: {e}") from e
        except Exception as e:
            raise DataError(f"Грешка при извличане на данни: {e}") from e

    def _convert_to_dataframe(self, ohlcv_data: list, timeframe: str) -> pd.DataFrame:
        """
        Конвертира OHLCV данни в pandas DataFrame

        Args:
            ohlcv_data: Списък с OHLCV данни от CCXT
            timeframe: Времеви интервал ('1d' или '1w')

        Returns:
            DataFrame с колони: Date, Open, High, Low, Close, Volume
        """
        if not ohlcv_data:
            raise DataError(f"No OHLCV data received for timeframe {timeframe}")

        df = pd.DataFrame(
            ohlcv_data, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"]
        )

        # Конвертираме timestamp в datetime
        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Премахваме timestamp колоната и пренареждаме
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

        # Задаваме Date като index
        df.set_index("Date", inplace=True)

        # Конвертираме в numeric типове
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Премахваме NaN стойности
        df.dropna(inplace=True)

        logger.info(f"Конвертирани {len(df)} {timeframe} данни")
        return df

    def get_latest_price(self) -> float:
        """
        Връща най-новата цена на BNB

        Returns:
            Последната Close цена

        Raises:
            NetworkError: If price fetch fails
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return float(ticker["last"])
        except ccxt.NetworkError as e:
            raise NetworkError(f"Network error fetching latest price: {e}") from e
        except Exception as e:
            raise DataError(f"Грешка при извличане на последната цена: {e}") from e
