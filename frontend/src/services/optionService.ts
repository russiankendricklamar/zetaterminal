/**
 * Service for option pricing operations
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Сохраняет реестр опционов или поверхности волатильности в Supabase Storage в формате parquet
 */
export const saveRegistryToParquet = async (
  data: any[],
  registryType: 'option' | 'volatility_surface' = 'option'
): Promise<{ success: boolean; data: any }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/database/export/registry/parquet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        registry_type: registryType,
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
