import type { HistoricalStatus } from '../types/contract'

export interface StatusInfo {
  label: string
  cls: string
  icon: string
}

export interface DirectionInfo {
  label: string
  icon: string
}

export interface VariationAssessment {
  label: string
  cls: string
  icon: string
}

export function statusInfo(estado: HistoricalStatus | string): StatusInfo {
  if (estado === 'procesado') {
    return { label: 'Disponible', cls: 'status-tag--ready', icon: 'check_circle' }
  }
  if (estado === 'pendiente_revision') {
    return { label: 'En revisión', cls: 'status-tag--review', icon: 'error' }
  }
  return { label: 'En integración', cls: 'status-tag--pending', icon: 'schedule' }
}

export function directionInfo(sentido: string): DirectionInfo {
  const normalized = normalizeText(sentido || '')
  if (normalized === 'ascendente') {
    return { label: 'Mayor es mejor', icon: 'arrow_upward' }
  }
  if (normalized === 'descendente') {
    return { label: 'Menor es mejor', icon: 'arrow_downward' }
  }
  if (normalized === 'regular') {
    return { label: 'Mantener en rango', icon: 'sync_alt' }
  }
  if (normalized === 'nominal') {
    return { label: 'Referencia nominal', icon: 'tag' }
  }
  return { label: 'No especificado', icon: 'remove' }
}

export function formatNumber(value: number): string {
  return value.toLocaleString('es-MX', { maximumFractionDigits: 2 })
}

export function formatValue(value: number | null | undefined, unidad?: string): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  const formatted = formatNumber(value)
  return unidad === 'Porcentaje' ? `${formatted} %` : formatted
}

export function formatVariation(diff: number | null | undefined, unidad?: string): string {
  if (diff === null || diff === undefined || Number.isNaN(diff)) return '—'
  const rounded = Math.round(diff * 100) / 100
  const prefix = rounded > 0 ? '+' : ''
  const suffix = unidad === 'Porcentaje' ? ' pp' : ''
  return `${prefix}${formatNumber(rounded === 0 ? 0 : rounded)}${suffix}`
}

export function assessVariation(diff: number | null | undefined, sentido: string): VariationAssessment | null {
  if (diff === null || diff === undefined || Number.isNaN(diff)) return null
  const rounded = Math.round(diff * 100) / 100
  const icon = rounded > 0
    ? 'trending_up'
    : rounded < 0
      ? 'trending_down'
      : 'trending_flat'
  const dir = normalizeText(sentido || '')
  if (rounded === 0 || (dir !== 'ascendente' && dir !== 'descendente')) {
    return { label: 'Sin cambio', cls: 'trend--neutral', icon }
  }
  const favorable = (dir === 'ascendente' && rounded > 0) || (dir === 'descendente' && rounded < 0)
  return favorable
    ? { label: 'Favorable', cls: 'trend--good', icon }
    : { label: 'Desfavorable', cls: 'trend--bad', icon }
}

export function normalizeText(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

export function formatDate(iso?: string): string {
  if (!iso) return ''
  const parsed = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(parsed.getTime())) return ''
  return parsed.toLocaleDateString('es-MX', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}
