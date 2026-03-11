/**
 * Shared registry service — единая функция saveRegistryToParquet
 * вместо дублирования в bondService, swapService, forwardService, optionService.
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

export type RegistryType = 'bond' | 'swap' | 'forward' | 'option'

/**
 * Сохраняет реестр в серверное хранилище в формате Parquet.
 */
export const saveRegistryToParquet = async (
  registryType: RegistryType,
  data: Record<string, unknown>[]
): Promise<{ success: boolean; data: Record<string, unknown> }> => {
  const response = await fetch(`${getApiBaseUrl()}/api/database/export/registry/parquet`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({ registry_type: registryType, data }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}
