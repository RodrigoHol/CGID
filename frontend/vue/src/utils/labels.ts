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
    return { label: 'Con serie histórica', cls: 'status-tag--ready', icon: 'pi pi-chart-line' }
  }
  if (estado === 'pendiente_revision') {
    return { label: 'En revisión', cls: 'status-tag--pending', icon: 'pi pi-search' }
  }
  return { label: 'En integración', cls: 'status-tag--pending', icon: 'pi pi-clock' }
}

export function directionInfo(sentido: string): DirectionInfo {
  const normalized = normalizeText(sentido || '')
  if (normalized === 'ascendente') {
    return { label: 'Mayor es mejor', icon: 'pi pi-arrow-up' }
  }
  if (normalized === 'descendente') {
    return { label: 'Menor es mejor', icon: 'pi pi-arrow-down' }
  }
  if (normalized === 'regular') {
    return { label: 'Mantener en rango', icon: 'pi pi-arrows-h' }
  }
  return { label: 'No especificado', icon: 'pi pi-minus' }
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
    ? 'pi pi-arrow-up-right'
    : rounded < 0
      ? 'pi pi-arrow-down-right'
      : 'pi pi-minus'
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
