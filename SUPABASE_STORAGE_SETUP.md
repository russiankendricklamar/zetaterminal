# Настройка Supabase Storage для файлов

## Шаг 1: Создание Bucket в Supabase

1. В Supabase Dashboard перейди в **Storage**
2. Нажми **New bucket**
3. Настройки:
   - **Name:** `files`
   - **Public bucket:** OFF (приватный) или ON (публичный) - в зависимости от нужного доступа
   - Нажми **Create bucket**

## Шаг 2: Настройка политик доступа (RLS)

Если bucket приватный, нужно настроить политики:

1. В Storage → `files` bucket → **Policies**
2. Создай политики:

**Для чтения (SELECT):**
```sql
CREATE POLICY "Allow authenticated read"
ON storage.objects FOR SELECT
USING (bucket_id = 'files' AND auth.role() = 'authenticated');
```

**Для записи (INSERT):**
```sql
CREATE POLICY "Allow authenticated upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'files' AND auth.role() = 'authenticated');
```

**Для удаления (DELETE):**
```sql
CREATE POLICY "Allow authenticated delete"
ON storage.objects FOR DELETE
USING (bucket_id = 'files' AND auth.role() = 'authenticated');
```

Если нужен публичный доступ, используй:
```sql
CREATE POLICY "Allow public read"
ON storage.objects FOR SELECT
USING (bucket_id = 'files');
```

## Шаг 3: Структура папок

Рекомендуемая структура в Storage:
```
files/
  ├── reports/
  │   ├── 2026/
  │   │   ├── 01/
  │   │   │   ├── report_2026-01-13.pdf
  │   │   │   └── ...
  │   │   └── 02/
  │   └── ...
  ├── registers/
  │   ├── 2026/
  │   │   ├── 01/
  │   │   │   ├── register_2026-01-13.xlsx
  │   │   │   └── ...
  │   │   └── ...
  └── exports/
      └── ...
```

## Шаг 4: Использование через API

### Загрузка файла (через API endpoint)

**Пример через curl:**
```bash
curl -X POST https://your-api.com/api/files/upload \
  -F "file=@/path/to/file.pdf" \
  -F "file_type=report" \
  -F "description=Daily report"
```

**Пример через Python:**
```python
from src.database.storage import StorageService
from src.database.repositories import FileRepository
from src.database.models import FileRecord

storage = StorageService(bucket_name="files")
file_repo = FileRepository()

# Загрузить файл
with open("report.pdf", "rb") as f:
    file_info = storage.upload_file(
        file_path="reports/2026/01/report_2026-01-13.pdf",
        file_data=f,
        file_type="report",
        description="Daily bond report"
    )

# Сохранить метаданные в БД
file_record = FileRecord(
    file_name="report_2026-01-13.pdf",
    file_path=file_info["path"],
    file_type="report",
    file_size=file_info["size"],
    mime_type="application/pdf",
    description="Daily bond report"
)
file_repo.create(file_record)
```

### Получение файла

**Публичный URL (если bucket публичный):**
```python
url = storage.get_public_url("reports/2026/01/report.pdf")
```

**Подписанный URL (для приватных файлов):**
```python
url = storage.get_signed_url("reports/2026/01/report.pdf", expires_in=3600)
```

## Шаг 5: Автоматизация сохранения отчетов

### После генерации отчета:

```python
from src.database.storage import StorageService
from src.database.repositories import FileRepository
from src.database.models import FileRecord
import io

# Генерация отчета (например, в формате PDF или Excel)
report_data = generate_report()  # bytes или file-like object

# Загрузка в Storage
storage = StorageService()
file_path = storage.generate_file_path("reports", "report_2026-01-13.pdf")
file_info = storage.upload_file(
    file_path=file_path,
    file_data=io.BytesIO(report_data),
    file_type="report",
    description="Daily bond valuation report"
)

# Сохранение метаданных
file_repo = FileRepository()
file_record = FileRecord(
    file_name="report_2026-01-13.pdf",
    file_path=file_info["path"],
    file_type="report",
    file_size=file_info["size"],
    mime_type="application/pdf"
)
file_repo.create(file_record)
```

## Лимиты Supabase Storage

**Free tier:**
- 1 GB storage
- 2 GB bandwidth

**Pro tier ($25/мес):**
- 100 GB storage
- 200 GB bandwidth

## Полезные ссылки

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Storage Python Client](https://supabase.com/docs/reference/python/storage-createbucket)
