"""
Stock Template Processor
Обработка шаблона для акций на основе Excel-структуры

Использует:
- Данные из ISS MOEX API
- Расчёт метрик (волатильность, бета, активность)
- Генерация итогового Template
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from scipy.stats import linregress

from moex_iss_client import MoexISSClient


class StockTemplateProcessor:
    """
    Процессор для автоматизированного шаблона акций
    """

    def __init__(self, ticker: str, isin: Optional[str] = None):
        """
        Инициализация процессора

        Args:
            ticker: тикер акции (например, 'GAZP')
            isin: ISIN код (если известен)
        """
        self.ticker = ticker
        self.isin = isin
        self.client = MoexISSClient()

        # Хранилища данных
        self.security_info = None
        self.history_data = None
        self.market_data = None
        self.index_history = None
        self.ratings_data = None

        # Рассчитанные метрики
        self.metrics = {}

    def fetch_all_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """
        Загрузка всех необходимых данных с MOEX

        Args:
            start_date: начальная дата для исторических данных
            end_date: конечная дата
        """
        print(f"Загрузка данных для {self.ticker}...")

        # 1. Информация о ценной бумаге
        self.security_info = self.client.get_security_info(self.ticker)

        if not self.isin and 'description' in self.security_info:
            desc_df = self.security_info['description']
            isin_row = desc_df[desc_df['name'] == 'ISIN']
            if not isin_row.empty:
                self.isin = isin_row['value'].iloc[0]

        print(f"  ✓ ISIN: {self.isin}")

        # 2. Исторические котировки
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        self.history_data = self.client.get_security_history(
            self.ticker,
            start_date=start_date,
            end_date=end_date
        )
        print(f"  ✓ История: {len(self.history_data)} записей")

        # 3. Текущие рыночные данные
        self.market_data = self.client.get_market_data(self.ticker)
        print(f"  ✓ Рыночные данные: {len(self.market_data)} записей")

        # 4. История индекса МосБиржи (для расчёта беты)
        self.index_history = self.client.get_index_history(
            'IMOEX',
            start_date=start_date,
            end_date=end_date
        )
        print(f"  ✓ История индекса IMOEX: {len(self.index_history)} записей")

        print("Данные загружены.\n")

    def calculate_metrics(self, period_days: int = 30) -> Dict:
        """
        Расчёт ключевых метрик

        Args:
            period_days: период для расчёта активности (дней)

        Returns:
            Словарь с метриками
        """
        if self.history_data is None or self.history_data.empty:
            raise ValueError("Исторические данные не загружены. Вызовите fetch_all_data().")

        df = self.history_data.copy()

        # Фильтр по периоду активности
        end_date = df['TRADEDATE'].max()
        start_date = end_date - pd.Timedelta(days=period_days)
        df_period = df[df['TRADEDATE'] >= start_date].copy()

        # 1. Активность рынка
        n_trading_days = df_period['WAPRICE'].notna().sum()
        avg_trades_per_day = df_period['NUMTRADES'].mean()
        avg_volume = df_period['VOLUME'].mean()

        # 2. Капитализация и free-float (из security_info)
        mcap, free_float_pct = self._extract_capitalization()

        # 3. Средний дневной объём за 3 месяца (3m ADTV)
        df_3m = df[df['TRADEDATE'] >= (end_date - pd.Timedelta(days=90))].copy()
        adtv_3m = df_3m['VOLUME'].mean() / 1e6  # млн руб

        # 4. Волатильность (годовая)
        volatility_annual = self._calculate_volatility(df)

        # 5. β-коэффициент
        beta = self._calculate_beta(df, self.index_history)

        # 6. Средняя цена за год
        avg_price_year = df['WAPRICE'].mean()

        # 7. Текущая цена
        current_price = df['WAPRICE'].iloc[-1] if not df.empty else None

        # 8. Критерии активности
        free_float_value_rub = mcap * free_float_pct if mcap else 0
        avg_volume_pct = (avg_volume / free_float_value_rub * 100) if free_float_value_rub > 0 else 0

        criteria = {
            'days_criterion': n_trading_days >= period_days,  # каждый день
            'trades_criterion': avg_trades_per_day >= 10,
            'volume_criterion': avg_volume_pct >= 0.0001,
            'free_float_pct_criterion': free_float_pct >= 0.1,  # 10%
            'free_float_rub_criterion': free_float_value_rub >= 1e9  # 1 млрд
        }

        is_active = (
            criteria['days_criterion'] and
            criteria['trades_criterion'] and
            criteria['volume_criterion'] and
            criteria['free_float_rub_criterion']
        )

        self.metrics = {
            'n_trading_days': n_trading_days,
            'avg_trades_per_day': avg_trades_per_day,
            'avg_volume': avg_volume,
            'avg_volume_pct': avg_volume_pct,
            'mcap': mcap,
            'free_float_pct': free_float_pct,
            'free_float_value_rub': free_float_value_rub,
            'adtv_3m': adtv_3m,
            'volatility_annual': volatility_annual,
            'beta': beta,
            'avg_price_year': avg_price_year,
            'current_price': current_price,
            'is_active': is_active,
            'criteria': criteria
        }

        return self.metrics

    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """
        Расчёт годовой волатильности (Historical Volatility)

        Args:
            df: DataFrame с историческими данными

        Returns:
            Годовая волатильность (%)
        """
        df = df.copy()
        df = df.dropna(subset=['WAPRICE'])

        if len(df) < 2:
            return 0.0

        # Log-returns
        df['log_ret'] = np.log(df['WAPRICE'] / df['WAPRICE'].shift(1))

        # Дневная волатильность
        vol_daily = df['log_ret'].std()

        # Аннуализация (252 торговых дня)
        vol_annual = vol_daily * np.sqrt(252) * 100  # в процентах

        return vol_annual

    def _calculate_beta(
        self,
        stock_df: pd.DataFrame,
        index_df: pd.DataFrame
    ) -> float:
        """
        Расчёт β-коэффициента (регрессия доходностей акции на индекс)

        Args:
            stock_df: DataFrame с данными акции
            index_df: DataFrame с данными индекса

        Returns:
            β-коэффициент
        """
        if stock_df is None or stock_df.empty or index_df is None or index_df.empty:
            return 1.0  # нейтральное значение

        # Объединяем по дате
        stock_ret = stock_df[['TRADEDATE', 'WAPRICE']].copy()
        stock_ret = stock_ret.rename(columns={'WAPRICE': 'stock_price'})

        index_ret = index_df[['TRADEDATE', 'CLOSE']].copy()
        index_ret = index_ret.rename(columns={'CLOSE': 'index_price'})

        merged = pd.merge(stock_ret, index_ret, on='TRADEDATE', how='inner')

        if len(merged) < 30:  # минимум 30 точек для надёжной оценки
            return 1.0

        # Процентные доходности
        merged['stock_ret'] = merged['stock_price'].pct_change()
        merged['index_ret'] = merged['index_price'].pct_change()
        merged = merged.dropna()

        if len(merged) < 20:
            return 1.0

        # Линейная регрессия
        slope, intercept, r_value, p_value, std_err = linregress(
            merged['index_ret'],
            merged['stock_ret']
        )

        return slope

    def _extract_capitalization(self) -> Tuple[float, float]:
        """
        Извлечение капитализации и free-float из security_info

        Returns:
            (капитализация в руб, free-float в долях)
        """
        if self.market_data is None or self.market_data.empty:
            return 0.0, 0.0

        # Капитализация может быть в разных полях
        mcap = 0.0
        if 'MARKETPRICE' in self.market_data.columns and 'ISSUESIZE' in self.market_data.columns:
            price = self.market_data['MARKETPRICE'].iloc[0]
            issue_size = self.market_data['ISSUESIZE'].iloc[0]
            if price and issue_size:
                mcap = float(price) * float(issue_size)

        # Free-float - примерное значение (в реальности нужен отдельный источник)
        # Для Газпрома ~0.5% по историческим данным
        free_float = 0.005  # 0.5% - placeholder

        return mcap, free_float

    def generate_template(self) -> pd.DataFrame:
        """
        Генерация итогового Template (форматированный отчёт)

        Returns:
            DataFrame в формате Template листа
        """
        if not self.metrics:
            self.calculate_metrics()

        # Извлекаем данные из security_info
        desc = self.security_info.get('description', pd.DataFrame())

        def get_value(name: str) -> str:
            row = desc[desc['name'] == name]
            return row['value'].iloc[0] if not row.empty else 'N/A'

        emitent = get_value('EMITENT_TITLE')
        sector = get_value('SECTYPE')
        listing_level = get_value('LISTLEVEL')

        # Рейтинги (заглушка - требуется отдельный источник)
        ratings = {
            'expert_ra': 'N/A',
            'akra': 'N/A',
            'ncr': 'N/A',
            'raex_europe': 'N/A'
        }

        # Формируем Template
        template_data = [
            [f"{self.ticker}, акция об.", self.ticker, None, None],
            ["ISIN", self.isin, None, None],
            ["Эмитент", emitent, None, None],
            ["Сектор", sector, None, None],
            ["Тип долевой ц.б.", "Акции прочих резидентов (обыкновенные)", None, None],
            ["Коэффициент конвертации акций в депрасписки", "-", None, None],
            ["Место обращения ц. б.", "Московская биржа. Основная сессия", None, None],
            ["Кредитный рейтинг эмитента", None, None, None],
            ["Эксперт РА", ratings['expert_ra'], None, None],
            ["АКРА", ratings['akra'], None, None],
            ["НКР", ratings['ncr'], None, None],
            ["RAEX-Europe", ratings['raex_europe'], None, None],
            ["Параметры ценной бумаги", None, None, None],
            ["Дата регистрации", get_value('REGNUMBER'), None, None],
            ["Уровень листинга на МосБирже", f"{listing_level} уровень листинга", None, None],
            ["Рыночная капитализация, млн руб", f"{self.metrics['mcap']/1e6:.2f}", None, None],
            ["Количество акций в обращении, млн шт.", "N/A", None, None],
            ["Free-float, %", f"{self.metrics['free_float_pct']*100:.2f}", None, None],
            ["Free-float, млн руб", f"{self.metrics['free_float_value_rub']/1e6:.2f}", None, None],
            ["Анализируемый период", None, None, None],
            ["Активность рынка", "активный" if self.metrics['is_active'] else "неактивный", None, None],
            ["Критерии активности", None, None, None],
            ["Кол-во торговых дней за месяц", 
             "выполняется" if self.metrics['criteria']['days_criterion'] else "не выполняется",
             self.metrics['n_trading_days'], "≥21"],
            ["Кол-во сделок за 1 торговый день",
             "выполняется" if self.metrics['criteria']['trades_criterion'] else "не выполняется",
             f"{self.metrics['avg_trades_per_day']:.0f}", "≥10"],
            ["Объём сделок за 1 торговый день",
             "выполняется" if self.metrics['criteria']['volume_criterion'] else "не выполняется",
             f"{self.metrics['avg_volume_pct']:.6f}%", "≥0.0001%"],
            ["Free-float, %",
             "выполняется" if self.metrics['criteria']['free_float_pct_criterion'] else "не выполняется",
             f"{self.metrics['free_float_pct']*100:.2f}", "≥10%"],
            ["Free-float, млрд руб.",
             "выполняется" if self.metrics['criteria']['free_float_rub_criterion'] else "не выполняется",
             f"{self.metrics['free_float_value_rub']/1e9:.2f}", "≥1"],
            ["Рыночные показатели", None, None, None],
            ["Средний дневной объём торгов за 3 месяца (3m ADTV), млн. руб", 
             f"{self.metrics['adtv_3m']:.2f}", None, None],
            ["Средневзвешанная цена за последний день, руб",
             f"{self.metrics['current_price']:.2f}", None, None],
            ["Средняя цена акций за год",
             f"{self.metrics['avg_price_year']:.2f}", None, None],
            ["Волатильность курса акций за год",
             f"{self.metrics['volatility_annual']:.2f}%", None, None],
            ["β–коэффициент",
             f"{self.metrics['beta']:.4f}", None, None],
        ]

        df_template = pd.DataFrame(
            template_data,
            columns=['Параметр', 'Значение', 'Доп. инфо', 'Критерий']
        )

        return df_template

    def export_to_excel(self, filename: str = 'stock_template_output.xlsx'):
        """
        Экспорт данных в Excel (3 листа: Calculation, Template, Help Page)

        Args:
            filename: имя выходного файла
        """
        if self.history_data is None:
            raise ValueError("Данные не загружены. Вызовите fetch_all_data().")

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Лист 1: Calculation (сырые данные)
            self.history_data.to_excel(writer, sheet_name='Calculation', index=False)

            # Лист 2: Template (форматированный отчёт)
            template_df = self.generate_template()
            template_df.to_excel(writer, sheet_name='Template', index=False)

            # Лист 3: Метрики (справка)
            metrics_df = pd.DataFrame([self.metrics]).T
            metrics_df.columns = ['Значение']
            metrics_df.to_excel(writer, sheet_name='Metrics')

        print(f"✅ Данные экспортированы в {filename}")


# Пример использования
if __name__ == "__main__":
    # Инициализация
    processor = StockTemplateProcessor('GAZP')

    # Загрузка данных
    processor.fetch_all_data(
        start_date='2025-01-01',
        end_date='2026-01-01'
    )

    # Расчёт метрик
    metrics = processor.calculate_metrics(period_days=30)

    print("\n=== КЛЮЧЕВЫЕ МЕТРИКИ ===")
    print(f"Волатильность (год): {metrics['volatility_annual']:.2f}%")
    print(f"β-коэффициент: {metrics['beta']:.4f}")
    print(f"3m ADTV: {metrics['adtv_3m']:.2f} млн ₽")
    print(f"Активность: {'✓ активный' if metrics['is_active'] else '✗ неактивный'}")

    # Генерация Template
    template = processor.generate_template()
    print("\n=== TEMPLATE (первые 15 строк) ===")
    print(template.head(15))

    # Экспорт в Excel
    processor.export_to_excel('GAZP_automated.xlsx')
