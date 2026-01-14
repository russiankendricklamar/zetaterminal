# Экспорт данных в формат Parquet

## Что такое Parquet?

Parquet - это колоночный формат данных, оптимизированный для аналитики:
- **Эффективное сжатие** (обычно в 5-10 раз меньше чем CSV)
- **Быстрые запросы** (читает только нужные колонки)
- **Поддержка типов данных** (сохраняет типы, даты, etc.)
- **Широко используется** в Big Data (Spark, Pandas, Polars, etc.)

## Использование

### 1. Экспорт через API

#### Экспорт рыночных данных:

```bash
# Все данные
curl -X POST https://your-api.com/api/db/export/market-data/parquet

# По тикеру
curl -X POST "https://your-api.com/api/db/export/market-data/parquet?ticker=SBER.ME"

# По датам
curl -X POST "https://your-api.com/api/db/export/market-data/parquet?start_date=2026-01-01&end_date=2026-01-31"

# По типу данных
curl -X POST "https://your-api.com/api/db/export/market-data/parquet?data_type=stock"
```

#### Экспорт таблицы:

```bash
curl -X POST https://your-api.com/api/db/export/table/market_data_daily/parquet
```

### 2. Использование в Python

```python
from src.database.parquet_export import ParquetExporter

exporter = ParquetExporter()

# Экспорт рыночных данных
result = exporter.export_market_data_to_parquet(
    ticker="SBER.ME",
    data_type="stock",
    start_date="2026-01-01",
    end_date="2026-01-31"
)

print(f"Exported to: {result['file_path']}")
print(f"Records: {result['records_count']}")

# Чтение Parquet файла
df = exporter.read_parquet_from_storage("exports/2026/01/market_data_20260113.parquet")
print(df.head())
```

### 3. Автоматический ежедневный экспорт

#### Через n8n:

```
Schedule Trigger (Cron: 0 1 * * *)  # Каждый день в 1:00
  → HTTP Request (POST /api/db/export/market-data/parquet)
  → Email/Slack (уведомление об успехе)
```

#### Через cron:

```bash
# Каждый день в 1:00
0 1 * * * cd /path/to/project/backend && python scripts/daily_parquet_export.py
```

#### Через скрипт:

```bash
cd backend
python scripts/daily_parquet_export.py
```

## Где хранятся файлы?

Parquet файлы сохраняются в **Supabase Storage** в bucket `files`:

```
files/
  └── exports/
      └── parquet/
          └── 2026/
              └── 01/
                  ├── market_data_20260113.parquet
                  ├── market_data_stock_20260113.parquet
                  └── ...
```

## Работа с Parquet файлами

### Чтение в Python:

```python
import pandas as pd

# Читать из локального файла
df = pd.read_parquet('data.parquet')

# Читать из URL (если файл публичный)
df = pd.read_parquet('https://your-storage.supabase.co/.../file.parquet')

# Читать через экспортер (из Storage)
from src.database.parquet_export import ParquetExporter
exporter = ParquetExporter()
df = exporter.read_parquet_from_storage('exports/2026/01/file.parquet')
```

### Чтение в других инструментах:

**Pandas:**
```python
df = pd.read_parquet('file.parquet')
```

**Polars (быстрее для больших данных):**
```python
import polars as pl
df = pl.read_parquet('file.parquet')
```

**Apache Spark:**
```python
df = spark.read.parquet('file.parquet')
```

**Python с PyArrow:**
```python
import pyarrow.parquet as pq
table = pq.read_table('file.parquet')
df = table.to_pandas()
```

## Преимущества Parquet для аналитики

1. **Меньший размер файлов** - сжатие до 10x
2. **Быстрые запросы** - читает только нужные колонки
3. **Сохранение типов** - даты остаются датами, числа - числами
4. **Разделение по партициям** - можно разделить по датам/типерам
5. **Стандартный формат** - поддерживается всеми аналитическими инструментами

## Примеры использования

### Анализ данных в Jupyter:

```python
import pandas as pd

# Загрузить данные
df = pd.read_parquet('market_data_20260113.parquet')

# Анализ
df.groupby('data_type')['price'].mean()
df[df['ticker'] == 'SBER.ME'].plot(x='date', y='price')
```

### Загрузка в базу данных:

```python
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_parquet('data.parquet')
engine = create_engine('postgresql://...')
df.to_sql('analytics_table', engine, if_exists='append')
```

## API Endpoints

- `POST /api/db/export/market-data/parquet` - экспорт рыночных данных
  - Query params: `ticker`, `data_type`, `start_date`, `end_date`, `file_name`
  
- `POST /api/db/export/table/{table_name}/parquet` - экспорт таблицы
  - Path param: `table_name`
  - Query param: `file_name`

## Лимиты

- Размер файла зависит от данных (обычно очень компактный)
- Supabase Storage Free tier: 1 GB (хватит на тысячи Parquet файлов)
- Рекомендуется использовать сжатие `snappy` (баланс скорости и размера)
