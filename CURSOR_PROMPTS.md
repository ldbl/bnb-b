# 🤖 CURSOR PROMPTS - BNB Trading System

*Готови за употреба prompts за подобряване на системата*

## **1. Market Regime Detection Implementation**
```
Implement market regime detection for the BNB trading system. Create a MarketRegimeDetector class that:
- Detects BULL/BEAR/RANGE market conditions based on price action vs ATH
- Uses configurable thresholds (bull_market_threshold=0.7, bear_market_threshold=-0.2)  
- Blocks SHORT signals during strong bull markets (short_disabled_in_bull=true)
- Add the detect_market_regime() method to SignalGenerator class
- Integrate with existing trend analysis from TrendAnalyzer module
- Return regime classification with confidence scores
```

## **2. SHORT Signal Enhancement - Fibonacci + Weekly Tails**
```
Enhance SHORT signals by implementing confluence between FibonacciAnalyzer and WeeklyTailsAnalyzer. Create fibonacci_weekly_tails_short_confluence() method that:
- Uses existing swing detection from FibonacciAnalyzer for resistance levels (61.8%, 78.6%)
- Combines with rejection tails from WeeklyTailsAnalyzer
- Generates SHORT signals only when Fibonacci resistance coincides with weekly rejection wicks (within 2% proximity)
- Calculates combined confidence score from both modules
- Add detailed reasoning for each signal
```

## **3. Elliott Wave + Divergence SHORT System**
```
Create elliott_divergence_short_system() that combines ElliottWaveAnalyzer and DivergenceDetector for high-confidence SHORT signals. Implement:
- Detection of Wave 5 completion (wave_completion > 0.8)
- Confirmation with bearish divergence signals (confidence > 0.7)
- Generate SHORT signal only when both conditions align
- Set high confidence score (0.9) for this strong confluence
- Add proper reasoning and validation logic
```

## **4. Sentiment + Whale Tracker Combo**
```
Build sentiment_whale_short_system() combining SentimentAnalyzer and WhaleTracker data. Create logic for:
- Detecting extreme greed conditions (fear_greed_index > 80)
- Identifying whale distribution patterns (mega_whale_sells > mega_whale_buys)
- Adding social sentiment confirmation (social_sentiment < 0.3)
- Generate SHORT signals with 0.85 confidence when all conditions align
- Include comprehensive reasoning for market psychology + institutional flows
```

## **5. Dynamic Risk Management System**
```
Implement advanced risk management with calculate_position_size() and calculate_dynamic_stop_loss() functions:
- Use Kelly Criterion with safety margin for position sizing
- Apply volatility adjustment to reduce risk in volatile conditions
- Cap maximum risk at 5% per trade
- Create trend-adjusted stop losses (tighter stops in strong trends)
- Add ATR-based stop loss calculation with dynamic multipliers
- Integrate with existing signal confidence scores
```

## **6. Ensemble SHORT Strategy**
```
Create EnsembleShortStrategy class that combines all SHORT systems with weighted voting:
- Implement weighted scoring system (fibonacci_tails: 0.25, elliott_divergence: 0.20, etc.)
- Require minimum 3 systems agreement for SHORT signal generation
- Calculate ensemble confidence score with total_score > 0.6 threshold
- Track contributing systems and provide detailed reasoning
- Add multi-system validation and conflict resolution
```

## **7. Performance Analytics Enhancement**
```
Upgrade PerformanceAnalytics class with advanced metrics:
- Add Sharpe ratio, Sortino ratio, Calmar ratio calculations
- Implement rolling 30-day performance analysis
- Create market condition correlation tracking
- Add signal degradation detection with automated alerts
- Build quarterly performance comparison dashboard
- Include profit factor and average trade duration metrics
```

## **8. Automated Testing & Parameter Optimization**
```
Build automated backtesting pipeline with parameter optimization:
- Create automated_backtest_pipeline() for daily performance monitoring
- Implement parameter optimization using Bayesian methods and scipy.optimize
- Add performance degradation alerts (accuracy < 0.75 threshold)
- Use TimeSeriesSplit for proper cross-validation
- Create objective function minimizing negative Sharpe ratio
- Integrate with existing backtesting infrastructure
```

## **9. Data Quality Validation System**
```
Enhance DataFetcher with comprehensive data validation:
- Implement validate_data_quality() method checking for missing data, gaps, volume anomalies
- Add secondary data source integration (CoinGecko, CryptoCompare)
- Create cross-validation between different data sources
- Build anomaly detection for irregular price/volume data
- Calculate quality scores and compile data issue reports
- Add data source failover mechanisms
```

## **10. Caching & Performance Optimization**
```
Implement SignalCache class with Redis integration and parallel processing:
- Add LRU caching for expensive calculations (Fibonacci levels, Elliott waves)
- Create Redis-based persistent caching for historical analysis
- Implement parallel_analysis() using ThreadPoolExecutor and asyncio
- Optimize processor-intensive modules (ElliottWave, Fibonacci, TechnicalIndicators)
- Add cache invalidation strategies and memory management
- Measure and optimize execution time for all analyzers
```

---

*Създадено: 2025-08-28*
*Базирано на анализ от RECOMMENDATIONS.md*