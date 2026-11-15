# -*- coding: utf-8 -*-
"""
Masterplan Whitechapel 240 x 180 m -- layout tecnico + validacion (Division D).

NO toca Unreal. Genera, a partir de las tablas de este archivo:
  SourceData/D/masterplan_240/whitechapel_layout.json
  SourceData/D/masterplan_240/whitechapel_buildings.csv
  SourceData/D/masterplan_240/whitechapel_routes.csv
  SourceData/D/masterplan_240/whitechapel_masterplan.svg
  SourceData/D/masterplan_240/validation_report.md

Sistema del plano (documento WHITECHAPEL_MASTERPLAN_CON_REQUISITOS_ASSETS_CLAUDE.md):
  origen SO, +x = este, +y = norte, metros. Rect = (x0, y0, x1, y1) absolutos.
Transformacion al editor (comprobada en el mapa real: X de Unreal = norte, Y = este):
  UE_X = OFF_X + 100*y ;  UE_Y = OFF_Y + 100*x ;  UE_Z = OFF_Z + 100*z
  yaw_UE = 90 - heading_plano   (heading 0 = este, 90 = norte)

Solo Python estandar. Uso:  python -I Scripts/D/masterplan240_layout.py
"""
import csv, json, math, os, sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "SourceData", "D", "masterplan_240")

# Offset recomendado [PROPUESTA]: distrito fuera de la geometria actual (Ground llega a UE_Y 11500)
OFF = {"recommended": (0.0, 12000.0, 0.0), "spawn_aligned": (-600.0, -8600.0, 0.0)}

def ue(x, y, off="recommended"):
    ox, oy, _ = OFF[off]
    return (round(ox + 100 * y), round(oy + 100 * x))

# ---------------------------------------------------------------- envolventes (masterplan §2)
ZONES = {
    "Z01": ("Calle de llegada / inicio", (94, 0, 114, 27)),
    "Z02": ("Plaza y mercado (envolvente)", (29, 16, 113, 83)),
    "Z03": ("Plaza despejada interior", (46, 29, 99, 70)),
    "Z04": ("Taller + patio de Jack", (122, 17, 168, 69)),
    "Z05": ("Calle taller-escape", (151, 61, 181, 79)),
    "Z06": ("Corredor de escape", (158, 70, 192, 135)),
    "Z07": ("Ruta alternativa central", (108, 87, 175, 112)),
    "Z08": ("Transito al refugio", (175, 125, 209, 151)),
    "Z09": ("Refugio y patio secreto", (194, 139, 235, 176)),
    "Z10": ("Registro medico", (193, 105, 236, 140)),
    "Z11": ("Informe fabricado", (193, 68, 237, 106)),
    "Z12": ("Paso central hacia archivo", (107, 100, 165, 126)),
    "Z13": ("Antepatio del Supervisor", (65, 108, 113, 144)),
    "Z14": ("Acceso lateral al archivo", (111, 120, 151, 149)),
    "Z15": ("Complejo del archivo", (33, 137, 130, 179)),
    "Z16": ("Sala de eleccion", (65, 151, 89, 168)),
    "Z17": ("Calles escenograficas oeste", (0, 16, 29, 176)),
    "Z18": ("Calles escenograficas este", (237, 16, 240, 176)),
}

# ---------------------------------------------------------------- nodos (§3.2). Ajustes documentados en NODE_NOTES
NODES = {
    "N01": (104, 9), "N02": (104, 32), "N03": (78, 48), "N04": (106, 48), "N05": (117, 48),
    "N06": (140, 45), "N07": (158, 64), "N08": (176, 75), "N09": (176, 103), "N10": (181, 127),
    "N11": (205.5, 143), "N12": (214, 158), "N13": (211, 122), "N14": (212, 87), "N15": (161, 115),
    "N16": (120, 115), "N17": (94, 122), "N18": (122, 137), "N19": (92, 149), "N20": (77, 160),
}
TEST_POINTS = {"J0": (150, 52)}  # puesto de Jack en el taller (punto de prueba, no es nodo del masterplan)
NODE_NOTES = {
    "N11": "(203,146) -> (205.5,143): el porton queda en el muro sur del recinto (y=145); el nodo se pone delante.",
    "N15": "(161,111) -> (161,115): y=111 cae en la hilera de casas norte de la ruta azul; se centra en el paso central.",
    "N03": "La fuente se centra en (75,48); N03 queda en su anillo libre (se ajusta solo el punto de prueba si cae en solido).",
}

# ---------------------------------------------------------------- espacios transitables
# kind: street | alley | plaza | patio | arena-court | interior | door | scenic(no nav)
# minw = ancho libre minimo exigido (masterplan §3.1 / §5); axis = eje longitudinal para medir secciones
WALK = [
    # id, kind, rect, axis, minw_free, spec_text
    ("W-SAV", "street", (84, 2, 124, 14), "x", 7.0, "Avenida visual sur 12 m (tramo navegable, cerrado con barricadas en x=84 y x=124)"),
    ("W-Z01", "street", (99, 0, 109, 24), "y", 7.0, "Calle de llegada 10 m"),
    ("W-PS1", "alley", (95, 14, 99, 24), "y", 2.7, "Paso de servicio avenida-plaza 4 m"),
    ("W-PL", "plaza", (41, 24, 109, 72), None, None, "Plaza 68 x 48 (contiene Z03 46-99 x 29-70)"),
    ("W-STE", "street", (109, 44, 140, 52), "x", 6.0, "Corredor este plaza-taller 8 m"),
    ("W-PN", "street", (84, 72, 92, 106), "y", 5.5, "Calle norte plaza-antepatio 8 m (ruta amarilla de la imagen)"),
    ("W-ALA1", "alley", (92, 92, 130, 96.5), "x", 2.7, "Ruta azul A, tramo oeste 4,5 m"),
    ("W-PTCP", "patio", (130, 92, 142, 102), None, None, "Patio intermedio 12 x 10"),
    ("W-ARCP", "alley", (134.25, 102, 137.75, 112), "y", 2.7, "Pasaje cubierto 3,5 m (arco)"),
    ("W-ALA3", "alley", (142, 98, 166, 102.5), "x", 2.7, "Ruta azul A, tramo este 4,5 m"),
    ("W-STCP", "street", (112, 112, 176, 118), "x", 5.0, "Paso central 6 m"),
    ("W-FC", "arena-court", (76, 106, 112, 137), None, None, "Antepatio del Supervisor 36 x 31"),
    ("W-AC", "patio", (112, 124, 130, 146), None, None, "Patio de acceso al archivo 18 x 22 (reja N18)"),
    ("W-PAS", "alley", (156, 40, 160, 58), "y", 2.7, "Pasillo junto al taller 4 m"),
    ("W-PTW", "patio", (146, 58, 160, 71), None, None, "Patio trasero del taller 14 x 13"),
    ("W-STX", "street", (160, 60, 179, 67), "x", 5.0, "Calle taller-escape 7 m"),
    ("W-ESC1", "street", (172, 60, 179, 84), "y", 5.0, "Escape tramo 1, 7 m"),
    ("W-NK1", "alley", (174, 84, 178.5, 91), "y", 4.2, "Estrechamiento 1: 4,5 m x 7 m"),
    ("W-ESCW", "arena-court", (166, 91, 183, 106), None, None, "Ensanche de combate 17 x 15"),
    ("W-NK2", "alley", (176, 106, 180.5, 113), "y", 4.2, "Estrechamiento 2: 4,5 m x 7 m"),
    ("W-ESC2", "street", (176, 113, 183, 139), "y", 5.0, "Escape tramo 2, 7 m"),
    ("W-NI1", "patio", (179, 72, 183, 78), None, None, "Nicho de cobertura 4 x 6"),
    ("W-NI2", "patio", (183, 118, 187, 124), None, None, "Nicho de cobertura 4 x 6"),
    ("W-SV1", "alley", (179, 80, 182.5, 91), "y", 2.2, "Pasadizo de servicio 3,5 m"),
    ("W-TR", "street", (176, 139, 210, 145), "x", 5.0, "Transito al refugio 6 m"),
    ("W-REFP", "patio", (202, 145.5, 222, 162.5), None, None, "Patio del refugio 20 x 17"),
    ("W-REFY", "patio", (222, 145.5, 235, 150), None, None, "Patio de servicio del refugio"),
    ("W-STEV", "alley", (224, 64, 228.5, 145), "y", 4.0, "Corredor sur-norte de evidencias 4,5 m (ruta verde)"),
    ("W-ALB1", "alley", (179, 64, 224, 68), "x", 3.0, "Ruta verde B, 4 m"),
    ("W-ALB2", "alley", (183, 97, 212, 100.5), "x", 2.7, "Retorno evidencias-escape 3,5 m"),
    ("W-PTRP", "patio", (212, 96, 224, 106), None, None, "Patio de carga del informe 12 x 10"),
    ("W-INFP", "patio", (213, 133, 224, 142), None, None, "Patio exterior de enfermeria 11 x 9"),
    ("W-SW", "scenic", (23, 14, 29, 100), "y", None, "Calle escenografica oeste 6 m (sin NavMesh, cerrada)"),
]

