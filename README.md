# 🚀 BNB Trading System

**Проста, но ефективна система за анализ на BNB и генериране на Long/Short сигнали с фокус върху Fibonacci нива и седмични опашки.**

## 🎯 Основни характеристики

- **Fibonacci анализ** - ПРИОРИТЕТ №1: Автоматично намиране на swing points и изчисляване на всички Fib нива
- **Седмични опашки** - ПРИОРИТЕТ №2: Анализ на седмични опашки за последните 8 седмици
- **Технически индикатори**: RSI, MACD, Bollinger Bands
- **Цел**: Поне **75% точност** на сигналите
- **Валидация**: Проверява всеки сигнал след 2 седмици
- **Записване**: Записва всички сигнали и резултати в CSV файл

## 📁 Структура на проекта

```
bnb_trading/
├── config.toml              # Всички параметри тук
├── main.py                  # Главен файл
├── data_fetcher.py          # Binance API с ccxt (daily + weekly data)
├── fibonacci.py             # СПЕЦИАЛЕН модул за Fib calculations
├── weekly_tails.py          # СПЕЦИАЛЕН модул за седмични опашки
├── indicators.py            # RSI, MACD, BB
├── signal_generator.py      # Long/Short логика с Fib + опашки приоритет
├── validator.py             # Проверява сигнали след 2 седмици
├── results.csv              # Записва всички сигнали и резултати
├── requirements.txt         # pandas, ccxt, ta-lib, numpy
└── README.md               # Този файл
```

## 🚀 Инсталация

### 1. Клониране на проекта
```bash
git clone <repository-url>
cd bnb_trading
```

### 2. Инсталиране на зависимости
```bash
pip install -r requirements.txt
```

### 3. Инсталиране на TA-Lib (може да е сложно)

**За macOS:**
```bash
brew install ta-lib
pip install ta-lib
```

**За Ubuntu/Debian:**
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install ta-lib
```

**За Windows:**
- Изтеглете pre-compiled wheel от: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
- Инсталирайте с: `pip install TA_Lib‑0.4.24‑cp39‑cp39‑win_amd64.whl`

## ⚙️ Конфигурация

Всички параметри са в `config.toml` файла:

```toml
[data]
symbol = "BNB/USDT"           # Търговска двойка
lookback_days = 500           # Брой дни за анализ
timeframes = ["1d", "1w"]     # Daily + weekly данни

[fibonacci]
swing_lookback = 100          # Периоди за swing points
key_levels = [0.382, 0.618]  # Най-важните Fib нива
proximity_threshold = 0.01    # 1% близост до ниво
min_swing_size = 0.15         # Минимум 15% swing

[weekly_tails]
lookback_weeks = 8            # Анализира последните 8 седмици
min_tail_size = 0.03          # Минимум 3% от body
strong_tail_size = 0.05       # 5%+ = много силна опашка

[signals]
fibonacci_weight = 0.35       # 35% тежест за Fibonacci
weekly_tails_weight = 0.35    # 35% тежест за седмични опашки
rsi_weight = 0.15            # 15% за RSI
macd_weight = 0.10           # 10% за MACD
bb_weight = 0.05             # 5% за Bollinger
min_confirmations = 2         # Минимум 2 индикатора
confidence_threshold = 0.7    # Минимум увереност
fib_tail_required = true      # Изисква Fib ИЛИ tail за сигнал
```

## 🎯 Логика за сигнали

### LONG сигнал:
- Цената се отбива от Fib support (38.2% или 61.8%)
- RSI < 30 (oversold)
- MACD bullish cross
- Цена под Bollinger lower band
- **Бонус**: Съвпадение с долна седмична опашка

### SHORT сигнал:
- Цената достига Fib resistance (38.2% или 61.8%)
- RSI > 70 (overbought)
- MACD bearish cross
- Цена над Bollinger upper band
- **Бонус**: Съвпадение с горна седмична опашка

### HOLD сигнал:
- Ако Fibonacci не показва ясно ниво
- ИЛИ < 2 други индикатора се съгласяват
- ИЛИ няма значими седмични опашки

## 🚀 Използване

### 1. Стартиране на системата
```bash
python main.py
```

### 2. Тестване на отделни модули
```bash
# Тест на Fibonacci анализатора
python fibonacci.py

