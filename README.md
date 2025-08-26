# �� BNB Trading System - Интелигентна Swing Trading Система

**Цел: 75%+ точност на сигналите** базирана на Fibonacci нива, Weekly Tails и Technical Analysis.

## 🎯 Основни Характеристики

- **Fibonacci Retracement & Extensions** - основни сигнали
- **Weekly Tails Analysis** - анализ на седмични опашки
- **Technical Indicators** - RSI, MACD, Bollinger Bands
- **Trend Analysis** - анализ на тренда и адаптивни стратегии
- **Optimal Levels** - исторически валидирани entry/exit точки
- **Real-time Data** - данни от Binance API чрез CCXT

## 📊 Архитектура

```
bnb_trading/
├── config.toml              # Всички параметри тук
├── main.py                  # Главна точка за стартиране
├── data_fetcher.py          # Binance API интеграция
├── fibonacci.py             # Fibonacci изчисления
├── weekly_tails.py          # Weekly wick/тails анализ
├── indicators.py            # Technical indicators (RSI, MACD, BB)
├── signal_generator.py      # Комбинира всички сигнали
├── optimal_levels.py        # Оптимални trading нива
├── trend_analyzer.py        # Тренд анализ и адаптивни стратегии
├── elliott_wave_analyzer.py # Elliott Wave структурен анализ
├── validator.py             # Валидация на сигналите
├── backtester.py            # Backtesting на стратегията
└── data/                    # Резултати и данни
```

## 🚀 Инсталация

1. **Клонирайте репозиторията:**
```bash
git clone <repository-url>
cd bnb-b
```

2. **Инсталирайте зависимостите:**
```bash
pip install -r requirements.txt
```

3. **Стартирайте системата:**
```bash
python3 main.py
```

## 📈 Как работи системата

### 1. **Fibonacci Analysis**
- Автоматично намира swing high/low точки
- Изчислява retracement нива (23.6%, 38.2%, 50%, 61.8%, 78.6%)
- Изчислява extension нива (100%, 127.2%, 141.4%, 161.8%, 200%, 261.8%)

### 2. **Weekly Tails Analysis**
- Анализира седмични wicks/тails
- Определя доминантни опашки (LONG/SHORT)
- Изчислява силата на опашките

### 3. **Technical Indicators**
- **RSI** (14 периода) - oversold/overbought нива
- **MACD** (8,17,9) - trend и momentum
- **Bollinger Bands** (20,2) - волатилност и позиция

### 4. **Trend Analysis**
- Анализира дневен и седмичен тренд
- Определя силата на тренда
- Range анализ (разширяване/свиване)
- Генерира адаптивни entry стратегии

### 5. **Optimal Levels**
- Намира исторически валидирани нива
- Брои докосвания на ценови нива
- Генерира entry/exit препоръки

### 6. **Elliott Wave Analysis**
- Анализира Elliott Wave структурите
- Определя текущата вълна (1-5) и степента
- Валидира Elliott Wave правилата
- Генерира wave-based trading сигнали
- Multi-timeframe анализ (daily + weekly)

### 7. **Signal Generation**
- Комбинира всички анализи
- Изчислява confidence score
- Генерира финален сигнал (LONG/SHORT/HOLD)

## ⚙️ Конфигурация

Всички параметри са в `config.toml`:

```toml
[data]
symbol = "BNB/USDT"
lookback_days = 500
timeframes = ["1d", "1w"]

[fibonacci]
swing_lookback = 100
key_levels = [0.382, 0.618]
proximity_threshold = 0.015
min_swing_size = 0.12

[weekly_tails]
lookback_weeks = 8
min_tail_size = 0.025
strong_tail_size = 0.04

[indicators]
rsi_period = 14
rsi_overbought = 75
rsi_oversold = 25
macd_fast = 8
macd_slow = 17
macd_signal = 9
bb_period = 20
bb_std = 2.0

[signals]
fibonacci_weight = 0.35
weekly_tails_weight = 0.35
rsi_weight = 0.15
macd_weight = 0.10
bb_weight = 0.05
min_confirmations = 2
confidence_threshold = 0.7

[trend]
trend_lookback_days = 30
trend_threshold = 0.015

[elliott_wave]
enabled = true
lookback_periods = 50
min_wave_strength = 0.02
confidence_threshold = 60
```

