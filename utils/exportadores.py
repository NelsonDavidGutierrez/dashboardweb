import io
import math
from datetime import datetime

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Paleta corporativa J&M
COLOR_AMARILLO = "FFC107"
COLOR_NEGRO = "121212"
COLOR_GRIS = "9E9E9E"


def _valor_a_texto(valor) -> str:
    """Convierte cualquier valor de celda (float, NaN, None, texto, etc.)
    a un texto seguro para exportar, sin lanzar errores por NaN."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)) or pd.isna(valor):
        return ""
    return str(valor)


def generar_excel_riesgos(df: pd.DataFrame) -> bytes:
    """Genera un archivo .xlsx con la matriz de riesgos, con encabezado
    estilizado, columnas autoajustadas y filtros habilitados."""
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        hoja = "Matriz de Riesgos"
        df.to_excel(writer, index=False, sheet_name=hoja, startrow=1)
        ws = writer.sheets[hoja]

        # Título superior
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(len(df.columns), 1))
        celda_titulo = ws.cell(row=1, column=1)
        celda_titulo.value = "INGENIERÍA Y SUMINISTROS J&M S.A.S. — Matriz de Riesgos IPVRDC / GTC-45"
        celda_titulo.font = Font(bold=True, size=12, color="FFFFFF")
        celda_titulo.fill = PatternFill("solid", fgColor=COLOR_NEGRO)
        celda_titulo.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[1].height = 24

        # Encabezado de columnas (fila 2, ya que to_excel empezó en startrow=1 -> fila real 2)
        fila_encabezado = 2
        for col_idx in range(1, len(df.columns) + 1):
            celda = ws.cell(row=fila_encabezado, column=col_idx)
            celda.font = Font(bold=True, color="000000")
            celda.fill = PatternFill("solid", fgColor=COLOR_AMARILLO)
            celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Autoajustar ancho de columnas (convirtiendo todo a texto de forma segura,
        # incluyendo NaN/None/valores numéricos, para evitar errores de tipo)
        for col_idx, nombre_col in enumerate(df.columns, start=1):
            letra = get_column_letter(col_idx)
            textos = [_valor_a_texto(v) for v in df[nombre_col]]
            largos = [len(t) for t in textos] + [len(_valor_a_texto(nombre_col))]
            ancho_maximo = max(largos) if largos else len(_valor_a_texto(nombre_col))
            ws.column_dimensions[letra].width = min(max(ancho_maximo + 2, 10), 45)

        # Filtros y panel congelado (encabezados siempre visibles)
        ws.auto_filter.ref = f"A{fila_encabezado}:{get_column_letter(len(df.columns))}{fila_encabezado + len(df)}"
        ws.freeze_panes = f"A{fila_encabezado + 1}"

    buffer.seek(0)
    return buffer.getvalue()


def _dividir_columnas_en_bloques(columnas, ancho_disponible_pt, ancho_minimo_col_pt, columna_fija=None):
    """Divide la lista de columnas en bloques que quepan en el ancho de
    página disponible. Si se indica `columna_fija`, esa columna se repite
    al inicio de cada bloque (excepto el primero) para dar contexto."""
    columnas = list(columnas)
    if columna_fija in columnas:
        resto = [c for c in columnas if c != columna_fija]
    else:
        columna_fija = None
        resto = columnas

    max_cols_por_bloque = max(1, int(ancho_disponible_pt // ancho_minimo_col_pt))
    # Si hay columna fija, esta ocupa un espacio en cada bloque adicional
    max_cols_resto = max_cols_por_bloque - 1 if columna_fija else max_cols_por_bloque
    max_cols_resto = max(1, max_cols_resto)

    bloques = []
    for i in range(0, len(resto), max_cols_resto):
        grupo = resto[i:i + max_cols_resto]
        if columna_fija and i > 0:
            grupo = [columna_fija] + grupo
        bloques.append(grupo)

    if not bloques:
        bloques = [resto]
    return bloques


def generar_pdf_riesgos(df: pd.DataFrame) -> bytes:
    """Genera un archivo .pdf en horizontal con la matriz de riesgos
    formateada como tabla, con encabezado corporativo. Si la matriz tiene
    muchas columnas (como una matriz GTC-45 completa), las divide en
    bloques por páginas para que el contenido siga siendo legible."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1 * cm,
        rightMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )

    elementos = []

    estilo_titulo = ParagraphStyle(
        "TituloJM",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#121212"),
        spaceAfter=2,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloJM",
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#616161"),
        spaceAfter=10,
    )
    # wordWrap="CJK" fuerza el corte de palabras largas sin espacios,
    # evitando que una celda desborde el ancho de columna.
    estilo_celda = ParagraphStyle(
        "CeldaJM",
        fontName="Helvetica",
        fontSize=6.5,
        leading=8,
        wordWrap="CJK",
    )
    estilo_celda_encabezado = ParagraphStyle(
        "CeldaEncabezadoJM",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.black,
        wordWrap="CJK",
    )

    elementos.append(Paragraph("INGENIERÍA Y SUMINISTROS J&amp;M S.A.S.", estilo_titulo))
    elementos.append(
        Paragraph(
            f"Matriz de Riesgos (IPVRDC / GTC-45) — Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            estilo_subtitulo,
        )
    )
    elementos.append(Spacer(1, 6))

    if df.empty:
        elementos.append(Paragraph("No hay registros en la matriz de riesgos.", estilo_celda))
        doc.build(elementos)
        buffer.seek(0)
        return buffer.getvalue()

    ancho_disponible = landscape(A4)[0] - 2 * cm
    ancho_minimo_col = 2.3 * cm  # ancho mínimo legible por columna

    columna_identificadora = df.columns[0]  # p. ej. "id", se repite en cada bloque
    bloques_columnas = _dividir_columnas_en_bloques(
        df.columns, ancho_disponible, ancho_minimo_col, columna_fija=columna_identificadora
    )

    total_bloques = len(bloques_columnas)
    for idx_bloque, columnas_bloque in enumerate(bloques_columnas):
        if total_bloques > 1:
            elementos.append(
                Paragraph(
                    f"Bloque de columnas {idx_bloque + 1} de {total_bloques}",
                    estilo_subtitulo,
                )
            )

        encabezados = [Paragraph(_valor_a_texto(col), estilo_celda_encabezado) for col in columnas_bloque]
        filas = [encabezados]
        for _, fila in df[columnas_bloque].iterrows():
            filas.append([Paragraph(_valor_a_texto(v), estilo_celda) for v in fila.tolist()])

        num_columnas = len(columnas_bloque)
        ancho_columna = ancho_disponible / num_columnas

        tabla = Table(filas, colWidths=[ancho_columna] * num_columnas, repeatRows=1)
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFC107")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDBDBD")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        elementos.append(tabla)

        if idx_bloque < total_bloques - 1:
            elementos.append(PageBreak())

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()