"""Data validation functions for BNB Trading System."""

import logging
from typing import Any

import numpy as np
import pandas as pd

from bnb_trading.core.exceptions import DataError

logger = logging.getLogger(__name__)


def add_ath_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Добавя ATH (All Time High) анализ към DataFrame

    Args:
        df: DataFrame с OHLCV данни

    Returns:
        DataFrame с ATH колони
    """
    try:
        # Копираме DataFrame за да не променяме оригинала
        df = df.copy()

        # 🔥 НОВА ЛОГИКА: Rolling ATH от последните 180 дни за историческа точност
        # Това позволява SHORT сигнали в текущия пазарен контекст
        df["ATH"] = df["High"].rolling(window=180, min_periods=30).max()

        # Изчисляваме разстоянието до ATH в проценти
        df["ATH_Distance_Pct"] = ((df["ATH"] - df["Close"]) / df["ATH"]) * 100

        # Определяме дали цената е близо до ATH (< 10% - по-релакс за SHORT)
        df["Near_ATH"] = df["ATH_Distance_Pct"] < 10.0

        # ATH Proximity Score (по-висок = по-близо до ATH)
        df["ATH_Proximity_Score"] = np.where(
            df["ATH_Distance_Pct"] < 10.0,
            1.0 - (df["ATH_Distance_Pct"] / 10.0),  # 0.0 до 1.0
            0.0,
        )

        # ATH Trend - дали сме в ATH режим
        df["ATH_Trend"] = df["ATH"] == df["High"]

        logger.info(
            f"ROLLING ATH анализ добавен (180 дни). Текуща ATH: ${df['ATH'].iloc[-1]:.2f}"
        )
        logger.info(f"Разстояние до ATH: {df['ATH_Distance_Pct'].iloc[-1]:.2f}%")
        logger.info(f"Близо до ATH: {df['Near_ATH'].iloc[-1]}")

        return df

    except Exception as e:
        logger.exception(f"Грешка при ATH анализ: {e}")
        return df


def add_bnb_burn_columns(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Phase 1.5: Добавя BNB burn колони към DataFrame

    Добавя две нови колони:
    - burn_event: True ако датата е burn дата
    - burn_window: True ако датата е в burn прозорец (pre/post burn)

    Args:
        df: DataFrame с OHLCV данни
        config: Конфигурационен dict с bnb_burn секцията

    Returns:
        DataFrame с добавени burn колони
    """
    try:
        if df is None or df.empty:
            logger.warning("Празен DataFrame - няма да се добавят burn колони")
            return df

        # Копираме DataFrame за да не модифицираме оригинала
        df_with_burn = df.copy()

        # Инициализираме burn колоните с False
        df_with_burn["burn_event"] = False
        df_with_burn["burn_window"] = False

        # Извличаме burn дати
        burn_dates = _fetch_bnb_burn_dates(config)

        if not burn_dates:
            logger.info("Няма burn дати - всички burn колони остават False")
            return df_with_burn

        burn_config = config.get("bnb_burn", {})
        pre_burn_days = burn_config.get("pre_burn_window_days", 14)
        post_burn_days = burn_config.get("post_burn_window_days", 7)

        # За всяка burn дата маркираме съответните дати
        for burn_date in burn_dates:
            # Burn event - точната дата
            if burn_date in df_with_burn.index:
                df_with_burn.loc[burn_date, "burn_event"] = True

            # Burn window - преди и след burn
            burn_window_start = burn_date - pd.Timedelta(days=pre_burn_days)
            burn_window_end = burn_date + pd.Timedelta(days=post_burn_days)

            # Филтрираме датите в burn прозореца
            burn_window_mask = (df_with_burn.index >= burn_window_start) & (
                df_with_burn.index <= burn_window_end
            )
            df_with_burn.loc[burn_window_mask, "burn_window"] = True

            logger.info(
                f"Обработена burn дата {burn_date.strftime('%Y-%m-%d')}: "
                f"прозорец {burn_window_start.strftime('%Y-%m-%d')} до {burn_window_end.strftime('%Y-%m-%d')}"
            )

        # Статистика
        burn_events_count = df_with_burn["burn_event"].sum()
        burn_window_days = df_with_burn["burn_window"].sum()

        logger.info(
            f"Добавени burn колони: {burn_events_count} burn събития, "
            f"{burn_window_days} дни в burn прозорци"
        )

        return df_with_burn

    except Exception as e:
        logger.exception(f"Грешка при добавяне на burn колони: {e}")
        # Връщаме оригиналния DataFrame без burn колони при грешка
        return df


def validate_data_quality(df: pd.DataFrame) -> dict[str, Any]:
    """
    Валидира качеството на данните

    Args:
        df: DataFrame за валидация

    Returns:
        Dict с информация за качеството на данните
    """
    if df is None or df.empty:
        raise DataError("Empty or None DataFrame provided for validation")

    total_rows = len(df)
    missing_data = df.isnull().sum().sum()
    duplicate_dates = df.index.duplicated().sum()

    # Проверяваме за аномални цени
    price_range = df["High"].max() - df["Low"].min()
    avg_price = df["Close"].mean()
    price_volatility = price_range / avg_price

    quality_report = {
        "total_rows": total_rows,
        "missing_data": missing_data,
        "duplicate_dates": duplicate_dates,
        "price_range": price_range,
        "avg_price": avg_price,
        "price_volatility": price_volatility,
        "data_quality_score": (
            (total_rows - missing_data - duplicate_dates) / total_rows
            if total_rows > 0
            else 0
        ),
    }

    logger.info(f"Качество на данните: {quality_report['data_quality_score']:.2%}")
    return quality_report


def _fetch_bnb_burn_dates(config: dict) -> list[pd.Timestamp]:
    """
    Phase 1.5: Извлича BNB burn дати от конфигурацията

    Този метод извлича burn датите от config.toml и ги конвертира
    в pandas Timestamp обекти за лесно сравнение с DataFrame индексите.

    Args:
        config: Конфигурационен dict с bnb_burn секцията

    Returns:
        List с burn дати като pandas Timestamp обекти

    Note:
        В бъдеще ще се разшири с API интеграция към bnbburn.info
    """
    try:
        burn_config = config.get("bnb_burn", {})
        burn_dates_source = burn_config.get("burn_dates_source", "manual")
        burn_dates_list = burn_config.get("burn_dates", [])

        burn_dates = []

        if burn_dates_source == "manual" and burn_dates_list:
            for date_str in burn_dates_list:
                try:
                    # Конвертираме string в Timestamp
                    burn_date = pd.to_datetime(date_str)
                    burn_dates.append(burn_date)
                    logger.info(f"Добавена burn дата: {burn_date.strftime('%Y-%m-%d')}")
                except ValueError as e:
                    logger.warning(f"Невалидна burn дата: {date_str} - {e}")

        logger.info(f"Общо извлечени burn дати: {len(burn_dates)}")
        return burn_dates

    except Exception as e:
        logger.exception(f"Грешка при извличане на burn дати: {e}")
        return []
