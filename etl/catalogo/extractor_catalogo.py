import pdfplumber
import pandas as pd
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PDF_DEFAULT = ROOT / "data" / "raw" / "catalogos" / "pvd_2025_2030" / "Indicadores_PVD_Catalogo.pdf"
OUTPUT_DEFAULT = ROOT / "data" / "processed" / "catalogo" / "indicadores.csv"

ENCABEZADOS_PDF = (
    r'Plan Veracruzano de Desarrollo\s*\n?\s*\(PVD\)\s*2025-2030'
    r'(?:\s*:\s*Programas derivados)?'
    r'|GOBIERNO DEL ESTADO DE\s*VERACRUZ\s*2024-2030\s*POR AMOR A\s*VERACRUZ'
)


def limpiar_bloque(texto):
    """Normaliza un bloque conservando el contenido útil del PDF."""
    texto = re.sub(ENCABEZADOS_PDF, ' ', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', texto)

    # pdfplumber puede partir una URL al final de una línea (tabul\nados).
    # Solo se unen continuaciones que empiezan con caracteres propios de URL.
    for _ in range(3):
        anterior = texto
        texto = re.sub(
            r'(https?://[^\s\n]+)\s*\n\s*([a-z0-9][^\s\n]*)',
            r'\1\2',
            texto,
            flags=re.IGNORECASE,
        )
        if texto == anterior:
            break

    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def extraer_medio_verificacion(ficha):
    """Extrae el medio del indicador y usa los medios de sus variables como respaldo."""
    inicio = re.search(r'Medio de verificación del', ficha, re.IGNORECASE)
    fin = re.search(
        r'III\.\s*Características\s+del\s+Indicador',
        ficha[inicio.end():] if inicio else '',
        re.IGNORECASE,
    )

    medio_indicador = ''
    if inicio and fin:
        bloque = ficha[inicio.end():inicio.end() + fin.start()]
        bloque = re.sub(
            r'\bindicador\s*2\.1\.11\b|\b2\.1\.11\b|\bindicador\b',
            ' ',
            bloque,
            flags=re.IGNORECASE,
        )
        medio_indicador = limpiar_bloque(bloque)

    # Cuando el campo 2.1.11 dice N/A o está vacío, las fuentes de las
    # variables suelen contener el enlace concreto que permite verificarlo.
    inicio_variables = re.search(r'IV\.\s*Datos\s+de\s+las\s+variables', ficha, re.IGNORECASE)
    fin_variables = re.search(
        r'V\.\s*Determinación\s+de\s+metas',
        ficha[inicio_variables.end():] if inicio_variables else '',
        re.IGNORECASE,
    )
    medios_variables = []
    if inicio_variables and fin_variables:
        bloque_variables = ficha[
            inicio_variables.end():inicio_variables.end() + fin_variables.start()
        ]
        encontrados = re.findall(
            r'Medio de verificación4\.1\.3(.*?)(?=Unidad de medida4\.1\.4|'
            r'Nombre de la variable4\.1\.1|$)',
            bloque_variables,
            flags=re.IGNORECASE | re.DOTALL,
        )
        medios_variables = [
            limpiar_bloque(medio)
            for medio in encontrados
            if limpiar_bloque(medio)
        ]

    es_vacio = (
        not medio_indicador
        or bool(re.match(r'^(?:N/A|NA|N/D)\b', medio_indicador, re.IGNORECASE))
    )
    if es_vacio and medios_variables:
        return ' | '.join(dict.fromkeys(medios_variables))
    return medio_indicador


def procesar_pdf_completo(pdf_path):
    print(f"Iniciando lectura de {pdf_path}. Esto puede tomar un par de minutos...")
    texto_completo = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                texto_pagina = page.extract_text(layout=True)
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
    except Exception as e:
        print(f"Error al leer PDF: {e}")
        return []

    # 1. Limpieza de espacios gigantes
    texto_limpio = re.sub(r'[ \t]{2,}', ' ', texto_completo)
    
    # 2. BARRIDO DE BASURA (Encabezados y pies de página)
    # Esto soluciona los campos vacíos al cruzar de página borrando los textos estáticos
    texto_limpio = re.sub(ENCABEZADOS_PDF, ' ', texto_limpio, flags=re.IGNORECASE)
    texto_limpio = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', texto_limpio) # Quita números de página aislados
    
    # Separador principal de cada indicador
    fichas = re.split(r'I\.\s*Datos\s+de\s+Alineación', texto_limpio)
    
    if len(fichas) > 1:
        fichas = fichas[1:] 
    else:
        return []
        
    print(f"Lectura terminada. Se encontraron {len(fichas)} indicadores. Extrayendo datos limpios...")
    
    indicadores = []
    for i, ficha in enumerate(fichas):
        indicador = {}
        
        # --- 1. DATOS DE IDENTIFICACIÓN ---
        m_clave = re.search(r'Clave\s*2\.1\.1\s*([A-Z0-9\-\.]+)', ficha)
        indicador['clave'] = m_clave.group(1).strip() if m_clave else f"Pendiente_{i}"
        
        m_eje = re.search(r'Eje Rector (?:o Transversal\s*1\.1\.1\s*Eje Rector )?(\d\.[^\n]+)', ficha)
        indicador['eje_rector'] = m_eje.group(1).strip() if m_eje else "No encontrado"
        
        m_nombre = re.search(r'Nombre\s*2\.1\.2(.*?)Descripción o definición', ficha, re.DOTALL)
        indicador['nombre'] = m_nombre.group(1).strip() if m_nombre else "No encontrado"
        
        # --- 2. TEXTOS LARGOS (Expediente) ---
        m_desc = re.search(r'Descripción o definición\s*2\.1\.3(.*?)Dimensión a medir', ficha, re.DOTALL)
        indicador['descripcion'] = m_desc.group(1).strip().replace('\n', ' ') if m_desc else ""
        
        m_form = re.search(r'Fórmula o método de\s*cálculo\s*2\.1\.7(.*?)Unidad de medida', ficha, re.DOTALL)
        indicador['formula'] = m_form.group(1).strip().replace('\n', ' ') if m_form else ""
        
        m_unidad = re.search(r'Unidad de medida del\s*indicador\s*2\.1\.8\s*([^\n]+)', ficha)
        indicador['unidad_medida'] = m_unidad.group(1).strip() if m_unidad else ""
        
        m_sentido = re.search(r'Sentido del indicador\s*2\.1\.10\s*([A-Za-z]+)', ficha)
        indicador['sentido'] = m_sentido.group(1).strip() if m_sentido else ""
        
        # --- CORRECCIÓN MEDIO DE VERIFICACIÓN ---
        # Anclamos directamente en 2.1.11 y cortamos en III. Características
        indicador['medio_verificacion'] = extraer_medio_verificacion(ficha)
        
        # --- 3. METAS Y GRÁFICAS ---
        m_base = re.search(r'Línea base\s*5\.1\.1.*?(\d{4})\s+([\d\.]+)', ficha, re.DOTALL)
        indicador['linea_base_anio'] = int(m_base.group(1)) if m_base else None
        indicador['linea_base_valor'] = float(m_base.group(2)) if m_base else None
        
        m_meta = re.search(r'Meta sexenal\s*5\.1\.2.*?(\d{4})\s+([\d\.]+)', ficha, re.DOTALL)
        indicador['meta_2030_valor'] = float(m_meta.group(2)) if m_meta else None
        
        m_intermedias = re.search(r'Metas intermedias\s*5\.1\.3(.*?)Fecha de publicación', ficha, re.DOTALL)
        metas_json = {}
        if m_intermedias:
            bloque_metas = m_intermedias.group(1)
            pares = re.findall(r'(\d{4})\s+([\d\.]+)', bloque_metas)
            for anio, valor in pares:
                metas_json[anio] = float(valor)
                
        indicador['metas_intermedias_json'] = json.dumps(metas_json)
        
        indicadores.append(indicador)
        
    return indicadores

def main(pdf_path=PDF_DEFAULT, output_path=OUTPUT_DEFAULT):
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"Error: No se encuentra {pdf_file}")
        return
        
    datos = procesar_pdf_completo(pdf_file)
    
    if datos:
        df = pd.DataFrame(datos)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n¡Éxito! Se exportaron {len(datos)} indicadores a '{output_path}'.")

if __name__ == "__main__":
    main()