# ---------------------------------------------------------------- familias (anexo §12.3) [PROPUESTA]
FAM = {
    # id: (nombre, h_min, h_max, candidato local)
    "AR01": ("Vivienda pequena 5,5-6 x 10-12", 6.5, 7.5, "SM_House_Brick"),
    "AR02": ("Vivienda mediana 7 x 12-13", 8.0, 10.0, "SM_House_Filler"),
    "AR03": ("Comercio 8-9 x 12-13", 8.5, 11.0, "SM_House_Shop"),
    "AR04": ("Esquina de manzana", 7.0, 9.0, "SM_House_Corner"),
    "AR05": ("Almacen / deposito 10-15 x 11-18", 7.5, 10.0, "SM_House_Filler / SM_House_Workshop"),
    "AR06": ("Taller de Jack 16 x 18", 6.0, 7.0, "SM_House_Workshop"),
    "AR07": ("Casa-refugio 13 x 12", 7.0, 9.0, "SM_House_Brick / SM_House_ShopLow"),
    "AR08": ("Enfermeria 18 x 20", 9.0, 11.0, "-"),
    "AR09": ("Archivo (cuerpos)", 10.0, 14.0, "SM_House_Agency"),
    "AR10": ("Cobertizo / anexo 4-6 x 6-9", 3.0, 4.5, "-"),
}

BUILD = []  # dicts

def add(bid, group, fam, rect, front, special=False, interior=None, doors=None, note=""):
    BUILD.append(dict(id=bid, group=group, fam=fam, rect=rect, front=front, special=special,
                      interior=interior or [], doors=doors or [], note=note))

def rowx(prefix, group, fam, x, y0, y1, widths, front, note=""):
    """hilera a lo largo de x; cada casa ocupa [x, x+w] x [y0, y1]"""
    for i, w in enumerate(widths):
        add(f"{prefix}{i+1:02d}", group, fam, (x, y0, x + w, y1), front, note=note)
        x += w

def rowy(prefix, group, fam, y, x0, x1, widths, front, note=""):
    for i, w in enumerate(widths):
        add(f"{prefix}{i+1:02d}", group, fam, (x0, y, x1, y + w), front, note=note)
        y += w

# --- piezas especiales (10)
add("SP-TALLER", "HITO", "AR06", (140, 40, 156, 58), "W", True,
    interior=[(140.4, 40.4, 155.6, 57.6)],
    doors=[(139.4, 44, 140.6, 46.5), (147.8, 57.4, 150.8, 58.6), (155.4, 48, 156.6, 50.5)],
    note="Entrada N06 al oeste (calle este); puerta trasera 3 m al patio (paso de Jack); puerta lateral al pasillo")
add("SP-ANEXO", "HITO", "AR10", (160, 40, 168, 50), "W", True, note="Anexo de almacen 8 x 10; puerta al pasillo")
add("SP-REFUGIO", "HITO", "AR07", (222, 150, 235, 162), "W", True,
    interior=[(222.4, 150.4, 234.6, 161.6)], doors=[(221.4, 154, 222.6, 156.6)],
    note="Estancia usable 8 x 7 dentro; puerta al patio")
add("SP-COBERTIZO", "HITO", "AR10", (197, 146, 202, 153), "E", True, note="Cobertizo 5 x 7 pegado al muro oeste")
add("SP-ENFERMERIA", "HITO", "AR08", (206, 113, 224, 133), "E", True,
    interior=[(207, 118, 215, 127), (215, 120, 223.6, 122.6)], doors=[(223.4, 120, 224.6, 122.6)],
    note="Sala del registro 8 x 9 + pasillo 2,6 m hacia el corredor de evidencias")
add("SP-INFORME", "HITO", "AR05", (206, 78, 220, 96), "N", True,
    interior=[(208, 84, 217, 94), (213, 94, 215.6, 95.6)], doors=[(213, 95.4, 215.6, 96.6)],
    note="Sala de archivo de la agencia 9 x 10; acceso por el patio de carga")
add("SP-ARCH-CENTRAL", "HITO", "AR09", (56, 146, 94, 170), "S", True,
    interior=[(84.4, 146.4, 93.6, 151), (65, 151, 89, 168)], doors=[(90, 145.4, 94.5, 146.6), (93.4, 148.4, 94.6, 151.6)],
    note="Cuerpo central 38 x 24; vestibulo N19 y sala de eleccion Z16 24 x 17")
add("SP-ARCH-ALA-O", "HITO", "AR09", (37, 146, 56, 168), "S", True, note="Ala oeste 19 x 22, fachada")
add("SP-ARCH-ALA-E", "HITO", "AR09", (100, 146, 118, 166), "S", True,
    interior=[(100.4, 146.4, 117.6, 152)], doors=[(113.5, 145.4, 116.5, 146.6), (99.4, 148.4, 100.6, 151.6)],
    note="Ala este 18 x 20; entrada desde el patio de acceso (N18) y galeria hacia el vestibulo")
add("SP-ARCH-PORTICO", "HITO", "AR09", (84, 137, 100, 146), "S", True,
    interior=[(86, 137.6, 98, 145.6)], doors=[(88, 136.4, 96, 137.6), (90, 145.4, 94.5, 146.6)],
    note="Portico 16 x 9 con hueco de 8 m bajo cubierta; puertas del archivo (4,5 m) al fondo")
# conector (no cuenta como edificio)
add("CX-ARCH-GALERIA", "CONECTOR", "AR09", (94, 148, 100, 152), "S", True,
    interior=[(93.4, 148.4, 100.6, 151.6)], note="Galeria interior 3,2 m entre ala este y vestibulo")

