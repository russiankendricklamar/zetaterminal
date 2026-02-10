"""
Example Usage Script
Пример использования библиотеки для анализа акций
"""

from stock_template_processor import StockTemplateProcessor
from moex_iss_client import MoexISSClient


def example_1_basic_analysis():
    """
    Пример 1: Базовый анализ Газпрома за последний год
    """
    print("\n" + "="*70)
    print("ПРИМЕР 1: Базовый анализ Газпрома")
    print("="*70)

    processor = StockTemplateProcessor('GAZP')

    # Загрузка данных за последний год
    processor.fetch_all_data(
        start_date='2025-02-01',
        end_date='2026-02-10'
    )

    # Расчёт метрик
    metrics = processor.calculate_metrics(period_days=30)

    # Вывод результатов
    print(f"\nВолатильность (годовая): {metrics['volatility_annual']:.2f}%")
    print(f"β-коэффициент: {metrics['beta']:.4f}")
    print(f"3m ADTV: {metrics['adtv_3m']:.2f} млн ₽")
    print(f"Активность: {'✓ АКТИВНЫЙ' if metrics['is_active'] else '✗ НЕАКТИВНЫЙ'}")

    # Экспорт
    processor.export_to_excel('example_GAZP.xlsx')
    print("\n✅ Результат сохранён в example_GAZP.xlsx")


def example_2_multiple_tickers():
    """
    Пример 2: Сравнительный анализ нескольких акций
    """
    print("\n" + "="*70)
    print("ПРИМЕР 2: Сравнительный анализ")
    print("="*70)

    tickers = ['GAZP', 'SBER', 'LKOH', 'YNDX']
    results = []

    for ticker in tickers:
        print(f"\n⏳ Анализ {ticker}...")

        processor = StockTemplateProcessor(ticker)
        processor.fetch_all_data(start_date='2025-01-01', end_date='2026-01-01')
        metrics = processor.calculate_metrics()

        results.append({
            'Тикер': ticker,
            'Волатильность, %': round(metrics['volatility_annual'], 2),
            'β': round(metrics['beta'], 4),
            '3m ADTV, млн ₽': round(metrics['adtv_3m'], 2),
            'Активность': 'Да' if metrics['is_active'] else 'Нет'
        })

    # Вывод сравнительной таблицы
    import pandas as pd
    df_results = pd.DataFrame(results)
    print("\n" + "="*70)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print("="*70)
    print(df_results.to_string(index=False))


def example_3_custom_period():
    """
    Пример 3: Анализ за конкретный период с кастомными параметрами
    """
    print("\n" + "="*70)
    print("ПРИМЕР 3: Анализ Сбербанка за Q1 2024")
    print("="*70)

    processor = StockTemplateProcessor('SBER')

    # Q1 2024: январь-март
    processor.fetch_all_data(
        start_date='2024-01-01',
        end_date='2024-03-31'
    )

    # Оценка активности за 20 торговых дней
    metrics = processor.calculate_metrics(period_days=20)

    print(f"\nПериод: Q1 2024 (01.01.2024 - 31.03.2024)")
    print(f"Торговых дней: {metrics['n_trading_days']}")
    print(f"Средняя цена: {metrics['avg_price_year']:.2f} ₽")
    print(f"Волатильность: {metrics['volatility_annual']:.2f}%")
    print(f"β: {metrics['beta']:.4f}")


def example_4_direct_api_usage():
    """
    Пример 4: Прямое использование ISS API клиента
    """
    print("\n" + "="*70)
    print("ПРИМЕР 4: Прямое использование API")
    print("="*70)

    client = MoexISSClient()

    # 1. Поиск бумаги
    print("\n1. Поиск 'Газпром':")
    search_results = client.search_securities('Газпром', limit=5)
    print(search_results[['SECID', 'SHORTNAME', 'ISIN']].head())

    # 2. Информация о бумаге
    print("\n2. Спецификация GAZP:")
    info = client.get_security_info('GAZP')
    if 'description' in info:
        desc_df = info['description']
        important_fields = ['ISIN', 'EMITENT_TITLE', 'LISTLEVEL']
        for field in important_fields:
            row = desc_df[desc_df['name'] == field]
            if not row.empty:
                print(f"  {field}: {row['value'].iloc[0]}")

    # 3. Текущие данные
    print("\n3. Текущие рыночные данные:")
    market_data = client.get_market_data('GAZP')
    if not market_data.empty:
        if 'LAST' in market_data.columns:
            print(f"  Последняя цена: {market_data['LAST'].iloc[0]}")
        if 'VOLTODAY' in market_data.columns:
            print(f"  Объём торгов: {market_data['VOLTODAY'].iloc[0]:,.0f}")

    # 4. История индекса
    print("\n4. Последние 5 дней индекса IMOEX:")
    index_history = client.get_index_history('IMOEX', start_date='2026-02-01')
    if not index_history.empty:
        print(index_history[['TRADEDATE', 'CLOSE']].tail())


def example_5_beta_calculation():
    """
    Пример 5: Детальный расчёт β-коэффициента
    """
    print("\n" + "="*70)
    print("ПРИМЕР 5: Расчёт β для портфеля акций")
    print("="*70)

    import pandas as pd

    tickers = ['GAZP', 'SBER', 'LKOH']
    betas = []

    for ticker in tickers:
        processor = StockTemplateProcessor(ticker)
        processor.fetch_all_data(start_date='2024-01-01', end_date='2025-01-01')
        metrics = processor.calculate_metrics()

        betas.append({
            'Тикер': ticker,
            'β': metrics['beta'],
            'Интерпретация': (
                'Более волатилен, чем рынок' if metrics['beta'] > 1.0
                else 'Защитная акция' if metrics['beta'] < 1.0
                else 'Нейтральная'
            )
        })

    df_betas = pd.DataFrame(betas)
    print("\n" + df_betas.to_string(index=False))

    # Средневзвешенный β портфеля (равные веса)
    avg_beta = df_betas['β'].mean()
    print(f"\nСредневзвешенный β портфеля: {avg_beta:.4f}")


if __name__ == "__main__":
    # Запуск примеров
    example_1_basic_analysis()
    example_2_multiple_tickers()
    example_3_custom_period()
    example_4_direct_api_usage()
    example_5_beta_calculation()

    print("\n" + "="*70)
    print("✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ")
    print("="*70)
