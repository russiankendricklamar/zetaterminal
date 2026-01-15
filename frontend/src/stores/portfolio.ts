import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Bank {
  name: string
  regNumber: string
}

interface Position {
  symbol: string
  name: string
  price: string
  dayChange: number
  notional: number
  allocation: number
  targetAllocation: number
  color: string
}

const portfolioTemplates = {
  portfolio1: [
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 850000, allocation: 12, targetAllocation: 10, color: '#3b82f6' },
    { symbol: 'GAZP', name: 'Газпром', price: '187.30', dayChange: -0.48, notional: 720000, allocation: 10, targetAllocation: 12, color: '#10b981' },
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 650000, allocation: 9, targetAllocation: 8, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 580000, allocation: 8, targetAllocation: 9, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 510000, allocation: 7, targetAllocation: 6, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 480000, allocation: 6, targetAllocation: 7, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 450000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 420000, allocation: 5, targetAllocation: 6, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 4, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 350000, allocation: 4, targetAllocation: 5, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 320000, allocation: 4, targetAllocation: 4, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 300000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 280000, allocation: 3, targetAllocation: 4, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 260000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 240000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    { symbol: 'SU26238', name: 'ОФЗ 26238', price: '98.50', dayChange: 0.15, notional: 220000, allocation: 3, targetAllocation: 3, color: '#6366f1' },
    { symbol: 'SU26239', name: 'ОФЗ 26239', price: '99.20', dayChange: 0.08, notional: 200000, allocation: 2, targetAllocation: 3, color: '#8b5cf6' },
    { symbol: 'SU26240', name: 'ОФЗ 26240', price: '97.80', dayChange: -0.05, notional: 180000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'RU000A0ZZZN2', name: 'Газпром обл', price: '101.50', dayChange: 0.22, notional: 160000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0JX0J6', name: 'Роснефть обл', price: '100.30', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0K4', name: 'Лукойл обл', price: '99.90', dayChange: 0.12, notional: 120000, allocation: 1, targetAllocation: 2, color: '#ec4899' },
    { symbol: 'RU000A0JX0L2', name: 'Сбер обл', price: '102.10', dayChange: 0.25, notional: 100000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0M0', name: 'ВТБ обл', price: '98.70', dayChange: 0.10, notional: 90000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0N8', name: 'Альфа обл', price: '100.50', dayChange: 0.20, notional: 80000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0P3', name: 'Россельхоз обл', price: '99.40', dayChange: 0.15, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fecdd3' }
  ] as Position[],
  portfolio2: [
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 920000, allocation: 13, targetAllocation: 11, color: '#3b82f6' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 680000, allocation: 9, targetAllocation: 10, color: '#10b981' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 560000, allocation: 8, targetAllocation: 8, color: '#fbbf24' },
    { symbol: 'AFKS', name: 'АФК Система', price: '12.34', dayChange: -0.45, notional: 480000, allocation: 7, targetAllocation: 7, color: '#8b5cf6' },
    { symbol: 'FIVE', name: 'X5 Retail', price: '2345.67', dayChange: 1.85, notional: 420000, allocation: 6, targetAllocation: 6, color: '#ec4899' },
    { symbol: 'PHOR', name: 'ФосАгро', price: '5678.90', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'HYDR', name: 'РусГидро', price: '0.678', dayChange: 0.34, notional: 340000, allocation: 5, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'IRAO', name: 'Интер РАО', price: '3.456', dayChange: -0.23, notional: 300000, allocation: 4, targetAllocation: 4, color: '#84cc16' },
    { symbol: 'FEES', name: 'ФСК ЕЭС', price: '0.189', dayChange: 0.12, notional: 280000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'SNGS', name: 'Сургутнефтегаз', price: '45.67', dayChange: 0.89, notional: 260000, allocation: 4, targetAllocation: 3, color: '#a855f7' },
    { symbol: 'SNGSP', name: 'Сургутнефтегаз-п', price: '34.56', dayChange: 0.67, notional: 240000, allocation: 3, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'AFLT', name: 'Аэрофлот', price: '56.78', dayChange: -1.23, notional: 220000, allocation: 3, targetAllocation: 3, color: '#eab308' },
    { symbol: 'PIKK', name: 'ПИК', price: '890.12', dayChange: 0.45, notional: 200000, allocation: 3, targetAllocation: 2, color: '#22c55e' },
    { symbol: 'LSRG', name: 'ЛСР', price: '456.78', dayChange: -0.34, notional: 180000, allocation: 2, targetAllocation: 2, color: '#3b82f6' },
    { symbol: 'UPRO', name: 'Юнипро', price: '12.34', dayChange: 0.56, notional: 160000, allocation: 2, targetAllocation: 2, color: '#10b981' },
    { symbol: 'SU26241', name: 'ОФЗ 26241', price: '98.90', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26242', name: 'ОФЗ 26242', price: '99.60', dayChange: 0.12, notional: 120000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26243', name: 'ОФЗ 26243', price: '97.50', dayChange: -0.08, notional: 100000, allocation: 1, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'RU000A0ZZZN3', name: 'Газпром обл', price: '101.80', dayChange: 0.28, notional: 90000, allocation: 1, targetAllocation: 1, color: '#c084fc' },
    { symbol: 'RU000A0JX0J7', name: 'Роснефть обл', price: '100.60', dayChange: 0.22, notional: 80000, allocation: 1, targetAllocation: 1, color: '#d946ef' },
    { symbol: 'RU000A0JX0K5', name: 'Лукойл обл', price: '100.20', dayChange: 0.15, notional: 70000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0L3', name: 'Сбер обл', price: '102.40', dayChange: 0.30, notional: 60000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0M1', name: 'ВТБ обл', price: '99.00', dayChange: 0.12, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0N9', name: 'Альфа обл', price: '100.80', dayChange: 0.25, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0P4', name: 'Россельхоз обл', price: '99.70', dayChange: 0.18, notional: 40000, allocation: 1, targetAllocation: 1, color: '#fecdd3' }
  ] as Position[],
  portfolio3: [
    { symbol: 'GAZP', name: 'Газпром', price: '187.30', dayChange: -0.48, notional: 980000, allocation: 14, targetAllocation: 12, color: '#10b981' },
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 780000, allocation: 11, targetAllocation: 11, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 640000, allocation: 9, targetAllocation: 9, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 520000, allocation: 7, targetAllocation: 7, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 460000, allocation: 6, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 400000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 360000, allocation: 5, targetAllocation: 5, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 320000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 300000, allocation: 4, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 280000, allocation: 4, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 260000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 240000, allocation: 3, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 220000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 200000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 180000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26244', name: 'ОФЗ 26244', price: '98.30', dayChange: 0.20, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26245', name: 'ОФЗ 26245', price: '99.10', dayChange: 0.14, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26246', name: 'ОФЗ 26246', price: '97.20', dayChange: -0.10, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN4', name: 'Газпром обл', price: '102.10', dayChange: 0.32, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J8', name: 'Роснефть обл', price: '100.90', dayChange: 0.26, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K6', name: 'Лукойл обл', price: '100.50', dayChange: 0.18, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L4', name: 'Сбер обл', price: '102.70', dayChange: 0.35, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M2', name: 'ВТБ обл', price: '99.30', dayChange: 0.14, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N0', name: 'Альфа обл', price: '101.10', dayChange: 0.28, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P5', name: 'Россельхоз обл', price: '100.00', dayChange: 0.20, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ] as Position[],
  portfolio4: [
    { symbol: 'SBER', name: 'Сбербанк', price: '285.50', dayChange: 1.24, notional: 1100000, allocation: 15, targetAllocation: 13, color: '#3b82f6' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 720000, allocation: 10, targetAllocation: 10, color: '#fbbf24' },
    { symbol: 'AFKS', name: 'АФК Система', price: '12.34', dayChange: -0.45, notional: 580000, allocation: 8, targetAllocation: 8, color: '#8b5cf6' },
    { symbol: 'FIVE', name: 'X5 Retail', price: '2345.67', dayChange: 1.85, notional: 500000, allocation: 7, targetAllocation: 7, color: '#ec4899' },
    { symbol: 'PHOR', name: 'ФосАгро', price: '5678.90', dayChange: -0.12, notional: 440000, allocation: 6, targetAllocation: 6, color: '#ef4444' },
    { symbol: 'HYDR', name: 'РусГидро', price: '0.678', dayChange: 0.34, notional: 400000, allocation: 6, targetAllocation: 5, color: '#06b6d4' },
    { symbol: 'IRAO', name: 'Интер РАО', price: '3.456', dayChange: -0.23, notional: 360000, allocation: 5, targetAllocation: 5, color: '#84cc16' },
    { symbol: 'FEES', name: 'ФСК ЕЭС', price: '0.189', dayChange: 0.12, notional: 320000, allocation: 4, targetAllocation: 4, color: '#f97316' },
    { symbol: 'SNGS', name: 'Сургутнефтегаз', price: '45.67', dayChange: 0.89, notional: 300000, allocation: 4, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'SNGSP', name: 'Сургутнефтегаз-п', price: '34.56', dayChange: 0.67, notional: 280000, allocation: 4, targetAllocation: 3, color: '#14b8a6' },
    { symbol: 'AFLT', name: 'Аэрофлот', price: '56.78', dayChange: -1.23, notional: 260000, allocation: 4, targetAllocation: 3, color: '#eab308' },
    { symbol: 'PIKK', name: 'ПИК', price: '890.12', dayChange: 0.45, notional: 240000, allocation: 3, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'LSRG', name: 'ЛСР', price: '456.78', dayChange: -0.34, notional: 220000, allocation: 3, targetAllocation: 2, color: '#3b82f6' },
    { symbol: 'UPRO', name: 'Юнипро', price: '12.34', dayChange: 0.56, notional: 200000, allocation: 3, targetAllocation: 2, color: '#10b981' },
    { symbol: 'MAGN', name: 'ММК', price: '45.67', dayChange: 0.23, notional: 180000, allocation: 2, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'SU26247', name: 'ОФЗ 26247', price: '98.70', dayChange: 0.22, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26248', name: 'ОФЗ 26248', price: '99.50', dayChange: 0.16, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26249', name: 'ОФЗ 26249', price: '97.00', dayChange: -0.12, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN5', name: 'Газпром обл', price: '102.40', dayChange: 0.36, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J9', name: 'Роснефть обл', price: '101.20', dayChange: 0.30, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K7', name: 'Лукойл обл', price: '100.80', dayChange: 0.22, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L5', name: 'Сбер обл', price: '103.00', dayChange: 0.40, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M3', name: 'ВТБ обл', price: '99.60', dayChange: 0.16, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N1', name: 'Альфа обл', price: '101.40', dayChange: 0.30, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P6', name: 'Россельхоз обл', price: '100.30', dayChange: 0.22, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ] as Position[],
  portfolio5: [
    { symbol: 'LKOH', name: 'Лукойл', price: '7456.75', dayChange: 0.92, notional: 1200000, allocation: 16, targetAllocation: 14, color: '#fbbf24' },
    { symbol: 'GMKN', name: 'Норникель', price: '18420.20', dayChange: -0.15, notional: 840000, allocation: 12, targetAllocation: 12, color: '#8b5cf6' },
    { symbol: 'YNDX', name: 'Яндекс', price: '3254.48', dayChange: 2.15, notional: 640000, allocation: 9, targetAllocation: 9, color: '#ec4899' },
    { symbol: 'ROSN', name: 'Роснефть', price: '456.80', dayChange: 1.05, notional: 560000, allocation: 8, targetAllocation: 8, color: '#ef4444' },
    { symbol: 'NVTK', name: 'Новатэк', price: '1234.50', dayChange: -0.32, notional: 480000, allocation: 7, targetAllocation: 6, color: '#06b6d4' },
    { symbol: 'TATN', name: 'Татнефть', price: '567.90', dayChange: 0.78, notional: 420000, allocation: 6, targetAllocation: 6, color: '#84cc16' },
    { symbol: 'ALRS', name: 'Алроса', price: '89.45', dayChange: -0.12, notional: 380000, allocation: 5, targetAllocation: 5, color: '#f97316' },
    { symbol: 'MGNT', name: 'Магнит', price: '6789.00', dayChange: 1.45, notional: 340000, allocation: 5, targetAllocation: 4, color: '#a855f7' },
    { symbol: 'MOEX', name: 'Московская биржа', price: '234.56', dayChange: 0.67, notional: 300000, allocation: 4, targetAllocation: 4, color: '#14b8a6' },
    { symbol: 'POLY', name: 'Полиметалл', price: '456.78', dayChange: -0.89, notional: 280000, allocation: 4, targetAllocation: 4, color: '#eab308' },
    { symbol: 'CHMF', name: 'Северсталь', price: '1234.56', dayChange: 1.23, notional: 260000, allocation: 4, targetAllocation: 3, color: '#22c55e' },
    { symbol: 'PLZL', name: 'Полюс', price: '9876.54', dayChange: -0.45, notional: 240000, allocation: 3, targetAllocation: 3, color: '#3b82f6' },
    { symbol: 'VTBR', name: 'ВТБ', price: '0.0234', dayChange: 0.12, notional: 220000, allocation: 3, targetAllocation: 3, color: '#10b981' },
    { symbol: 'NLMK', name: 'НЛМК', price: '145.30', dayChange: -0.28, notional: 200000, allocation: 3, targetAllocation: 2, color: '#6366f1' },
    { symbol: 'RTKM', name: 'Ростелеком', price: '89.45', dayChange: 0.65, notional: 180000, allocation: 2, targetAllocation: 2, color: '#fbbf24' },
    { symbol: 'SU26250', name: 'ОФЗ 26250', price: '98.10', dayChange: 0.24, notional: 160000, allocation: 2, targetAllocation: 2, color: '#8b5cf6' },
    { symbol: 'SU26251', name: 'ОФЗ 26251', price: '99.00', dayChange: 0.18, notional: 140000, allocation: 2, targetAllocation: 2, color: '#a78bfa' },
    { symbol: 'SU26252', name: 'ОФЗ 26252', price: '96.80', dayChange: -0.14, notional: 120000, allocation: 2, targetAllocation: 2, color: '#c084fc' },
    { symbol: 'RU000A0ZZZN6', name: 'Газпром обл', price: '102.70', dayChange: 0.40, notional: 100000, allocation: 1, targetAllocation: 2, color: '#d946ef' },
    { symbol: 'RU000A0JX0J0', name: 'Роснефть обл', price: '101.50', dayChange: 0.34, notional: 90000, allocation: 1, targetAllocation: 1, color: '#ec4899' },
    { symbol: 'RU000A0JX0K8', name: 'Лукойл обл', price: '101.10', dayChange: 0.25, notional: 80000, allocation: 1, targetAllocation: 1, color: '#f472b6' },
    { symbol: 'RU000A0JX0L6', name: 'Сбер обл', price: '103.30', dayChange: 0.45, notional: 70000, allocation: 1, targetAllocation: 1, color: '#fb7185' },
    { symbol: 'RU000A0JX0M4', name: 'ВТБ обл', price: '99.90', dayChange: 0.18, notional: 60000, allocation: 1, targetAllocation: 1, color: '#fda4af' },
    { symbol: 'RU000A0JX0N2', name: 'Альфа обл', price: '101.70', dayChange: 0.35, notional: 50000, allocation: 1, targetAllocation: 1, color: '#fecdd3' },
    { symbol: 'RU000A0JX0P7', name: 'Россельхоз обл', price: '100.60', dayChange: 0.25, notional: 45000, allocation: 1, targetAllocation: 1, color: '#fbbf24' }
  ] as Position[]
}

export const defaultBank: Bank = { name: 'АО ЮниКредит Банк', regNumber: '1' }

// List of all banks
const banksList: Bank[] = [
  { name: 'АО ЮниКредит Банк', regNumber: '1' },
  { name: 'АО "КАБ "Викинг"', regNumber: '2' },
  { name: 'ООО "Примтеркомбанк"', regNumber: '21' },
  { name: 'ПАО Банк "АЛЕКСАНДРОВСКИЙ"', regNumber: '53' },
  { name: 'АКБ "Энергобанк" (АО)', regNumber: '67' },
  { name: 'МОРСКОЙ БАНК (АО)', regNumber: '77' },
  { name: 'АО КБ "САММИТ БАНК"', regNumber: '85' },
  { name: 'АО "БКС Банк"', regNumber: '101' },
  { name: 'ПАО КБ "Сельмашбанк"', regNumber: '106' },
  { name: 'АО АКБ "ЦентроКредит"', regNumber: '121' },
  { name: 'АО "Авто Финанс Банк"', regNumber: '170' },
  { name: 'Прио-Внешторгбанк (ПАО)', regNumber: '212' },
  { name: 'ООО "СПЕЦСТРОЙБАНК"', regNumber: '236' },
  { name: 'АО КБ "Урал ФД"', regNumber: '249' },
  { name: 'АО КБ "Хлынов"', regNumber: '254' },
  { name: 'АО "ГУТА-БАНК"', regNumber: '256' },
  { name: 'АО "АБ "РОССИЯ"', regNumber: '328' },
  { name: 'ООО Банк "Саратов"', regNumber: '330' },
  { name: 'Банк ГПБ (АО)', regNumber: '354' },
  { name: 'АО "Витабанк"', regNumber: '356' },
  { name: 'АО Банк "Аверс"', regNumber: '415' },
  { name: 'ПАО КБ "УБРиР"', regNumber: '429' },
  { name: 'ПАО "СПБ Банк"', regNumber: '435' },
  { name: 'ПАО "Банк "Санкт-Петербург"', regNumber: '436' },
  { name: 'ООО "Камкомбанк"', regNumber: '438' },
  { name: 'АО "БАЛАКОВО-БАНК"', regNumber: '444' },
  { name: 'АО "Кубаньторгбанк"', regNumber: '478' },
  { name: 'АО "ТАТСОЦБАНК"', regNumber: '480' },
  { name: 'ООО КБ "РостФинанс"', regNumber: '481' },
  { name: 'ПАО "ЧЕЛИНДБАНК"', regNumber: '485' },
  { name: 'ПАО "Донкомбанк"', regNumber: '492' },
  { name: 'ПАО "ЧЕЛЯБИНВЕСТБАНК"', regNumber: '493' },
  { name: 'АО Банк "Венец"', regNumber: '524' },
  { name: 'АО КБ "Приобье"', regNumber: '537' },
  { name: 'ООО "Промсельхозбанк"', regNumber: '538' },
  { name: 'АО КБ "Солидарность"', regNumber: '554' },
  { name: 'АО "Банк Акцепт"', regNumber: '567' },
  { name: 'ООО "ЗЕМКОМБАНК"', regNumber: '574' },
  { name: 'АО АБ "Капитал"', regNumber: '575' },
  { name: 'АО БАНК "СНГБ"', regNumber: '588' },
  { name: 'АО "Великие Луки банк"', regNumber: '598' },
  { name: 'Банк ИПБ (АО)', regNumber: '600' },
  { name: 'АО "Первый Инвестиционный Банк"', regNumber: '604' },
  { name: 'ПАО Банк "Кузнецкий"', regNumber: '609' },
  { name: 'АО "Датабанк"', regNumber: '646' },
  { name: 'АО "Почта Банк"', regNumber: '650' },
  { name: 'ООО КБ "ГТ банк"', regNumber: '665' },
  { name: 'ПАО КБ "РусьРегионБанк"', regNumber: '685' },
  { name: 'Банк "Нальчик" ООО', regNumber: '695' },
  { name: 'ПАО "НИКО-БАНК"', regNumber: '702' },
  { name: 'АО Банк Синара', regNumber: '705' },
  { name: 'ООО КБЭР "Банк Казани"', regNumber: '708' },
  { name: 'АО УКБ "Белгородсоцбанк"', regNumber: '760' },
  { name: 'ООО "РУСБС"', regNumber: '779' },
  { name: 'АО "Роял Кредит Банк"', regNumber: '783' },
  { name: 'АО НКБ "СЛАВЯНБАНК"', regNumber: '804' },
  { name: '"Банк Заречье" (АО)', regNumber: '817' },
  { name: 'ООО "Вайлдберриз Банк"', regNumber: '841' },
  { name: 'ООО КБ "Кетовский"', regNumber: '842' },
  { name: 'АО "Дальневосточный банк"', regNumber: '843' },
  { name: 'КБ "Долинск" (АО)', regNumber: '857' },
  { name: 'Банк Пермь (АО)', regNumber: '875' },
  { name: 'ПАО "Норвик Банк"', regNumber: '902' },
  { name: 'АО "ВЛАДБИЗНЕСБАНК"', regNumber: '903' },
  { name: 'АО "Банк "Торжок"', regNumber: '933' },
  { name: 'ПАО "Совкомбанк"', regNumber: '963' },
  { name: 'АО "ПЕРВОУРАЛЬСКБАНК"', regNumber: '965' },
  { name: 'ООО КБ "Дружба"', regNumber: '990' },
  { name: 'Банк ВТБ (ПАО)', regNumber: '1000' },
  { name: 'ООО "Хакасский муниципальный банк"', regNumber: '1049' },
  { name: 'АО «ТелеПорт Банк»', regNumber: '1052' },
  { name: 'АО "РЕАЛИСТ БАНК"', regNumber: '1067' },
  { name: 'ПАО Комбанк "Химик"', regNumber: '1114' },
  { name: 'ООО "Костромаселькомбанк"', regNumber: '1115' },
  { name: 'ООО "Цифра банк"', regNumber: '1143' },
  { name: '"Братский АНКБ" АО', regNumber: '1144' },
  { name: 'ООО КБ "Калуга"', regNumber: '1151' },
  { name: 'АО "Кузнецкбизнесбанк"', regNumber: '1158' },
  { name: 'АО комбанк "Арзамас"', regNumber: '1281' },
  { name: 'ПАО "Банк Ставр"', regNumber: '1288' },
  { name: 'АО КБ "ВАКОБАНК"', regNumber: '1291' },
  { name: 'КБ "ЭНЕРГОТРАНСБАНК" (АО)', regNumber: '1307' },
  { name: 'АО Банк "ТКПБ"', regNumber: '1312' },
  { name: 'АО "Экономбанк"', regNumber: '1319' },
  { name: 'АО "АЛЬФА-БАНК"', regNumber: '1326' },
  { name: 'АО "Солид Банк"', regNumber: '1329' },
  { name: 'Банк "Левобережный" (ПАО)', regNumber: '1343' },
  { name: 'ПАО УКБ "Новобанк"', regNumber: '1352' },
  { name: 'ООО КБ "Уралфинанс"', regNumber: '1370' },
  { name: 'Банк "Снежинский" АО', regNumber: '1376' },
  { name: 'ООО банк "Элита"', regNumber: '1399' },
  { name: 'ПАО Сбербанк', regNumber: '1481' },
  { name: 'ПАО "РосДорБанк"', regNumber: '1573' },
  { name: 'АО "Тимер Банк"', regNumber: '1581' },
  { name: '"СДМ-Банк" (ПАО)', regNumber: '1637' },
  { name: 'ООО Банк Оранжевый', regNumber: '1659' },
  { name: 'Креди Агриколь КИБ АО', regNumber: '1680' },
  { name: 'ПАО "Томскпромстройбанк"', regNumber: '1720' },
  { name: 'АО "ИК Банк"', regNumber: '1732' },
  { name: 'ПАО "БыстроБанк"', regNumber: '1745' },
  { name: 'ООО "НОВОКИБ"', regNumber: '1747' },
  { name: 'АО МОСОБЛБАНК', regNumber: '1751' },
  { name: 'АО ЕАТПБанк', regNumber: '1765' },
  { name: 'АО КИБ "ЕВРОАЛЬЯНС"', regNumber: '1781' },
  { name: 'АО АКИБ "Почтобанк"', regNumber: '1788' },
  { name: 'АО БАНК "Ермак"', regNumber: '1809' },
  { name: '"Азиатско-Тихоокеанский Банк" (АО)', regNumber: '1810' },
  { name: 'МКБ "Дон-Тексбанк" ООО', regNumber: '1818' },
  { name: 'ООО "Инбанк"', regNumber: '1829' },
  { name: 'АКБ "ФОРА-БАНК" (АО)', regNumber: '1885' },
  { name: 'АО "Банк "Вологжанин"', regNumber: '1896' },
  { name: 'АКБ "Ланта-Банк" (АО)', regNumber: '1920' },
  { name: 'АО КБ "Модульбанк"', regNumber: '1927' },
  { name: 'АО "Банк ДАЛЕНА"', regNumber: '1948' },
  { name: 'АО БАНК НБС', regNumber: '1949' },
  { name: 'ПАО "НБД-Банк"', regNumber: '1966' },
  { name: 'ООО "АвтоКредитБанк"', regNumber: '1973' },
  { name: 'ПАО "МОСКОВСКИЙ КРЕДИТНЫЙ БАНК"', regNumber: '1978' },
  { name: '"СИБСОЦБАНК" ООО', regNumber: '2015' },
  { name: 'Банк "СЕРВИС РЕЗЕРВ" (АО)', regNumber: '2034' },
  { name: 'ООО "ЖИВАГО БАНК"', regNumber: '2065' },
  { name: 'ООО "АЛТЫНБАНК"', regNumber: '2070' },
  { name: 'КМ "Профильный Банк" (АО)', regNumber: '2103' },
  { name: 'АКБ "ПЕРЕСВЕТ" (ПАО)', regNumber: '2110' },
  { name: 'АО АКБ "Алеф-Банк"', regNumber: '2119' },
  { name: 'АКБ "НРБанк" (АО)', regNumber: '2170' },
  { name: 'АКБ "Форштадт" (АО)', regNumber: '2208' },
  { name: 'ТКБ БАНК ПАО', regNumber: '2210' },
  { name: 'АО "Банк Интеза"', regNumber: '2216' },
  { name: 'ПАО КБ "Центр-инвест"', regNumber: '2225' },
  { name: 'АО КБ "КОСМОС"', regNumber: '2245' },
  { name: 'АКБ "ТЕНДЕР-БАНК" (АО)', regNumber: '2252' },
  { name: 'ПАО "МТС-Банк"', regNumber: '2268' },
  { name: 'ПАО "БАНК УРАЛСИБ"', regNumber: '2275' },
  { name: 'АО "Банк Русский Стандарт"', regNumber: '2289' },
  { name: 'АКБ "Абсолют Банк" (ПАО)', regNumber: '2306' },
  { name: 'АО Банк Инго', regNumber: '2307' },
  { name: 'АКБ "БЭНК ОФ ЧАЙНА" (АО)', regNumber: '2309' },
  { name: 'АО "Банк ДОМ.РФ"', regNumber: '2312' },
  { name: 'ООО "Бланк банк"', regNumber: '2368' },
  { name: 'АО "НДБанк"', regNumber: '2374' },
  { name: 'Банк "ИТУРУП" (ООО)', regNumber: '2390' },
  { name: 'АО АКБ "ЕВРОФИНАНС МОСНАРБАНК"', regNumber: '2402' },
  { name: 'ООО КБ "МВС Банк"', regNumber: '2407' },
  { name: 'Банк Глобус (АО)', regNumber: '2438' },
  { name: 'ПАО АКБ "Металлинвестбанк"', regNumber: '2440' },
  { name: 'ПАО "МЕТКОМБАНК"', regNumber: '2443' },
  { name: 'АО "ГЕНБАНК"', regNumber: '2490' },
  { name: 'АО "Банк Кредит Свисс (Москва)"', regNumber: '2494' },
  { name: 'ИНГ БАНК (ЕВРАЗИЯ) АО', regNumber: '2495' },
  { name: 'ООО "Крона-Банк"', regNumber: '2499' },
  { name: 'ООО "банк Раунд"', regNumber: '2506' },
  { name: 'АО "Тольяттихимбанк"', regNumber: '2507' },
  { name: 'КБ "Кубань Кредит" ООО', regNumber: '2518' },
  { name: 'ЭКСИ-Банк (АО)', regNumber: '2530' },
  { name: 'АО КБ "Пойдём!"', regNumber: '2534' },
  { name: 'АО АКБ "НОВИКОМБАНК"', regNumber: '2546' },
  { name: 'АО Банк "ПСКБ"', regNumber: '2551' },
  { name: 'АО КБ "Ситибанк"', regNumber: '2557' },
  { name: '"ЗИРААТ БАНК (МОСКВА)" (АО)', regNumber: '2559' },
  { name: 'ИКБР "ЯРИНТЕРБАНК" (ООО)', regNumber: '2564' },
  { name: 'ООО БАНК "КУРГАН"', regNumber: '2568' },
  { name: 'Банк РМП (АО)', regNumber: '2574' },
  { name: 'Банк "КУБ" (АО)', regNumber: '2584' },
  { name: 'ПАО "АКИБАНК"', regNumber: '2587' },
  { name: 'ПАО "АК БАРС" БАНК', regNumber: '2590' },
  { name: 'АКБ "Алмазэргиэнбанк" АО', regNumber: '2602' },
  { name: 'АО "ИТ Банк"', regNumber: '2609' },
  { name: 'АО Банк "Объединенный капитал"', regNumber: '2611' },
  { name: 'АО АКБ "МЕЖДУНАРОДНЫЙ ФИНАНСОВЫЙ КЛУБ"', regNumber: '2618' },
  { name: 'КБ "Дж.П. Морган Банк Интернешнл" (ООО)', regNumber: '2629' },
  { name: 'АО АИКБ "Енисейский объединенный банк"', regNumber: '2645' },
  { name: 'АКБ "НООСФЕРА" (АО)', regNumber: '2650' },
  { name: 'ООО КБ "Алтайкапиталбанк"', regNumber: '2659' },
  { name: 'АКБ "СЛАВИЯ" (АО)', regNumber: '2664' },
  { name: 'АО "ТБанк"', regNumber: '2673' },
  { name: 'КБ "Крокус-Банк" (ООО)', regNumber: '2682' },
  { name: 'КБ "ЛОКО-Банк" (АО)', regNumber: '2707' },
  { name: '"Северный Народный Банк" (АО)', regNumber: '2721' },
  { name: 'БАНК "МСКБ" (АО)', regNumber: '2722' },
  { name: 'ПАО СКБ Приморья "Примсоцбанк"', regNumber: '2733' },
  { name: 'АКБ "Держава" ПАО', regNumber: '2738' },
  { name: 'АО "БМ-Банк"', regNumber: '2748' },
  { name: 'АО "НК Банк"', regNumber: '2755' },
  { name: 'ИНВЕСТТОРГБАНК АО', regNumber: '2763' },
  { name: 'АО "ОТП Банк"', regNumber: '2766' },
  { name: 'ЮГ-Инвестбанк (ПАО)', regNumber: '2772' },
  { name: 'ООО "АТБ" Банк', regNumber: '2776' },
  { name: 'АО МС Банк Рус', regNumber: '2789' },
  { name: 'АО РОСЭКСИМБАНК', regNumber: '2790' },
  { name: 'Банк "Вятич" (АО)', regNumber: '2796' },
  { name: 'АО "Банк ФИНАМ"', regNumber: '2799' },
  { name: 'Банк "Йошкар-Ола" (ПАО)', regNumber: '2802' },
  { name: 'АКБ "Трансстройбанк" (АО)', regNumber: '2807' },
  { name: 'АО "БАНК СГБ"', regNumber: '2816' },
  { name: 'АО КБ "Соколовский"', regNumber: '2830' },
  { name: 'ООО КБ "СИНКО-БАНК"', regNumber: '2838' },
  { name: 'ООО "СМЛТ Банк"', regNumber: '2846' },
  { name: 'ООО КБ "Столичный Кредит"', regNumber: '2853' },
  { name: '(АО "Банк "Агророс")', regNumber: '2860' },
  { name: 'АО "ИШБАНК"', regNumber: '2867' },
  { name: 'АКБ "Кузбассхимбанк" (ПАО)', regNumber: '2868' },
  { name: 'АО КБ "НИБ"', regNumber: '2876' },
  { name: 'ПАО АКБ "АВАНГАРД"', regNumber: '2879' },
  { name: 'АО КБ "АГРОПРОМКРЕДИТ"', regNumber: '2880' },
  { name: '"СОЦИУМ-БАНК" (ООО)', regNumber: '2881' },
  { name: '"БСТ-БАНК" АО', regNumber: '2883' },
  { name: 'ООО "Земский банк"', regNumber: '2900' },
  { name: '"Банк Кремлевский" ООО', regNumber: '2905' },
  { name: 'ООО КБ "АРЕСБАНК"', regNumber: '2914' },
  { name: 'ББР Банк (АО)', regNumber: '2929' },
  { name: 'КБ "НМБ" ООО', regNumber: '2932' },
  { name: 'АО "УРАЛПРОМБАНК"', regNumber: '2964' },
  { name: 'АО "ГОРБАНК"', regNumber: '2982' },
  { name: 'КБ "Байкалкредобанк" (АО)', regNumber: '2990' },
  { name: 'КБ "СТРОЙЛЕСБАНК" (ООО)', regNumber: '2995' },
  { name: 'ООО "ПроКоммерцБанк"', regNumber: '2996' },
  { name: 'АО "Углеметбанк"', regNumber: '2997' },
  { name: 'АО "Экспобанк"', regNumber: '2998' },
  { name: 'ПАО АКБ "Приморье"', regNumber: '3001' },
  { name: 'АО Банк "Развитие-Столица"', regNumber: '3013' },
  { name: '"Республиканский Кредитный Альянс" ООО', regNumber: '3017' },
  { name: 'АО "Яндекс Банк"', regNumber: '3027' },
  { name: '"Нацинвестпромбанк" (АО)', regNumber: '3077' },
  { name: '"Вэйбанк" АО', regNumber: '3095' },
  { name: 'АО "РФК-банк"', regNumber: '3099' },
  { name: 'ООО КБ "ЭКО-ИНВЕСТ"', regNumber: '3116' },
  { name: 'АО "НС Банк"', regNumber: '3124' },
  { name: 'АО "Таганрогбанк"', regNumber: '3136' },
  { name: 'АО "Банк БЖФ"', regNumber: '3138' },
  { name: 'ПАО "Контур.Банк"', regNumber: '3161' },
  { name: 'АО "МОСКОМБАНК"', regNumber: '3172' },
  { name: 'ООО КБ "ВНЕШФИНБАНК"', regNumber: '3173' },
  { name: 'ПАО "БАЛТИНВЕСТБАНК"', regNumber: '3176' },
  { name: 'КБ "Континенталь" ООО', regNumber: '3184' },
  { name: 'Эс-Би-Ай Банк ООО', regNumber: '3185' },
  { name: 'АО "Сити Инвест Банк"', regNumber: '3194' },
  { name: 'АО НОКССБАНК', regNumber: '3202' },
  { name: 'АО "Свой Банк"', regNumber: '3223' },
  { name: 'МП Банк (ООО)', regNumber: '3224' },
  { name: 'БАНК "АГОРА" ООО', regNumber: '3231' },
  { name: 'АО "СЭБ Банк"', regNumber: '3235' },
  { name: 'ПАО ФИНСТАР БАНК', regNumber: '3245' },
  { name: 'АО БАНК "МОСКВА-СИТИ"', regNumber: '3247' },
  { name: 'ПАО "Банк ПСБ"', regNumber: '3251' },
  { name: 'АО "Газэнергобанк"', regNumber: '3252' },
  { name: 'ПАО Банк ЗЕНИТ', regNumber: '3255' },
  { name: 'МКИБ "РОССИТА-БАНК" ООО', regNumber: '3257' },
  { name: 'АО "БАНК ОРЕНБУРГ"', regNumber: '3269' },
  { name: 'АО "Первый Дортрансбанк"', regNumber: '3271' },
  { name: 'Банк "ТРАСТ" (ПАО)', regNumber: '3279' },
  { name: 'Банк "ВБРР" (АО)', regNumber: '3287' },
  { name: 'АО "Райффайзенбанк"', regNumber: '3292' },
  { name: '"Русьуниверсалбанк" (ООО)', regNumber: '3293' },
  { name: 'АО "ПроБанк"', regNumber: '3296' },
  { name: 'АО "Классик Эконом Банк"', regNumber: '3298' },
  { name: 'АО "КОШЕЛЕВ-БАНК"', regNumber: '3300' },
  { name: 'Азия-Инвест Банк (АО)', regNumber: '3303' },
  { name: 'АО "Кредит Европа Банк (Россия)"', regNumber: '3311' },
  { name: 'ООО "Дойче Банк"', regNumber: '3328' },
  { name: 'АО "Денизбанк Москва"', regNumber: '3330' },
  { name: 'АО "КОММЕРЦБАНК (ЕВРАЗИЯ)"', regNumber: '3333' },
  { name: 'АО "Мидзухо Банк (Москва)"', regNumber: '3337' },
  { name: 'АО "МСП Банк"', regNumber: '3340' },
  { name: 'ООО "Мурманский расчетный Банк"', regNumber: '3341' },
  { name: 'АО "Россельхозбанк"', regNumber: '3349' },
  { name: 'КБ "Ренессанс Кредит" (ООО)', regNumber: '3354' },
  { name: 'КБ "Москоммерцбанк" (АО)', regNumber: '3365' },
  { name: 'КБ "Максима" (ООО)', regNumber: '3379' },
  { name: 'АО "Банк Финсервис"', regNumber: '3388' },
  { name: '"НТХ БАНК АО"', regNumber: '3390' },
  { name: '"Банк "МБА-МОСКВА" ООО', regNumber: '3395' },
  { name: 'АО "МБ Банк"', regNumber: '3396' },
  { name: 'АО КБ "РУСНАРБАНК"', regNumber: '3403' },
  { name: '"БНП ПАРИБА БАНК" АО', regNumber: '3407' },
  { name: 'КБ "РБА" (ООО)', regNumber: '3413' },
  { name: 'ООО "Банк РСИ"', regNumber: '3415' },
  { name: 'ООО "Унифондбанк"', regNumber: '3416' },
  { name: 'КБ "Новый век" (ООО)', regNumber: '3417' },
  { name: 'АО Банк "Национальный стандарт"', regNumber: '3421' },
  { name: 'ООО "Первый Клиентский Банк"', regNumber: '3436' },
  { name: '"Коммерческий Индо Банк" ООО', regNumber: '3446' },
  { name: 'Банк "РЕСО Кредит" (АО)', regNumber: '3450' },
  { name: 'ООО "Ю Би Эс Банк"', regNumber: '3463' },
  { name: 'АО "Эм-Ю-Эф-Джи Банк (Евразия)"', regNumber: '3465' },
  { name: 'АО КБ "ЮНИСТРИМ"', regNumber: '3467' },
  { name: 'Санкт-Петербургский банк инвестиций (АО)', regNumber: '3468' },
  { name: 'АО "Тойота Банк"', regNumber: '3470' },
  { name: 'ООО "МБ РУС Банк"', regNumber: '3473' },
  { name: 'АйСиБиСи Банк (АО)', regNumber: '3475' },
  { name: 'АО "Ури Банк"', regNumber: '3479' },
  { name: 'ООО "БМВ Банк"', regNumber: '3482' },
  { name: 'ООО "Ориджин Банк"', regNumber: '3490' },
  { name: 'АО "СМБСР Банк"', regNumber: '3494' },
  { name: 'ООО "Пихта Банк"', regNumber: '3500' },
  { name: 'АО "БАНК БЕРЕЙТ"', regNumber: '3505' },
  { name: '"СеверСтройБанк" АО', regNumber: '3507' },
  { name: 'ООО "Чайна Констракшн Банк"', regNumber: '3515' },
  { name: 'ООО "КЭБ ЭйчЭнБи Банк"', regNumber: '3525' },
  { name: 'АО "Банк ЧБРР"', regNumber: '3527' },
  { name: 'ООО "Чайнасельхозбанк"', regNumber: '3529' },
  { name: 'ЦМРБанк (ООО)', regNumber: '3531' },
  { name: 'АО "Банк 131"', regNumber: '3538' },
  { name: 'ООО "ОЗОН Банк"', regNumber: '3542' },
  { name: 'ООО Банк "Пэйджин"', regNumber: '3543' },
  { name: 'ООО "Банк Точка"', regNumber: '3545' }
]

function getPortfolioByBank(bankRegNumber: string): string {
  const num = parseInt(bankRegNumber) % 5
  const portfolios = ['portfolio1', 'portfolio2', 'portfolio3', 'portfolio4', 'portfolio5']
  return portfolios[num] || 'portfolio1'
}

export const usePortfolioStore = defineStore('portfolio', () => {
  // Инициализация selectedBank из localStorage или defaultBank
  const getInitialBank = (): Bank => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('selectedBank')
      if (saved) {
        try {
          return JSON.parse(saved)
        } catch (e) {
          console.error('Failed to parse selectedBank from localStorage:', e)
        }
      }
    }
    return defaultBank
  }
  
  const selectedBank = ref<Bank>(getInitialBank())

  const positions = computed<Position[]>(() => {
    if (!selectedBank.value) return portfolioTemplates.portfolio1
    const portfolioKey = getPortfolioByBank(selectedBank.value.regNumber)
    return portfolioTemplates[portfolioKey as keyof typeof portfolioTemplates] || portfolioTemplates.portfolio1
  })

  const correlationMatrix = computed(() => {
    const allAssets = [...positions.value]
    
    const getCorrelation = (symbol1: string, symbol2: string): number => {
      if (symbol1 === symbol2) return 1.0
      
      const isBond1 = symbol1.includes('SU') || symbol1.includes('RU000')
      const isBond2 = symbol2.includes('SU') || symbol2.includes('RU000')
      
      const hash = (str: string) => {
        let hash = 0
        for (let i = 0; i < str.length; i++) {
          hash = ((hash << 5) - hash) + str.charCodeAt(i)
          hash = hash & hash
        }
        return Math.abs(hash)
      }
      
      if (isBond1 && isBond2) {
        const seed = hash(symbol1 + symbol2) % 100
        return 0.7 + (seed / 100) * 0.2
      }
      
      if (!isBond1 && !isBond2) {
        const sameSector = 
          (symbol1.includes('SBER') && symbol2.includes('VTBR')) ||
          (symbol1.includes('VTBR') && symbol2.includes('SBER')) ||
          (symbol1.includes('GAZP') && symbol2.includes('ROSN')) ||
          (symbol1.includes('ROSN') && symbol2.includes('GAZP')) ||
          (symbol1.includes('LKOH') && symbol2.includes('TATN')) ||
          (symbol1.includes('TATN') && symbol2.includes('LKOH')) ||
          (symbol1.includes('NVTK') && symbol2.includes('GAZP')) ||
          (symbol1.includes('GAZP') && symbol2.includes('NVTK'))
        
        if (sameSector) {
          const seed = hash(symbol1 + symbol2) % 100
          return 0.6 + (seed / 100) * 0.3
        }
        const seed = hash(symbol1 + symbol2) % 100
        return 0.3 + (seed / 100) * 0.4
      }
      
      const seed = hash(symbol1 + symbol2) % 100
      return -0.1 + (seed / 100) * 0.3
    }
    
    return allAssets.map((asset) => {
      const values = allAssets.map((otherAsset) => {
        return getCorrelation(asset.symbol, otherAsset.symbol)
      })
      
      return {
        label: asset.symbol,
        values: values
      }
    })
  })

  function setSelectedBank(bank: Bank) {
    selectedBank.value = bank
    localStorage.setItem('selectedBank', JSON.stringify(bank))
  }

  const banks = ref<Bank[]>(banksList)

  return {
    selectedBank,
    positions,
    correlationMatrix,
    banks,
    setSelectedBank
  }
})