# --- manzanas ambientales (§6)
# M-A oeste de plaza (frente este) + PL-B01/B02
rowy("MA-", "M-A", "AR01", 24, 30, 41, [6, 6, 6, 6, 6, 6], "E", "PL-B02 incluidas")
add("MA-07", "M-A", "AR03", (29, 60, 41, 68), "E", note="PL-B01 comercio occidental 8 x 12")
add("MA-08", "M-A", "AR04", (29, 68, 41, 76), "E", note="Esquina NO de la plaza")
rowy("MA-N", "M-A", "AR01", 87, 72, 84, [6, 6, 6], "E", "Frente oeste de la calle norte")
# M-B norte de plaza (frente sur) + PL-B03/B04
add("MB-01", "M-B", "AR05", (41, 72, 53, 87), "S", note="PL-B04 almacen norte 12 x 15")
add("MB-02", "M-B", "AR03", (53, 72, 62, 85), "S", note="PL-B03 comercio norte 9 x 13")
rowx("MB-R", "M-B", "AR03", 62, 72, 85, [8, 8], "S")
add("MB-05", "M-B", "AR01", (78, 72, 84, 85), "S", note="Remate junto a la calle norte")
rowx("MB-E", "M-B", "AR03", 92, 72, 85, [8, 8], "S", "Al este de la calle norte")
# M-C sur / sureste de plaza (PL-B05/B06)
rowx("MC-S", "M-C", "AR01", 41, 14, 24, [6] * 9, "N", "PL-B06 incluidas; lado camara")
rowy("MC-E", "M-C", "AR01", 14, 109, 119, [6, 6, 6, 6, 6], "W", "Fachada este de la llegada y de la plaza")
add("MC-P", "M-C", "AR03", (109, 64, 121, 72), "W", note="PL-B05 frente este de la plaza")
# M-D junto al taller
rowx("MD-S", "M-D", "AR01", 122, 32, 44, [6, 6, 6], "N", "Sur de la calle este; lado camara")
rowx("MD-N", "M-D", "AR01", 109, 52, 64, [6, 6, 6, 6, 6], "S", "Norte de la calle este")
add("MD-W", "M-D", "AR05", (124, 16, 139, 27), "N", note="Almacen 15 x 11 (11 x 15 girado)")
add("MD-T", "M-D", "AR01", (140, 28, 146, 40), "N", note="Edificio falso que cierra el taller por el sur")
# M-E flanqueando la ruta azul
rowx("ME-S", "M-E", "AR01", 108, 81, 92, [5.5, 5.5, 5.5, 5.5, 5.5, 5.5], "N", "Sur de la ruta azul; lado camara")
rowx("ME-N", "M-E", "AR01", 92, 96.5, 105.5, [6, 6, 6], "S", "Norte de la ruta azul (espalda al antepatio)")
rowx("ME-M", "M-E", "AR01", 112, 96.5, 107.5, [5.5, 5.5, 5.5], "S")
add("ME-A1", "M-E", "AR10", (130, 102, 134.25, 112), "E", note="Flanco oeste del arco")
rowx("ME-A", "M-E", "AR01", 137.75, 102.5, 112, [6, 6, 6, 6], "S", "Norte de la ruta azul este")
rowx("ME-B", "M-E", "AR01", 142, 88, 98, [6, 6, 6], "N", "Sur de la ruta azul este")
add("ME-C", "M-E", "AR04", (160, 91, 166, 98), "N", note="Esquina hacia el ensanche")
# M-F alrededor del escape
rowy("MF-W", "M-F", "AR01", 67, 160, 172, [6, 6, 6, 6], "E", "Oeste del tramo 1; lado camara")
rowx("MF-X", "M-F", "AR01", 160, 50, 60, [6, 6, 6], "N", "Sur de la calle taller-escape; lado camara")
rowy("MF-E", "M-F", "AR01", 68, 183, 195, [6, 6, 6, 6], "W", "Este del tramo 1")
add("MF-D1", "M-F", "AR05", (195, 84, 205, 97), "N", note="Deposito 10 x 13")
rowx("MF-N", "M-F", "AR01", 183, 100.5, 110.5, [6, 6], "S")
add("MF-D2", "M-F", "AR05", (199, 100.5, 212, 110.5), "S", note="Deposito 13 x 10")
rowy("MF-R", "M-F", "AR01", 124, 183, 195, [6, 6], "W", "Este del tramo 2")
# M-G este de evidencias
rowx("MG-S", "M-G", "AR01", 206, 68, 78, [6, 6, 6], "S", "Norte de la ruta verde")
rowx("MG-B", "M-G", "AR01", 179, 52, 64, [6, 6, 6, 6, 6, 6, 6], "N", "Sur de la ruta verde; lado camara")
rowy("MG-E", "M-G", "AR01", 64, 228.5, 238.5, [6, 6, 6, 6, 6], "W", "Este del corredor de evidencias")
rowy("MG-F", "M-G", "AR05", 94, 228.5, 238.5, [13, 13, 12], "W", "Depositos al este del corredor")
rowy("MG-G", "M-G", "AR01", 132, 228.5, 238.5, [6, 6], "W")
# M-H perimetro del refugio
rowx("MH-", "M-H", "AR02", 176, 146, 158, [7, 7, 7], "S", "Norte del transito")
add("MH-04", "M-H", "AR02", (196, 127, 203, 139), "N", note="Sur del transito")
# M-I perimetro del archivo
rowy("MI-W", "M-I", "AR02", 137, 24, 37, [7, 7, 7, 7, 7], "E", "Oeste del archivo")
rowy("MI-F", "M-I", "AR01", 106, 64, 76, [6, 6, 6, 6, 6], "E", "Oeste del antepatio (graderio/fachada); lado camara")
rowx("MI-C", "M-I", "AR10", 112, 118, 124, [6, 6, 6], "S", "Cobertizos entre paso central y patio de acceso")
rowx("MI-P", "M-I", "AR01", 130, 118, 130, [6, 6, 6, 6, 6, 6, 6], "S", "Norte del paso central")
rowy("MI-A", "M-I", "AR02", 130, 130, 143, [8, 8], "W", "Este del patio de acceso")
# M-J fachadas lejanas (12)
rowy("MJ-W", "M-J", "AR01", 28, 12, 23, [6, 6, 6, 6], "E", "Fondo oeste tras la calle escenografica")
rowx("MJ-N", "M-J", "AR01", 58, 170, 179, [6, 6, 6, 6], "S", "Fondo norte tras el archivo")
rowx("MJ-S", "M-J", "AR01", 146, 30, 40, [6, 6, 6, 6], "N", "Fondo sureste tras el taller")
# siluetas sin interior ni colision de juego (no cuentan como casas)
for i, r in enumerate([(170, 18, 230, 33), (0, 100, 22, 176), (130, 163, 196, 179), (118, 167, 130, 179),
                       (0, 16, 11, 100), (240 - 3, 16, 240, 176)]):
    add(f"SIL-{i+1:02d}", "SIL", "SIL", r, "-", note="Masa de tejados/silueta lejana, sin NavMesh")

