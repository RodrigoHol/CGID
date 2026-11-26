import type { Baseline, HistoricalPoint, Indicator } from '../types/contract'
import { assessVariation, formatNumber, formatValue, formatVariation, normalizeText } from './labels'

export interface FormulaExplanation {
  text: string
  isFallback: boolean
}

export interface UnitExplanation {
  text: string
  isFallback: boolean
}

export interface VariationBaseOption {
  key: string
  label: string
  shortLabel: string
  year: number | null
  value: number
  kind: 'baseline' | 'series'
}

export interface TimeRemainingInfo {
  years: number
  months: number
  totalMonths: number
  label: string
  isExpired: boolean
}

export type ProgressStatus =
  | 'achieved'
  | 'in_progress'
  | 'regressed'
  | 'awaiting_post_baseline'
  | 'maintenance'
  | 'no_series'
  | 'incomplete_goal'

export type ProgressTone = 'good' | 'neutral' | 'bad'

export interface GoalProgress {
  status: ProgressStatus
  percent: number | null
  rawPercent: number | null
  barPercent: number
  tone: ProgressTone
  shortLabel: string
  badgeLabel: string
  detail: string
}

export interface ChartInterpretation {
  tone: ProgressTone
  icon: string
  text: string
}

function formatDeltaText(absDiff: number, unidad?: string): string {
  const rounded = Math.round(absDiff * 100) / 100
  const formatted = formatNumber(rounded === 0 ? 0 : rounded)
  if (unidad === 'Porcentaje') {
    return `${formatted} ${rounded === 1 ? 'punto porcentual' : 'puntos porcentuales'}`
  }
  if (unidad) {
    return `${formatted} (${unidad})`
  }
  return formatted
}

export function explainFormula(indicator: Indicator): FormulaExplanation {
  const rawFormula = indicator.formula.trim()
  if (rawFormula) {
    return { text: rawFormula, isFallback: false }
  }

  const combined = normalizeText(`${indicator.nombre} ${indicator.descripcion} ${indicator.unidadMedida}`)
  if (
    indicator.unidadMedida === 'Porcentaje'
    || combined.includes('porcentaje')
    || combined.includes('proporcion')
  ) {
    return {
      text: 'Cálculo directo reportado por la fuente oficial como proporción porcentual sobre su universo de referencia. La ficha técnica del PVD no desglosa una fórmula algebraica; consulta la descripción del indicador y la fuente oficial.',
      isFallback: true,
    }
  }

  if (
    combined.includes('tasa')
    || combined.includes('indice')
    || combined.includes('pibe')
    || combined.includes('producto interno')
  ) {
    return {
      text: 'Cifra agregada, tasa o índice calculado directamente con la metodología oficial de la fuente. La ficha técnica del PVD no incluye una expresión matemática explícita; el detalle metodológico se consulta en el medio de verificación oficial.',
      isFallback: true,
    }
  }

  return {
    text: 'Cálculo directo reportado por la fuente oficial. La ficha técnica del PVD no incluye fórmula matemática explícita; consulta la descripción del indicador y el documento oficial al final de esta página.',
    isFallback: true,
  }
}

export function explainBaseline(indicator: Indicator): string {
  const { anio, valor } = indicator.lineaBase
  if (valor === null) {
    return 'Sin valor numérico de línea base registrado en la ficha oficial del PVD.'
  }
  if (anio === null) {
    return 'Punto de partida oficial del PVD (sin año de corte especificado en la ficha).'
  }
  if (anio < 2024) {
    return `Punto de partida oficial del PVD (${anio}, medición previa al inicio del sexenio 2024–2030).`
  }
  if (anio === 2024) {
    return 'Punto de partida oficial del PVD al arranque del sexenio (2024).'
  }
  return `Punto de partida oficial del PVD con corte ${anio} (primer periodo de referencia del sexenio).`
}

export function explainUnit(unidadMedida: string): UnitExplanation {
  const trimmed = unidadMedida.trim()
  if (trimmed) {
    return { text: trimmed, isFallback: false }
  }
  return {
    text: 'Según metodología de la fuente oficial (sin etiqueta en ficha PVD)',
    isFallback: true,
  }
}

