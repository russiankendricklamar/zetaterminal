import { isTauri } from './apiBase'

let _tauriFetch: typeof globalThis.fetch | null = null

async function getTauriFetch(): Promise<typeof globalThis.fetch> {
  if (!_tauriFetch) {
    const mod = await import('@tauri-apps/plugin-http')
    _tauriFetch = mod.fetch as unknown as typeof globalThis.fetch
  }
  return _tauriFetch
}

export async function appFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  if (isTauri()) {
    const f = await getTauriFetch()
    return f(input, init)
  }
  return fetch(input, init)
}