# ---------------------------------------------------------------- muros, verjas y portones
WALLS = [
    # refugio: recinto con porton principal SO y de servicio SE
    ("WL-REF-S1", (197, 145, 204, 145.5)), ("WL-REF-S2", (207, 145, 224.5, 145.5)),
    ("WL-REF-S3", (228, 145, 235.5, 145.5)), ("WL-REF-W", (196.5, 145, 197, 174)),
    ("WL-REF-N", (196.5, 173.5, 235.5, 174)), ("WL-REF-E", (235, 145, 235.5, 174)),
    ("WL-REF-I", (202, 162.5, 222, 163)),  # cierre norte del patio (huerto detras)
    # antepatio: muro este con la reja N18
    ("WL-FC-E1", (111.75, 124, 112.25, 128)), ("WL-FC-E2", (111.75, 132.5, 112.25, 137)),
    ("WL-FC-STEP", (100, 137, 112, 146)),       # escalinata/jardinera entre portico y patio de acceso
    ("WL-FC-SW", (76, 137, 84, 146)),           # escalinata oeste del portico
    # patio del taller: cierres oeste y norte, puerta N07 al este
    ("WL-PTW-W", (145.5, 58, 146, 71)), ("WL-PTW-N", (146, 71, 160, 71.5)),
    ("WL-PTW-E1", (159.75, 58, 160.25, 62.5)), ("WL-PTW-E2", (159.75, 65.5, 160.25, 71)),
    # barricadas de cierre de la avenida sur
    ("WL-SAV-W", (83.5, 2, 84, 14)), ("WL-SAV-E", (124, 2, 124.5, 14)),
    # muros bajos que cierran huecos fuera de los nichos del escape
    ("WL-ESC-A", (179, 68, 183, 72)), ("WL-ESC-B", (179, 78, 183, 80)), ("WL-ESC-C", (182.5, 84, 183, 91)),
    # cierre de la calle escenografica oeste (no navegable)
    ("WL-SW-S", (29, 14, 30, 24)),
]
BORDER_WALLS = {"WL-FC-E1", "WL-FC-E2", "WL-PTW-E1", "WL-PTW-E2"}  # muros de linde entre dos espacios (intencionados)
GATES = [
    # id, rect, ancho util, propietario funcional, estados por fase
    ("G-07", (159.75, 62.5, 160.25, 65.5), 3.0, "C/B (BP_Door, Jack)", "Puerta lateral del taller (N07). Cerrada en Acto I; se abre al final del encuentro con Jack."),
    ("G-PN-S", (84, 84, 92, 84.5), 8.0, "C (BP_Door)", "[PROPUESTA] Verja de la calle norte. Cerrada en Actos I-II (evita saltar al escape por la ruta azul)."),
    ("G-PN-N", (84, 105.5, 92, 106), 8.0, "C (BP_Door)", "[PROPUESTA] Reja al antepatio desde la calle norte. Abre en Acto III."),
    ("G-CP", (112, 112, 112.5, 118), 6.0, "C (BP_Door)", "[PROPUESTA] Reja del antepatio en el paso central. Abre al registrar las dos evidencias."),
    ("G-AC", (111.75, 128, 112.25, 132.5), 4.5, "C (BP_Door)", "Reja N18 (acceso lateral). Abre al derrotar al Supervisor; checkpoint."),
    ("G-ARCH", (90, 145.4, 94.5, 145.9), 4.5, "C", "[DECISION] Puertas frontales del archivo: bloqueo narrativo (selladas) o entrada principal."),
    ("G-WING", (113.5, 145.6, 116.5, 146.1), 3.0, "C", "Puerta del ala este (segundo porton hacia N19)."),
    ("G-REF-M", (204, 145, 207, 145.5), 3.0, "C", "Porton principal del refugio (N11). Abierto en Acto II."),
    ("G-REF-S", (224.5, 145, 228, 145.5), 3.5, "C", "Porton de servicio del refugio. Cerrado hasta que Jack esta a salvo."),
    ("G-A3", (165.5, 98, 166, 102.5), 4.5, "C", "Puerta opcional de la ruta azul (abierta)."),
    ("G-B1", (179, 64, 179.5, 68), 4.0, "C", "[PROPUESTA] Ruta verde desde el escape: cerrada hasta que Jack esta a salvo."),
    ("G-B2", (183, 97, 183.5, 100.5), 3.5, "C", "[PROPUESTA] Retorno evidencias-escape: cerrada hasta que Jack esta a salvo."),
]
PHASES = [
    ("Acto I", {"G-07", "G-PN-S", "G-PN-N", "G-CP", "G-AC", "G-ARCH", "G-WING", "G-REF-S", "G-B1", "G-B2"},
     {"N01", "N02", "N03", "N04", "N05", "N06", "N07"}),
    ("Acto II escape", {"G-PN-S", "G-PN-N", "G-CP", "G-AC", "G-ARCH", "G-WING", "G-REF-S", "G-B1", "G-B2"},
     {"N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10", "N11", "N12", "N15", "N16"}),
    ("Acto II evidencias", {"G-PN-S", "G-PN-N", "G-CP", "G-AC", "G-ARCH", "G-WING"},
     {"N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10", "N11", "N12", "N13", "N14", "N15", "N16"}),
    ("Acto III jefe", {"G-PN-S", "G-AC", "G-ARCH", "G-WING"},
     {"N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17"}),
    ("Acto III archivo", {"G-PN-S", "G-ARCH"}, set(NODES)),
]

# ---------------------------------------------------------------- props y obstaculos (centro, tamano)
PROPS = []
def prop(pid, kind, cx, cy, sx, sy, asset):
    PROPS.append(dict(id=pid, kind=kind, rect=(cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2), asset=asset))

prop("PR-FOUNT", "fuente", 75, 48, 5.0, 5.0, "SM_Fountain_Square + base nueva")
for i, x in enumerate([49.5, 57.5, 65.5]):
    prop(f"PR-STALL-N{i+1}", "puesto", x, 68.75, 5.0, 3.5, "SM_MarketStall (generar)")
for i, x in enumerate([49.5, 57.5, 65.5, 73.5]):
    prop(f"PR-STALL-S{i+1}", "puesto", x, 27.75, 5.0, 3.5, "SM_MarketStall (generar)")
prop("PR-CART-PL", "carro", 42.9, 44.25, 2.2, 4.5, "SM_Cart_Victorian (generar)")
for i, (x, y) in enumerate([(43.5, 33), (43.5, 64), (106.5, 27), (106.5, 69), (100.5, 12), (120, 51.4),
                            (172.6, 82), (182.4, 116.5), (176.6, 135), (186, 144.4), (130, 112.4),
                            (150, 117.6), (77, 108), (110.5, 135.5), (204, 161.5), (223.4, 104), (84.4, 79)]):
    prop(f"PR-LAMP-{i+1:02d}", "farola", x, y, 0.6, 0.6, "BP_GasLamp / SM_GasLamp_A")
for i, (x, y, k) in enumerate([(42.6, 37, "caja"), (42.6, 58, "caja"), (107.4, 38, "barril"), (107.4, 60, "caja"),
                               (80, 25.2, "caja"), (92, 25.0, "barril"), (75, 71, "caja"), (100, 71.2, "barril")]):
    s = 1.2 if k == "caja" else 0.8
    prop(f"PR-COV-PL{i+1}", k, x, y, s, s, "SM_CrateStack_A" if k == "caja" else "SM_Barrel_A")
for i, (x, y, k) in enumerate([(172.7, 74, "caja"), (178.5, 62.5, "barril"), (181.5, 75, "caja"), (181.6, 73, "barril"),
                               (185, 121, "caja"), (182.5, 130, "barril"), (100, 95.9, "caja"), (128, 92.5, "barril")]):
    s = 1.2 if k == "caja" else 0.8
    prop(f"PR-COV-ES{i+1}", k, x, y, s, s, "SM_CrateStack_A" if k == "caja" else "SM_Barrel_A")
for i, (x, y, k) in enumerate([(203.2, 160.5, "caja"), (203.2, 158.5, "barril"), (221.2, 146.6, "caja"), (220.5, 160.5, "carretilla")]):
    s = {"caja": (1.2, 1.2), "barril": (0.8, 0.8), "carretilla": (1.1, 1.8)}[k]
    prop(f"PR-COV-RF{i+1}", k, x, y, s[0], s[1], {"caja": "SM_CrateStack_A", "barril": "SM_Barrel_A", "carretilla": "SM_Handcart_A (escala 0,65)"}[k])
for i, (x, y) in enumerate([(78.5, 113), (78.5, 131), (109.5, 113), (109.5, 131)]):
    prop(f"PR-PILLAR-{i+1}", "pilar", x, y, 2.0, 2.0, "SM_ArchivePillar_A")
prop("PR-TABLE-W", "mesa", 143, 55.5, 2.0, 0.9, "SM_WorkshopTable_A")
prop("PR-SHELF-W1", "estante", 155.3, 43.5, 0.5, 2.0, "SM_Shelf_A")
prop("PR-SHELF-W2", "estante", 155.3, 53.5, 0.5, 2.0, "SM_Shelf_A")
prop("PR-DESK-INF", "escritorio", 210, 125.5, 1.8, 0.85, "SM_Desk_Infirmary (generar)")
prop("PR-DESK-RPT", "escritorio", 212, 92.5, 1.6, 0.8, "SM_WorkshopTable_A o SM_Desk_Agency")
prop("PR-ST-OFF", "estacion", 74.5, 163.5, 2.0, 1.4, "SM_RecordStation_Official + base")
prop("PR-ST-AUT", "estacion", 79.5, 163.5, 2.0, 1.4, "SM_RecordStation_Authentic + base")
prop("PR-COT", "catre", 232.5, 158.5, 1.45, 2.45, "SM_Cot_A")

