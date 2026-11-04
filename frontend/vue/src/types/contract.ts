export type HistoricalStatus =
  | 'procesado'
  | 'fuente_identificada'
  | 'pendiente_revision'

export interface Baseline {
  anio: number | null
  valor: number | null
}

export interface IndicatorSource {
  url: string
  medioVerificacion: string
  archivoCrudo: string
  observaciones: string
}

export interface Indicator {
  id: string
  clave: string
  nombre: string
  descripcion: string
  formula: string
  unidadMedida: string
  sentido: string
  ejeRector: string
  lineaBase: Baseline
  meta2030: number | null
  metasIntermedias: Partial<Record<string, number>>
  estadoHistorico: HistoricalStatus
  periodosDisponibles: number[]
  tieneHistorico: boolean
  fuente: IndicatorSource
}

export interface HistoricalPoint {
  anio: number
  valor: number
}

export interface HistoricalSeries {
  entidad: string
  datos: HistoricalPoint[]
}

export type HistoricalData = Record<string, HistoricalSeries>

export interface DataSource {
  idIndicador: string
  institucion: string
  nombre: string
  url: string
  archivoCrudo: string
  archivoProcesado: string
  periodos: number[]
  entidad: string
  estado: HistoricalStatus
  observaciones: string
}

export interface Summary {
  entidad: string
  totalIndicadores: number
  indicadoresConHistorico: number
  indicadoresSinHistorico: number
  indicadoresConMeta2030: number
  porEstadoHistorico: Record<string, number>
  periodosHistoricos: number[]
}

export interface FrontendData {
  indicadores: Indicator[]
  historicos: HistoricalData
  fuentes: DataSource[]
  resumen: Summary
}
