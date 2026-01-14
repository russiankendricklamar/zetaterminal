/**
 * Сервис для работы с оценкой свопов
 */

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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
  try {
    const response = await fetch(`${API_BASE_URL}/api/swap/valuate`, {
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
    console.error('Swap Valuation Failed:', error);
    throw error;
  }
};

/**
 * Сохраняет реестр свопов в Supabase Storage в формате parquet
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
        registry_type: 'swap',
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
