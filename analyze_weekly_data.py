#!/usr/bin/env python3
"""
Анализатор на седмични данни за SHORT сигнали
Извлича седмични данни и анализира защо SHORT сигналите не се хващат
Фокусира се върху ГОРНИ опашки (>100% от тялото) като SHORT потенциал
"""

import sys
sys.path.append('.')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_fetcher import BNBDataFetcher
from weekly_tails import WeeklyTailsAnalyzer
import logging

# Намаляваме logging
logging.getLogger().setLevel(logging.ERROR)

def analyze_weekly_data():
    """Анализира седмичните данни за SHORT сигнали"""

    print("🔍 АНАЛИЗ НА СЕДМИЧНИ ДАННИ ЗА SHORT СИГНАЛИ")
    print("=" * 60)

    # 1. Извличаме данни
    print("\n📊 Извличаме седмични данни...")
    data_fetcher = BNBDataFetcher()
    data = data_fetcher.fetch_bnb_data(365)  # 1 година данни

    if not data or 'weekly' not in data:
        print("❌ Грешка при извличане на данни!")
        return

    weekly_df = data['weekly']
    print(f"✅ Извлечени {len(weekly_df)} седмични записа")
    print(f"📅 Период: {weekly_df.index[0].date()} до {weekly_df.index[-1].date()}")
    print(f"📊 Колонки в weekly_df: {list(weekly_df.columns)}")

    # 2. Инициализираме анализатора
    try:
        import toml
        with open('config.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)
        weekly_analyzer = WeeklyTailsAnalyzer(config)
    except Exception as e:
        print(f"❌ Грешка при инициализация: {e}")
        return

    # 3. Анализираме всяка седмица за SHORT сигнали
    print("\n🎯 Анализираме всяка седмица...")

    short_signals_found = []
    large_tails_short = []
    all_tails_data = []

    for i, (date, row) in enumerate(weekly_df.iterrows()):
        try:
            # Проверяваме всяка свещ за опашки
            open_price = row['Open']
            high_price = row['High']
            low_price = row['Low']
            close_price = row['Close']

            # Изчисляваме опашките ПРАВИЛНО
            upper_wick = high_price - max(open_price, close_price)
            lower_wick = min(open_price, close_price) - low_price
            body = abs(close_price - open_price)
            total_range = high_price - low_price  # Обща височина на свещта

            # Debug: показваме детайли за първите няколко
            if i < 3:
                print(".2f")

            tail_data = {
                'date': date.date(),
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'body': body,
                'total_range': total_range,
                'upper_wick': upper_wick,
                'lower_wick': lower_wick,
                # ПРАВИЛНО ИЗЧИСЛЕНИЕ: процент спрямо общата височина, не спрямо тялото!
                'upper_wick_pct': (upper_wick / total_range * 100) if total_range > 0 else 0,
                'lower_wick_pct': (lower_wick / total_range * 100) if total_range > 0 else 0,
                'next_week_change': None
            }

            # Проверяваме какво се случва следващата седмица
            if i < len(weekly_df) - 1:
                next_row = weekly_df.iloc[i + 1]
                next_close = next_row['Close']
                change_pct = ((next_close - close_price) / close_price) * 100
                tail_data['next_week_change'] = change_pct

            all_tails_data.append(tail_data)

            # Ако горната опашка е голяма (> 50% от общата височина) - SHORT потенциал
            if tail_data['upper_wick_pct'] > 50:
                large_tails_short.append(tail_data)
                print(".1f")

            # Ако има голяма горна опашка, анализираме подробно
            if tail_data['upper_wick_pct'] > 50:
                print(f"\n   🎯 ГОЛЯМА ГОРНА ОПАШКА: {date.date()} - {tail_data['upper_wick_pct']:.1f}%")

                # Анализираме ръчно свещта
                is_bullish = close_price > open_price
                upper_tail = high_price - max(open_price, close_price)
                lower_tail = min(open_price, close_price) - low_price
                body_size = abs(close_price - open_price)

                print(f"   🕯️  СВЕЩ: {'BULLISH' if is_bullish else 'BEARISH'} | Body: {body_size:.2f}")
                print(f"   📊 Опашки - Upper: {upper_tail:.2f} | Lower: {lower_tail:.2f}")

                # Какъв сигнал очакваме според ръчния анализ
                expected_signal = 'SHORT' if not is_bullish and upper_tail > lower_tail else 'LONG' if is_bullish and lower_tail > upper_tail else 'HOLD'
                print(f"   🎯 ОЧАКВАН СИГНАЛ: {expected_signal}")

                # Генерираме сигнал с анализатора (само за свещи с големи опашки)
                try:
                    # Първо анализираме опашките, после генерираме сигнал
                    current_data = weekly_df.iloc[:i+1]
                    print(f"   📊 Подаваме {len(current_data)} седмици на анализатора")

                    # Стъпка 1: Анализираме опашките
                    tails_analysis = weekly_analyzer.analyze_weekly_tails(current_data)

                    if tails_analysis:
                        # Стъпка 2: Генерираме сигнал от анализа
                        signal = weekly_analyzer.get_weekly_tails_signal(tails_analysis)
                        if signal:
                            print(f"   📊 АНАЛИЗАТОР СИГНАЛ: {signal.get('signal', 'N/A')} (сила: {signal.get('strength', 0):.2f})")
                            print(f"   📝 Причина: {signal.get('reason', 'N/A')}")

                            if signal.get('signal') == 'SHORT':
                                short_signals_found.append({
                                    'date': date.date(),
                                    'signal': signal
                                })
                                print(f"   🔴 НАМЕРЕН SHORT СИГНАЛ!")
                                print(f"   📊 SHORT сила: {signal.get('strength', 0):.3f}")
                                print(f"   📝 SHORT причина: {signal.get('reason', 'N/A')}")
                                print(f"   🔢 SHORT опашки: {signal.get('tail_count', 0)}")
                    else:
                        print(f"   ⚪ Няма значими опашки за анализ")

                except Exception as e:
                    print(f"   ❌ Грешка в анализатора: {e}")
                    import traceback
                    print(f"   🔍 Детайли: {traceback.format_exc()}")

            # Генерираме сигнал с анализатора (без debug за всички)
            try:
                current_data = weekly_df.iloc[:i+1]
                tails_analysis = weekly_analyzer.analyze_weekly_tails(current_data)
                if tails_analysis:
                    signal = weekly_analyzer.get_weekly_tails_signal(tails_analysis)
                    if signal and signal.get('signal') == 'SHORT':
                        short_signals_found.append({
                            'date': date.date(),
                            'signal': signal
                        })
            except:
                pass  # Тихо игнорираме грешките за да не замърсяваме изхода

        except Exception as e:
            print(f"   ❌ Грешка в седмица {i+1}: {e}")
            continue

    # 4. Резултати
    print("\n📊 РЕЗУЛТАТИ:")
    print(f"🔴 Големи горни опашки (>50%): {len(large_tails_short)}")
    print(f"❌ SHORT сигнали от анализатора: {len(short_signals_found)}")
    print(f"📈 Общо анализирани седмици: {len(all_tails_data)}")

    # 5. Статистики за опашките
    if all_tails_data:
        lower_wicks = [d['lower_wick_pct'] for d in all_tails_data]
        upper_wicks = [d['upper_wick_pct'] for d in all_tails_data]

        print("\n📈 СТАТИСТИКИ ЗА ОПАШКИТЕ:")
        print(f"   🔽 Средна долна опашка: {np.mean(lower_wicks):.1f}%")
        print(f"   🔼 Средна горна опашка: {np.mean(upper_wicks):.1f}%")
        print(f"   🔽 Макс. долна опашка: {max(lower_wicks):.1f}%")
        print(f"   🔼 Макс. горна опашка: {max(upper_wicks):.1f}%")

    # 6. Детайли за най-големите опашки
    if large_tails_short:
        print("\n🎯 НАЙ-ГОЛЕМИ ГОРНИ ОПАШКИ (>50%) - SHORT ПОТЕНЦИАЛ:")
        # Сортираме по големина на опашката
        sorted_tails = sorted(large_tails_short, key=lambda x: x['upper_wick_pct'], reverse=True)
        for tail in sorted_tails[:10]:  # Топ 10
            change_str = ".2f" if tail['next_week_change'] is not None else "N/A"
            print(f"📅 {tail['date']}: горна опашка {tail['upper_wick_pct']:.1f}%, следваща седмица: {change_str}")

    # 7. Защо няма SHORT сигнали?
    print("\n🔍 ЗАЩО НЯМА SHORT СИГНАЛИ?")
    print("💡 Възможни причини:")

    if not large_tails_short:
        print("   ❌ Няма достатъчно големи горни опашки в данните")
        print("   💡 В последната година BNB е в силен възходящ тренд")
        print("   💡 Почти няма седмици с големи горни опашки (съпротива отгоре)")
    else:
        print("   ✅ Има големи горни опашки, но анализаторът не ги засича")
        print("   🔧 Вероятно weekly_tails.py не търси правилните критерии за SHORT")

    # 8. Анализ на тренда
    if all_tails_data:
        print("\n📊 АНАЛИЗ НА ТРЕНДА:")
        weekly_changes = [d['next_week_change'] for d in all_tails_data if d['next_week_change'] is not None]
        if weekly_changes:
            positive_changes = sum(1 for c in weekly_changes if c > 0)
            print(f"   📈 Позитивни седмици: {positive_changes}/{len(weekly_changes)} ({positive_changes/len(weekly_changes)*100:.1f}%)")
            print(f"   💰 Средна седмична промяна: {np.mean(weekly_changes):+.2f}%")
            print("   ✅ BNB е в СИЛЕН ВЪЗХОДЯЩ ТРЕНД - това обяснява липсата на SHORT сигнали!")

    # 7. Проверяваме конфигурацията
    print("\n⚙️  ТЕКУЩИ НАСТРОЙКИ ЗА SHORT:")
    try:
        import toml
        with open('config.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)

        if 'short_signals' in config:
            short_config = config['short_signals']
            print(f"   🔴 min_fibonacci_resistance: {short_config.get('min_fibonacci_resistance', 'N/A')}")
            print(f"   🔴 volume_confirmation: {short_config.get('volume_confirmation', 'N/A')}")
            print(f"   🔴 burn_filter: {short_config.get('burn_filter', 'N/A')}")

        if 'weekly_tails' in config:
            tails_config = config['weekly_tails']
            print(f"   🔴 min_tail_strength: {tails_config.get('min_tail_strength', 'N/A')}")

    except Exception as e:
        print(f"   ❌ Грешка при четене на config: {e}")

    return large_tails_short, short_signals_found

if __name__ == "__main__":
    analyze_weekly_data()
