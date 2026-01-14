#!/usr/bin/env python3
"""
Скрипт для ежедневной загрузки рыночных данных.
Можно запускать через cron или n8n.
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.database.repositories import MarketDataRepository
from src.database.models import MarketDataDaily
from src.services.yfinance_service import (
    get_stock_info,
    get_bond_info,
    get_currency_rate,
    get_index_info
)

# Список инструментов для мониторинга
TICKERS = {
    "stocks": ["SBER.ME", "GAZP.ME", "LKOH.ME", "YNDX.ME", "ROSN.ME"],
    "bonds": ["SU26238RMFS4"],  # Пример ISIN облигации
    "currencies": ["USDRUB=X", "EURRUB=X"],
    "indices": ["IMOEX.ME"]  # Индекс Мосбиржи
}


def fetch_and_save_market_data():
    """Загружает рыночные данные и сохраняет в БД."""
    repo = MarketDataRepository()
    today = datetime.now().strftime("%Y-%m-%d")
    
    results = {
        "success": 0,
        "errors": 0,
        "errors_list": []
    }
    
    # Загрузка акций
    print(f"Загрузка данных акций...")
    for ticker in TICKERS["stocks"]:
        try:
            data = get_stock_info(ticker)
            record = MarketDataDaily(
                ticker=ticker,
                data_type="stock",
                date=today,
                price=data.get("price"),
                volume=data.get("volume"),
                change_percent=data.get("changePercent"),
                metadata={
                    "name": data.get("name"),
                    "marketCap": data.get("marketCap"),
                    "peRatio": data.get("peRatio"),
                    "currency": data.get("currency")
                }
            )
            repo.create_or_update(record)
            results["success"] += 1
            print(f"✓ {ticker}: {data.get('price')}")
        except Exception as e:
            results["errors"] += 1
            results["errors_list"].append(f"{ticker}: {str(e)}")
            print(f"✗ {ticker}: {str(e)}")
    
    # Загрузка валют
    print(f"\nЗагрузка данных валют...")
    for ticker in TICKERS["currencies"]:
        try:
            data = get_currency_rate(ticker.replace("=X", ""), "RUB")
            record = MarketDataDaily(
                ticker=ticker,
                data_type="currency",
                date=today,
                price=data.get("rate"),
                change_percent=data.get("changePercent"),
                metadata={
                    "base": data.get("base"),
                    "quote": data.get("quote")
                }
            )
            repo.create_or_update(record)
            results["success"] += 1
            print(f"✓ {ticker}: {data.get('rate')}")
        except Exception as e:
            results["errors"] += 1
            results["errors_list"].append(f"{ticker}: {str(e)}")
            print(f"✗ {ticker}: {str(e)}")
    
    # Загрузка индексов
    print(f"\nЗагрузка данных индексов...")
    for ticker in TICKERS["indices"]:
        try:
            data = get_index_info(ticker)
            record = MarketDataDaily(
                ticker=ticker,
                data_type="index",
                date=today,
                price=data.get("price"),
                change_percent=data.get("changePercent"),
                metadata={
                    "name": data.get("name")
                }
            )
            repo.create_or_update(record)
            results["success"] += 1
            print(f"✓ {ticker}: {data.get('price')}")
        except Exception as e:
            results["errors"] += 1
            results["errors_list"].append(f"{ticker}: {str(e)}")
            print(f"✗ {ticker}: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"Результаты: {results['success']} успешно, {results['errors']} ошибок")
    if results["errors_list"]:
        print("\nОшибки:")
        for error in results["errors_list"]:
            print(f"  - {error}")
    
    return results


if __name__ == "__main__":
    print(f"Запуск загрузки рыночных данных: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    fetch_and_save_market_data()
