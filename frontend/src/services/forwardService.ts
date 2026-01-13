/**
 * Сервис для работы с оценкой форвардов различных типов
 */

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface ForwardValuationRequest {
  forwardType: string;
  spotPrice: number;
  timeToMaturity: number;
  marketForwardPrice: number;
  contractSize?: number;
  
  // Cost-of-Carry параметры (для bond, commodity, equity, rate)
  dividendYield?: number;
  carryingCost?: number;
  convenienceYield?: number;
  riskFreeRate?: number;
  repoRate?: number;
  
  // FX параметры (для валютных форвардов)
  buyCurrency?: string;
  sellCurrency?: string;
  buyAmount?: number;
  sellAmount?: number;
  dealDate?: string;
  valuationDate?: string;
  expirationDate?: string;
  settlementCurrency?: string;
  internalRate?: number;
  externalRate?: number;
}

export interface ForwardValuationResponse {
  fairForwardPrice: number;
  forwardValue: number;
  intrinsicValue: number;
  timeValue: number;
  totalValue: number;
  delta: number;
  rho: number;
  netCarry: number;
  scenarios: Array<{
    id: number;
    name: string;
    spotPrice: number;
    change: number;
    forwardValue: number;
    pnlLong: number;
    pnlShort: number;
    isBase: boolean;
  }>;
  // Дополнительные поля для FX
  currencyPair?: string;
  forwardRateMin?: number;
  forwardRateMax?: number;
  forwardDiff?: number | string;
  fairValueMin?: number;
  fairValueMax?: number;
  discountFactorInternal?: number;
  discountFactorExternal?: number;
}

/**
 * Выполняет оценку форварда
 */
export const valuateForward = async (
  request: ForwardValuationRequest
): Promise<ForwardValuationResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/forward/valuate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Forward Valuation Failed:', error);
    throw error;
  }
};
