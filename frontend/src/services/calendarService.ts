/**
 * Calendar Service — Nager.Date, Russian Calendar
 *
 * Proxied through backend at /api/calendar/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface PublicHoliday {
  date: string
  localName: string
  name: string
  countryCode: string
  fixed: boolean
  global: boolean
  types: string[]
}

export interface RussianCalendarDay {
  date: string
  type: 'holiday' | 'preholiday' | 'work_transfer'
  type_code: number
  name: string
}

export interface RussianCalendar {
  year: number
  country: string
  days: RussianCalendarDay[]
  total_holidays: number
  total_preholidays: number
  provider: string
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

export async function getPublicHolidays(countryCode: string, year: number): Promise<PublicHoliday[]> {
  return fetchJson(`${API_BASE}/api/calendar/holidays/${countryCode}/${year}`)
}

export async function getNextHolidays(countryCode: string): Promise<PublicHoliday[]> {
  return fetchJson(`${API_BASE}/api/calendar/next-holidays/${countryCode}`)
}

export async function isTodayHoliday(countryCode: string): Promise<{ is_holiday: boolean; country_code: string }> {
  return fetchJson(`${API_BASE}/api/calendar/is-today-holiday/${countryCode}`)
}

export async function getRussianCalendar(year: number): Promise<RussianCalendar> {
  return fetchJson(`${API_BASE}/api/calendar/russia/${year}`)
}