export function buildVariationBaseOptions(
  indicator: Indicator,
  series: HistoricalPoint[],
): VariationBaseOption[] {
  if (!series.length) return []
  const latest = series[series.length - 1]
  const options: VariationBaseOption[] = []

  if (indicator.lineaBase.valor !== null) {
    const lbYear = indicator.lineaBase.anio
    options.push({
      key: 'lineaBase',
      label: lbYear ? `Línea base PVD (${lbYear})` : 'Línea base PVD',
      shortLabel: lbYear ? `Línea base (${lbYear})` : 'Línea base PVD',
      year: lbYear,
      value: indicator.lineaBase.valor,
      kind: 'baseline',
    })
  }

  const priorPoints = series.filter((pt) => pt.anio < latest.anio).reverse()
  for (const pt of priorPoints) {
    options.push({
      key: `year:${pt.anio}`,
      label: pt.anio === 2024 ? 'Inicio de sexenio (2024)' : `Año ${pt.anio}`,
      shortLabel: String(pt.anio),
      year: pt.anio,
      value: pt.valor,
      kind: 'series',
    })
  }

  return options
}

export function getDefaultVariationBaseKey(
  options: VariationBaseOption[],
  _indicator: Indicator,
  series: HistoricalPoint[],
): string | null {
  if (!options.length) return null
  if (options.some((opt) => opt.key === 'lineaBase')) return 'lineaBase'
  if (options.some((opt) => opt.key === 'year:2024')) return 'year:2024'
  const firstSeriesYear = series[0]?.anio
  if (firstSeriesYear !== undefined) {
    const firstKey = `year:${firstSeriesYear}`
    if (options.some((opt) => opt.key === firstKey)) return firstKey
  }
  return options[0]?.key ?? null
}

function parseReferenceDate(referenceIsoDate?: string): Date {
  if (referenceIsoDate) {
    const parsed = new Date(`${referenceIsoDate}T00:00:00`)
    if (!Number.isNaN(parsed.getTime())) return parsed
  }
  return new Date()
}

export function calculateTimeRemaining(
  targetYear = 2030,
  referenceIsoDate?: string,
): TimeRemainingInfo {
  const ref = parseReferenceDate(referenceIsoDate)
  const currentYear = ref.getFullYear()
  const currentMonth = ref.getMonth() + 1 // 1..12
  const totalMonths = Math.max(0, (targetYear - currentYear) * 12 + (12 - currentMonth))

  if (totalMonths === 0) {
    return {
      years: 0,
      months: 0,
      totalMonths: 0,
      label: 'Cierre de meta alcanzado',
      isExpired: true,
    }
  }

  const years = Math.floor(totalMonths / 12)
  const months = totalMonths % 12
  const parts: string[] = []
  if (years > 0) parts.push(`${years} ${years === 1 ? 'año' : 'años'}`)
  if (months > 0) parts.push(`${months} ${months === 1 ? 'mes' : 'meses'}`)

  return {
    years,
    months,
    totalMonths,
    label: parts.join(' y '),
    isExpired: false,
  }
}

