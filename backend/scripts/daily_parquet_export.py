#!/usr/bin/env python3
"""
Скрипт для ежедневного экспорта данных в Parquet формат.
Можно запускать через cron или n8n.
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.database.parquet_export import ParquetExporter


def daily_export():
    """Ежедневный экспорт данных в Parquet."""
    exporter = ParquetExporter()
    
    # Экспорт рыночных данных за вчерашний день
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    results = []
    
    # Экспорт всех рыночных данных за вчера
    try:
        result = exporter.export_market_data_to_parquet(
            start_date=yesterday,
            end_date=today,
            file_name=f"market_data_daily_{yesterday}.parquet"
        )
        results.append(("market_data", "success", result))
        print(f"✓ Exported market data: {result['records_count']} records")
    except Exception as e:
        results.append(("market_data", "error", str(e)))
        print(f"✗ Error exporting market data: {e}")
    
    # Экспорт по типам данных
    for data_type in ["stock", "currency", "index"]:
        try:
            result = exporter.export_market_data_to_parquet(
                data_type=data_type,
                start_date=yesterday,
                end_date=today,
                file_name=f"market_data_{data_type}_{yesterday}.parquet"
            )
            results.append((f"market_data_{data_type}", "success", result))
            print(f"✓ Exported {data_type} data: {result['records_count']} records")
        except Exception as e:
            results.append((f"market_data_{data_type}", "error", str(e)))
            print(f"✗ Error exporting {data_type} data: {e}")
    
    print(f"\n{'='*50}")
    print(f"Export completed: {len([r for r in results if r[1] == 'success'])}/{len(results)} successful")
    
    return results


if __name__ == "__main__":
    print(f"Daily Parquet Export: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    daily_export()
