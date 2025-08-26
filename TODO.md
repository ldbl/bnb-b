# 🚀 BNB Trading System - TODO & Подобрения

## 🎯 **КРИТИЧНИ ПОДОБРЕНИЯ (Приоритет 1)**

### **1. 🔴 SHORT Сигнали - Основен Фокус**
**Проблем**: 0% точност на SHORT сигналите (18/18 неуспешни)
**Цел**: Достигне 60%+ точност на SHORT сигналите
**Философия**: По-добре 0 сигнала отколкото грешен сигнал

#### **1.1 Trend Filter за SHORT сигнали (ЛЕСНО)**
- [ ] Добави проверка: **НЕ генерирай SHORT при силни UPTREND**
- [ ] SHORT само когато трендът е **NEUTRAL** или **WEAK_DOWNTREND**
- [ ] Добави **trend_strength_threshold = 0.3** в config.toml
- [ ] Използвай съществуващия `trend_analyzer.py`

#### **1.2 Fibonacci Logic за SHORT (ЛЕСНО)**
- [ ] Поправи логиката: SHORT само на **resistance** нива
- [ ] Добави проверка: цената трябва да е **ПОД** Fibonacci нивото
- [ ] SHORT само когато цената **отскача** от resistance ниво
- [ ] Използвай съществуващия `fibonacci.py`

#### **1.3 Weekly Tails за SHORT (ЛЕСНО)**
- [ ] SHORT само при **bearish tails** (долни опашки)
- [ ] Добави проверка за **tail strength > 0.6**
- [ ] SHORT само когато опашката е **над** Fibonacci resistance
- [ ] Използвай съществуващия `weekly_tails.py`

#### **1.4 Volume Confirmation (ЛЕСНО)**
- [ ] Добави **volume_confirmation** за SHORT сигнали
- [ ] SHORT само при **обем > 1.5x среден** за 14 периода
- [ ] Използвай съществуващия `indicators.py`

#### **1.5 BNB Burn Filter за SHORT (ЛЕСНО)**
- [ ] **НЕ генерирай SHORT при burn** (14 дни преди и 7 дни след)
- [ ] Добави **burn_event** и **pre_burn_window** колонки в `data_fetcher.py`
- [ ] Автоматично извличане на burn дати от Binance API или bnbburn.info
- [ ] SHORT само извън burn периодите

### **2. 📊 Подобряване на LONG сигнали (ЛЕСНО)**
**Проблем**: 100% точност, но може да пропускаме сигнали
**Цел**: Запази високата точност, добави EMA потвърждение + BNB Burn логика

#### **2.1 EMA Crossover за LONG (ЛЕСНО)**
- [ ] Добави **EMA10 > EMA50** потвърждение за LONG
- [ ] Използвай съществуващия `moving_averages.py`
- [ ] Добави в `signal_generator.py`

#### **2.2 BNB Burn Enhancement за LONG (ЛЕСНО)**
- [ ] **Увеличи confidence** за LONG преди burn (14 дни)
- [ ] **Buy на подкрепа** преди burn ($750-800)
- [ ] **Sell на 5-7% ръст** след burn ($840-850)
- [ ] Използвай burn дати за timing

#### **2.3 Risk Management (ЛЕСНО)**
- [ ] Добави **stop-loss** препоръки в Fibonacci support нива
- [ ] **Risk/Reward ratio** минимум 1:2
- [ ] Добави в `signal_generator.py`

## 🔧 **ТЕХНИЧЕСКИ ПОДОБРЕНИЯ (Приоритет 2)**

### **3. 📈 Enhanced Indicators (ЛЕСНО)**
- [ ] Добави **ATR (Average True Range)** за volatility в `indicators.py`
- [ ] Използвай TA-Lib `ATR` функция
- [ ] Добави в config.toml

### **4. 🎯 Signal Quality Filters (ЛЕСНО)**
- [ ] **Multi-timeframe confirmation** (daily + weekly)
- [ ] Използвай съществуващите анализатори
- [ ] Добави в `signal_generator.py`

### **5. 📊 Backtesting Improvements (ЛЕСНО)**
- [ ] **Sharpe ratio** и **Max drawdown** изчисления
- [ ] Добави в `backtester.py`
- [ ] Използвай numpy за изчисления

### **6. 🔥 BNB Burn Backtesting (ЛЕСНО)**
- [ ] **Тествай burn-aware стратегия** за Q2 2025 (юли burn)
- [ ] **Валидирай за Q3-Q4 2024** (+31% от $533 до $701)
- [ ] **Тествай септември 2025** корекция ($834.96→$750-800)
- [ ] **Метрики**: >5% monthly, >25% quarterly, drawdown <10% monthly

## ⚙️ **КОНФИГУРАЦИЯ И НАСТРОЙКИ**

