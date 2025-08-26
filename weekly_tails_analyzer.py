"""
Weekly Tails Analyzer - Анализира всички weekly tails и показва възможности за вход/изход
"""

import pandas as pd
import numpy as np
import toml
import logging
from datetime import datetime, timedelta
import sys
import os

# Добавяме текущата директория в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import BNBDataFetcher
from weekly_tails import WeeklyTailsAnalyzer

# Настройваме logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyTailsDetailedAnalyzer:
    """Анализатор за weekly tails и възможности за вход/изход"""
    
    def __init__(self, config_file: str = 'config.toml'):
        """
        Инициализира анализатора
        
        Args:
            config_file: Път до конфигурацията
        """
        try:
            # Зареждаме конфигурацията
            self.config = toml.load(config_file)
            logger.info(f"Конфигурация заредена от {config_file}")
            
            # Инициализираме компонентите
            self.data_fetcher = BNBDataFetcher(self.config['data']['symbol'])
            self.tails_analyzer = WeeklyTailsAnalyzer(self.config)
            
            logger.info("Weekly Tails Analyzer инициализиран успешно")
            
        except Exception as e:
            logger.error(f"Грешка при инициализиране на Weekly Tails Analyzer: {e}")
            raise
    
    def analyze_all_weekly_tails(self, lookback_days: int = 500):
        """
        Анализира всички weekly tails за последните N дни
        
        Args:
            lookback_days: Брой дни за lookback
        """
        try:
            logger.info(f"Анализ на всички weekly tails за последните {lookback_days} дни...")
            
            # Извличаме данни
            data = self.data_fetcher.fetch_bnb_data(lookback_days)
            
            if not data or 'weekly' not in data:
                raise ValueError("Неуспешно извличане на weekly данни")
            
            weekly_df = data['weekly']
            logger.info(f"Weekly данни извлечени: {len(weekly_df)} редове")
            
            # Анализираме всички weekly tails
            all_tails_analysis = self._analyze_all_tails(weekly_df)
            
            # Анализираме възможностите за вход/изход
            entry_exit_analysis = self._analyze_entry_exit_opportunities(weekly_df, all_tails_analysis)
            
            # Експортираме резултатите
            self._export_tails_analysis(all_tails_analysis, entry_exit_analysis)
            
            return {
                'tails_analysis': all_tails_analysis,
                'entry_exit_analysis': entry_exit_analysis
            }
            
        except Exception as e:
            logger.error(f"Грешка при анализ на weekly tails: {e}")
            return {'error': f'Грешка: {e}'}
    
    def _analyze_all_tails(self, weekly_df: pd.DataFrame):
        """
        Анализира всички weekly tails
        """
        try:
            tails_analysis = []
            
            # Анализираме всяка седмица
            for i in range(len(weekly_df)):
                current_date = weekly_df.index[i]
                current_data = weekly_df.iloc[i]
                
                # Взимаме данните до текущата дата
                historical_data = weekly_df[:i+1]
                
                if len(historical_data) < 8:
                    continue
                
                try:
                    # Анализираме опашките
                    tails = self.tails_analyzer.analyze_weekly_tails(historical_data)
                    
                    if tails:
                        for tail in tails:
                            tail['date'] = current_date
                            tail['price'] = current_data['Close']
                            tails_analysis.append(tail)
                
                except Exception as e:
                    logger.warning(f"Грешка при анализ на опашки за {current_date}: {e}")
                    continue
            
            logger.info(f"Анализирани {len(tails_analysis)} weekly tails")
            return tails_analysis
            
        except Exception as e:
            logger.error(f"Грешка при анализ на всички опашки: {e}")
            return []
    
    def _analyze_entry_exit_opportunities(self, weekly_df: pd.DataFrame, tails_analysis: list):
        """
        Анализира възможностите за вход/изход базирани на опашките
        """
        try:
            opportunities = []
            
            for tail in tails_analysis:
                if tail['signal'] == 'HOLD':
                    continue
                
                entry_date = tail['date']
                entry_price = tail['price']
                signal_type = tail['signal']
                
                # Търсим възможност за изход в следващите седмици
                future_data = weekly_df[weekly_df.index > entry_date]
                
                if len(future_data) < 2:
                    continue
                
                # Анализираме следващите 4 седмици за възможност за изход
                for i in range(min(4, len(future_data))):
                    exit_date = future_data.index[i]
                    exit_price = future_data.iloc[i]['Close']
                    
                    # Изчисляваме P&L
                    if signal_type == 'LONG':
                        profit_loss = exit_price - entry_price
                        profit_loss_pct = (profit_loss / entry_price) * 100
                        success = profit_loss > 0
                    elif signal_type == 'SHORT':
                        profit_loss = entry_price - exit_price
                        profit_loss_pct = (profit_loss / entry_price) * 100
                        success = profit_loss > 0
                    else:
                        continue
                    
                    # Проверяваме дали е добра възможност за изход
                    if success and profit_loss_pct >= 5:  # Минимум 5% печалба
                        opportunity = {
                            'entry_date': entry_date,
                            'exit_date': exit_date,
                            'signal_type': signal_type,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_loss': profit_loss,
                            'profit_loss_pct': profit_loss_pct,
                            'weeks_to_exit': i + 1,
                            'tail_strength': tail['signal_strength'],
                            'tail_reason': tail['reason']
                        }
                        opportunities.append(opportunity)
                        break  # Намерихме първата добра възможност за изход
            
            logger.info(f"Намерени {len(opportunities)} възможности за вход/изход")
            return opportunities
            
        except Exception as e:
            logger.error(f"Грешка при анализ на възможностите за вход/изход: {e}")
            return []
    
    def _export_tails_analysis(self, tails_analysis: list, entry_exit_analysis: list):
        """
        Експортира резултатите от анализа
        """
        try:
            # Създаваме директорията data ако не съществува
            os.makedirs('data', exist_ok=True)
            
            # Експортираме анализ на опашките
            with open('data/weekly_tails_analysis.txt', 'w', encoding='utf-8') as f:
                f.write("BNB Trading System - WEEKLY TAILS АНАЛИЗ\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"ПЕРИОД НА АНАЛИЗА: Последните {len(tails_analysis)} weekly tails\n")
                f.write(f"Генерирано на: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Статистика по тип опашка
                long_tails = [t for t in tails_analysis if t['signal'] == 'LONG']
                short_tails = [t for t in tails_analysis if t['signal'] == 'SHORT']
                hold_tails = [t for t in tails_analysis if t['signal'] == 'HOLD']
                
                f.write("СТАТИСТИКА ПО ТИП ОПАШКА:\n")
                f.write(f"  LONG опашки: {len(long_tails)} ({len(long_tails)/len(tails_analysis)*100:.1f}%)\n")
                f.write(f"  SHORT опашки: {len(short_tails)} ({len(short_tails)/len(tails_analysis)*100:.1f}%)\n")
                f.write(f"  HOLD опашки: {len(hold_tails)} ({len(hold_tails)/len(tails_analysis)*100:.1f}%)\n\n")
                
                # Най-силните опашки
                f.write("НАЙ-СИЛНИТЕ ОПАШКИ:\n")
                f.write("-" * 80 + "\n")
                
                # Сортираме по сила
                sorted_tails = sorted(tails_analysis, key=lambda x: x['signal_strength'], reverse=True)
                
                for i, tail in enumerate(sorted_tails[:20], 1):
                    f.write(f"{i:2d}. {tail['date'].strftime('%Y-%m-%d')} | {tail['signal']:5s} | "
                           f"Сила: {tail['signal_strength']:5.1f}% | Цена: ${tail['price']:8.2f} | "
                           f"{tail['reason']}\n")
                
                f.write("\n")
                
                # Детайлен анализ на всяка опашка
                f.write("ДЕТАЙЛЕН АНАЛИЗ НА ВСИЧКИ ОПАШКИ:\n")
                f.write("=" * 80 + "\n")
                
                for tail in tails_analysis:
                    f.write(f"Дата: {tail['date'].strftime('%Y-%m-%d')}\n")
                    f.write(f"Сигнал: {tail['signal']}\n")
                    f.write(f"Сила: {tail['signal_strength']:.1f}%\n")
                    f.write(f"Цена: ${tail['price']:.2f}\n")
                    f.write(f"Причина: {tail['reason']}\n")
                    f.write("-" * 40 + "\n")
            
            # Експортираме анализ на възможностите за вход/изход
            with open('data/entry_exit_opportunities.txt', 'w', encoding='utf-8') as f:
                f.write("BNB Trading System - ВЪЗМОЖНОСТИ ЗА ВХОД/ИЗХОД\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"НАМЕРЕНИ ВЪЗМОЖНОСТИ: {len(entry_exit_analysis)}\n")
                f.write(f"Генерирано на: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if not entry_exit_analysis:
                    f.write("Няма намерени възможности за вход/изход.\n")
                    return
                
                # Статистика по тип сигнал
                long_opportunities = [o for o in entry_exit_analysis if o['signal_type'] == 'LONG']
                short_opportunities = [o for o in entry_exit_analysis if o['signal_type'] == 'SHORT']
                
                f.write("СТАТИСТИКА ПО ТИП СИГНАЛ:\n")
                f.write(f"  LONG възможности: {len(long_opportunities)}\n")
                f.write(f"  SHORT възможности: {len(short_opportunities)}\n\n")
                
                # Среден P&L
                if entry_exit_analysis:
                    avg_profit = np.mean([o['profit_loss_pct'] for o in entry_exit_analysis])
                    avg_weeks = np.mean([o['weeks_to_exit'] for o in entry_exit_analysis])
                    
                    f.write("ОБЩА СТАТИСТИКА:\n")
                    f.write(f"  Среден P&L: {avg_profit:.2f}%\n")
                    f.write(f"  Средно време до изход: {avg_weeks:.1f} седмици\n\n")
                
                # Най-добрите възможности
                f.write("НАЙ-ДОБРИТЕ ВЪЗМОЖНОСТИ (по P&L):\n")
                f.write("-" * 80 + "\n")
                
                # Сортираме по P&L
                sorted_opportunities = sorted(entry_exit_analysis, key=lambda x: x['profit_loss_pct'], reverse=True)
                
                for i, opp in enumerate(sorted_opportunities[:20], 1):
                    f.write(f"{i:2d}. {opp['entry_date'].strftime('%Y-%m-%d')} | {opp['signal_type']:5s} | "
                           f"Вход: ${opp['entry_price']:8.2f} | Изход: ${opp['exit_price']:8.2f} | "
                           f"P&L: {opp['profit_loss_pct']:+6.2f}% | "
                           f"Седмици: {opp['weeks_to_exit']}\n")
                
                f.write("\n")
                
                # Детайлен анализ на всяка възможност
                f.write("ДЕТАЙЛЕН АНАЛИЗ НА ВЪЗМОЖНОСТИТЕ:\n")
                f.write("=" * 80 + "\n")
                
                for opp in entry_exit_analysis:
                    f.write(f"ВХОД: {opp['entry_date'].strftime('%Y-%m-%d')} | {opp['signal_type']} | ${opp['entry_price']:.2f}\n")
                    f.write(f"ИЗХОД: {opp['exit_date'].strftime('%Y-%m-%d')} | ${opp['exit_price']:.2f}\n")
                    f.write(f"P&L: {opp['profit_loss_pct']:+.2f}% (${opp['profit_loss']:+.2f})\n")
                    f.write(f"Време до изход: {opp['weeks_to_exit']} седмици\n")
                    f.write(f"Сила на опашката: {opp['tail_strength']:.1f}%\n")
                    f.write(f"Причина: {opp['tail_reason']}\n")
                    f.write("-" * 40 + "\n")
            
            logger.info("Weekly tails анализ експортиран успешно")
            
        except Exception as e:
            logger.error(f"Грешка при експортиране на анализа: {e}")

def main():
    """Главна функция за анализ на weekly tails"""
    try:
        print("🔍 Анализ на всички Weekly Tails...")
        print("🎯 Цел: Намери колко пъти може да се влезе LONG/SHORT и да се излезе на печалба")
        
        # Създаваме анализатора
        analyzer = WeeklyTailsDetailedAnalyzer()
        
        # Анализираме всички weekly tails
        results = analyzer.analyze_all_weekly_tails(500)
        
        if 'error' in results:
            print(f"❌ Грешка: {results['error']}")
            return
        
        # Показваме резултатите
        tails_analysis = results['tails_analysis']
        entry_exit_analysis = results['entry_exit_analysis']
        
        print(f"\n📊 РЕЗУЛТАТИ ОТ АНАЛИЗА:")
        print(f"   Анализирани weekly tails: {len(tails_analysis)}")
        print(f"   Намерени възможности за вход/изход: {len(entry_exit_analysis)}")
        
        if entry_exit_analysis:
            # Статистика
            long_opps = [o for o in entry_exit_analysis if o['signal_type'] == 'LONG']
            short_opps = [o for o in entry_exit_analysis if o['signal_type'] == 'SHORT']
            
            print(f"   LONG възможности: {len(long_opps)}")
            print(f"   SHORT възможности: {len(short_opps)}")
            
            # Среден P&L
            avg_profit = np.mean([o['profit_loss_pct'] for o in entry_exit_analysis])
            print(f"   Среден P&L: {avg_profit:+.2f}%")
            
            # Най-добра възможност
            best_opp = max(entry_exit_analysis, key=lambda x: x['profit_loss_pct'])
            print(f"   Най-добра възможност: {best_opp['profit_loss_pct']:+.2f}% ({best_opp['signal_type']})")
        
        print(f"\n✅ Анализът е завършен успешно!")
        print(f"📁 Резултатите са записани в:")
        print(f"   - data/weekly_tails_analysis.txt")
        print(f"   - data/entry_exit_opportunities.txt")
        
    except Exception as e:
        logger.error(f"Критична грешка: {e}")
        print(f"❌ Критична грешка: {e}")

if __name__ == "__main__":
    main()
