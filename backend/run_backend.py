#!/usr/bin/env python3
"""
Скрипт для запуска бэкенда с автоматической установкой зависимостей.
Использует текущий Python интерпретатор.
"""
import sys
import os
import subprocess

def check_and_install_dependencies():
    """Проверяет и устанавливает зависимости при необходимости"""
    try:
        import dotenv
        import fastapi
        import uvicorn
        import numpy
        import pandas
        import scipy
        import cvxpy
        import pydantic
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"⚠️  Отсутствует зависимость: {e.name}")
        print("📦 Установка зависимостей...")
        
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if not os.path.exists(requirements_file):
            print(f"❌ Файл {requirements_file} не найден!")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', requirements_file, '--upgrade', '--quiet'],
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Зависимости установлены!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при установке зависимостей:")
            print(e.stderr)
            return False

def main():
    """Главная функция запуска"""
    print("🚀 Запуск Stochastic Dashboard Backend")
    print(f"🐍 Python: {sys.executable}")
    print("=" * 60)
    
    # Проверяем и устанавливаем зависимости
    if not check_and_install_dependencies():
        print("❌ Не удалось установить зависимости")
        sys.exit(1)
    
    print()
    print("🌐 Запуск сервера...")
    print("=" * 60)
    
    # Импортируем и запускаем uvicorn
    try:
        import uvicorn
        from dotenv import load_dotenv
        
        # Загружаем переменные окружения
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        debug = os.getenv("DEBUG", "true").lower() == "true"
        
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=debug
        )
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
