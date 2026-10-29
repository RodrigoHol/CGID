CREATE TABLE catalogo_indicadores (
    id_indicador TEXT PRIMARY KEY,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    formula TEXT,
    unidad_medida TEXT,
    sentido TEXT,
    medio_verificacion TEXT,
    linea_base_anio INTEGER,
    linea_base_valor NUMERIC,
    meta_2030_valor NUMERIC,
    metas_intermedias_json TEXT,
    fecha_carga TIMESTAMP NOT NULL
);
