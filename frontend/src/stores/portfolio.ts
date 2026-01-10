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

const defaultBank: Bank = { name: 'АО ЮниКредит Банк', regNumber: '1' }

function getPortfolioByBank(bankRegNumber: string): string {
  const num = parseInt(bankRegNumber) % 5
  const portfolios = ['portfolio1', 'portfolio2', 'portfolio3', 'portfolio4', 'portfolio5']
  return portfolios[num] || 'portfolio1'
}

export const usePortfolioStore = defineStore('portfolio', () => {
  const selectedBank = ref<Bank>(() => {
    const saved = localStorage.getItem('selectedBank')
    return saved ? JSON.parse(saved) : defaultBank
  })

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

  return {
    selectedBank,
    positions,
    correlationMatrix,
    setSelectedBank
  }
})
