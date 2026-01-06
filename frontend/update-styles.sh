#!/bin/bash

# Скрипт для массового обновления стилей Apple Liquid Glass на всех страницах

PAGES_DIR="src/pages"

# Функция для обновления .glass-card
update_glass_card() {
  local file=$1
  # Ищем и заменяем старые стили .glass-card
  sed -i '' 's/backdrop-filter: blur(30px) saturate(160%);/backdrop-filter: blur(40px) saturate(180%);\n  -webkit-backdrop-filter: blur(40px) saturate(180%);/g' "$file"
  sed -i '' 's/backdrop-filter: blur(40px) saturate(160%);/backdrop-filter: blur(40px) saturate(180%);\n  -webkit-backdrop-filter: blur(40px) saturate(180%);/g' "$file"
  
  # Добавляем улучшенные тени если их нет
  if ! grep -q "inset 0 1px 0 rgba(255, 255, 255, 0.1)" "$file"; then
    sed -i '' 's/box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);/box-shadow: \n    0 20px 40px -10px rgba(0, 0, 0, 0.4),\n    inset 0 1px 0 rgba(255, 255, 255, 0.1);/g' "$file"
  fi
}

# Обновляем все .vue файлы
for file in "$PAGES_DIR"/*.vue; do
  if [ -f "$file" ]; then
    echo "Updating $file..."
    update_glass_card "$file"
  fi
done

echo "Done!"
