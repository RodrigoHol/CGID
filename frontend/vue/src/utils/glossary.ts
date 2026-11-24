export interface GlossaryTerm {
  key: string
  term: string
  definition: string
}

export const GLOSSARY_TERMS: GlossaryTerm[] = [
  {
    key: 'lineaBase',
    term: 'Línea base',
    definition: 'Valor inicial y año de referencia con los que se compara el avance del indicador a lo largo del tiempo.',
  },
  {
    key: 'meta2030',
    term: 'Meta 2030',
    definition: 'Valor objetivo establecido en el Plan Veracruzano de Desarrollo para alcanzar al cierre del periodo 2025–2030.',
  },
  {
    key: 'ultimoValor',
    term: 'Último valor',
    definition: 'Dato más reciente disponible en la serie histórica oficial publicada para Veracruz.',
  },
  {
    key: 'variacionObservada',
    term: 'Variación observada',
    definition: 'Diferencia entre el primer dato y el último dato registrado en la serie histórica disponible.',
  },
  {
    key: 'sentido',
    term: 'Sentido',
    definition: 'Indica cómo interpretar un cambio en el indicador: si conviene que aumente (mayor es mejor), disminuya (menor es mejor) o se mantenga en rango.',
  },
  {
    key: 'serieHistorica',
    term: 'Serie histórica',
    definition: 'Conjunto de observaciones anuales o periódicas obtenidas de fuentes oficiales sin interpolar ni estimar años faltantes.',
  },
  {
    key: 'conSerieHistorica',
    term: 'Con serie histórica',
    definition: 'Indicador cuya serie de datos oficiales ya fue extraída, validada y publicada para consulta y descarga en el catálogo.',
  },
  {
    key: 'enIntegracion',
    term: 'En integración',
    definition: 'Indicador cuya fuente oficial ya fue localizada y se encuentra en proceso de extracción y validación de su serie histórica.',
  },
  {
    key: 'puntosPorcentuales',
    term: 'Puntos porcentuales (pp)',
    definition: 'Diferencia aritmética directa entre dos porcentajes (por ejemplo, pasar de 44.5 % a 41.5 % equivale a −3 pp).',
  },
  {
    key: 'ejeRector',
    term: 'Eje rector',
    definition: 'Gran ámbito temático del Plan Veracruzano de Desarrollo 2025–2030 al que contribuye el indicador.',
  },
]

export const GLOSSARY_BY_KEY: Record<string, GlossaryTerm> = Object.fromEntries(
  GLOSSARY_TERMS.map((item) => [item.key, item]),
)