# areas que deben quedar libres de cualquier obstaculo
CLEAR = [
    ("Arena plaza A 18x16", (46, 40, 64, 56)),
    ("Arena plaza B 16x14", (88, 41, 104, 55)),
    ("Ensanche de escape 17x15", (166, 91, 183, 106)),
    ("Arena Supervisor 26x24", (81, 110, 107, 134)),
    ("Sala final libre 15x10", (69.5, 151.5, 84.5, 161.5)),
    ("Espera de Jack 5x5 (refugio)", (211.5, 155.5, 216.5, 160.5)),
    ("Interaccion Jack r2,5 (taller)", (147.5, 49.5, 152.5, 54.5)),
    ("Spawn r3", (101, 6, 107, 12)),
    ("Frente estacion oficial 2,5", (73.5, 160.5, 75.5, 162.8)),
    ("Frente estacion autentica 2,5", (78.5, 160.5, 80.5, 162.8)),
    ("Frente escritorio informe 2x2", (211, 90.1, 213, 92.1)),
    ("Patio intermedio 12x10", (130, 92, 142, 102)),
    ("Patio trasero taller 14x13 (sin la mesa)", (146, 58, 160, 71)),
]
CIRCLES_CLEAR = [("Anillo de la fuente (5 m)", (75, 48), 2.5, 7.5)]

# ---------------------------------------------------------------- rutas obligatorias
ROUTES = [
    # id, nodos, ancho minimo libre, fase, descripcion
    ("R-MAIN-1", ["N01", "N02", "N03", "N04", "N05", "N06"], 1.0, "Acto I", "Llegada, plaza y calle al taller"),
    ("R-MAIN-2", ["N06", "N07", "N08", "N09", "N10", "N11", "N12"], 1.0, "Acto II", "Escape con Jack (cuellos 4,5 m)"),
    ("R-MAIN-3", ["N12", "N13", "N14", "N15", "N16"], 1.0, "Acto II", "Evidencias y regreso al eje"),
    ("R-MAIN-4", ["N16", "N17", "N18", "N19", "N20"], 1.0, "Acto III", "Jefe, reja, archivo, eleccion"),
    ("R-ALT-A", ["N09", "N15"], 2.7, "Acto II", "Ruta azul: ensanche -> AL-A3 -> patio -> arco -> paso central"),
    ("R-ALT-B", ["N08", "N14", "N13", "N12"], 2.2, "Acto II tras Jack", "Ruta verde: escape -> informe -> enfermeria -> refugio"),
    ("R-JACK", ["J0", "N07", "N08", "N09", "N10", "N11", "N12"], 2.4, "Acto II", "Trayecto de Jack desde su puesto en el taller (J0) al refugio"),
]

# =============================================================== geometria
def area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])

def inter(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))

def ov(a, b, eps=1e-6):
    i = inter(a, b)
    return (i[2] - i[0] > eps) and (i[3] - i[1] > eps)

def inside(r, outer, tol=0.0):
    return r[0] >= outer[0] - tol and r[1] >= outer[1] - tol and r[2] <= outer[2] + tol and r[3] <= outer[3] + tol

def gap(a, b):
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)

# =============================================================== rasterizado
RES = 0.25
NX, NY = int(240 / RES), int(180 / RES)

def ix_overlap(x0, x1, n):
    a = max(0, int(math.floor(x0 / RES + 1e-6)))
    b = min(n - 1, int(math.ceil(x1 / RES - 1e-6)) - 1)
    return a, b

def ix_center(x0, x1, n):
    a = max(0, int(math.ceil(x0 / RES - 0.5 - 1e-9)))
    b = min(n - 1, int(math.floor(x1 / RES - 0.5 + 1e-9)))
    return a, b

def mark(grid, r, val, mode):
    f = ix_overlap if mode == "overlap" else ix_center
    i0, i1 = f(r[0], r[2], NX)
    j0, j1 = f(r[1], r[3], NY)
    for j in range(j0, j1 + 1):
        row = grid[j]
        for i in range(i0, i1 + 1):
            row[i] = val

def build_grid(closed_gates, with_props=True):
    dom = [bytearray(NX) for _ in range(NY)]
    for w in WALK:
        if w[1] != "scenic":
            mark(dom, w[2], 1, "center")
    for b in BUILD:
        for r in b["interior"] + b["doors"]:
            mark(dom, r, 1, "center")
    for g in GATES:
        mark(dom, g[1], 1, "overlap")
    blk = [bytearray(NX) for _ in range(NY)]
    for b in BUILD:  # estricto: cada edificio solo se abre por SUS interiores y puertas
        if b["group"] == "SIL":
            continue
        own = [bytearray(NX) for _ in range(NY)] if (b["interior"] or b["doors"]) else None
        if own is None:
            mark(blk, b["rect"], 1, "overlap")
            continue
        mark(own, b["rect"], 1, "overlap")
        for r in b["interior"] + b["doors"]:
            mark(own, r, 0, "center")
        i0, i1 = ix_overlap(b["rect"][0], b["rect"][2], NX); j0, j1 = ix_overlap(b["rect"][1], b["rect"][3], NY)
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                if own[j][i]:
                    blk[j][i] = 1
    for _, r in WALLS:
        mark(blk, r, 1, "overlap")
    for g in GATES:
        if g[0] in closed_gates:
            mark(blk, g[1], 1, "overlap")
    if with_props:
        for p in PROPS:
            mark(blk, p["rect"], 1, "overlap")
    free = [bytearray(NX) for _ in range(NY)]
    for j in range(NY):
        d, b, f = dom[j], blk[j], free[j]
        for i in range(NX):
            f[i] = 1 if (d[i] and not b[i]) else 0
    return free

def dist_field(free):
    INF = 1e9
    D = [[(0.0 if not free[j][i] else INF) for i in range(NX)] for j in range(NY)]
    s2 = math.sqrt(2)
    for j in range(NY):
        for i in range(NX):
            v = D[j][i]
            if v == 0:
                continue
            if i > 0: v = min(v, D[j][i - 1] + 1)
            if j > 0:
                v = min(v, D[j - 1][i] + 1)
                if i > 0: v = min(v, D[j - 1][i - 1] + s2)
                if i < NX - 1: v = min(v, D[j - 1][i + 1] + s2)
            D[j][i] = v
    for j in range(NY - 1, -1, -1):
        for i in range(NX - 1, -1, -1):
            v = D[j][i]
            if v == 0:
                continue
            if i < NX - 1: v = min(v, D[j][i + 1] + 1)
            if j < NY - 1:
                v = min(v, D[j + 1][i] + 1)
                if i < NX - 1: v = min(v, D[j + 1][i + 1] + s2)
                if i > 0: v = min(v, D[j + 1][i - 1] + s2)
            D[j][i] = v
    # distancia aproximada en metros desde el centro de celda hasta el borde libre
    return [[(v - 0.5) * RES for v in row] for row in D]

def cell(p):
    return (min(NX - 1, int(p[0] / RES)), min(NY - 1, int(p[1] / RES)))

def snap(D, p, r, maxd=3.0):
    i0, j0 = cell(p)
    if D[j0][i0] >= r:
        return (i0, j0), 0.0
    best = None
    R = int(maxd / RES)
    for dj in range(-R, R + 1):
        for di in range(-R, R + 1):
            i, j = i0 + di, j0 + dj
            if 0 <= i < NX and 0 <= j < NY and D[j][i] >= r:
                d = math.hypot(di, dj) * RES
                if best is None or d < best[1]:
                    best = ((i, j), d)
    return best if best else (None, None)

def bfs(D, start, r):
    seen = bytearray(NX * NY)
    q = deque([start])
    seen[start[1] * NX + start[0]] = 1
    while q:
        i, j = q.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < NX and 0 <= b < NY and not seen[b * NX + a] and D[b][a] >= r:
                seen[b * NX + a] = 1
                q.append((a, b))
    return seen

def path_len(D, s, t, r):
    """BFS 8-conexo; devuelve longitud aproximada (m) o None"""
    prev = {s: None}
    q = deque([s])
    while q:
        c = q.popleft()
        if c == t:
            break
        i, j = c
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == dj == 0:
                    continue
                a, b = i + di, j + dj
                if 0 <= a < NX and 0 <= b < NY and (a, b) not in prev and D[b][a] >= r:
                    prev[(a, b)] = c
                    q.append((a, b))
    if t not in prev:
        return None
    L, c = 0.0, t
    while prev[c] is not None:
        p = prev[c]
        L += math.hypot(c[0] - p[0], c[1] - p[1]) * RES
        c = p
    return L

