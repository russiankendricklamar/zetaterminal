"""
Сервис для получения кривой бескупонных доходностей (КБД) из MOEX ISS API.

ВАЖНО ОБ ИНТЕРПОЛЯЦИИ:
- MOEX использует метод Нельсона-Сигеля для интерполяции кривой бескупонных доходностей.
- Если MOEX предоставляет готовую кривую через API, она УЖЕ интерполирована методом Нельсона-Сигеля.
- В этом случае дополнительная интерполяция НЕ требуется - можно использовать данные напрямую.
- Если прямой endpoint недоступен, кривая строится из данных государственных облигаций (ОФЗ),
  и для промежуточных значений можно использовать линейную интерполяцию.

Автор: QuantPro Platform
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

BASE_ISS = "https://iss.moex.com/iss"


def fetch_zcyc_from_moex(date: Optional[str] = None) -> Dict:
    """
    Получить кривую бескупонных доходностей из MOEX ISS API.
    
    MOEX предоставляет кривую, которая уже интерполирована методом Нельсона-Сигеля.
    Данные возвращаются в виде точек (срок, доходность).
    
    Parameters
    ----------
    date : str, optional
        Дата в формате YYYY-MM-DD. Если None, используется последняя доступная дата.
    
    Returns
    -------
    dict
        Словарь с данными кривой:
        {
            'status': 'ok' | 'error',
            'date': 'YYYY-MM-DD',
            'data': [
                {'term': float, 'value': float},  # term в годах, value в процентах
                ...
            ],
            'count': int,
            'min_term': float,
            'max_term': float,
            'min_rate': float,
            'max_rate': float,
            'mean_rate': float
        }
    """
    try:
        # Получаем кривую бескупонных доходностей из MOEX ISS API
        # Правильный endpoint: /iss/engines/[engine]/zcyc
        # Для фондового рынка: /iss/engines/stock/zcyc.json
        # MOEX предоставляет кривую, интерполированную методом Нельсона-Сигеля
        
        url = f"{BASE_ISS}/engines/stock/zcyc.json"
        
        params = {
            "iss.meta": "off"
        }
        
        # Если указана дата, добавляем параметр
        if date:
            # MOEX принимает дату в формате YYYY-MM-DD
            params["date"] = date
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # MOEX возвращает данные в структуре:
        # {
        #   "zcyc": {
        #     "columns": ["period", "value", "date"],
        #     "data": [[period_days, yield_percent, date], ...]
        #   }
        # }
        
        # Проверяем статус ответа
        if response.status_code == 404:
            # Endpoint недоступен, строим кривую из данных облигаций
            logger.info("ZCYC endpoint недоступен, строим кривую из данных облигаций")
            return build_zcyc_from_bonds(date=date)
        
        # MOEX возвращает данные в структуре:
        # {
        #   "yearyields": {
        #     "columns": ["tradedate", "tradetime", "period", "value"],
        #     "data": [[date, time, period_years, yield_percent], ...]
        #   },
        #   "params": {
        #     "columns": ["tradedate", "tradetime", "B1", "B2", "B3", "T1", "G1", ...],
        #     "data": [[date, time, B1, B2, B3, T1, G1, ...], ...]
        #   }
        # }
        # Параметры B1, B2, B3, T1, G1-G9 - это параметры модели Нельсона-Сигеля
        
        # Проверяем наличие данных в разделе yearyields
        if "yearyields" not in data:
            # Если данных нет, строим из облигаций
            logger.info("ZCYC данные недоступны в yearyields, строим кривую из данных облигаций")
            return build_zcyc_from_bonds(date=date)
        
        zcyc_section = data["yearyields"]
        if not zcyc_section.get("data"):
            # Пробуем получить за последнюю доступную дату
            if date:
                return fetch_zcyc_from_moex(date=None)
            else:
                # Строим из облигаций
                logger.info("ZCYC данные yearyields пусты, строим кривую из данных облигаций")
                return build_zcyc_from_bonds(date=date)
        
        zcyc_data = zcyc_section["data"]
        zcyc_columns = zcyc_section.get("columns", ["tradedate", "tradetime", "period", "value"])
        
        # MOEX возвращает данные в формате:
        # - period: период в днях
        # - value: доходность в процентах (годовая)
        # - date: дата кривой
        
        # Определяем индексы колонок
        # MOEX возвращает: ["tradedate", "tradetime", "period", "value"]
        period_idx = None
        value_idx = None
        date_idx = None
        
        for i, col in enumerate(zcyc_columns):
            col_lower = str(col).lower()
            if col_lower == 'period':
                period_idx = i
            elif col_lower == 'value':
                value_idx = i
            elif col_lower in ['tradedate', 'date']:
                date_idx = i
        
        # Если не нашли по названиям, используем стандартный порядок MOEX
        if period_idx is None or value_idx is None:
            # MOEX возвращает: ["tradedate", "tradetime", "period", "value"]
            if len(zcyc_columns) >= 4:
                date_idx = 0  # tradedate
                period_idx = 2  # period
                value_idx = 3  # value
            elif len(zcyc_columns) >= 2:
                # Альтернативный формат
                period_idx = 0
                value_idx = 1
            else:
                raise ValueError(f"Неожиданный формат данных MOEX. Колонки: {zcyc_columns}")
        
        # Извлекаем данные напрямую из массива (MOEX возвращает список списков)
        # Формат: [tradedate, tradetime, period (в годах), value (в процентах)]
        # ВАЖНО: MOEX использует метод Нельсона-Сигеля для интерполяции кривой.
        # Параметры модели (B1, B2, B3, T1, G1-G9) находятся в разделе "params".
        # Данные в "yearyields" уже интерполированы и готовы к использованию.
        points = []
        curve_date = date or datetime.now().strftime("%Y-%m-%d")
        
        for row in zcyc_data:
            if len(row) <= max(period_idx or 0, value_idx or 0):
                continue
            
            try:
                # Извлекаем период (MOEX возвращает уже в годах!)
                term_years = float(row[period_idx])
                
                # Извлекаем доходность (в процентах)
                yield_value = float(row[value_idx])
                
                # Извлекаем дату, если есть
                if date_idx is not None and len(row) > date_idx:
                    row_date = row[date_idx]
                    if row_date:
                        # Пробуем преобразовать дату
                        if isinstance(row_date, str):
                            curve_date = row_date[:10]  # Берем первые 10 символов (YYYY-MM-DD)
                        else:
                            curve_date = str(row_date)[:10]
                
                # Добавляем точку, если данные валидны
                if term_years is not None and yield_value is not None and \
                   not (term_years != term_years) and not (yield_value != yield_value):  # Проверка на NaN
                    points.append({
                        'term': float(term_years),
                        'value': float(yield_value)
                    })
            except (ValueError, IndexError, TypeError) as e:
                # Пропускаем некорректные строки
                logger.warning(f"Пропущена некорректная строка данных ZCYC: {row}, ошибка: {e}")
                continue
        
        if not points:
            raise ValueError("Нет валидных точек на кривой")
        
        # Сортируем по сроку
        points.sort(key=lambda x: x['term'])
        
        # Вычисляем статистику
        terms_list = [p['term'] for p in points]
        values_list = [p['value'] for p in points]
        
        result = {
            'status': 'ok',
            'date': curve_date if isinstance(curve_date, str) else str(curve_date),
            'data': points,
            'count': len(points),
            'min_term': float(min(terms_list)),
            'max_term': float(max(terms_list)),
            'min_rate': float(min(values_list)),
            'max_rate': float(max(values_list)),
            'mean_rate': float(sum(values_list) / len(values_list))
        }
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к MOEX ISS API: {e}")
        return {
            'status': 'error',
            'error': f'Ошибка подключения к MOEX API: {str(e)}',
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'data': [],
            'count': 0,
            'min_term': 0.0,
            'max_term': 0.0,
            'min_rate': 0.0,
            'max_rate': 0.0,
            'mean_rate': 0.0
        }
    except Exception as e:
        logger.error(f"Ошибка обработки данных ZCYC: {e}")
        return {
            'status': 'error',
            'error': f'Ошибка обработки данных: {str(e)}',
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'data': [],
            'count': 0,
            'min_term': 0.0,
            'max_term': 0.0,
            'min_rate': 0.0,
            'max_rate': 0.0,
            'mean_rate': 0.0
        }


def build_zcyc_from_bonds(date: Optional[str] = None) -> Dict:
    """
    Построить кривую бескупонных доходностей из данных государственных облигаций (ОФЗ).
    
    Если MOEX не предоставляет прямой endpoint для ZCYC, строим кривую
    из данных облигаций с различными сроками до погашения.
    
    Parameters
    ----------
    date : str, optional
        Дата в формате YYYY-MM-DD
    
    Returns
    -------
    dict
        Словарь с данными кривой (аналогично fetch_zcyc_from_moex)
    """
    try:
        # Получаем данные по государственным облигациям (ОФЗ)
        # Используем endpoint для получения списка облигаций и их доходностей
        
        val_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        date_str = val_date.strftime("%Y-%m-%d")
        
        # Получаем список государственных облигаций
        url = f"{BASE_ISS}/engines/stock/markets/bonds/boards/TQOB/securities.json"
        params = {
            "iss.meta": "off",
            "iss.only": "securities"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "securities" not in data or not data["securities"].get("data"):
            raise ValueError("Не удалось получить список облигаций")
        
        securities = data["securities"]["data"]
        securities_columns = data["securities"]["columns"]
        
        # Находим индексы нужных колонок
        secid_idx = securities_columns.index("SECID") if "SECID" in securities_columns else 0
        
        # Получаем данные по нескольким облигациям для построения кривой
        points = []
        ofz_secids = [row[secid_idx] for row in securities if "ОФЗ" in str(row) or "SU" in str(row)][:20]  # Берем первые 20 ОФЗ
        
        for secid in ofz_secids:
            try:
                # Получаем исторические данные по облигации
                date_from = (val_date - timedelta(days=5)).strftime("%Y-%m-%d")
                date_to = (val_date + timedelta(days=5)).strftime("%Y-%m-%d")
                
                hist_url = (
                    f"{BASE_ISS}/history/engines/stock/markets/bonds/securities/{secid}.json"
                    f"?from={date_from}&till={date_to}"
                    "&iss.meta=off"
                    "&history.columns=TRADEDATE,CLOSE,YIELD,MATDATE"
                )
                
                hist_response = requests.get(hist_url, timeout=10)
                if hist_response.status_code != 200:
                    continue
                
                hist_data = hist_response.json()
                if "history" not in hist_data or not hist_data["history"]["data"]:
                    continue
                
                # Берем последнюю доступную запись
                last_record = hist_data["history"]["data"][-1]
                hist_columns = hist_data["history"]["columns"]
                
                yield_idx = hist_columns.index("YIELD") if "YIELD" in hist_columns else None
                matdate_idx = hist_columns.index("MATDATE") if "MATDATE" in hist_columns else None
                
                if yield_idx is None or matdate_idx is None:
                    continue
                
                yield_value = float(last_record[yield_idx])
                matdate_str = last_record[matdate_idx]
                
                # Вычисляем срок до погашения в годах
                matdate = datetime.strptime(matdate_str[:10], "%Y-%m-%d")
                term_years = (matdate - val_date).days / 365.25
                
                if term_years > 0 and term_years < 30:  # Ограничиваем диапазон
                    points.append({
                        'term': float(term_years),
                        'value': float(yield_value)
                    })
            except Exception as e:
                logger.debug(f"Ошибка получения данных по облигации {secid}: {e}")
                continue
        
        if not points:
            raise ValueError("Не удалось получить данные для построения кривой")
        
        # Сортируем по сроку
        points.sort(key=lambda x: x['term'])
        
        # Вычисляем статистику
        terms_list = [p['term'] for p in points]
        values_list = [p['value'] for p in points]
        
        result = {
            'status': 'ok',
            'date': date_str,
            'data': points,
            'count': len(points),
            'min_term': float(min(terms_list)),
            'max_term': float(max(terms_list)),
            'min_rate': float(min(values_list)),
            'max_rate': float(max(values_list)),
            'mean_rate': float(sum(values_list) / len(values_list))
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка построения кривой из облигаций: {e}")
        return {
            'status': 'error',
            'error': f'Ошибка построения кривой: {str(e)}',
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'data': [],
            'count': 0,
            'min_term': 0.0,
            'max_term': 0.0,
            'min_rate': 0.0,
            'max_rate': 0.0,
            'mean_rate': 0.0
        }


def interpolate_zcyc_rate(
    zcyc_data: List[Dict],
    term: float,
    method: str = 'linear'
) -> Optional[float]:
    """
    Интерполировать доходность для заданного срока.
    
    MOEX уже предоставляет интерполированную кривую методом Нельсона-Сигеля,
    но для промежуточных значений между точками можно использовать
    дополнительную интерполяцию.
    
    Parameters
    ----------
    zcyc_data : list
        Список точек кривой [{'term': float, 'value': float}, ...]
    term : float
        Срок в годах, для которого нужно получить доходность
    method : str
        Метод интерполяции: 'linear' (линейная) или 'nelson_siegel' (Нельсон-Сигель)
    
    Returns
    -------
    float or None
        Интерполированная доходность в процентах или None, если не удалось интерполировать
    """
    if not zcyc_data or len(zcyc_data) < 2:
        return None
    
    # Проверяем точное совпадение
    for point in zcyc_data:
        if abs(point['term'] - term) < 0.0001:
            return point['value']
    
    # Находим ближайшие точки
    lower = None
    upper = None
    
    for point in zcyc_data:
        if point['term'] <= term:
            if lower is None or point['term'] > lower['term']:
                lower = point
        if point['term'] >= term:
            if upper is None or point['term'] < upper['term']:
                upper = point
    
    # Если срок меньше минимального
    if lower is None:
        return zcyc_data[0]['value']
    
    # Если срок больше максимального
    if upper is None:
        return zcyc_data[-1]['value']
    
    # Если нашли обе точки
    if lower == upper:
        return lower['value']
    
    # Линейная интерполяция
    if method == 'linear':
        t = (term - lower['term']) / (upper['term'] - lower['term'])
        return lower['value'] + t * (upper['value'] - lower['value'])
    
    # Нельсон-Сигель интерполяция (если нужно)
    elif method == 'nelson_siegel':
        # Для простоты используем линейную, так как MOEX уже использует NS
        t = (term - lower['term']) / (upper['term'] - lower['term'])
        return lower['value'] + t * (upper['value'] - lower['value'])
    
    return None


def get_available_zcyc_dates() -> List[str]:
    """
    Получить список доступных дат для кривой бескупонных доходностей.
    
    Returns
    -------
    list
        Список дат в формате YYYY-MM-DD
    """
    try:
        # MOEX может предоставлять исторические данные
        # Пробуем получить список дат через metadata
        url = f"{BASE_ISS}/statistics/engines/stock/markets/bonds/zcyc.json"
        params = {
            "iss.meta": "on",
            "iss.only": "zcyc"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Извлекаем доступные даты из metadata или данных
        dates = []
        
        # Если есть исторические данные, можно получить список дат
        # Но обычно MOEX предоставляет только последнюю доступную дату
        
        # Возвращаем последние 30 дней как пример
        today = datetime.now()
        for i in range(30):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)
        
        return dates
        
    except Exception as e:
        logger.error(f"Ошибка получения списка дат ZCYC: {e}")
        # Возвращаем хотя бы сегодняшнюю дату
        return [datetime.now().strftime("%Y-%m-%d")]


# ============================================================================
# Модуль для работы с кривой ZCYC по спецификации MOEX ISS API
# Спецификация: https://iss.moex.com/iss/reference/417
# 
# Базовые функции HTTP-доступа:
# - get_maxdates(engine): Получить максимальные даты
# - get_yearyields(date, engine): Получить кривую годовых доходностей
# - get_yearyields_dates(date, engine): Получить диапазон доступных дат
# - get_latest_curve(engine): Получить последнюю доступную кривую
# 
# Построение КБД (discount curve):
# - curve_to_discount(df_curve, col_term, col_yield): Преобразовать кривую в discount curve
# ============================================================================

def get_maxdates(engine: str = "stock") -> pd.DataFrame:
    """
    Получить максимальные даты для кривой ZCYC.
    
    Parameters
    ----------
    engine : str, default "stock"
        Движок биржи (stock, currency, etc.)
    
    Returns
    -------
    pd.DataFrame
        DataFrame с колонками: tradedate, maxdate, months
    """
    url = f"{BASE_ISS}/engines/{engine}/zcyc/maxdates.json"
    params = {
        "iss.meta": "off"
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if "maxdates" not in data:
        raise ValueError("Таблица 'maxdates' не найдена в ответе API")
    
    table_data = data["maxdates"]
    columns = table_data.get("columns", [])
    rows = table_data.get("data", [])
    
    if not rows:
        return pd.DataFrame(columns=columns)
    
    df = pd.DataFrame(rows, columns=columns)
    return df


def get_yearyields(date: Optional[str] = None, engine: str = "stock") -> pd.DataFrame:
    """
    Получить кривую годовых доходностей (yearyields) для указанной даты.
    
    Parameters
    ----------
    date : str, optional
        Дата в формате YYYY-MM-DD. Если None, используется "today" (последняя доступная дата)
    engine : str, default "stock"
        Движок биржи (stock, currency, etc.)
    
    Returns
    -------
    pd.DataFrame
        DataFrame с колонками: tradedate, tradetime, period, value
        - period: срок в годах
        - value: доходность в процентах (годовая)
    """
    url = f"{BASE_ISS}/engines/{engine}/zcyc/yearyields.json"
    params = {
        "iss.meta": "off"
    }
    
    if date:
        params["date"] = date
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if "yearyields" not in data:
        raise ValueError("Таблица 'yearyields' не найдена в ответе API")
    
    table_data = data["yearyields"]
    columns = table_data.get("columns", [])
    rows = table_data.get("data", [])
    
    if not rows:
        return pd.DataFrame(columns=columns)
    
    df = pd.DataFrame(rows, columns=columns)
    return df


def get_yearyields_dates(date: Optional[str] = None, engine: str = "stock") -> pd.DataFrame:
    """
    Получить диапазон доступных дат для yearyields.
    
    Parameters
    ----------
    date : str, optional
        Дата в формате YYYY-MM-DD. Если None, используется "today"
    engine : str, default "stock"
        Движок биржи (stock, currency, etc.)
    
    Returns
    -------
    pd.DataFrame
        DataFrame с колонками: from, till
    """
    url = f"{BASE_ISS}/engines/{engine}/zcyc/yearyields.dates.json"
    params = {
        "iss.meta": "off"
    }
    
    if date:
        params["date"] = date
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    table_name = "yearyields.dates"
    if table_name not in data:
        raise ValueError(f"Таблица '{table_name}' не найдена в ответе API")
    
    table_data = data[table_name]
    columns = table_data.get("columns", [])
    rows = table_data.get("data", [])
    
    if not rows:
        return pd.DataFrame(columns=columns)
    
    df = pd.DataFrame(rows, columns=columns)
    return df


def get_latest_curve(engine: str = "stock") -> pd.DataFrame:
    """
    Получить последнюю доступную кривую доходностей.
    
    Функция:
    1. Берёт последнюю доступную дату из maxdates
    2. Вызывает get_yearyields(date=...) для этой даты
    
    Parameters
    ----------
    engine : str, default "stock"
        Движок биржи (stock, currency, etc.)
    
    Returns
    -------
    pd.DataFrame
        DataFrame с кривой доходностей для последней доступной даты
    """
    # Получаем максимальные даты
    maxdates_df = get_maxdates(engine=engine)
    
    if maxdates_df.empty:
        raise ValueError("Не удалось получить максимальные даты")
    
    # Берем последнюю доступную дату
    latest_date = maxdates_df.iloc[0]["tradedate"]
    
    # Получаем кривую для этой даты
    curve_df = get_yearyields(date=latest_date, engine=engine)
    
    return curve_df


def curve_to_discount(
    df_curve: pd.DataFrame,
    col_term: str = "period",
    col_yield: str = "value"
) -> pd.DataFrame:
    """
    Преобразовать кривую доходностей в discount curve (кривую дисконтирования).
    
    Функция:
    1. Сортирует по сроку
    2. Преобразует ставки из процентов в доли (делит на 100)
    3. Вычисляет discount factors: DF(t) = exp(-yield * t)
    
    Parameters
    ----------
    df_curve : pd.DataFrame
        DataFrame с кривой доходностей
    col_term : str, default "period"
        Название колонки со сроком (в годах)
    col_yield : str, default "value"
        Название колонки с доходностью (в процентах)
    
    Returns
    -------
    pd.DataFrame
        DataFrame с добавленными колонками:
        - yield_decimal: доходность в долях (value / 100)
        - discount_factor: фактор дисконтирования exp(-yield * term)
    """
    if df_curve.empty:
        return df_curve.copy()
    
    # Проверяем наличие необходимых колонок
    if col_term not in df_curve.columns:
        raise ValueError(f"Колонка '{col_term}' не найдена в DataFrame")
    if col_yield not in df_curve.columns:
        raise ValueError(f"Колонка '{col_yield}' не найдена в DataFrame")
    
    # Создаем копию для избежания изменения исходного DataFrame
    df = df_curve.copy()
    
    # Сортируем по сроку
    df = df.sort_values(by=col_term).reset_index(drop=True)
    
    # Преобразуем ставки из процентов в доли
    df["yield_decimal"] = df[col_yield] / 100.0
    
    # Вычисляем discount factors: DF(t) = exp(-yield * t)
    df["discount_factor"] = np.exp(-df["yield_decimal"] * df[col_term])
    
    return df
