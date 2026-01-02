"""
Модуль оценки облигаций через доходный подход (DCF)
Использует данные MOEX ISS API.
"""

import logging
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

BASE_ISS = "https://iss.moex.com/iss"

class BondPricer:
    """Класс для оценки облигаций и расчета метрик"""
    
    @staticmethod
    def fetch_bond_data(secid: str, from_date: str = "2000-01-01", day_count: int = 365) -> Dict:
        """
        Загружает параметры облигации из MOEX ISS API
        """
        try:
            # 1. Описание облигации
            desc_url = (
                f"{BASE_ISS}/securities/{secid}.json"
                "?iss.meta=off"
                "&iss.only=description"
                "&description.columns=name,title,value"
            )
            
            r = requests.get(desc_url, timeout=10)
            r.raise_for_status()
            data = r.json()
            rows = data["description"]["data"]
            params = {name: value for name, title, value in rows}
            
            if not params:
                raise ValueError(f"Облигация {secid} не найдена")

            face_value = float(params.get("FACEVALUE") or 0.0)
            coupon_percent = float(params.get("COUPONPERCENT") or 0.0)
            
            # Обработка дат
            issue_date_str = params.get("ISSUEDATE")
            mat_date_str = params.get("MATDATE")
            
            if not issue_date_str or not mat_date_str:
                raise ValueError("Не указана дата выпуска или погашения")
                
            issue_date = pd.to_datetime(issue_date_str)
            mat_date = pd.to_datetime(mat_date_str)
            
            # 2. Купоны и амортизация
            bond_url = (
                f"{BASE_ISS}/statistics/engines/stock/markets/bonds/bondization/{secid}.json"
                f"?from={from_date}"
                "&iss.only=coupons,amortizations"
                "&iss.meta=off"
            )
            
            rb = requests.get(bond_url, timeout=10)
            rb.raise_for_status()
            jb = rb.json()
            
            if "coupons" not in jb:
                raise RuntimeError("В bondization нет таблицы coupons")
            
            ctab = jb["coupons"]
            coupons_df = pd.DataFrame(ctab["data"], columns=ctab["columns"])
            
            if coupons_df.empty:
                raise RuntimeError("Нет данных по купонам")
            
            # Нормализация колонок
            date_col = "coupondate" if "coupondate" in coupons_df.columns else "date"
            
            if "value_rub" in coupons_df.columns:
                value_col = "value_rub"
            elif "value" in coupons_df.columns:
                value_col = "value"
            elif "VALUE" in coupons_df.columns:
                value_col = "VALUE"
            else:
                raise RuntimeError("Не найдена колонка с суммой купона")
            
            coupons_df[date_col] = pd.to_datetime(coupons_df[date_col])
            coupons_df[value_col] = coupons_df[value_col].astype(float)
            coupons_df = coupons_df.sort_values(date_col).reset_index(drop=True)
            
            coupons = coupons_df[date_col].tolist()
            
            # Определение частоты выплат
            if len(coupons) >= 2:
                period_days = (coupons[1] - coupons[0]).days
            else:
                period_days = 182 # Fallback to semi-annual
            
            payments_per_year = round(day_count / period_days) if period_days > 0 else 2
            
            # Генерация полных дат купонов (прошлые + будущие до погашения)
            coupon_dates_full = list(coupons)
            last = coupons[-1] if coupons else issue_date + pd.Timedelta(days=period_days)
            current = last
            
            # Достраиваем график, если API вернул не всё
            while current < mat_date:
                current = current + pd.Timedelta(days=period_days)
                if current < mat_date:
                    coupon_dates_full.append(current)
            
            # Всегда добавляем дату погашения как купонную дату (для выплаты номинала/купона)
            coupon_dates_full.append(mat_date)
            coupon_dates_full = sorted(list(set(coupon_dates_full)))
            
            # Маппинг известных значений
            coupon_map = {d.date(): v for d, v in zip(coupons_df[date_col], coupons_df[value_col])}
            last_coupon_value = coupons_df[value_col].iloc[-1] if not coupons_df.empty else 0.0
            
            # Заполняем значения
            coupon_values_full = [coupon_map.get(d.date(), last_coupon_value) for d in coupon_dates_full]
            
            return {
                "face_value": face_value,
                "coupon_percent": coupon_percent,
                "payments_per_year": payments_per_year,
                "issue_date": issue_date,
                "mat_date": mat_date,
                "coupon_dates_full": coupon_dates_full,
                "coupon_values_full": coupon_values_full,
            }

        except Exception as e:
            logger.error(f"Error fetching bond data for {secid}: {e}")
            raise

    @staticmethod
    def calculate_metrics(
        bond_data: Dict, 
        valuation_date: pd.Timestamp, 
        discount_yield: float,
        day_count: int = 365
    ) -> Dict:
        """
        Рассчитывает Dirty Price, Clean Price, НКД, Дюрацию
        """
        coupon_dates_full = bond_data["coupon_dates_full"]
        coupon_values_full = bond_data["coupon_values_full"]
        face_value = bond_data["face_value"]
        mat_date = bond_data["mat_date"]
        
        # 1. НКД (Accrued Interest)
        past_coupons = [d for d in coupon_dates_full if d <= valuation_date]
        future_coupons = [d for d in coupon_dates_full if d > valuation_date]
        
        nkd = 0.0
        if past_coupons and future_coupons:
            last_coupon_date = past_coupons[-1]
            next_coupon_date = future_coupons[0]
            
            coupon_period_days = (next_coupon_date - last_coupon_date).days
            days_since_last_coupon = (valuation_date - last_coupon_date).days
            
            # Находим индекс последнего купона для правильной суммы
            try:
                last_coupon_idx = coupon_dates_full.index(last_coupon_date)
                # Берем сумму следующего купона (так как она накапливается)
                if last_coupon_idx + 1 < len(coupon_values_full):
                    current_coupon_amount = coupon_values_full[last_coupon_idx + 1] 
                else:
                    current_coupon_amount = coupon_values_full[-1]
                    
                if coupon_period_days > 0:
                    nkd = current_coupon_amount * days_since_last_coupon / coupon_period_days
            except ValueError:
                pass

        # 2. Денежные потоки (Cash Flows)
        # Формируем DataFrame только для будущих выплат
        future_dates = []
        future_values = []
        
        for d, v in zip(coupon_dates_full, coupon_values_full):
            if d > valuation_date:
                future_dates.append(d)
                val = v
                # Если дата совпадает с погашением, добавляем номинал
                if d == mat_date:
                    val += face_value
                future_values.append(val)
        
        cf_df = pd.DataFrame({
            "date": future_dates,
            "cf": future_values
        })
        
        dirty_price = 0.0
        duration = 0.0
        cash_flows_detailed = []

        if not cf_df.empty:
            cf_df["t"] = (cf_df["date"] - valuation_date).dt.days / day_count
            cf_df["df"] = 1.0 / ((1.0 + discount_yield) ** cf_df["t"])
            cf_df["pv"] = cf_df["cf"] * cf_df["df"]
            
            dirty_price = cf_df["pv"].sum()
            
            # Дюрация Макалея
            if dirty_price > 0:
                weights = cf_df["pv"] / dirty_price
                duration = (weights * cf_df["t"]).sum()
            
            # Детализация для фронтенда
            for _, row in cf_df.iterrows():
                cash_flows_detailed.append({
                    "date": row["date"].isoformat(),
                    "t": float(row["t"]),
                    "cf": float(row["cf"]),
                    "df": float(row["df"]),
                    "pv": float(row["pv"])
                })
        
        clean_price = dirty_price - nkd
        
        # Полный список купонов для отображения
        all_coupons_detailed = []
        for d, v in zip(coupon_dates_full, coupon_values_full):
            all_coupons_detailed.append({
                "date": d.isoformat(),
                "value": float(v),
                "isPaid": bool(d <= valuation_date)
            })

        return {
            "dirtyPrice": float(dirty_price),
            "accruedInterest": float(nkd),
            "cleanPrice": float(clean_price),
            "pricePercent": float((clean_price / face_value * 100) if face_value else 0),
            "duration": float(duration),
            "cashFlows": cash_flows_detailed,
            "allCoupons": all_coupons_detailed
        }