## 📊 Използване

### **Основен анализ:**
```bash
python3 main.py
```

### **Backtesting:**
```bash
python3 backtester.py
```

## 📁 Резултати

Системата генерира следните файлове в `data/` директорията:

- `analysis_results.txt` - основен анализ
- `results_summary.txt` - обобщение на резултатите
- `backtest_results.txt` - backtesting резултати
- `results.csv` - история на сигналите
- `bnb_trading.log` - лог файл

## 🎯 Trading Стратегии

### **LONG сигнали:**
- Fibonacci support нива
- Weekly LONG tails
- RSI oversold
- MACD bullish crossover
- Bollinger Bands долна лента

### **SHORT сигнали:**
- Fibonacci resistance нива
- Weekly SHORT tails
- RSI overbought
- MACD bearish crossover
- Bollinger Bands горна лента
- Elliott Wave 5 completion
- Correction patterns (ABC)

### **Адаптивни стратегии:**
- **UPTREND**: Pullback entry към support нива
- **DOWNTREND**: Bounce entry към resistance нива
- **NEUTRAL**: Range trading между границите

## 📈 Примерен изход

```
🎯 ТЕКУЩ СИГНАЛ ЗА ДНЕС - КЛЮЧОВА ИНФОРМАЦИЯ 🎯

🚀 СИГНАЛ: LONG | Увереност: 4.0 | Приоритет: HIGHEST

🚀 FIBONACCI EXTENSIONS (текуща цена: $851.10):
  100.0%          $  900.71 (🔴抵抗力) + 5.83% нагоре
  161.8% (ЗЛАТНО) $1,085.78 (🔴抵抗力) +27.57% нагоре

🔢 FIBONACCI RETRACEMENT (текуща цена: $851.10):
   78.6%                $  836.63 (🟢 поддръжка) -  1.70% надолу
   61.8% (ЗЛАТНО СЕЧЕНИЕ) $  786.32 (🟢 поддръжка) -  7.61% надолу

📊 ТЕХНИЧЕСКИ ИНДИКАТОРИ:
   RSI:  55.1 (🟡 неутрален)
   MACD:  +13.716 (🟢 bullish)
   Bollinger:  +0.61 (🟡 централна лента)

📈 TREND АНАЛИЗ:
   🎯 ОСНОВЕН ТРЕНД: UPTREND (увереност: HIGH)
   📊 СЕДМИЧЕН ТРЕНД: UPTREND (STRONG) +32.18%
   🎯 АДАПТИВНА СТРАТЕГИЯ: PULLBACK_ENTRY

🌊 ELLIOTT WAVE АНАЛИЗ:
   🎯 ОСНОВЕН АНАЛИЗ: WAVE_5
   📅 ДНЕВЕН АНАЛИЗ: WAVE_5 (UPTREND)
   💡 TRADING СИГНАЛИ: PREPARE_SELL
```

## 🔧 Разработка

### **Добавяне на нов индикатор:**
1. Създайте нов модул в `indicators.py`
2. Добавете го в `signal_generator.py`
3. Конфигурирайте теглото в `config.toml`

### **Модифициране на Fibonacci логика:**
1. Редактирайте `fibonacci.py`
2. Тествайте с `python3 main.py`

## 📊 Производителност

- **Целна точност**: 75%+
- **Време за анализ**: <5 секунди
- **Покритие**: Daily + Weekly данни
- **Lookback период**: 500 дни

## 🚫 Забранява се

- Хардкоднати тестови данни
- Тестови сигнали
- Симулирани резултати
- Тестови конфигурации

## ✅ Правилно използване

- **main.py** - единствената точка за стартиране
- **Реални данни** - от Binance API чрез ccxt
- **Конфигурация** - всички параметри в config.toml
- **Логване** - всички операции се записват в лог файлове

## 🤝 Принос

1. Fork-нете репозиторията
2. Създайте feature branch
3. Направете промените
4. Тествайте с `python3 main.py`
5. Създайте Pull Request

## 📄 Лиценз

MIT License - вижте `LICENSE` файла за детайли.

## 📞 Поддръжка

За въпроси и предложения, моля създайте Issue в GitHub.

---

**⚠️ Disclaimer**: Тази система е за образователни цели. Не гарантира печалби. Търгувайте на свой риск.**
