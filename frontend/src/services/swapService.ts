/**
 * Сервис для работы с оценкой свопов
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = getApiBaseUrl();

export interface SwapValuationRequest {
  notional: number;
  tenor: number;
  fixedRate: number;
  floatingRate: number;
  spread: number;
  couponsPerYear: number;
  discountRate: number;
  volatility?: number;
  swapType?: string;
}

export interface CashFlow {
  period: number;
  date: string;
  fixedLeg: number;
  floatingLeg: number;
  net: number;
  pv: number;
}

export interface SwapValuationResponse {
  pvFixedLeg: number;
  pvFloatingLeg: number;
  swapValue: number;
  duration: number;
  dv01: number;
  spreadDv01: number;
  convexity: number;
  cashflows: CashFlow[];
  scenarios: Array<{
    name: string;
    fixedRate: number;
    floatingRate: number;
    pvFixed: number;
    pvFloating: number;
    swapValue: number;
    pnl: number;
    isBase: boolean;
  }>;
}

/**
 * Выполняет оценку свопа
 */
export const valuateSwap = async (
  request: SwapValuationRequest
): Promise<SwapValuationResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/swap/valuate`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

// ============================================
// FX Swap types
// ============================================

export interface FxSwapLeg {
  buyCurrency: string;
  sellCurrency: string;
  nominalBuy: number;
  nominalSell: number;
  date: string;
}

export interface FxSwapValuationRequest {
  nearLeg: FxSwapLeg;
  farLeg: FxSwapLeg;
  valuationDate: string;
  settlementCurrency: string;
  spotMin: number;
  spotMax: number;
  rateInternal: number;
  rateExternal: number;
}

export interface FxSwapValuationResponse {
  currencyPair: string;
  direction: string;
  spotMin: number;
  spotMax: number;
  spotDiff: number;
  daysNear: number;
  daysFar: number;
  dfInternalNear: number;
  dfExternalNear: number;
  dfInternalFar: number;
  dfExternalFar: number;
  fxNear: number;
  fxFar: number;
  swapPointsDeal: number;
  swapPointsCalc: number;
  divergence: number;
  fvNearMin: number;
  fvNearMax: number;
  fvFarMin: number;
  fvFarMax: number;
  fvTotalMin: number;
  fvTotalMax: number;
  rateInternal: number;
  rateExternal: number;
}

/**
 * Выполняет оценку FX-свопа
 */
export const valuateFxSwap = async (
  request: FxSwapValuationRequest
): Promise<FxSwapValuationResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/swap/valuate-fx`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export { saveRegistryToParquet } from '@/utils/registryService';
