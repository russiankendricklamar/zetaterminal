/**
 * REPO Analysis API client
 */

import { getApiBaseUrl } from '@/utils/apiBase'
import { getApiKey } from '@/utils/apiHeaders'

const API_BASE_URL = getApiBaseUrl()

export interface TrafficMetric {
  metric: string
  value: number | null
  light: 'green' | 'yellow' | 'red' | 'gray'
}

export interface RepoAnalysisResponse {
  summary: {
    total_rows: number
    columns: string[]
  }
  chains: {
    nodes: number
    edges: number
    borrowers: string[]
    lenders: string[]
    intermediaries: string[]
    chains: string[][]
    graph_edges: { source: string; target: string; weight: number }[]
  }
  concentration: {
    hhi: number
    entropy: number
    cr3: number
    cr5: number
    cr10: number
    gini: number
    num_participants: number
    top_participants: { name: string; volume: number; share_pct: number }[]
  }
  collateral: {
    issuer_hhi: number | null
    haircut_stats: {
      mean: number | null
      median: number | null
      std: number | null
      min: number | null
      max: number | null
    } | null
    var_99_10d: number | null
  }
  coverage: {
    coverage_ratio: {
      mean: number
      median: number
      min: number
      below_1: number
    } | null
    wrong_way_risk: {
      count: number
      volume: number
      pct_of_total: number
    } | null
  }
  liquidity: {
    tenor_buckets: {
      bucket: string
      max_days: number
      volume: number
      share_pct: number
    }[]
    rollover_risk_pct: number
    total_volume: number
  }
  systemic: {
    centrality_table: {
      node: string
      degree: number
      betweenness: number
      pagerank: number
      eigenvector: number
      debt_rank: number
    }[]
    max_debt_rank: number
    num_nodes: number
    num_edges: number
    density: number
  }
  stress: {
    scenarios: {
      scenario: string
      stressed_haircut: number
      stressed_rate: number
      stressed_collateral: number
      coverage_ratio: number
      potential_loss: number
      rollover_shock: number
    }[]
    adversarial: {
      optimal_haircut_shock: number
      optimal_price_shock: number
      max_loss: number
    } | null
  }
  traffic_light: {
    metrics: TrafficMetric[]
    overall: 'green' | 'yellow' | 'red'
    recommendations: string[]
  }
}

export const analyzeRepo = async (file: File): Promise<RepoAnalysisResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const apiKey = getApiKey()
  const headers: Record<string, string> = {}
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`
  }

  const response = await fetch(`${API_BASE_URL}/api/repo/analyze`, {
    method: 'POST',
    headers,
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return await response.json()
}