# Тест на Weekly Tails анализатора
python weekly_tails.py

# Тест на Technical Indicators
python indicators.py

# Тест на Signal Generator
python signal_generator.py

# Тест на Signal Validator
python validator.py
```

### 3. Тест на Data Fetcher
```bash
python data_fetcher.py
```

## 📊 Изходен формат

Системата показва:

1. **Текущия сигнал** (LONG/SHORT/HOLD)
2. **Активните Fibonacci нива** и разстоянията до тях
3. **Последните седмични опашки** и тяхната сила (%)
4. **Съвпадения** между Fib нива и опашки
5. **Точността** на последните 20 сигнала
6. **Причината** за сигнала (акцент върху Fib+опашки)
7. **Следващото Fibonacci ниво** за влизане/излизане

## 📈 Приоритет на сигналите

**Приоритет (намаляващ):**
1. **HIGHEST**: Fibonacci + Седмична опашка съвпадение
2. **HIGH**: Само Fibonacci сигнал
3. **MEDIUM**: Само Weekly Tails сигнал
4. **LOW**: Само технически индикатори (RSI/MACD/BB)

## 🔍 Валидация на сигнали

- Всеки сигнал се записва в `results.csv`
- След 2 седмици се проверява резултатът
- Изчислява се P&L и точност
- Анализира се защо неуспешните сигнали са се провалили

## 📊 Статистика

Системата предоставя:

- **Обща точност** на сигналите
- **Точност по тип** (LONG vs SHORT)
- **Точност по приоритет** (Fib+Tail vs само Fib vs други)
- **Среден P&L** за успешни/неуспешни сигнали
- **Анализ на грешки** за подобрение

## 🛠️ Персонализация

### Промяна на Fibonacci нива
```toml
[fibonacci]
key_levels = [0.236, 0.382, 0.5, 0.618, 0.786]  # Добавете повече нива
```

### Промяна на тежестите
```toml
[signals]
fibonacci_weight = 0.40       # Увеличете Fibonacci тежестта
weekly_tails_weight = 0.30    # Намалете Weekly Tails тежестта
```

### Промяна на RSI нива
```toml
[indicators]
rsi_overbought = 80           # По-консервативно
rsi_oversold = 20             # По-консервативно
```

## 🚨 Често срещани проблеми

### 1. TA-Lib инсталация
- Използвайте pre-compiled wheels за Windows
- За macOS: `brew install ta-lib`
- За Linux: компилирайте от source

### 2. CCXT грешки
- Проверете интернет връзката
- Binance API може да има ограничения
- Използвайте `enableRateLimit: true`

### 3. Данни не се зареждат
- Проверете Binance API статуса
- Намалете `lookback_days` в config.toml
- Проверете лог файла `bnb_trading.log`

## 📝 Логове

Системата създава `bnb_trading.log` файл с подробна информация за:
- Извличане на данни
- Генериране на сигнали
- Валидация на резултати
- Грешки и предупреждения

## 🔮 Бъдещи подобрения

- [ ] Добавяне на повече технически индикатори
- [ ] Machine Learning интеграция
- [ ] Real-time сигнали
- [ ] Email уведомления
- [ ] Web интерфейс
- [ ] Backtesting модул
- [ ] Risk management
- [ ] Portfolio tracking

## 📞 Поддръжка

За въпроси и проблеми:
1. Проверете лог файла `bnb_trading.log`
2. Тествайте отделните модули
3. Проверете конфигурацията в `config.toml`
4. Уверете се, че всички зависимости са инсталирани

## 📄 Лиценз

Този проект е за образователни цели. Използвайте на свой риск.

---

**🎯 Запомнете: Fibonacci + Седмични опашки са основата на системата!**

**Без валидно Fib ниво И без >3% седмична опашка = само HOLD сигнали от други индикатори.**