export function calculateGoalProgress(
  indicator: Indicator,
  series: HistoricalPoint[],
): GoalProgress {
  const latest = series.at(-1)
  if (!latest) {
    return {
      status: 'no_series',
      percent: null,
      rawPercent: null,
      barPercent: 0,
      tone: 'neutral',
      shortLabel: 'Sin serie',
      badgeLabel: 'Sin serie histórica',
      detail: 'Aún no hay observaciones oficiales integradas para calcular el porcentaje de avance hacia 2030.',
    }
  }

  const lb = indicator.lineaBase.valor
  const target = indicator.meta2030
  if (target === null || lb === null) {
    return {
      status: 'incomplete_goal',
      percent: null,
      rawPercent: null,
      barPercent: 0,
      tone: 'neutral',
      shortLabel: target === null ? 'Sin meta' : 'Sin base',
      badgeLabel: target === null ? 'Sin meta 2030' : 'Sin línea base',
      detail: 'Se requiere contar tanto con línea base como con Meta 2030 numérica para calcular el porcentaje de avance.',
    }
  }

  // Protege división entre cero cuando la meta sexenal busca mantener el valor de línea base.
  if (target === lb) {
    const tolerance = Math.max(0.05, Math.abs(target) * 0.005)
    const onTarget = Math.abs(latest.valor - target) <= tolerance
    return {
      status: 'maintenance',
      percent: onTarget ? 100 : 0,
      rawPercent: onTarget ? 100 : 0,
      barPercent: onTarget ? 100 : 0,
      tone: onTarget ? 'good' : 'bad',
      shortLabel: onTarget ? '100 % · En meta' : 'Fuera de rango',
      badgeLabel: onTarget ? 'En meta (mantenimiento)' : 'Fuera de objetivo',
      detail: onTarget
        ? `La meta es mantener el nivel de ${formatValue(target, indicator.unidadMedida)} y el último dato (${formatValue(latest.valor, indicator.unidadMedida)}) está dentro del rango.`
        : `La meta es mantener ${formatValue(target, indicator.unidadMedida)}, pero el último dato (${formatValue(latest.valor, indicator.unidadMedida)}) muestra una desviación de ${formatDeltaText(Math.abs(latest.valor - target), indicator.unidadMedida)}.`,
    }
  }

  // Evita reportar falsos avances o retrocesos cuando el último dato histórico es previo a la línea base (p. ej. línea base 2025 vs dato 2024).
  if (indicator.lineaBase.anio !== null && latest.anio < indicator.lineaBase.anio) {
    return {
      status: 'awaiting_post_baseline',
      percent: null,
      rawPercent: null,
      barPercent: 0,
      tone: 'neutral',
      shortLabel: 'Sin dato post-base',
      badgeLabel: 'Sin dato posterior a línea base',
      detail: `El último dato oficial corresponde a ${latest.anio} (${formatValue(latest.valor, indicator.unidadMedida)}); aún no se publican mediciones posteriores a la línea base (${indicator.lineaBase.anio}).`,
    }
  }

  const rawPercent = ((latest.valor - lb) / (target - lb)) * 100

  if (rawPercent < 0) {
    const regressionAbs = Math.abs(latest.valor - lb)
    return {
      status: 'regressed',
      percent: 0,
      rawPercent,
      barPercent: 0,
      tone: 'bad',
      shortLabel: '0 % · retroceso',
      badgeLabel: 'Con retroceso',
      detail: `0 % de avance · retroceso de ${formatDeltaText(regressionAbs, indicator.unidadMedida)} respecto a la línea base (${formatValue(lb, indicator.unidadMedida)}).`,
    }
  }

  if (rawPercent >= 100) {
    return {
      status: 'achieved',
      percent: 100,
      rawPercent,
      barPercent: 100,
      tone: 'good',
      shortLabel: '100 % · En meta',
      badgeLabel: 'Meta 2030 alcanzada',
      detail: `El último dato (${formatValue(latest.valor, indicator.unidadMedida)} en ${latest.anio}) ya alcanza la Meta 2030 de ${formatValue(target, indicator.unidadMedida)}.`,
    }
  }

  const rounded = rawPercent > 0 && rawPercent < 10
    ? Math.round(rawPercent * 10) / 10
    : Math.round(rawPercent)
  const gapAbs = Math.abs(target - latest.valor)
  const tone: ProgressTone = rawPercent >= 50 ? 'good' : 'neutral'

  return {
    status: 'in_progress',
    percent: rounded,
    rawPercent,
    barPercent: Math.max(0, Math.min(100, rawPercent)),
    tone,
    shortLabel: `${formatNumber(rounded)} %`,
    badgeLabel: rawPercent >= 50 ? 'Avance favorable' : 'Avance en curso',
    detail: `Avance de ${formatNumber(rounded)} % hacia la meta. Faltan ${formatDeltaText(gapAbs, indicator.unidadMedida)} para llegar a ${formatValue(target, indicator.unidadMedida)} en 2030.`,
  }
}