def section_widths(free, rect, axis):
    """ancho libre minimo por secciones transversales (descarta 1 m en cada extremo)"""
    i0, i1 = ix_center(rect[0], rect[2], NX)
    j0, j1 = ix_center(rect[1], rect[3], NY)
    res = []
    if axis == "x":
        rng, cross = range(i0 + 4, i1 - 3), (j0, j1)
        for i in rng:
            run = best = 0
            for j in range(cross[0], cross[1] + 1):
                run = run + 1 if free[j][i] else 0
                best = max(best, run)
            res.append((best * RES, (i + 0.5) * RES))
    else:
        rng, cross = range(j0 + 4, j1 - 3), (i0, i1)
        for j in rng:
            run = best = 0
            for i in range(cross[0], cross[1] + 1):
                run = run + 1 if free[j][i] else 0
                best = max(best, run)
            res.append((best * RES, (j + 0.5) * RES))
    return min(res) if res else (None, None)

# =============================================================== validacion
def validate():
    rep = {"overlaps_bb": [], "overlaps_bw": [], "overlaps_pw": [], "overlaps_clear": [], "small_gaps": [],
           "envelopes": [], "widths": [], "phases": [], "routes": [], "nodes": []}
    solids = [b for b in BUILD if b["group"] != "SIL"]
    for i in range(len(solids)):
        for k in range(i + 1, len(solids)):
            a, b = solids[i], solids[k]
            if ov(a["rect"], b["rect"]):
                rep["overlaps_bb"].append((a["id"], b["id"], round(area(inter(a["rect"], b["rect"])), 2)))
            else:
                g = gap(a["rect"], b["rect"])
                if 0.01 < g < 3.0:
                    rep["small_gaps"].append((a["id"], b["id"], round(g, 2)))
    walk_nav = [w for w in WALK if w[1] != "scenic"]
    for b in BUILD:
        for w in WALK:
            if ov(b["rect"], w[2]):
                rep["overlaps_bw"].append((b["id"], w[0], round(area(inter(b["rect"], w[2])), 2)))
    for wid, r in WALLS:
        if wid in BORDER_WALLS:
            continue
        for w in walk_nav:
            if ov(r, w[2]):
                rep["overlaps_bw"].append((wid, w[0], round(area(inter(r, w[2])), 2)))
    for p in PROPS:
        for name, r in CLEAR:
            if ov(p["rect"], r):
                rep["overlaps_clear"].append((p["id"], name))
        for name, c, rin, rout in CIRCLES_CLEAR:
            if p["id"] == "PR-FOUNT":
                continue
            cx = min(max(c[0], p["rect"][0]), p["rect"][2]); cy = min(max(c[1], p["rect"][1]), p["rect"][3])
            if math.hypot(cx - c[0], cy - c[1]) < rout:
                rep["overlaps_clear"].append((p["id"], name))
        hosted = any(inside(p["rect"], r) for b in BUILD for r in b["interior"])
        in_walk = any(inside(p["rect"], w[2]) for w in walk_nav)
        if not (hosted or in_walk):
            rep["overlaps_pw"].append((p["id"], "fuera de espacio transitable/interior"))
    # piezas especiales dentro de su envolvente
    env_of = {"SP-TALLER": "Z04", "SP-ANEXO": "Z04", "SP-REFUGIO": "Z09", "SP-COBERTIZO": "Z09",
              "SP-ENFERMERIA": "Z10", "SP-INFORME": "Z11", "SP-ARCH-CENTRAL": "Z15", "SP-ARCH-ALA-O": "Z15",
              "SP-ARCH-ALA-E": "Z15", "SP-ARCH-PORTICO": "Z15"}
    for bid, z in env_of.items():
        b = next(x for x in BUILD if x["id"] == bid)
        rep["envelopes"].append((bid, z, inside(b["rect"], ZONES[z][1], tol=0.01)))
    rep["envelopes"].append(("Z16 sala dentro del cuerpo central", "Z16",
                             inside(ZONES["Z16"][1], next(x for x in BUILD if x["id"] == "SP-ARCH-CENTRAL")["rect"])))
    for name, r in CLEAR:
        if "Arena plaza" in name:
            rep["envelopes"].append((name + " fuera de edificios", "Z03", inside(r, (41, 24, 109, 72))))
    # anchos libres con props
    free_all = build_grid(closed_gates=set(), with_props=True)
    for w in WALK:
        if w[3] and w[4]:
            mw, at = section_widths(free_all, w[2], w[3])
            rep["widths"].append((w[0], w[5], w[4], mw, at, mw is not None and mw + 1e-6 >= w[4]))
    # fases (holgura jugador 0,45 m)
    for name, closed, expected in PHASES:
        D = dist_field(build_grid(closed))
        s, _ = snap(D, NODES["N01"], 0.45)
        seen = bfs(D, s, 0.45)
        got = set()
        for n, p in NODES.items():
            c, d = snap(D, p, 0.45)
            if c and seen[c[1] * NX + c[0]]:
                got.add(n)
        rep["phases"].append((name, sorted(got), sorted(expected - got), sorted(got - expected)))
    # rutas con todos los portones abiertos
    D_all = dist_field(free_all)
    for rid, nodes, minw, phase, desc in ROUTES:
        r = minw / 2.0
        D = D_all
        legs, ok = [], True
        for a, b in zip(nodes, nodes[1:]):
            P = {**NODES, **TEST_POINTS}
            ca, da = snap(D, P[a], r)
            cb, db = snap(D, P[b], r)
            L = path_len(D, ca, cb, r) if ca and cb else None
            legs.append((a, b, None if L is None else round(L, 1)))
            ok = ok and L is not None
        rep["routes"].append((rid, desc, minw, phase, ok, legs))
    D = D_all
    for n, p in NODES.items():
        c, d = snap(D, p, 0.45)
        rep["nodes"].append((n, p, d, None if c is None else round(D[c[1]][c[0]], 2)))
    return rep

# =============================================================== salidas
def heading(front):
    return {"E": 0, "N": 90, "W": 180, "S": 270}.get(front, 0)

def camera_side(front):
    # camara al SO mirando al NE (yaw 45): fachadas que miran al N o al E estan en el lado de camara
    return front in ("N", "E")

