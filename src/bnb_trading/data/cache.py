"""Data caching functionality for BNB Trading System."""

import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DataCache:
    """Simple in-memory data cache for API responses."""

    def __init__(self, cache_ttl_minutes: int = 30):
        """
        Initialize data cache.

        Args:
            cache_ttl_minutes: Cache time-to-live in minutes
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)

    def get(self, key: str) -> pd.DataFrame | None:
        """
        Get cached data if available and not expired.

        Args:
            key: Cache key

        Returns:
            Cached DataFrame or None if not found/expired
        """
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]
        cache_time = cache_entry["timestamp"]

        if datetime.now() - cache_time > self.cache_ttl:
            # Cache expired
            del self._cache[key]
            return None

        # Ensure we return the correct type
        cached_data = cache_entry["data"]
        if isinstance(cached_data, pd.DataFrame):
            return cached_data
        return None

    def set(self, key: str, data: pd.DataFrame) -> None:
        """
        Store data in cache.

        Args:
            key: Cache key
            data: DataFrame to cache
        """
        self._cache[key] = {"data": data.copy(), "timestamp": datetime.now()}

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        total_entries = len(self._cache)
        expired_entries = 0

        now = datetime.now()
        for entry in self._cache.values():
            if now - entry["timestamp"] > self.cache_ttl:
                expired_entries += 1

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60,
        }
