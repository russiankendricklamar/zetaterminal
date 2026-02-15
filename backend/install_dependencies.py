#!/usr/bin/env python3
"""
Скрипт для установки всех зависимостей бэкенда.
Запустите этот файл: python3 install_dependencies.py
"""
import subprocess
import sys
import os

def install_requirements():
    """Устанавливает зависимости из requirements.txt"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print(f"❌ Файл {requirements_file} не найден!")
        return False
    
    print("📦 Установка зависимостей из requirements.txt...")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file, '--upgrade'],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✅ Зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей:")
        print(e.stderr)
        return False

def create_env_file():
    """Создает .env файл из env.example если его нет"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    env_example = os.path.join(os.path.dirname(__file__), 'env.example')
    
    if os.path.exists(env_file):
        print("ℹ️  Файл .env уже существует, пропускаем создание.")
        return
    
    if not os.path.exists(env_example):
        print("⚠️  Файл env.example не найден, пропускаем создание .env")
        return
    
    print("📝 Создание .env файла из env.example...")
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Файл .env создан!")
    except Exception as e:
        print(f"⚠️  Не удалось создать .env файл: {e}")

def main():
    """Главная функция"""
    print("🚀 Установка зависимостей для Zeta Terminal Backend")
    print("=" * 60)
    
    # Создаем .env файл
    create_env_file()
    print()
    
    # Устанавливаем зависимости
    success = install_requirements()
    print()
    
    if success:
        print("=" * 60)
        print("✅ Готово! Теперь вы можете запустить бэкенд:")
        print("   python3 src/main.py")
        print("   или")
        print("   uvicorn src.main:app --reload --port 8000")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Установка не удалась. Проверьте ошибки выше.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
