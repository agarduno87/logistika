#!/usr/bin/env python3
"""
Construye logistika-precios.xlsx — el modelo que produce las bandas de precio.

Uso:
    python3 tools/build_pricing.py

Diseño: NADA está calculado en Python. Todos los números que dependen de otro
número son fórmulas de Excel, para que el libro siga sirviendo cuando Adriana
cambie una hora estimada o su ingreso objetivo. Lo único escrito a mano son los
supuestos, y todos están marcados en amarillo con su justificación al lado.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "logistika-precios.xlsx"

FONT = "Arial"
BLUE = Font(name=FONT, size=10, color="0000FF")          # dato que se captura
BLACK = Font(name=FONT, size=10)                          # fórmula
GREEN = Font(name=FONT, size=10, color="008000")          # liga a otra hoja
BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True, color="27407A")
SUB = Font(name=FONT, size=10, italic=True, color="5A6684")
HEAD = Font(name=FONT, size=10, bold=True, color="FFFFFF")

FILL_HEAD = PatternFill("solid", fgColor="385DAB")
FILL_INPUT = PatternFill("solid", fgColor="FFFF00")       # el usuario lo edita
FILL_BAND = PatternFill("solid", fgColor="FDF0D5")
FILL_TINT = PatternFill("solid", fgColor="F6F8FD")

THIN = Side(style="thin", color="D5DCEC")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MXN = '$#,##0;($#,##0);-'
MXN0 = '$#,##0'
PCT = '0.0%'
HRS = '#,##0.0'
NUM = '#,##0'


def head(ws, row, labels, start=1):
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=start + i, value=label)
        c.font = HEAD
        c.fill = FILL_HEAD
        c.border = BOX
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = TITLE
    if sub:
        ws["A2"] = sub
        ws["A2"].font = SUB
    ws.sheet_view.showGridLines = False


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


def inp(ws, ref, value, fmt=None, note=None):
    """Celda de captura: amarilla y azul, con su nota al lado."""
    c = ws[ref]
    c.value = value
    c.font = BLUE
    c.fill = FILL_INPUT
    c.border = BOX
    if fmt:
        c.number_format = fmt
    if note:
        n = ws.cell(row=c.row, column=c.column + 1, value=note)
        n.font = SUB
        n.alignment = Alignment(wrap_text=True, vertical="top")
    return c


def fx(ws, ref, formula, fmt=None, bold=False, fill=None):
    c = ws[ref]
    c.value = formula
    c.font = BOLD if bold else BLACK
    c.border = BOX
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def lbl(ws, ref, text, bold=False):
    c = ws[ref]
    c.value = text
    c.font = BOLD if bold else BLACK
    return c


# ---------------------------------------------------------------------------
# 1. Léeme
# ---------------------------------------------------------------------------
def sheet_readme(wb):
    ws = wb.create_sheet("Léeme")
    title(ws, "Modelo de precios — logistika",
          "Cómo se usa este libro y qué significa cada color")
    widths(ws, {"A": 4, "B": 34, "C": 88})

    rows = [
        ("", "", ""),
        ("QUÉ ES ESTO", "", ""),
        ("", "Para qué sirve",
         "Calcula bandas de precio para los productos de logistika a partir de la capacidad real "
         "de Adriana y de su ingreso objetivo. No son precios de mercado: son el piso por debajo "
         "del cual el trabajo pierde dinero, y el objetivo que hace que el negocio valga la pena."),
        ("", "Qué NO es",
         "No es un estudio de mercado. Nadie ha cotizado a la competencia todavía. Antes de "
         "publicar un precio hay que contrastarlo (ver la hoja 'Validación de mercado')."),
        ("", "Moneda",
         "Todo en pesos mexicanos. La hoja 'Supuestos' tiene el tipo de cambio para cotizar en "
         "dólares a clientes extranjeros."),
        ("", "", ""),
        ("CÓMO SE USA", "", ""),
        ("", "1. Supuestos",
         "Edita SOLO las celdas amarillas. Son las horas que Adriana puede dedicar, lo que quiere "
         "ganar y sus costos fijos. Todo lo demás se recalcula solo."),
        ("", "2. Horas por producto",
         "Ajusta las horas estimadas de cada entregable. Es el supuesto que más mueve el precio "
         "y el que Adriana puede corregir mejor que nadie."),
        ("", "3. Bandas de precio",
         "Sale el resultado: piso, objetivo y premium por producto. De ahí se elige lo que se publica."),
        ("", "4. Capacidad",
         "Comprueba cuántos clientes caben en sus horas. Esta hoja es la que dice si PARTNER "
         "se puede lanzar o no."),
        ("", "5. Matriz",
         "Qué servicio entra en qué nivel. Es lo que va publicado en el sitio."),
        ("", "", ""),
        ("COLORES", "", ""),
        ("", "Amarillo con letra azul", "Dato que capturas tú. Son los únicos que debes tocar."),
        ("", "Letra negra", "Fórmula. Si la sobrescribes, el modelo deja de recalcularse."),
        ("", "Letra verde", "Trae un valor de otra hoja."),
        ("", "", ""),
        ("ADVERTENCIA", "", ""),
        ("", "Los supuestos son míos",
         "Las horas por entregable y los costos fijos son estimaciones razonadas, no datos que "
         "Adriana me haya dado. Cada una tiene su justificación escrita al lado. Revísalas una "
         "por una antes de usar cualquier número de salida: si las horas están mal, el precio "
         "está mal, por muy bien que calcule el libro."),
    ]
    r = 4
    for a, b, c in rows:
        if a:
            cell = ws.cell(row=r, column=1, value=a)
            cell.font = Font(name=FONT, size=11, bold=True, color="385DAB")
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        if b:
            ws.cell(row=r, column=2, value=b).font = BOLD
        if c:
            cc = ws.cell(row=r, column=3, value=c)
            cc.font = BLACK
            cc.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = max(15, 13 * (len(c) // 88 + 1))
        r += 1
    return ws


# ---------------------------------------------------------------------------
# 2. Supuestos
# ---------------------------------------------------------------------------
def sheet_assumptions(wb):
    ws = wb.create_sheet("Supuestos")
    title(ws, "Supuestos", "Edita solo las celdas amarillas. Todo lo demás se calcula.")
    widths(ws, {"A": 3, "B": 42, "C": 16, "D": 74})

    lbl(ws, "B4", "CAPACIDAD", bold=True)
    ws["B4"].fill = FILL_TINT
    lbl(ws, "B5", "Horas por semana dedicables a logistika")
    inp(ws, "C5", 12, HRS,
        "Adriana tiene un trabajo de tiempo completo. 12 h/semana son ~2 h entre semana más "
        "medio sábado. Si esto sube, sube todo lo demás.")
    lbl(ws, "B6", "Semanas facturables al año")
    inp(ws, "C6", 44, NUM, "52 menos vacaciones, puentes y las semanas muertas de diciembre.")
    lbl(ws, "B7", "% de horas no facturables (venta, propuestas, admin)")
    inp(ws, "C7", 0.35, PCT,
        "En consultoría independiente, un tercio del tiempo se va en conseguir el trabajo, "
        "no en hacerlo. Con 0.20 el modelo se vuelve optimista.")
    fx(ws, "C8", "=C5*C6*(1-C7)", HRS, bold=True)
    lbl(ws, "B8", "Horas facturables al año", bold=True)
    ws["D8"] = "Este es el número que limita todo el negocio."
    ws["D8"].font = SUB

    lbl(ws, "B10", "ECONOMÍA", bold=True)
    ws["B10"].fill = FILL_TINT
    lbl(ws, "B11", "Ingreso anual objetivo de logistika (MXN)")
    inp(ws, "C11", 480000, MXN,
        "Lo que Adriana quiere que le deje logistika al año, ADEMÁS de su sueldo. "
        "Cámbialo por su cifra real: es el supuesto más importante del libro.")
    lbl(ws, "B12", "Costos fijos anuales (MXN)")
    inp(ws, "C12", 60000, MXN,
        "Contador, software, seguro de responsabilidad, sitio, telefonía, membresías de cámara. "
        "Estimación mía, no un presupuesto suyo.")
    lbl(ws, "B13", "Margen objetivo sobre el piso")
    inp(ws, "C13", 0.35, PCT,
        "Colchón para reinversión, cuentas incobrables y trabajo no cobrado. "
        "Por debajo de 0.25 no queda margen para errores de estimación.")
    lbl(ws, "B14", "Factor premium (precio por valor)")
    inp(ws, "C14", 1.35, "0.00x",
        "Se aplica donde el valor para el cliente es mucho mayor que las horas invertidas, "
        "como el diagnóstico. No se aplica a trabajo por volumen.")

    lbl(ws, "B16", "TARIFAS DERIVADAS", bold=True)
    ws["B16"].fill = FILL_TINT
    lbl(ws, "B17", "Costo por hora facturable (piso)")
    fx(ws, "C17", "=IFERROR((C11+C12)/C8,0)", MXN, bold=True, fill=FILL_BAND)
    ws["D17"] = "Por debajo de esto, cada hora trabajada le cuesta dinero."
    ws["D17"].font = SUB
    lbl(ws, "B18", "Tarifa objetivo por hora")
    fx(ws, "C18", "=IFERROR(C17/(1-C13),0)", MXN, bold=True, fill=FILL_BAND)
    ws["D18"] = "Piso más el margen objetivo. Es la tarifa con la que se debe cotizar."
    ws["D18"].font = SUB
    lbl(ws, "B19", "Tarifa premium por hora")
    fx(ws, "C19", "=C18*C14", MXN, bold=True, fill=FILL_BAND)

    lbl(ws, "B21", "TIPO DE CAMBIO", bold=True)
    ws["B21"].fill = FILL_TINT
    lbl(ws, "B22", "MXN por USD")
    inp(ws, "C22", 18.50, "0.00",
        "CONFIRMAR antes de cotizar en dólares. Este número se mueve todas las semanas; "
        "el que está aquí es un marcador, no una cotización.")
    return ws


# ---------------------------------------------------------------------------
# 3. Horas por producto
# ---------------------------------------------------------------------------
PRODUCTS = [
    ("Health Check", "Diagnóstico de cadena de suministro (10–15 días)",
     10, 16, 26,
     "Entrevistas, revisión documental, análisis de costos, redacción del reporte y presentación. "
     "El rango alto es una operación con varios proveedores y sin datos ordenados."),
    ("START", "Consultoría y plan de importación",
     14, 22, 34,
     "Análisis de producto, proveedor y origen; clasificación arancelaria; costo en destino; "
     "régimen y ruta; expediente de viabilidad."),
    ("MANAGE — arranque", "Alta de cuenta: procedimientos, formatos, alta de proveedores",
     8, 14, 22,
     "Trabajo de una sola vez al iniciar la relación. Se cobra aparte o se amortiza en los "
     "primeros tres meses."),
    ("MANAGE — mensual", "Coordinación mensual base (sin embarques)",
     3, 5, 8,
     "Junta de seguimiento, reporte de indicadores, auditoría de facturas de proveedores."),
    ("MANAGE — por embarque", "Coordinación de un embarque de punta a punta",
     1.5, 2.5, 4.5,
     "Revisión documental previa, coordinación con forwarder y agente, seguimiento de ETA, "
     "liberación, entrega y cierre de expediente."),
    ("PARTNER — mensual", "Departamento externo de comercio exterior",
     18, 28, 40,
     "Incluye todo MANAGE más exportaciones, abastecimiento, cumplimiento y reporte a dirección. "
     "OJO: son horas que Adriana hoy no tiene."),
]


def sheet_hours(wb):
    ws = wb.create_sheet("Horas por producto")
    title(ws, "Horas estimadas por entregable",
          "El supuesto que más mueve el precio. Ajústalo con la experiencia de Adriana.")
    widths(ws, {"A": 3, "B": 24, "C": 44, "D": 11, "E": 11, "F": 11, "G": 13, "H": 62})

    head(ws, 4, ["Producto", "Qué incluye", "Horas\noptimista", "Horas\nbase",
                 "Horas\npesimista", "Horas\nponderadas", "Justificación del rango"], start=2)

    r = 5
    for name, desc, lo, base, hi, why in PRODUCTS:
        ws.cell(row=r, column=2, value=name).font = BOLD
        d = ws.cell(row=r, column=3, value=desc)
        d.font = BLACK
        d.alignment = Alignment(wrap_text=True, vertical="top")
        for col, val in ((4, lo), (5, base), (6, hi)):
            c = ws.cell(row=r, column=col, value=val)
            c.font = BLUE
            c.fill = FILL_INPUT
            c.number_format = HRS
            c.border = BOX
        # PERT: la estimación pesimista pesa igual que la optimista y la base pesa 4.
        # Un promedio simple subestima sistemáticamente el trabajo de coordinación.
        f = ws.cell(row=r, column=7, value=f"=(D{r}+4*E{r}+F{r})/6")
        f.font = BOLD
        f.number_format = HRS
        f.border = BOX
        f.fill = FILL_BAND
        j = ws.cell(row=r, column=8, value=why)
        j.font = SUB
        j.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 42
        r += 1

    note = ws.cell(row=r + 1, column=2,
                   value="Las horas ponderadas usan PERT: (optimista + 4×base + pesimista) / 6. "
                         "Un promedio simple subestima el trabajo de coordinación, porque lo que "
                         "sale mal siempre cuesta más de lo que se ahorra cuando sale bien.")
    note.font = SUB
    note.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r + 1, start_column=2, end_row=r + 2, end_column=8)
    return ws


# ---------------------------------------------------------------------------
# 4. Bandas de precio
# ---------------------------------------------------------------------------
def sheet_bands(wb):
    ws = wb.create_sheet("Bandas de precio")
    title(ws, "Bandas de precio por producto",
          "Salida del modelo. Nada aquí se captura a mano.")
    widths(ws, {"A": 3, "B": 24, "C": 13, "D": 15, "E": 15, "F": 15, "G": 14, "H": 56})

    head(ws, 4, ["Producto", "Horas\nponderadas", "Piso\n(MXN)", "Objetivo\n(MXN)",
                 "Premium\n(MXN)", "Objetivo\n(USD)", "Cómo se cobra"], start=2)

    how = ["Precio fijo, 50% al inicio y 50% contra entrega",
           "Precio fijo por proyecto",
           "Único, al firmar",
           "Iguala mensual",
           "Fee por embarque, se suma a la iguala",
           "Iguala mensual, contrato anual"]

    r = 5
    for i, (name, desc, lo, base, hi, why) in enumerate(PRODUCTS):
        src = 5 + i
        ws.cell(row=r, column=2, value=name).font = BOLD
        g = ws.cell(row=r, column=3, value=f"='Horas por producto'!G{src}")
        g.font = GREEN
        g.number_format = HRS
        g.border = BOX
        fx(ws, f"D{r}", f"=C{r}*Supuestos!$C$17", MXN)
        fx(ws, f"E{r}", f"=C{r}*Supuestos!$C$18", MXN, bold=True, fill=FILL_BAND)
        fx(ws, f"F{r}", f"=C{r}*Supuestos!$C$19", MXN)
        fx(ws, f"G{r}", f"=IFERROR(E{r}/Supuestos!$C$22,0)", MXN)
        h = ws.cell(row=r, column=8, value=how[i])
        h.font = SUB
        h.alignment = Alignment(wrap_text=True, vertical="top")
        r += 1

    lbl(ws, f"B{r+1}", "PAQUETE MANAGE — lo que factura un cliente típico", bold=True)
    ws[f"B{r+1}"].fill = FILL_TINT
    lbl(ws, f"B{r+2}", "Embarques al mes de un cliente promedio")
    inp(ws, f"C{r+2}", 12, NUM, "Rango objetivo del nivel MANAGE: entre 5 y 30 embarques al mes.")
    lbl(ws, f"B{r+3}", "Iguala mensual (objetivo)")
    fx(ws, f"C{r+3}", "=E8", MXN)
    lbl(ws, f"B{r+4}", "Fee por embarque (objetivo)")
    fx(ws, f"C{r+4}", "=E9", MXN)
    lbl(ws, f"B{r+5}", "Facturación mensual de ese cliente", bold=True)
    fx(ws, f"C{r+5}", f"=C{r+3}+C{r+2}*C{r+4}", MXN, bold=True, fill=FILL_BAND)
    lbl(ws, f"B{r+6}", "Horas que ese cliente consume al mes", bold=True)
    fx(ws, f"C{r+6}", f"='Horas por producto'!G8+C{r+2}*'Horas por producto'!G9", HRS, bold=True)

    warn = ws.cell(row=r + 8, column=2,
                   value="El precio de salida es el OBJETIVO, no el piso. El piso solo sirve para "
                         "saber cuándo hay que decir que no: si un cliente regatea por debajo de "
                         "esa columna, el trabajo cuesta dinero en vez de generarlo.")
    warn.font = SUB
    warn.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r + 8, start_column=2, end_row=r + 9, end_column=8)
    return ws


# ---------------------------------------------------------------------------
# 5. Capacidad
# ---------------------------------------------------------------------------
def sheet_capacity(wb):
    ws = wb.create_sheet("Capacidad")
    title(ws, "¿Cuánto cabe en las horas de Adriana?",
          "La restricción de este negocio es el tiempo, no la demanda. Esta hoja decide qué se lanza.")
    widths(ws, {"A": 3, "B": 46, "C": 16, "D": 80})

    lbl(ws, "B4", "HORAS DISPONIBLES", bold=True)
    ws["B4"].fill = FILL_TINT
    lbl(ws, "B5", "Horas facturables al año")
    fx(ws, "C5", "=Supuestos!C8", HRS)
    ws["C5"].font = GREEN
    lbl(ws, "B6", "Horas facturables al mes", bold=True)
    fx(ws, "C6", "=C5/12", HRS, bold=True, fill=FILL_BAND)

    lbl(ws, "B8", "LO QUE CONSUME CADA CLIENTE AL MES", bold=True)
    ws["B8"].fill = FILL_TINT
    lbl(ws, "B9", "Un cliente MANAGE, al volumen supuesto")
    fx(ws, "C9", "='Bandas de precio'!C17", HRS)
    ws["C9"].font = GREEN
    lbl(ws, "B10", "Un cliente PARTNER")
    fx(ws, "C10", "='Horas por producto'!G10", HRS)
    ws["C10"].font = GREEN

    lbl(ws, "B12", "CUÁNTOS CABEN", bold=True)
    ws["B12"].fill = FILL_TINT
    lbl(ws, "B13", "Clientes MANAGE simultáneos", bold=True)
    fx(ws, "C13", "=IFERROR(C6/C9,0)", "#,##0.00", bold=True, fill=FILL_BAND)
    ws["D13"] = ('=IF(C13<1,"NO CABE NI UNO. Al volumen supuesto, un solo cliente MANAGE pide más '
                 'horas de las que hay en el mes.","Caben "&TEXT(C13,"0.0")&". Redondea hacia abajo.")')
    ws["D13"].font = Font(name=FONT, size=10, bold=True, color="B0410E")
    ws["D13"].alignment = Alignment(wrap_text=True, vertical="top")

    lbl(ws, "B14", "Clientes PARTNER simultáneos", bold=True)
    fx(ws, "C14", "=IFERROR(C6/C10,0)", "#,##0.00", bold=True, fill=FILL_BAND)
    ws["D14"] = ('=IF(C14<1,"NO CABE. Lanzar solo START y MANAGE.","Cabe justo "&TEXT(C14,"0.00")&'
                 '"x: sin margen para un imprevisto ni para vender el siguiente proyecto.")')
    ws["D14"].font = Font(name=FONT, size=10, bold=True, color="B0410E")
    ws["D14"].alignment = Alignment(wrap_text=True, vertical="top")

    lbl(ws, "B16", "EL LÍMITE REAL DE MANAGE", bold=True)
    ws["B16"].fill = FILL_TINT
    lbl(ws, "B17", "Horas que quedan tras la iguala base")
    fx(ws, "C17", "=C6-'Horas por producto'!G8", HRS)
    lbl(ws, "B18", "Embarques al mes que caben en esas horas", bold=True)
    fx(ws, "C18", "=IFERROR(C17/'Horas por producto'!G9,0)", "#,##0.0", bold=True, fill=FILL_BAND)
    ws["D18"] = ("Máximo absoluto para UN cliente, consumiendo el 100% de las horas. "
                 "Para operar con holgura, la mitad.")
    ws["D18"].font = SUB
    ws["D18"].alignment = Alignment(wrap_text=True, vertical="top")
    lbl(ws, "B19", "Volumen supuesto en 'Bandas de precio'")
    fx(ws, "C19", "='Bandas de precio'!C13", NUM)
    ws["C19"].font = GREEN
    ws["D19"] = ('=IF(C19>C18,"El volumen supuesto NO cabe. Baja el volumen, sube las horas '
                 'disponibles, o no vendas MANAGE todavía.","El volumen supuesto cabe.")')
    ws["D19"].font = Font(name=FONT, size=10, bold=True, color="B0410E")
    ws["D19"].alignment = Alignment(wrap_text=True, vertical="top")

    lbl(ws, "B21", "INGRESO ALCANZABLE (limitado por capacidad)", bold=True)
    ws["B21"].fill = FILL_TINT
    lbl(ws, "B22", "Clientes MANAGE que se quisieran sostener")
    inp(ws, "C22", 2, NUM, "Lo que se desea. La línea de abajo lo recorta a lo que cabe.")
    lbl(ws, "B23", "Clientes que realmente caben", bold=True)
    fx(ws, "C23", "=MIN(C22,INT(C13))", NUM, bold=True)
    ws["D23"] = "Se toma el menor entre lo deseado y lo posible. Aquí es donde el plan se topa con el calendario."
    ws["D23"].font = SUB
    ws["D23"].alignment = Alignment(wrap_text=True, vertical="top")
    lbl(ws, "B24", "Facturación anual con esa cartera", bold=True)
    fx(ws, "C24", "='Bandas de precio'!C16*C23*12", MXN, bold=True, fill=FILL_BAND)
    lbl(ws, "B25", "Ingreso objetivo")
    fx(ws, "C25", "=Supuestos!C11", MXN)
    ws["C25"].font = GREEN
    lbl(ws, "B26", "Diferencia contra el objetivo", bold=True)
    fx(ws, "C26", "=C24-C25", MXN, bold=True)
    ws["D26"] = ('=IF(C23=0,"Con esta capacidad no cabe ningún cliente MANAGE: el ingreso tiene que '
                 'venir de diagnósticos y proyectos START.",IF(C26<0,"Falta. Sube precio, sube horas '
                 'o baja el objetivo.","El objetivo se alcanza."))')
    ws["D26"].font = Font(name=FONT, size=10, bold=True, color="B0410E")
    ws["D26"].alignment = Alignment(wrap_text=True, vertical="top")

    lbl(ws, "B28", "LA RUTA QUE SÍ CABE", bold=True)
    ws["B28"].fill = FILL_TINT
    lbl(ws, "B29", "Diagnósticos (Health Check) al año")
    inp(ws, "C29", 8, NUM, "Uno cada mes y medio. Es el producto de entrada y el que mejor paga por hora.")
    lbl(ws, "B30", "Proyectos START al año")
    inp(ws, "C30", 4, NUM, "Uno por trimestre, normalmente derivado de un diagnóstico previo.")
    lbl(ws, "B31", "Horas que consume ese plan")
    fx(ws, "C31", "=C29*'Horas por producto'!G5+C30*'Horas por producto'!G6", HRS, bold=True)
    lbl(ws, "B32", "Contra las horas disponibles al año")
    fx(ws, "C32", "=C5", HRS)
    lbl(ws, "B33", "Horas libres restantes", bold=True)
    fx(ws, "C33", "=C32-C31", HRS, bold=True, fill=FILL_BAND)
    lbl(ws, "B34", "Facturación anual de ese plan", bold=True)
    fx(ws, "C34", "=C29*'Bandas de precio'!E5+C30*'Bandas de precio'!E6", MXN, bold=True, fill=FILL_BAND)
    lbl(ws, "B35", "Contra el objetivo", bold=True)
    fx(ws, "C35", "=C34-Supuestos!C11", MXN, bold=True)
    ws["D35"] = ('=IF(C33<0,"Este plan tampoco cabe: baja el número de proyectos.",'
                 'IF(C35>=0,"Este plan alcanza el objetivo Y deja "&TEXT(C33,"0")&" horas libres para '
                 'un cliente recurrente.","No alcanza el objetivo, pero cabe. Suma proyectos o sube precio."))')
    ws["D35"].font = Font(name=FONT, size=10, bold=True, color="1B7A43")
    ws["D35"].alignment = Alignment(wrap_text=True, vertical="top")

    n = ws.cell(row=37, column=2,
                value="Lectura del modelo: con capacidad de medio tiempo, el trabajo por volumen "
                      "(coordinar muchos embarques) es el peor negocio por hora, y además es el que "
                      "más se parece a un empleo. Los diagnósticos y los proyectos de precio fijo "
                      "pagan mucho mejor la hora y se pueden agendar. Esa es la razón de arrancar "
                      "por ahí, no un capricho de posicionamiento.")
    n.font = SUB
    n.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=37, start_column=2, end_row=39, end_column=4)
    return ws


# ---------------------------------------------------------------------------
# 6. Sensibilidad
# ---------------------------------------------------------------------------
def sheet_sensitivity(wb):
    ws = wb.create_sheet("Sensibilidad")
    title(ws, "Qué pasa si cambian las horas disponibles y el margen",
          "Tarifa objetivo por hora (MXN) para cada combinación.")
    widths(ws, {"A": 3, "B": 22})
    for col in "CDEFG":
        ws.column_dimensions[col].width = 15

    lbl(ws, "B4", "Horas / semana ↓   Margen →", bold=True)
    margins = [0.20, 0.28, 0.35, 0.42, 0.50]
    for i, m in enumerate(margins):
        c = ws.cell(row=4, column=3 + i, value=m)
        c.font = HEAD
        c.fill = FILL_HEAD
        c.number_format = PCT
        c.border = BOX
        c.alignment = Alignment(horizontal="center")
    ws.cell(row=4, column=2).fill = FILL_HEAD
    ws.cell(row=4, column=2).font = HEAD
    ws.cell(row=4, column=2).alignment = Alignment(wrap_text=True, horizontal="center")
    ws.row_dimensions[4].height = 30

    hours = [6, 9, 12, 16, 20]
    for j, h in enumerate(hours):
        r = 5 + j
        c = ws.cell(row=r, column=2, value=h)
        c.font = BLUE
        c.fill = FILL_INPUT
        c.number_format = HRS
        c.border = BOX
        for i in range(len(margins)):
            col = get_column_letter(3 + i)
            f = ws.cell(row=r, column=3 + i)
            # piso = (ingreso + fijos) / (horas*semanas*(1-no facturable));  objetivo = piso/(1-margen)
            f.value = (f"=IFERROR((Supuestos!$C$11+Supuestos!$C$12)/"
                       f"($B{r}*Supuestos!$C$6*(1-Supuestos!$C$7))/(1-{col}$4),0)")
            f.font = BLACK
            f.number_format = MXN
            f.border = BOX

    n = ws.cell(row=12, column=2,
                value="Leer así: cada celda es la tarifa por hora que Adriana necesita cobrar "
                      "para llegar a su ingreso objetivo con esas horas y ese margen. Menos horas "
                      "disponibles obliga a cobrar más caro, no más barato — es el error más común "
                      "al empezar de medio tiempo.")
    n.font = SUB
    n.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=12, start_column=2, end_row=13, end_column=7)
    return ws


# ---------------------------------------------------------------------------
# 7. Matriz servicios × niveles
# ---------------------------------------------------------------------------
SERVICES = [
    ("Supply chain health check", "Diagnóstico de 10–15 días", "Incluido", "Incluido", "Incluido"),
    ("Plan de importación", "Producto, origen, arancel, costo en destino", "Incluido", "Incluido", "Incluido"),
    ("Gestión de importaciones", "Coordinación de cada embarque de punta a punta", "—", "Incluido", "Incluido"),
    ("Revisión documental previa", "Antes de que embarque el proveedor", "—", "Incluido", "Incluido"),
    ("Coordinación de forwarder y agente", "Selección, comparación y auditoría", "—", "Incluido", "Incluido"),
    ("Cierre de expediente e indicadores", "Costo real por embarque, OTIF, incidencias", "—", "Incluido", "Incluido"),
    ("Optimización de cadena de suministro", "Búsqueda de fugas de costo", "Proyecto aparte", "Proyecto aparte", "Incluido"),
    ("Torre de control logística", "Monitoreo, ETA, retrasos, incidencias", "—", "Proyecto aparte", "Incluido"),
    ("Exportaciones", "Además de importaciones", "—", "—", "Incluido"),
    ("Logística de abastecimiento", "Gestión de proveedores y compras", "—", "—", "Incluido"),
    ("Cumplimiento y auditoría documental", "Trámites y expedientes ante revisión", "—", "—", "Incluido"),
    ("Reporte a dirección", "Control de costos y KPIs al comité", "—", "—", "Incluido"),
    ("Logística de proyectos", "Obra, arranque de planta, transporte especializado", "Proyecto aparte", "Proyecto aparte", "Proyecto aparte"),
    ("Gerencia interina de logística", "3 a 12 meses cubriendo la función", "Proyecto aparte", "Proyecto aparte", "Proyecto aparte"),
]


def sheet_matrix(wb):
    ws = wb.create_sheet("Matriz")
    title(ws, "Matriz de servicios por nivel",
          "Qué entra en cada nivel. Esto es lo que va publicado en el sitio.")
    widths(ws, {"A": 3, "B": 40, "C": 52, "D": 16, "E": 16, "F": 16})

    head(ws, 4, ["Servicio", "Qué es", "START", "MANAGE", "PARTNER"], start=2)

    r = 5
    for name, desc, s, m, p in SERVICES:
        ws.cell(row=r, column=2, value=name).font = BOLD
        d = ws.cell(row=r, column=3, value=desc)
        d.font = BLACK
        d.alignment = Alignment(wrap_text=True, vertical="top")
        for col, val in ((4, s), (5, m), (6, p)):
            c = ws.cell(row=r, column=col, value=val)
            c.alignment = Alignment(horizontal="center")
            c.border = BOX
            if val == "Incluido":
                c.font = Font(name=FONT, size=10, bold=True, color="1B7A43")
                c.fill = PatternFill("solid", fgColor="E8F5EC")
            elif val == "Proyecto aparte":
                c.font = Font(name=FONT, size=9, color="8A5E08")
                c.fill = PatternFill("solid", fgColor="FDF0D5")
            else:
                c.font = Font(name=FONT, size=10, color="A9B2C6")
        r += 1

    lbl(ws, f"B{r+1}", "PRECIO DE CADA NIVEL", bold=True)
    ws[f"B{r+1}"].fill = FILL_TINT
    for i, (lvl, ref) in enumerate((("START", "E6"), ("MANAGE", "C16"), ("PARTNER", "E10"))):
        rr = r + 2 + i
        ws.cell(row=rr, column=2, value=lvl).font = BOLD
        f = ws.cell(row=rr, column=4, value=f"='Bandas de precio'!{ref}")
        f.font = GREEN
        f.number_format = MXN
        f.border = BOX
        ws.cell(row=rr, column=3,
                value={"START": "Proyecto de precio fijo",
                       "MANAGE": "Iguala + fee por embarque (12 embarques/mes)",
                       "PARTNER": "Iguala mensual, contrato anual"}[lvl]).font = SUB

    warn = ws.cell(row=r + 6, column=2,
                   value="PARTNER está en la matriz pero la hoja 'Capacidad' dice si cabe en las "
                         "horas de Adriana. Publicar un nivel que no se puede sostener es peor que "
                         "no ofrecerlo: el primer cliente que lo contrate se lleva la mala experiencia.")
    warn.font = Font(name=FONT, size=10, italic=True, color="B0410E")
    warn.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r + 6, start_column=2, end_row=r + 7, end_column=6)
    return ws


# ---------------------------------------------------------------------------
# 8. Validación de mercado
# ---------------------------------------------------------------------------
def sheet_validation(wb):
    ws = wb.create_sheet("Validación de mercado")
    title(ws, "Antes de publicar un precio",
          "El modelo da el piso. El mercado da el techo. Falta la mitad del dato.")
    widths(ws, {"A": 3, "B": 34, "C": 20, "D": 20, "E": 20, "F": 44})

    n = ws.cell(row=4, column=2,
                value="Este libro calcula lo que logistika NECESITA cobrar. No sabe lo que el "
                      "mercado de Querétaro está dispuesto a pagar, porque nadie lo ha preguntado "
                      "todavía. Sin este contraste, el riesgo no es cobrar caro: es cobrar barato "
                      "y no enterarse.")
    n.font = SUB
    n.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=4, start_column=2, end_row=5, end_column=6)

    head(ws, 7, ["A quién preguntar", "Qué preguntar", "Precio que mencionó",
                 "Fecha", "Fuente"], start=2)
    rows = [
        ("Un agente aduanal conocido",
         "Cuánto cobra un consultor externo que le audita al cliente", "", "", ""),
        ("Un ex-colega de Geodis o UTI",
         "Qué cobra hoy quien hace gestión de importaciones por fuera", "", "", ""),
        ("Un contacto en un parque industrial",
         "Qué presupuesto tienen para un diagnóstico externo", "", "", ""),
        ("Una empresa que ya dijo que no",
         "Qué le pareció caro y contra qué lo comparó", "", "", ""),
        ("Alguien del Foro de Logística de SEDESU",
         "Qué proveedores usan y en qué rango pagan", "", "", ""),
    ]
    r = 8
    for a, b, c, d, e in rows:
        ws.cell(row=r, column=2, value=a).font = BLACK
        cb = ws.cell(row=r, column=3, value=b)
        cb.font = BLACK
        cb.alignment = Alignment(wrap_text=True, vertical="top")
        for col in (4, 5, 6):
            cc = ws.cell(row=r, column=col)
            cc.fill = FILL_INPUT
            cc.border = BOX
            cc.font = BLUE
        ws.cell(row=r, column=4).number_format = MXN
        ws.row_dimensions[r].height = 30
        r += 1

    tip = ws.cell(row=r + 1, column=2,
                  value="Regla práctica: si nadie ha dicho que el precio le parece caro, está "
                        "bajo. Un porcentaje sano de propuestas rechazadas por precio está entre "
                        "el 20% y el 40%; con cero rechazos, se está dejando dinero en la mesa.")
    tip.font = SUB
    tip.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r + 1, start_column=2, end_row=r + 2, end_column=6)
    return ws


def main() -> None:
    wb = Workbook()
    wb.remove(wb.active)
    sheet_readme(wb)
    sheet_assumptions(wb)
    sheet_hours(wb)
    sheet_bands(wb)
    sheet_capacity(wb)
    sheet_sensitivity(wb)
    sheet_matrix(wb)
    sheet_validation(wb)
    wb.save(OUT)
    print(f"  {OUT.name}  ({len(wb.sheetnames)} hojas)")


if __name__ == "__main__":
    main()
