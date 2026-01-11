/**
 * Сервис для работы с оценкой облигаций (DCF)
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface BondValuationRequest {
  secid: string;
  valuationDate: string;
  discountYield1: number;
  discountYield2: number;
  dayCount?: number;
}

export interface ScenarioResults {
  dirtyPrice: number;
  cleanPrice: number;
  pricePercent: number;
  duration: number;
}

export interface CashFlow {
  date: string;
  t: number;
  cf: number;
  df: number;
  pv: number;
}

export interface Coupon {
  date: string;
  value: number;
  isPaid: boolean;
}

export interface BondValuationResponse {
  secid: string;
  faceValue: number;
  couponPercent: number;
  issueDate: string;
  maturityDate: string;
  paymentsPerYear: number;
  accruedInterest: number;
  scenario1: ScenarioResults;
  scenario2: ScenarioResults;
  cashFlows1: CashFlow[];
  cashFlows2: CashFlow[];
  allCoupons: Coupon[];
}

/**
 * Выполняет оценку облигации для двух сценариев доходности
 */
export const valuateBond = async (request: BondValuationRequest): Promise<BondValuationResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/bond/valuate`, {
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
    console.error('Bond Valuation Failed:', error);
    throw error;
  }
};
