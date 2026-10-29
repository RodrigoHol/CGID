CREATE TABLE fuentes (
    id_fuente TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    institucion TEXT,
    url TEXT,
    archivo_fuente TEXT,
    fecha_publicacion DATE,
    fecha_consulta DATE NOT NULL,
    hash_archivo TEXT,
    observaciones TEXT
);

CREATE TABLE periodos (
    id_periodo TEXT PRIMARY KEY,
    anio INTEGER,
    fecha_inicio DATE,
    fecha_fin DATE,
    frecuencia TEXT NOT NULL
);

CREATE TABLE ejes (
    id_eje TEXT PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('rector', 'transversal')),
    orden INTEGER
);

CREATE TABLE indicadores (
    id_indicador TEXT PRIMARY KEY,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    formula TEXT,
    unidad_medida TEXT,
    sentido TEXT,
    linea_base_anio INTEGER,
    linea_base_valor NUMERIC,
    meta_2030_valor NUMERIC,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE indicador_eje (
    id_indicador TEXT NOT NULL REFERENCES indicadores(id_indicador),
    id_eje TEXT NOT NULL REFERENCES ejes(id_eje),
    tipo_relacion TEXT NOT NULL CHECK (tipo_relacion IN ('principal', 'transversal')),
    es_principal BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id_indicador, id_eje)
);

CREATE TABLE valores_indicadores (
    id_valor TEXT PRIMARY KEY,
    id_indicador TEXT NOT NULL REFERENCES indicadores(id_indicador),
    id_fuente TEXT NOT NULL REFERENCES fuentes(id_fuente),
    id_periodo TEXT NOT NULL REFERENCES periodos(id_periodo),
    id_entidad TEXT,
    id_municipio TEXT,
    valor NUMERIC,
    valor_texto TEXT,
    unidad_medida TEXT,
    es_estimado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_publicacion DATE,
    fecha_consulta DATE NOT NULL,
    url_fuente TEXT,
    archivo_fuente TEXT,
    hash_archivo TEXT,
    version_dato TEXT
);

CREATE INDEX idx_valores_indicador_periodo
    ON valores_indicadores (id_indicador, id_periodo);
CREATE INDEX idx_valores_fuente
    ON valores_indicadores (id_fuente);
CREATE INDEX idx_indicador_eje
    ON indicador_eje (id_eje, id_indicador);