### **7. 📝 Config.toml Improvements (ЛЕСНО)**
```toml
[short_signals]
enabled = true
trend_filter = true
trend_strength_threshold = 0.3
min_fibonacci_resistance = true
volume_confirmation = true
min_tail_strength = 0.6
burn_filter = true
price_action_rejection = true
multi_timeframe_alignment = true
market_regime_detection = true
signal_quality_scoring = true
min_quality_score = 70
confidence_threshold = 0.8

[long_signals]
enabled = true
ema_confirmation = true
min_risk_reward = 2.0
burn_enhancement = true

[bnb_burn]
enabled = true
pre_burn_window_days = 14
post_burn_window_days = 7
burn_confidence_bonus = 0.15
burn_target_pct = 0.05

[market_regimes]
strong_bull = "SHORT_DISABLED"
weak_bull = "SHORT_HIGH_CONFIDENCE"
range = "SHORT_ENABLED"
bear = "SHORT_ENABLED"

[price_action]
rejection_wick_multiplier = 2.0
min_rejection_distance = 0.01

[signal_scoring]
fibonacci_weight = 35
weekly_tails_weight = 30
trend_weight = 20
volume_weight = 10
divergence_weight = 5

[risk_management]
stop_loss_enabled = true
position_sizing = true
max_risk_per_trade = 0.02

[indicators]
atr_period = 14
atr_multiplier = 2.0
```

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: SHORT Signals Fix + BNB Burn (1 седмица)**
1. [ ] Имплементирай trend filter за SHORT
2. [ ] Поправи Fibonacci logic
3. [ ] Добави volume confirmation
4. [ ] Добави BNB Burn filter за SHORT
5. [ ] Добави Price Action Rejection Patterns (ЛЕСНО)
   - [ ] Проверка за rejection от resistance нива
   - [ ] Long upper wick (rejection) - wick > body * 2
   - [ ] SHORT само след потвърждение на rejection
6. [ ] Добави Multi-timeframe Alignment (ЛЕСНО)
   - [ ] Daily трябва да показва слабост (DOWNTREND или WEAK)
   - [ ] Weekly не трябва да е в силен UPTREND
   - [ ] SHORT само когато и двата timeframe са aligned
7. [ ] Добави Market Regime Detection (ЛЕСНО)
   - [ ] STRONG_BULL: SHORT изключен
   - [ ] WEAK_BULL: SHORT с confidence threshold 0.8
   - [ ] RANGE: SHORT enabled
   - [ ] BEAR: SHORT enabled
8. [ ] Добави Signal Quality Scoring за SHORT (ЛЕСНО)
   - [ ] Fibonacci alignment: 35 точки
   - [ ] Weekly tails: 30 точки
   - [ ] Trend alignment: 20 точки
   - [ ] Volume confirmation: 10 точки
   - [ ] Divergence: 5 точки
   - [ ] SHORT само при score > 70
9. [ ] Тествай с backtest

### **Phase 2: LONG Enhancement + BNB Burn (3-4 дни)**
1. [ ] Добави EMA crossover потвърждение
2. [ ] Добави BNB Burn enhancement за LONG
3. [ ] Добави stop-loss препоръки
4. [ ] Тествай accuracy

### **Phase 3: Quality Filters + Burn Backtesting (3-4 дни)**
1. [ ] Добави ATR индикатор
2. [ ] Multi-timeframe confirmation
3. [ ] Sharpe ratio и drawdown
4. [ ] Тествай burn-aware стратегия

## 🎯 **SUCCESS METRICS**

### **Target Accuracy:**
- **Overall**: 75%+ (сега 67.3%)
- **LONG**: 80%+ (сега 100%)
- **SHORT**: 60%+ (сега 0%)

### **BNB Burn Targets:**
- **Monthly**: >5% ръст след burn
- **Quarterly**: >25% ръст след burn
- **Entry**: Buy на $750-800 преди burn
- **Exit**: Sell на $840-850 след burn

### **Risk Metrics:**
- **Max Drawdown**: < 10% monthly, < 15% quarterly
- **Sharpe Ratio**: > 1.5
- **Win Rate**: > 60%

## 💡 **ВАЖНИ ПРИНЦИПИ**

### **Хайдушкият кодекс:**
- **Rule #0**: Без over-engineering ✅
- **Rule #1**: Котвата (ясни нива $750-800) ✅
- **Rule #2**: Търпение (изчакване на burn) ✅
- **Rule #5**: Излизане на такт ($840-850) ✅
- **Rule #6**: Една битка (избягване на SHORT при burn) ✅

### **Философия:**
- **"Две напред, една назад"** - дисциплинирани сигнали
- **Качество над количество** - по-добре 0 сигнала отколкото грешен
- **Простота** - използвай съществуващите модули
- **BNB Burn timing** - улавяне на 5-7% ръст

---

## 📅 **TIMELINE**

- **Week 1**: SHORT signals fix + BNB Burn filter
- **Week 2**: LONG enhancement + BNB Burn enhancement
- **Week 3**: Quality filters + Burn backtesting

---

*Последна актуализация: 2025-08-26*
*Следващ review: След Phase 1*