def building_rows():
    rows = []
    for b in BUILD:
        x0, y0, x1, y1 = b["rect"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sx, sy = x1 - x0, y1 - y0
        width, depth = (sx, sy) if b["front"] in ("N", "S") else (sy, sx)
        if b["group"] == "SIL":
            h, occl = 9.0, "silueta"
        else:
            fam = FAM[b["fam"]]
            if b["special"]:
                h = fam[2] if b["fam"] in ("AR09",) else (fam[1] + fam[2]) / 2
            else:
                h = fam[1] if camera_side(b["front"]) else fam[2]
            occl = "fade/corte" if camera_side(b["front"]) else "fondo"
        hd = heading(b["front"])
        uex, uey = ue(cx, cy)
        rows.append(dict(ID=b["id"], Group=b["group"], Family=b["fam"],
                         Typology=FAM[b["fam"]][0] if b["fam"] in FAM else "Silueta lejana",
                         x=round(cx, 2), y=round(cy, 2), z=0, xMin=x0, yMin=y0, xMax=x1, yMax=y1,
                         FrontWidthM=round(width, 2), DepthM=round(depth, 2), HeightM=h, Front=b["front"],
                         HeadingPlan=hd, YawUE=(90 - hd) % 360, UE_X=uex, UE_Y=uey,
                         Asset=(FAM[b["fam"]][3] if b["fam"] in FAM else "kit de tejados simplificado"),
                         Status="PROPUESTA", Sublevel="L_Whitechapel_Geo_v5 [PROPUESTA]",
                         Interior="si" if b["interior"] else "no", Occlusion=occl, Note=b["note"]))
    return rows

def write_svg(path, rep):
    S, M = 4.0, 40  # px por metro, margen
    Wp, Hp = 240 * S + 2 * M + 260, 180 * S + 2 * M
    def X(x): return M + x * S
    def Y(y): return M + (180 - y) * S
    def R(r, **kw):
        a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return f'<rect x="{X(r[0]):.1f}" y="{Y(r[3]):.1f}" width="{(r[2]-r[0])*S:.1f}" height="{(r[3]-r[1])*S:.1f}" {a}/>'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wp:.0f}" height="{Hp:.0f}" viewBox="0 0 {Wp:.0f} {Hp:.0f}" font-family="Segoe UI, Arial" >',
         f'<rect width="100%" height="100%" fill="#f4f1ea"/>',
         R((0, 0, 240, 180), fill="#e3ded3", stroke="#555", stroke_width=1.5)]
    for x in range(0, 241, 10):
        o.append(f'<line x1="{X(x)}" y1="{Y(0)}" x2="{X(x)}" y2="{Y(180)}" stroke="#c9c2b4" stroke-width="{0.9 if x%50 else 1.6}"/>')
        o.append(f'<text x="{X(x)}" y="{Y(0)+14}" font-size="9" text-anchor="middle" fill="#444">{x}</text>')
    for y in range(0, 181, 10):
        o.append(f'<line x1="{X(0)}" y1="{Y(y)}" x2="{X(240)}" y2="{Y(y)}" stroke="#c9c2b4" stroke-width="{0.9 if y%50 else 1.6}"/>')
        o.append(f'<text x="{X(0)-6}" y="{Y(y)+3}" font-size="9" text-anchor="end" fill="#444">{y}</text>')
    kc = {"street": "#f2d98d", "alley": "#a9d6e5", "plaza": "#f7e6b0", "patio": "#cfe8c4", "arena-court": "#f7e6b0", "scenic": "#ddd"}
    for w in WALK:
        o.append(R(w[2], fill=kc[w[1]], stroke="none", opacity="0.95"))
    for b in BUILD:
        for r in b["interior"]:
            o.append(R(r, fill="#efe2c8", stroke="none"))
    for name, r in CLEAR:
        o.append(R(r, fill="none", stroke="#c0392b", stroke_width=1.2, stroke_dasharray="4 2"))
    fc = {"AR01": "#8d6e63", "AR02": "#795548", "AR03": "#a1665e", "AR04": "#6d4c41", "AR05": "#5d6d7e", "AR06": "#b9770e",
          "AR07": "#1e8449", "AR08": "#2471a3", "AR09": "#4a235a", "AR10": "#a6acaf", "SIL": "#bdb6a8"}
    for b in BUILD:
        hollow = bool(b["interior"])
        o.append(R(b["rect"], fill=fc[b["fam"]], fill_opacity="0.35" if hollow else ("0.55" if b["group"] == "SIL" else "0.9"),
                   stroke="#222", stroke_width=0.6))
        for r in b["interior"]:
            o.append(R(r, fill="#efe2c8", stroke="#7a5c2e", stroke_width=0.4))
    for wid, r in WALLS:
        o.append(R(r, fill="#333"))
    for g in GATES:
        o.append(R(g[1], fill="#e67e22", stroke="#a04000", stroke_width=0.6))
        x0, y0, x1, y1 = g[1]
        o.append(f'<text x="{X((x0+x1)/2)+3}" y="{Y((y0+y1)/2)-3}" font-size="7" fill="#a04000">{g[0]}</text>')
    for p in PROPS:
        o.append(R(p["rect"], fill="#2c3e50"))
    for zid, (name, r) in ZONES.items():
        o.append(R(r, fill="none", stroke="#7d3c98", stroke_width=0.8, stroke_dasharray="6 3", opacity="0.7"))
        o.append(f'<text x="{X(r[0])+2}" y="{Y(r[3])+9}" font-size="8" fill="#7d3c98">{zid}</text>')
    # rutas
    for rid, nodes, minw, phase, desc in ROUTES:
        col = {"R-MAIN": "#d4ac0d", "R-ALT-A": "#2e86c1", "R-ALT-B": "#28b463", "R-JACK": "none"}
        c = next((v for k, v in col.items() if rid.startswith(k)), "#d4ac0d")
        if c == "none":
            continue
        pts = " ".join(f"{X({**NODES, **TEST_POINTS}[n][0]):.1f},{Y({**NODES, **TEST_POINTS}[n][1]):.1f}" for n in nodes)
        o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="{"0" if rid.startswith("R-MAIN") else "5 3"}" opacity="0.85"/>')
    for n, (x, y) in NODES.items():
        o.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="3.2" fill="#c0392b" stroke="#fff" stroke-width="0.8"/>')
        o.append(f'<text x="{X(x)+4}" y="{Y(y)-4}" font-size="8" font-weight="bold" fill="#922b21">{n}</text>')
    # cotas de anchos libres medidos
    for wid, desc, need, got, at, ok in rep["widths"]:
        w = next(v for v in WALK if v[0] == wid)
        r = w[2]
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        o.append(f'<text x="{X(cx)}" y="{Y(cy)+3}" font-size="7.5" text-anchor="middle" fill="{"#1b4f72" if ok else "#c0392b"}">{wid[2:]} {got:.1f}m</text>')
    labels = [("INICIO", 104, 4), ("PLAZA", 70, 60), ("TALLER", 148, 49), ("CALLEJON", 171, 98), ("REFUGIO", 212, 167),
              ("ENFERMERIA", 215, 129), ("INFORME", 213, 81), ("SUPERVISOR", 94, 127), ("ARCHIVO", 72, 172), ("ACCESO", 121, 141),
              ("RUTA AZUL", 110, 94), ("RUTA VERDE", 200, 66)]
    for t, x, y in labels:
        o.append(f'<text x="{X(x)}" y="{Y(y)}" font-size="11" font-weight="bold" text-anchor="middle" fill="#111" opacity="0.8">{t}</text>')
    # escala y leyenda
    o.append(f'<line x1="{X(150)}" y1="{Y(-6)}" x2="{X(200)}" y2="{Y(-6)}" stroke="#000" stroke-width="2"/>')
    o.append(f'<text x="{X(175)}" y="{Y(-6)-4}" font-size="9" text-anchor="middle">50 m (cuadricula 10 m)</text>')
    lx = 240 * S + 2 * M - 10
    leg = [("#f2d98d", "Calle"), ("#a9d6e5", "Callejon / pasaje"), ("#f7e6b0", "Plaza / antepatio"), ("#cfe8c4", "Patio"),
           ("#efe2c8", "Interior accesible"), ("#8d6e63", "Vivienda AR01"), ("#795548", "Vivienda AR02"), ("#a1665e", "Comercio AR03"),
           ("#6d4c41", "Esquina AR04"), ("#5d6d7e", "Almacen AR05"), ("#b9770e", "Taller AR06"), ("#1e8449", "Refugio AR07"),
           ("#2471a3", "Enfermeria AR08"), ("#4a235a", "Archivo AR09"), ("#a6acaf", "Cobertizo AR10"), ("#bdb6a8", "Silueta lejana"),
           ("#333", "Muro"), ("#e67e22", "Porton / reja"), ("#2c3e50", "Prop / obstaculo")]
    o.append(f'<text x="{lx}" y="{M}" font-size="13" font-weight="bold">Whitechapel 240 x 180 m</text>')
    o.append(f'<text x="{lx}" y="{M+14}" font-size="9">Layout tecnico [PROPUESTA] - x este, y norte (m)</text>')
    for k, (c, t) in enumerate(leg):
        yy = M + 30 + k * 15
        o.append(f'<rect x="{lx}" y="{yy-9}" width="12" height="10" fill="{c}" stroke="#222" stroke-width="0.4"/>')
        o.append(f'<text x="{lx+18}" y="{yy}" font-size="9">{t}</text>')
    yy = M + 30 + len(leg) * 15 + 10
    for t in ["--- Envolvente Zxx (morado)", "- - Area que debe quedar libre (rojo)", "Linea amarilla: ruta principal",
              "Azul / verde discontinua: rutas A / B", "Cifras en calles: ancho libre", "medido tras colocar props"]:
        o.append(f'<text x="{lx}" y="{yy}" font-size="9">{t}</text>'); yy += 13
    o.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))

