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
  
  // Bond параметры
  accruedInterest?: number;
  couponRate?: number;
  couponFrequency?: number;
  faceValue?: number;
  lastCouponDate?: string;
  maturityDate?: string;
  dayCountConvention?: string;
  autoCalculateAI?: boolean;
  yieldCurveTenors?: number[];
  yieldCurveRates?: number[];
  
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
  // Дополнительные поля для Bond
  spotDirtyPrice?: number;
  forwardDirtyPrice?: number;
  aiForward?: number;
  pvCoupons?: number;
  couponSchedule?: Array<{
    couponNumber: number;
    couponDate: string;
    daysToPayment: number;
    yearsToPayment: number;
    couponAmount: number;
    discountRate: number;
    discountFactor: number;
    presentValue: number;
  }>;
  formulaBreakdown?: {
    spotCleanPrice: number;
    accruedInterestSpot: number;
    spotDirtyPrice: number;
    repoRate: number;
    timeToMaturity: number;
    financingCost: number;
    totalCouponsPV: number;
    forwardDirtyPriceBeforeAI: number;
    accruedInterestForward: number;
    forwardCleanPrice: number;
  };
  dv01?: number;
  convexity?: number;
  repoSensitivity?: number;
  daysToMaturity?: number;
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

/**
 * Сохраняет реестр форвардов в Supabase Storage в формате parquet
 */
export const saveRegistryToParquet = async (
  data: any[]
): Promise<{ success: boolean; data: any }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/database/export/registry/parquet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        registry_type: 'forward',
        data: data
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Save Registry to Parquet Failed:', error);
    throw error;
  }
};
