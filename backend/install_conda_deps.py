#!/usr/bin/env python3
"""
Скрипт для установки зависимостей в conda окружении.
Запустите этот файл из conda окружения: python install_conda_deps.py
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
    print(f"🐍 Python: {sys.executable}")
    print("=" * 60)
    
    try:
        # Используем pip из текущего окружения
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file, '--upgrade'],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Предупреждения:", result.stderr)
        print("✅ Зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке зависимостей:")
        print(e.stderr)
        return False

def main():
    """Главная функция"""
    print("🚀 Установка зависимостей для Zeta Terminal Backend")
    print(f"📍 Окружение: {os.environ.get('CONDA_DEFAULT_ENV', 'системное')}")
    print("=" * 60)
    print()
    
    # Устанавливаем зависимости
    success = install_requirements()
    print()
    
    if success:
        print("=" * 60)
        print("✅ Готово! Теперь вы можете запустить бэкенд:")
        print("   uvicorn src.main:app --reload --port 8000")
        print("   или")
        print("   python src/main.py")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Установка не удалась. Проверьте ошибки выше.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