export function buildHistoricalChartInterpretation(params: {
  points: HistoricalPoint[]
  baseline: Baseline
  target: number | null
  direction: string
  unit?: string
  entity?: string
  referenceIsoDate?: string
}): ChartInterpretation | null {
  const {
    points,
    baseline,
    target,
    direction,
    unit,
    entity = 'Veracruz',
    referenceIsoDate,
  } = params

  if (!points.length) return null

  const first = points[0]
  const last = points[points.length - 1]
  const assessment = points.length >= 2 ? assessVariation(last.valor - first.valor, direction) : null
  const dir = normalizeText(direction || '')

  let trendSentence: string
  if (points.length === 1) {
    trendSentence = `Solo se cuenta con una observación oficial (${first.anio}: ${formatValue(first.valor, unit)}), por lo que aún no es posible evaluar una tendencia entre años.`
  } else {
    const diff = last.valor - first.valor
    const diffFormatted = formatVariation(diff, unit)
    if (Math.round(diff * 100) === 0) {
      trendSentence = `Entre ${first.anio} y ${last.anio}, el indicador se mantuvo prácticamente estable alrededor de ${formatValue(last.valor, unit)}.`
    } else if (assessment?.cls === 'trend--good') {
      trendSentence = `Entre ${first.anio} y ${last.anio}, el indicador mejoró al pasar de ${formatValue(first.valor, unit)} a ${formatValue(last.valor, unit)} (${diffFormatted}).`
    } else if (assessment?.cls === 'trend--bad') {
      trendSentence = `Entre ${first.anio} y ${last.anio}, el indicador mostró una variación desfavorable al pasar de ${formatValue(first.valor, unit)} a ${formatValue(last.valor, unit)} (${diffFormatted}).`
    } else {
      trendSentence = `Entre ${first.anio} y ${last.anio}, el indicador pasó de ${formatValue(first.valor, unit)} a ${formatValue(last.valor, unit)} (${diffFormatted}).`
    }
  }

  let targetSentence = ''
  let targetReached = false
  if (target === null) {
    targetSentence = 'Este indicador no registra una Meta 2030 numérica en la ficha oficial.'
  } else {
    const tolerance = Math.max(0.05, Math.abs(target) * 0.005)
    if (dir === 'ascendente') {
      targetReached = last.valor >= target
    } else if (dir === 'descendente') {
      targetReached = last.valor <= target
    } else if (baseline.valor !== null && baseline.valor !== target) {
      targetReached = baseline.valor < target ? last.valor >= target : last.valor <= target
    } else {
      targetReached = Math.abs(last.valor - target) <= tolerance
    }

    if (targetReached) {
      targetSentence = `Con el dato más reciente (${formatValue(last.valor, unit)}), ${entity} ya alcanza la Meta 2030 (${formatValue(target, unit)}); el objetivo es sostener este nivel.`
    } else {
      const remainingTime = calculateTimeRemaining(2030, referenceIsoDate)
      const gapAbs = Math.abs(target - last.valor)
      const actionVerb = last.valor < target ? 'incrementar' : 'reducir'
      const horizonText = remainingTime.isExpired
        ? 'al cierre de 2030'
        : `en los próximos ${remainingTime.label}`
      targetSentence = `Para alcanzar la meta de ${formatValue(target, unit)} en 2030, ${entity} necesita ${actionVerb} ${formatDeltaText(gapAbs, unit)} adicionales ${horizonText}.`
    }
  }

  let tone: ProgressTone = 'neutral'
  let icon = 'insights'
  if (targetReached || assessment?.cls === 'trend--good') {
    tone = 'good'
    icon = dir === 'descendente' ? 'trending_down' : 'trending_up'
  } else if (assessment?.cls === 'trend--bad') {
    tone = 'bad'
    icon = dir === 'descendente' ? 'trending_up' : 'trending_down'
  }

  return {
    tone,
    icon,
    text: `${trendSentence} ${targetSentence}`.trim(),
  }
}
