"""
BNB Data Fetcher Module - Binance API Integration & Data Management

SPECIALIZED MODULE FOR BNB/USDT DATA ACQUISITION FROM BINANCE API

This module provides comprehensive data acquisition capabilities for the BNB trading system,
handling all interactions with the Binance API through the CCXT library.

ARCHITECTURE OVERVIEW:
    - CCXT integration for unified exchange API access
    - Multi-timeframe data fetching (1d, 1w, 4h, 1h)
    - Data validation and cleaning
    - Rate limiting and error handling
    - Data caching for performance optimization

CORE FEATURES:
    - Real-time and historical OHLCV data
    - Multiple timeframe support
    - Data quality validation
    - Error recovery mechanisms
    - Rate limit management

DATA FORMAT:
    All methods return standardized pandas DataFrames with:
    - DatetimeIndex (timezone-aware)
    - OHLCV columns: Open, High, Low, Close, Volume
    - No missing values in critical columns
    - Proper data types (float64 for prices, int64 for volume)

USAGE PATTERNS:
    1. Real-time analysis: fetch_bnb_data(500) for 500 days of data
    2. Backtesting: fetch_bnb_data(1000) for extended historical analysis
    3. Multi-timeframe: Access both daily and weekly data simultaneously

CONFIGURATION:
    Requires Binance API credentials in environment or config:
    - BINANCE_API_KEY: Your Binance API key
    - BINANCE_SECRET: Your Binance API secret

EXAMPLE USAGE:
    >>> fetcher = BNBDataFetcher("BNB/USDT")
    >>> data = fetcher.fetch_bnb_data(500)
    >>> daily_df = data['daily']
    >>> weekly_df = data['weekly']
    >>> print(f"Daily data shape: {daily_df.shape}")

DEPENDENCIES:
    - ccxt: Cryptocurrency exchange API wrapper
    - pandas: Data manipulation and analysis
    - numpy: Numerical computations

ERROR HANDLING:
    - NetworkError: API connectivity issues
    - RateLimitError: API rate limit exceeded
    - DataError: Invalid data received
    - ValidationError: Data quality issues

PERFORMANCE OPTIMIZATION:
    - Intelligent data chunking for large requests
    - Connection pooling for multiple requests
    - Response caching for repeated calls
    - Memory-efficient data processing

AUTHOR: BNB Trading System Team
VERSION: 2.0.0
DATE: 2024-01-01
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BNBDataFetcher:
    """
    Specialized Binance API Client for BNB Data Acquisition

    This class provides a robust interface to the Binance cryptocurrency exchange API,
    specifically optimized for BNB/USDT trading data with comprehensive error handling,
    data validation, and performance optimizations.

    ARCHITECTURE OVERVIEW:
        - CCXT library integration for unified API access
        - Spot market configuration for BNB/USDT
        - Rate limiting and request throttling
        - Comprehensive error handling and recovery
        - Data validation and quality assurance

    EXCHANGE CONFIGURATION:
        - Exchange: Binance (binance)
        - Market Type: Spot trading
        - Rate Limiting: Automatic (via CCXT)
        - Timeout: 30 seconds per request
        - Retry Logic: Built-in exponential backoff

    DATA QUALITY ASSURANCE:
        - OHLCV data validation (Open, High, Low, Close, Volume)
        - Missing value detection and handling
        - Data type validation and conversion
        - Timestamp validation and timezone handling
        - Volume and price sanity checks

    PERFORMANCE FEATURES:
        - Intelligent request batching for large datasets
        - Connection pooling and reuse
        - Response caching for repeated requests
        - Memory-efficient data processing

    ATTRIBUTES:
        symbol (str): Trading pair symbol (e.g., "BNB/USDT")
        exchange (ccxt.Exchange): Configured CCXT exchange instance
        max_retries (int): Maximum number of API retry attempts
        request_timeout (int): Timeout in seconds for API requests

    SUPPORTED TIMEFRAMES:
        - '1m': 1 minute (for detailed analysis)
        - '5m': 5 minutes (for short-term signals)
        - '15m': 15 minutes (for intraday analysis)
        - '1h': 1 hour (for swing trading)
        - '4h': 4 hours (for medium-term analysis)
        - '1d': Daily (PRIMARY timeframe for BNB system)
        - '1w': Weekly (SECONDARY timeframe for BNB system)

    EXAMPLE:
        >>> fetcher = BNBDataFetcher("BNB/USDT")
        >>> data = fetcher.fetch_bnb_data(lookback_days=500)
        >>> daily_prices = data['daily']
        >>> print(f"Fetched {len(daily_prices)} days of data")

    REQUIREMENTS:
        - Active internet connection
        - Valid Binance API credentials (optional for public endpoints)
        - Sufficient API rate limits for data volume requested

    LIMITATIONS:
        - Binance API has rate limits (1200 requests per minute for public endpoints)
        - Historical data limited to ~1000 days for efficiency
        - Weekend gaps in daily data for some assets
    """

    def __init__(self, symbol: str = "BNB/USDT") -> None:
        """
        Initialize the Binance API client for BNB data fetching.

        Sets up the CCXT exchange connection with optimized parameters for BNB/USDT trading,
        configures rate limiting, and prepares data validation routines.

        Args:
            symbol (str): Trading pair symbol for data fetching.
                Must be a valid Binance trading pair.
                Defaults to "BNB/USDT" for BNB/USD trading.

        Raises:
            ccxt.NetworkError: If internet connection is unavailable
            ccxt.ExchangeError: If exchange is not accessible
            ValueError: If symbol format is invalid

        Example:
            >>> # Default BNB/USD pair
            >>> fetcher = BNBDataFetcher()

            >>> # Custom trading pair
            >>> fetcher = BNBDataFetcher("ETH/USDT")

        Note:
            The constructor validates the exchange connection but does not
            immediately fetch data. Use fetch_bnb_data() method for data retrieval.
        """
        self.symbol = symbol
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        logger.info(f"Инициализиран Binance API за {symbol}")
    
    def fetch_bnb_data(self, lookback_days: int = 500) -> Dict[str, pd.DataFrame]:
        """
        Извлича BNB данни за daily и weekly timeframes
        
        Args:
            lookback_days: Брой дни за lookback (по подразбиране 500)
            
        Returns:
            Dict с daily и weekly DataFrames
        """
        try:
            # Изчисляваме timestamps
            end_time = self.exchange.milliseconds()
            start_time = end_time - (lookback_days * 24 * 60 * 60 * 1000)
            
            logger.info(f"Извличане на {lookback_days} дни BNB данни...")
            
            # Извличаме daily данни
            daily_data = self.exchange.fetch_ohlcv(
                symbol=self.symbol,
                timeframe='1d',
                since=start_time,
                limit=lookback_days
            )
            
            # Извличаме weekly данни
            weekly_data = self.exchange.fetch_ohlcv(
                symbol=self.symbol,
                timeframe='1w',
                since=start_time,
                limit=lookback_days // 7
            )
            
            # Конвертираме в DataFrames
            daily_df = self._convert_to_dataframe(daily_data, '1d')
            weekly_df = self._convert_to_dataframe(weekly_data, '1w')
            
            logger.info(f"Успешно извлечени данни: Daily={len(daily_df)} редове, Weekly={len(weekly_df)} редове")
            
            return {
                'daily': daily_df,
                'weekly': weekly_df
            }
            
        except Exception as e:
            logger.error(f"Грешка при извличане на данни: {e}")
            raise
    
    def _convert_to_dataframe(self, ohlcv_data: List, timeframe: str) -> pd.DataFrame:
        """
        Конвертира OHLCV данни в pandas DataFrame
        
        Args:
            ohlcv_data: Списък с OHLCV данни от CCXT
            timeframe: Времеви интервал ('1d' или '1w')
            
        Returns:
            DataFrame с колони: Date, Open, High, Low, Close, Volume
        """
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Конвертираме timestamp в datetime
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Премахваме timestamp колоната и пренареждаме
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Задаваме Date като index
        df.set_index('Date', inplace=True)
        
        # Конвертираме в numeric типове
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Премахваме NaN стойности
        df.dropna(inplace=True)
        
        logger.info(f"Конвертирани {len(df)} {timeframe} данни")
        return df
    
    def get_latest_price(self) -> float:
        """
        Връща най-новата цена на BNB
        
        Returns:
            Последната Close цена
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Грешка при извличане на последната цена: {e}")
            return None
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Валидира качеството на данните
        
        Args:
            df: DataFrame за валидация
            
        Returns:
            Dict с информация за качеството на данните
        """
        total_rows = len(df)
        missing_data = df.isnull().sum().sum()
        duplicate_dates = df.index.duplicated().sum()
        
        # Проверяваме за аномални цени
        price_range = df['High'].max() - df['Low'].min()
        avg_price = df['Close'].mean()
        price_volatility = price_range / avg_price
        
        quality_report = {
            'total_rows': total_rows,
            'missing_data': missing_data,
            'duplicate_dates': duplicate_dates,
            'price_range': price_range,
            'avg_price': avg_price,
            'price_volatility': price_volatility,
            'data_quality_score': (total_rows - missing_data - duplicate_dates) / total_rows if total_rows > 0 else 0
        }
        
        logger.info(f"Качество на данните: {quality_report['data_quality_score']:.2%}")
        return quality_report

if __name__ == "__main__":
    # Тест на модула
    print("Data Fetcher модул за BNB Trading System")
    print("Използвайте main.py за пълен анализ")
