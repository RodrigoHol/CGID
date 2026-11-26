export interface GlossaryTerm {
  key: string
  term: string
  definition: string
}

export const GLOSSARY_TERMS: GlossaryTerm[] = [
  {
    key: 'lineaBase',
    term: 'Línea base',
    definition: 'Punto de partida oficial (valor y año de referencia) establecido en el Plan Veracruzano de Desarrollo para medir cuánto avanza el indicador.',
  },
  {
    key: 'meta2030',
    term: 'Meta 2030',
    definition: 'Valor objetivo establecido en el Plan Veracruzano de Desarrollo para alcanzar al cierre del sexenio 2025–2030.',
  },
  {
    key: 'ultimoValor',
    term: 'Último valor',
    definition: 'Dato más reciente disponible en la serie histórica oficial publicada para Veracruz.',
  },
  {
    key: 'variacionObservada',
    term: 'Variación observada',
    definition: 'Cambio entre el último valor publicado y el periodo base que selecciones (línea base del PVD o cualquier año disponible en la serie histórica).',
  },
  {
    key: 'porcentajeAvance',
    term: 'Porcentaje de avance',
    definition: 'Proporción del camino recorrido desde la línea base hacia la Meta 2030. Si el indicador retrocedió respecto a su punto de partida, muestra 0 % de avance y señala el retroceso.',
  },
  {
    key: 'tiempoRestante',
    term: 'Tiempo restante',
    definition: 'Años y meses disponibles desde la fecha de corte actual hasta el cierre del horizonte sexenal en diciembre de 2030.',
  },
  {
    key: 'sentido',
    term: 'Sentido',
    definition: 'Indica cómo interpretar un cambio en el indicador: si conviene que aumente (Ascendente / mayor es mejor), disminuya (Descendente / menor es mejor), se mantenga estable (Regular) o sea una cifra nominal.',
  },
  {
    key: 'formula',
    term: 'Fórmula o método de cálculo',
    definition: 'Expresión matemática o explicación metodológica con la que la institución oficial calcula el valor del indicador.',
  },
  {
    key: 'ejeRector',
    term: 'Eje rector',
    definition: 'Gran ámbito temático del Plan Veracruzano de Desarrollo 2025–2030 al que contribuye el indicador.',
  },
  {
    key: 'periodicidad',
    term: 'Periodicidad',
    definition: 'Frecuencia con la que la fuente oficial publica nuevas mediciones del indicador (anual, bienal, trimestral, mensual o sexenal).',
  },
  {
    key: 'publicacion',
    term: 'Última y próxima publicación',
    definition: 'Fecha o mes del corte más reciente divulgado por la institución responsable y ventana estimada en que se difundirá la siguiente actualización.',
  },
  {
    key: 'brechaAtraso',
    term: 'Brecha / Atraso',
    definition: 'Distancia pendiente entre el último valor observado y la Meta 2030, o rezago frente al ritmo esperado para cumplir el objetivo sexenal.',
  },
  {
    key: 'mediaNacional',
    term: 'Media nacional',
    definition: 'Valor promedio de referencia para todo México, útil para ubicar si Veracruz se encuentra por arriba o por abajo del desempeño nacional.',
  },
  {
    key: 'semaforo',
    term: 'Semáforo',
    definition: 'Código visual de color e ícono: Verde indica datos disponibles o desempeño favorable; Ámbar, datos en integración o seguimiento moderado; Rojo, en revisión documental o variación desfavorable.',
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
    key: 'enRevision',
    term: 'En revisión',
    definition: 'Indicador cuya fuente o ficha metodológica requiere verificación documental adicional antes de publicar su serie histórica.',
  },
  {
    key: 'puntosPorcentuales',
    term: 'Puntos porcentuales (pp)',
    definition: 'Diferencia aritmética directa entre dos porcentajes (por ejemplo, pasar de 44.5 % a 41.5 % equivale a −3 pp).',
  },
  {
    key: 'totalCatalogo',
    term: 'Total en catálogo PVD',
    definition: 'Conjunto completo de indicadores estratégicos y derivados definidos en el Plan Veracruzano de Desarrollo 2025–2030.',
  },
]

export const GLOSSARY_BY_KEY: Record<string, GlossaryTerm> = Object.fromEntries(
  GLOSSARY_TERMS.map((item) => [item.key, item]),
)
