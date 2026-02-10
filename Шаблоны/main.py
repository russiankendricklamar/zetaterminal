"""
Main Automation Script
Основной скрипт для автоматизированной генерации отчётов по акциям

Использование:
    python main.py --ticker GAZP --period 365
    python main.py --ticker SBER --start 2024-01-01 --end 2025-01-01
"""

import argparse
from datetime import datetime, timedelta
from stock_template_processor import StockTemplateProcessor


def parse_args():
    """
    Парсинг аргументов командной строки
    """
    parser = argparse.ArgumentParser(
        description='Автоматизированная генерация Template для акций'
    )

    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help='Тикер акции (например, GAZP, SBER)'
    )

    parser.add_argument(
        '--isin',
        type=str,
        default=None,
        help='ISIN код (опционально, определится автоматически)'
    )

    parser.add_argument(
        '--start',
        type=str,
        default=None,
        help='Начальная дата (YYYY-MM-DD), по умолчанию -365 дней'
    )

    parser.add_argument(
        '--end',
        type=str,
        default=None,
        help='Конечная дата (YYYY-MM-DD), по умолчанию сегодня'
    )

    parser.add_argument(
        '--period',
        type=int,
        default=365,
        help='Период в днях (используется если --start не указан)'
    )

    parser.add_argument(
        '--activity-days',
        type=int,
        default=30,
        help='Период для расчёта активности рынка (дней)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Имя выходного Excel файла (по умолчанию <TICKER>_automated.xlsx)'
    )

    parser.add_argument(
        '--engine',
        type=str,
        default='stock',
        help='Торговая система (stock, currency, futures)'
    )

    parser.add_argument(
        '--market',
        type=str,
        default='shares',
        help='Рынок (shares, bonds, index)'
    )

    parser.add_argument(
        '--board',
        type=str,
        default=None,
        help='Режим торгов (например, TQBR)'
    )

    return parser.parse_args()


def main():
    """
    Основная логика автоматизации
    """
    args = parse_args()

    # Определяем даты
    if args.end is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    else:
        end_date = args.end

    if args.start is None:
        start_date = (datetime.now() - timedelta(days=args.period)).strftime('%Y-%m-%d')
    else:
        start_date = args.start

    # Формируем имя выходного файла
    if args.output is None:
        output_file = f"{args.ticker}_automated.xlsx"
    else:
        output_file = args.output

    # Баннер
    print("=" * 70)
    print("  АВТОМАТИЗИРОВАННАЯ ГЕНЕРАЦИЯ TEMPLATE ДЛЯ АКЦИЙ")
    print("=" * 70)
    print(f"Тикер:        {args.ticker}")
    print(f"Период:       {start_date} → {end_date}")
    print(f"Активность:   {args.activity_days} дней")
    print(f"Выход:        {output_file}")
    print("=" * 70)
    print()

    try:
        # 1. Инициализация процессора
        print("⏳ Инициализация процессора...")
        processor = StockTemplateProcessor(
            ticker=args.ticker,
            isin=args.isin
        )

        # 2. Загрузка данных с МосБиржи
        print("\n⏳ Загрузка данных с MOEX ISS...")
        processor.fetch_all_data(
            start_date=start_date,
            end_date=end_date
        )

        # 3. Расчёт метрик
        print("\n⏳ Расчёт метрик...")
        metrics = processor.calculate_metrics(period_days=args.activity_days)

        # 4. Вывод ключевых метрик
        print("\n" + "=" * 70)
        print("  КЛЮЧЕВЫЕ МЕТРИКИ")
        print("=" * 70)
        print(f"Волатильность (год):       {metrics['volatility_annual']:.2f}%")
        print(f"β-коэффициент:              {metrics['beta']:.4f}")
        print(f"3m ADTV:                    {metrics['adtv_3m']:.2f} млн ₽")
        print(f"Средняя цена (год):         {metrics['avg_price_year']:.2f} ₽")
        print(f"Текущая цена:               {metrics['current_price']:.2f} ₽")
        print(f"Капитализация:              {metrics['mcap']/1e9:.2f} млрд ₽")
        print(f"Free-float:                 {metrics['free_float_pct']*100:.2f}%")
        print()
        print(f"Активность рынка:           {'✓ АКТИВНЫЙ' if metrics['is_active'] else '✗ НЕАКТИВНЫЙ'}")

        if not metrics['is_active']:
            print("\nКритерии активности:")
            for key, value in metrics['criteria'].items():
                status = "✓" if value else "✗"
                print(f"  {status} {key}")

        print("=" * 70)

        # 5. Генерация Template
        print("\n⏳ Генерация Template...")
        template = processor.generate_template()
        print(f"  ✓ Сгенерировано строк: {len(template)}")

        # 6. Экспорт в Excel
        print(f"\n⏳ Экспорт в Excel: {output_file}...")
        processor.export_to_excel(output_file)

        # 7. Финальное сообщение
        print("\n" + "=" * 70)
        print("  ✅ УСПЕШНО ЗАВЕРШЕНО")
        print("=" * 70)
        print(f"Файл сохранён: {output_file}")
        print()

    except Exception as e:
        print("\n" + "=" * 70)
        print("  ❌ ОШИБКА")
        print("=" * 70)
        print(f"{type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
