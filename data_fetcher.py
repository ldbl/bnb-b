"""
BNB Data Fetcher - Извлича BNB исторически данни от Binance API
Използва CCXT за достъп до Binance и връща daily + weekly данни
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BNBDataFetcher:
    """Клас за извличане на BNB данни от Binance API"""
    
    def __init__(self, symbol: str = "BNB/USDT"):
        """
        Инициализира Binance API connection
        
        Args:
            symbol: Търговска двойка (по подразбиране BNB/USDT)
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