def main():
    os.makedirs(OUT, exist_ok=True)
    rep = validate()
    rows = building_rows()
    with open(os.path.join(OUT, "whitechapel_buildings.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "whitechapel_routes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Segment", "Kind", "xMin", "yMin", "xMax", "yMax", "SpecText", "MinFreeRequiredM", "MinFreeMeasuredM", "OK"])
        meas = {r[0]: r for r in rep["widths"]}
        for wk in WALK:
            m = meas.get(wk[0])
            w.writerow([wk[0], wk[1], *wk[2], wk[5], wk[4] or "", m[3] if m else "", ("si" if m[5] else "NO") if m else ""])
        w.writerow([])
        w.writerow(["Route", "Nodes", "MinWidthM", "Phase", "Connected", "Legs(m)", "Description"])
        for rid, desc, minw, phase, ok, legs in rep["routes"]:
            w.writerow([rid, "-".join([legs[0][0]] + [l[1] for l in legs]), minw, phase, "si" if ok else "NO",
                        "; ".join(f"{a}>{b}:{L}" for a, b, L in legs), desc])
        w.writerow([])
        w.writerow(["Gate", "xMin", "yMin", "xMax", "yMax", "UsefulWidthM", "Owner", "Behaviour"])
        for g in GATES:
            w.writerow([g[0], *g[1], g[2], g[3], g[4]])
    layout = {
        "meta": {"version": "masterplan240 v1 [PROPUESTA]", "date": "2026-11-15", "units": "m",
                 "axes": "x=este, y=norte, origen SO", "district": [0, 0, 240, 180],
                 "ue_transform": {"formula": "UE_X = OffX + 100*y ; UE_Y = OffY + 100*x ; yaw_UE = 90 - heading",
                                  "offsets_cm": OFF, "recommended": "recommended"}},
        "zones": {k: {"name": v[0], "rect": v[1]} for k, v in ZONES.items()},
        "nodes": {k: {"xy": v, "ue": ue(*v), "note": NODE_NOTES.get(k, "")} for k, v in NODES.items()},
        "walkable": [{"id": w[0], "kind": w[1], "rect": w[2], "axis": w[3], "minFree": w[4], "spec": w[5]} for w in WALK],
        "buildings": [{**{k: b[k] for k in ("id", "group", "fam", "rect", "front", "special", "interior", "doors", "note")}} for b in BUILD],
        "walls": [{"id": a, "rect": r} for a, r in WALLS],
        "gates": [{"id": g[0], "rect": g[1], "width": g[2], "owner": g[3], "behaviour": g[4]} for g in GATES],
        "phases": [{"name": n, "closed": sorted(c), "expectedReachable": sorted(e)} for n, c, e in PHASES],
        "props": PROPS, "mustStayClear": [{"name": n, "rect": r} for n, r in CLEAR],
        "routes": [{"id": r[0], "nodes": r[1], "minWidth": r[2], "phase": r[3], "desc": r[4]} for r in ROUTES],
        "families": {k: {"name": v[0], "hMin": v[1], "hMax": v[2], "candidate": v[3]} for k, v in FAM.items()},
    }
    with open(os.path.join(OUT, "whitechapel_layout.json"), "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False, indent=1)
    write_svg(os.path.join(OUT, "whitechapel_masterplan.svg"), rep)
    # informe de validacion
    L = ["# Validacion automatica del layout 240 x 180", "",
         f"Rejilla {RES} m. Holgura del jugador 0,45 m de radio. Generado por `Scripts/D/masterplan240_layout.py`.", ""]
    def sec(t, items, fmt):
        L.append(f"## {t} ({len(items)})"); L.append("")
        L.extend(fmt(i) for i in items) if items else L.append("- Ninguno.")
        L.append("")
    sec("Solapes edificio-edificio", rep["overlaps_bb"], lambda i: f"- {i[0]} x {i[1]}: {i[2]} m2")
    sec("Solapes solido-espacio transitable", rep["overlaps_bw"], lambda i: f"- {i[0]} x {i[1]}: {i[2]} m2")
    sec("Props en areas que deben quedar libres", rep["overlaps_clear"], lambda i: f"- {i[0]} en {i[1]}")
    sec("Props fuera de espacio transitable", rep["overlaps_pw"], lambda i: f"- {i[0]}: {i[1]}")
    sec("Envolventes", rep["envelopes"], lambda i: f"- {i[0]} en {i[1]}: {'OK' if i[2] else 'FUERA'}")
    L.append(f"## Huecos de 0-3 m entre volumenes independientes ({len(rep['small_gaps'])})"); L.append("")
    L.append("No son transitables: se cierran con medianera, muro o verja (no dejar grietas)."); L.append("")
    L.append(", ".join(f"{a}/{b} {g}" for a, b, g in rep["small_gaps"][:80]) + (" ..." if len(rep["small_gaps"]) > 80 else "")); L.append("")
    L.append("## Anchos libres tras colocar props"); L.append("")
    L.append("| Tramo | Exigido (m) | Medido (m) | Seccion mas estrecha | OK |"); L.append("|---|---:|---:|---:|---|")
    for wid, desc, need, got, at, ok in rep["widths"]:
        L.append(f"| {wid} {desc} | {need} | {got} | {at} | {'si' if ok else '**NO**'} |")
    L.append(""); L.append("## Alcance por fase (portones cerrados segun fase)"); L.append("")
    for name, got, missing, extra in rep["phases"]:
        L.append(f"- **{name}**: alcanzables {', '.join(got)}. Faltan: {', '.join(missing) or 'ninguno'}. Fugas: {', '.join(extra) or 'ninguna'}.")
    L.append(""); L.append("## Rutas (todos los portones abiertos)"); L.append("")
    for rid, desc, minw, phase, ok, legs in rep["routes"]:
        L.append(f"- **{rid}** ({desc}, holgura {minw} m): {'CONECTADA' if ok else '**CORTADA**'} - " +
                 "; ".join(f"{a}>{b} {L_} m" for a, b, L_ in legs))
    L.append(""); L.append("## Nodos (ajuste al punto libre mas cercano)"); L.append("")
    for n, p, d, cl in rep["nodes"]:
        L.append(f"- {n} {p}: desplazado {d} m, holgura {cl} m")
    # recuentos
    from collections import Counter
    cnt = Counter(b["group"] for b in BUILD)
    fam = Counter(b["fam"] for b in BUILD if b["group"] not in ("SIL", "CONECTOR"))
    tgt = {"M-A": 6, "M-B": 4, "M-C": 5, "M-D": 5, "M-E": 8, "M-F": 8, "M-G": 5, "M-H": 3, "M-I": 5, "M-J": 12, "HITO": 10}
    L.append(""); L.append("## Recuento de colocaciones"); L.append("")
    L.append("| Grupo | Objetivo masterplan | Colocadas |"); L.append("|---|---:|---:|")
    for g in tgt:
        L.append(f"| {g} | {tgt[g]} | {cnt.get(g, 0)} |")
    L.append(f"| Siluetas (no cuentan) | - | {cnt.get('SIL', 0)} |")
    L.append(""); L.append("Por familia: " + ", ".join(f"{k} {v}" for k, v in sorted(fam.items())))
    occ = sum(area(b["rect"]) for b in BUILD if b["group"] not in ("SIL",))
    L.append(""); L.append(f"Huella construida (sin siluetas): {occ:.0f} m2 de 43 200 m2 ({100*occ/43200:.1f} %).")
    with open(os.path.join(OUT, "validation_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    bad = len(rep["overlaps_bb"]) + len(rep["overlaps_bw"]) + len(rep["overlaps_clear"]) + len(rep["overlaps_pw"])
    bad += sum(1 for w in rep["widths"] if not w[5]) + sum(1 for r in rep["routes"] if not r[4])
    bad += sum(1 for p in rep["phases"] if p[2] or p[3]) + sum(1 for e in rep["envelopes"] if not e[2])
    print("\n".join(L[:8]))
    print(f"PROBLEMAS: {bad}")
    print(open(os.path.join(OUT, "validation_report.md"), encoding="utf-8").read())

if __name__ == "__main__":
    main()
