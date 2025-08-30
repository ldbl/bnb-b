# 🚀 BNB Търговска Система v2.1.0

Усъвършенствана система за техническа анализа за търговия с BNB/USDT с 22+ специализирани анализни модула

_Advanced Technical Analysis System for BNB/USDT Trading with 22+ Specialized Analysis Modules_

[![CI/CD Pipeline](https://github.com/ldbl/bnb-b/actions/workflows/ci.yml/badge.svg)](https://github.com/ldbl/bnb-b/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ldbl/bnb-b/branch/main/graph/badge.svg)](https://codecov.io/gh/ldbl/bnb-b)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📈 Текущи Показатели

-   **Обща Точност**: 59.7% (37/62 сигнала) - Най-нов 18-месечен backtest
-   **LONG Точност**: 63.3% (49 сигнала) - Подобрена производителност
-   **SHORT Точност**: 46.2% (13 сигнала) - Активно филтриране според пазарен режим
-   **Средна P&L**: +2.21% на сигнал
-   **Период на Backtest**: 540 дни (2024-03-07 до 2025-08-29)

_Current Performance: Overall Accuracy 59.7%, LONG 63.3%, SHORT 46.2%, Average P&L +2.21% per signal_

## 🏗️ Архитектура

### Модерна Структура на Проекта

```
bnb-b/
├── src/bnb_trading/          # Основен пакет с изходен код
│   ├── __init__.py           # Инициализация на пакет
│   ├── main.py               # Основна входна точка
│   ├── signal_generator.py   # Основно генериране на сигнали
│   ├── data_fetcher.py       # Интеграция с Binance API
│   ├── backtester.py         # Историческа валидация
│   └── ...                   # 22+ анализни модула
├── tests/                    # Цялостен пакет от тестове
│   ├── __init__.py
│   ├── conftest.py           # Споделени тестови fixtures
│   ├── test_signal_generator.py
│   └── ...                   # Модул-специфични тестове
├── data/                     # Резултати от анализи и backtests
├── .github/workflows/        # CI/CD автоматизация
├── config.toml               # Системна конфигурация
├── pyproject.toml            # Модерно Python пакетиране
├── requirements.txt          # Продукционни зависимости
├── requirements-dev.txt      # Развойни зависимости
└── Makefile                  # Развойни команди
```

_Modern Project Structure with comprehensive modular architecture_

## 🚀 Бърз Старт

### Инсталация

```bash
# Клониране на репозиторията
git clone https://github.com/ldbl/bnb-b.git
cd bnb-b

# Настройка на развойна среда
make dev-setup

# Или ръчна инсталация
pip install -r requirements-dev.txt
pip install -e .
```

### Основно Използване

```bash
# Генериране на текущ търговски сигнал
make signal

# Пускане на цялостен анализ
make analyze

# Изпълнение на 18-месечен backtest
make backtest

# Пускане на всички тестове
make test
```

### Python API

```python
from bnb_trading import SignalGenerator, BNBDataFetcher
import toml

# Зареждане на конфигурация
config = toml.load('config.toml')

# Инициализиране на компоненти
data_fetcher = BNBDataFetcher(config['data']['symbol'])
signal_gen = SignalGenerator(config)

# Извличане на данни и генериране на сигнали
data_response = data_fetcher.fetch_bnb_data()
daily_data = data_response['daily']
weekly_data = data_response['weekly']
signal = signal_gen.generate_signal(daily_data, weekly_data)

print(f"Сигнал: {signal['signal']}")
print(f"Увереност: {signal['confidence']:.1%}")
print(f"Обосновка: {signal['reason']}")
```

_Quick Start: Installation, basic usage commands, and Python API examples_

## 🔧 Разработка

### Предварителни Изисквания

-   Python 3.13+
-   TA-Lib библиотека за техническа анализа
-   Make (за развойни команди)

### Работен Процес за Разработка

```bash
# Форматиране на код
make format

# Пускане на linting
make lint

# Пускане на тестове с coverage
make test

# Пускане на специфични категории тестове
make test-unit        # Само unit тестове
make test-integration # Integration тестове
make test-slow        # Тестове изискващи пазарни данни
```

### Pre-commit Hooks

Автоматични проверки за качество на код при всеки commit:

```bash
# Инсталиране на hooks
make pre-commit

# Ръчно пускане
pre-commit run --all-files
```

_Development: Prerequisites, workflow, and automated quality checks_

## 📊 Основни Модули

### 🎯 Машина за Генериране на Сигнали

-   **SignalGenerator**: Оркестрира 22+ анализни модула с претеглено оценяване
-   **Мулти-времеви Анализ**: Корелация между дневни и седмични данни
-   **Пазарна Режимна Интелигентност**: STRONG_BULL детекция и SHORT блокиране

### 📈 Модули за Техническа Анализа

-   **Fibonacci Анализ** (35% тежест): Нива на поддръжка/съпротива
-   **Седмични Опашки Анализ** (40% тежест): Анализ на wick модели
-   **Технически Индикатори** (15% тежест): RSI, MACD, Bollinger Bands
-   **Плъзгащи Средни** (10% тежест): Потвърждение на тренд
-   **Elliott Wave Анализ**: Структура на вълни и сигнали за завършване
-   **Детекция на Дивергенция**: Анализ на дивергенция цена-момент
-   **Умен SHORT Генератор**: SHORT сигнали, осведомени за пазарния режим

### 🛡️ Управление на Риска

-   **Детекция на Пазарен Режим**: Bull/Bear/Neutral класификация
-   **ATH Близост Филтриране**: Предотвратява рискови SHORT сигнали
-   **Потвърждение чрез Обем**: Подобрена валидация на сигнали
-   **Време-базирана Валидация**: Реалистични периоди на държане

_Core Modules: Signal generation engine, technical analysis modules, and risk management_

## 🧪 Тестване

### Категории Тестове

-   **Unit Тестове**: Тестване на индивидуални модули
-   **Integration Тестове**: Тестване на взаимодействие между модули
-   **Бавни Тестове**: Пълна валидация с пазарни данни
-   **API Тестове**: Тестване на външни източници на данни

### Пускане на Тестове

```bash
# Всички тестове с coverage
pytest tests/ --cov=src/bnb_trading --cov-report=html

# Специфични маркери
pytest -m "unit"           # Само unit тестове
pytest -m "integration"    # Само integration тестове
pytest -m "slow"          # Тестове с пазарни данни
```

_Testing: Unit, integration, slow and API tests with comprehensive coverage_

## 📈 Конфигурация

Системата е напълно конфигурируема чрез `config.toml`:

```toml
[data]
symbol = "BNB/USDT"
lookback_days = 500
timeframes = ["1d", "1w"]

[signals]
fibonacci_weight = 0.35      # Основна тежест за анализ
weekly_tails_weight = 0.40   # Подобрена за LONG точност
confidence_threshold = 0.8   # Контрол на качеството

[smart_short]
enabled = true
bull_market_block = true     # Безопасност в bull пазари
min_ath_distance_pct = 5.0   # Управление на риска
```

_Configuration: Fully configurable system via config.toml with weights and risk management_

## 🔄 CI/CD Pipeline

Автоматизирано тестване и проверки за качество:

-   **Python Тестване**: 3.13
-   **Качество на Код**: Ruff (formatting & linting), mypy
-   **Сканиране за Сигурност**: Bandit анализ за сигурност
-   **Покритие на Тестове**: Цялостно докладване на покритието
-   **Integration Тестване**: Пълна системна валидация

_CI/CD Pipeline: Automated testing, quality checks, security scanning and integration validation_

## 📚 Документация

-   **[CLAUDE.md](CLAUDE.md)**: Ръководство за разработка и системен преглед
-   **[MODULES.md](MODULES.md)**: Подробна техническа документация
-   **[TODO.md](TODO.md)**: Пътна карта за разработка и приоритети

_Documentation: Development guide, technical specs, and roadmap_

## 🎯 Целеви Показатели

### Текущи срещу Целеви Показатели

| Метрика             | Текуща | Цел        | Статус         |
| ------------------- | ------ | ---------- | -------------- |
| LONG Точност        | 63.3%  | 85%+       | 🚧 В процес    |
| SHORT Точност       | 46.2%  | 75%+       | 🚧 В процес    |
| Обща Точност        | 59.7%  | 80%+       | 🚧 В процес    |
| Риск/Възнаграждение | 1:2.1  | 1:4 (LONG) | 🚧 Подобряване |

_Performance Targets: Current vs target metrics with improvement status_

## 🤝 Участие в Проекта

1. Форквайте репозиторията
2. Създайте feature branch: `git checkout -b feature/amazing-feature`
3. Направете промените си с тестове
4. Пуснете проверки за качество: `make ci-test`
5. Commit промените: `git commit -m 'Add amazing feature'`
6. Push към branch: `git push origin feature/amazing-feature`
7. Отворете Pull Request

### Стандарти за Разработка

-   **Качество на Код**: Ruff formatting & linting, mypy type checking
-   **Тестване**: Минимум 80% покритие на тестове изисква
-   **Документация**: Цялостни docstrings и примери
-   **Типова Безопасност**: Пълни type hints за всички публични APIs

_Contributing: Fork, feature branch, tests, quality checks, and pull request workflow_

## 📄 Лиценз

Този проект е лицензиран под MIT Лиценз - вижте [LICENSE](LICENSE) файла за подробности.

_This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details._

## ⚠️ Отказ от Отговорност

Този софтуер е само за образователни и изследователски цели. Търговията с криптовалути включва значителен риск от загуба. Никога не търгувайте с пари, които не можете да си позволите да загубите. Минали резултати не гарантират бъдещи резултати.

_This software is for educational and research purposes only. Cryptocurrency trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Past performance does not guarantee future results._

## 🙏 Благодарности

-   **TA-Lib**: Библиотека за техническа анализа
-   **CCXT**: Библиотека за търговия с криптовалутни борси
-   **Pandas**: Анализ и манипулация на данни
-   **NumPy**: Числени изчисления

_Acknowledgments: TA-Lib, CCXT, Pandas, and NumPy libraries_

---

_За подробна техническа документация, вижте [MODULES.md](MODULES.md)_
_За ръководство за разработка, вижте [CLAUDE.md](CLAUDE.md)_

_For detailed technical documentation, see [MODULES.md](MODULES.md)_
_For development guidance, see [CLAUDE.md](CLAUDE.md)_
