import indicadoresJson from '../../../../data/processed/frontend/indicadores_mvp.json'
import historicosJson from '../../../../data/processed/frontend/historicos_mvp.json'
import fuentesJson from '../../../../data/processed/frontend/fuentes_mvp.json'
import resumenJson from '../../../../data/processed/frontend/resumen_mvp.json'
import type {
  DataSource,
  FrontendData,
  HistoricalData,
  Indicator,
  Summary,
} from '../types/contract'

const data = {
  indicadores: indicadoresJson as Indicator[],
  historicos: historicosJson as HistoricalData,
  fuentes: fuentesJson as DataSource[],
  resumen: resumenJson as Summary,
}

export function loadFrontendData(): FrontendData {
  return data
}
