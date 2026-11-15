# -*- coding: utf-8 -*-
"""
Arte final del distrito 240 x 180 (masterplan aprobado) para L_Test_D. Division D.

Misma fuente que el plano y el blockout aprobados (masterplan240_layout.py). Sustituye el blockout
(etiquetas MP240 / MP240_PILOT / MP240_ART) por arte con volumen; etiqueta todo con MP240_FINAL.
No mueve el NavMeshBoundsVolume ni las luces interiores MP_Light_*.

Familias (ver SourceData/D/masterplan_240/PASO5_ASSETS.md):
  AR01/AR02/AR04 -> fachada Meshy SM_HouseFront_AR01 (6 x 2,81 m, alero 7,2) + cuerpo de kit hasta el fondo
                    de la parcela + cubierta a dos aguas de kit (pizarra) + canalon y bajante
  AR03           -> fachada Meshy SM_ShopFront_AR03 (8 x 5,1 m, alero 9,5) + cuerpo + cubierta
  AR05           -> fachada Meshy SM_WarehouseFront_AR05 (12 x 8,56 m, alero 8,5) + cuerpo + cubierta
  AR10           -> cobertizo de kit (madera + cubierta a un agua)
  especiales     -> cascaron de muros de kit (huecos de puerta del layout, dinteles) + cubierta + ventanas + cornisa
  SIL            -> franjas de 6 m de casas simplificadas (cuerpo + cubierta), alturas variadas
Escala por instancia: el ancho de la fachada se ajusta como maximo +-10 %; el resto lo cubren pilastras de ladrillo.
Uso: python -I Scripts/D/district_art_build.py <dir_salida_script>
"""
import importlib.util, json, math, os, sys, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "masterplan240_layout.py"))
mp = importlib.util.module_from_spec(spec); spec.loader.exec_module(mp)
dspec = importlib.util.spec_from_file_location("db", os.path.join(HERE, "district240_build.py"))
db = importlib.util.module_from_spec(dspec); dspec.loader.exec_module(db)

OFFX, OFFY, _ = mp.OFF["recommended"]
TAG = "MP240_FINAL"
KIT = "/Game/Unscripted/Art/Kit/"
MAT = "/Game/Unscripted/Art/Materials/"
BLD = "/Game/Unscripted/Art/Buildings/"
PR = "/Game/Unscripted/Art/Props/"
BOX, GABLE, MONO, CORN, WIN = (KIT + n for n in ("SM_KIT4_Box", "SM_KIT4_Gable", "SM_KIT4_Mono", "SM_KIT4_Cornice", "SM_KIT4_Window"))
CYL = "/Engine/BasicShapes/Cylinder"

def M(n):
    return MAT + n + "." + n
BRICK = [M("MI_ART_BrickA"), M("MI_ART_BrickB"), M("MI_ART_BrickC")]
SLATE, STONE, WOOD, IRON, GLASS, GLASSLIT, PLASTER = (M(n) for n in ("MI_ART_Slate", "MI_ART_Stone", "MI_ART_Wood", "MI_ART_Iron", "MI_ART_Glass", "MI_ART_GlassLit", "MI_ART_Plaster"))
FLOOR = {"cobble": "/Game/Unscripted/Materials/Blockout/MI_Cobble_Wet.MI_Cobble_Wet",
         "flag": "/Game/Unscripted/Materials/Blockout/MI_Flagstone_York.MI_Flagstone_York",
         "kerb": "/Game/Unscripted/Materials/Blockout/MI_Kerb_Granite.MI_Kerb_Granite",
         "ground": "/Game/Unscripted/Art/Materials/MI_ART_YardGround.MI_ART_YardGround",
         "puddle": "/Game/Unscripted/Art/Materials/MI_ART_WetPatch.MI_ART_WetPatch",
         "wood": WOOD}

FRONTS = {  # malla, ancho nativo, fondo nativo, alero, cubierta, variantes de material
    "house": (BLD + "SM_HouseFront_AR01/SM_HouseFront_AR01", 6.0, 2.81, 7.2, 2.6),
    "shop": (BLD + "SM_ShopFront_AR03/SM_ShopFront_AR03", 8.0, 5.1, 9.5, 3.0),
    "ware": (BLD + "SM_WarehouseFront_AR05/SM_WarehouseFront_AR05", 12.0, 8.56, 8.5, 3.4),
}
FRONT_MI = {"house": [BLD + "SM_HouseFront_AR01/MI_HouseFront_AR01%s.MI_HouseFront_AR01%s" % (s, s) for s in ("", "_B", "_C")],
            "shop": [BLD + "SM_ShopFront_AR03/MI_ShopFront_AR03%s.MI_ShopFront_AR03%s" % (s, s) for s in ("", "_B")],
            "ware": [BLD + "SM_WarehouseFront_AR05/MI_WarehouseFront_AR05.MI_WarehouseFront_AR05"]}

def yaw_of(front):
    return {"N": 0, "E": 90, "S": 180, "W": -90}[front]

def frame(rect, front):
    """origen en el centro del frente, f = normal hacia la calle, r = eje +Y local en el plano"""
    x0, y0, x1, y1 = rect
    if front == "N": o, f, W, D = ((x0 + x1) / 2, y1), (0, 1), x1 - x0, y1 - y0
    elif front == "S": o, f, W, D = ((x0 + x1) / 2, y0), (0, -1), x1 - x0, y1 - y0
    elif front == "E": o, f, W, D = (x1, (y0 + y1) / 2), (1, 0), y1 - y0, x1 - x0
    else: o, f, W, D = (x0, (y0 + y1) / 2), (-1, 0), y1 - y0, x1 - x0
    r = (f[1], -f[0])
    return o, f, r, W, D

def P(o, f, r, lx, ly):
    return (o[0] + f[0] * lx + r[0] * ly, o[1] + f[1] * lx + r[1] * ly)

def xf(px, py, z, yaw, sx=1.0, sy=1.0, sz=1.0):
    return {"location": {"x": round(OFFX + 100 * py, 2), "y": round(OFFY + 100 * px, 2), "z": round(100 * z, 2)},
            "rotation": {"pitch": 0, "yaw": yaw, "roll": 0}, "scale": {"x": round(sx, 4), "y": round(sy, 4), "z": round(sz, 4)}}

ITEMS = []
def add(label, folder, asset, xform, mats=None, kind="art", noncol=False):
    if asset == CYL:   # el cilindro del motor tiene el pivote en el centro
        xform["location"]["z"] = round(xform["location"]["z"] + 50 * xform["scale"]["z"], 2)
    if noncol:   # decorativo: malla sin colision (la colision por instancia no se puede cambiar via MCP)
        asset = KIT + ("SM_KIT4_DecoCyl" if asset == CYL else "SM_KIT4_DecoBox")
    ITEMS.append(dict(label=label, folder="MP240_FINAL/" + folder, asset=asset, xform=xform, mats=mats or [], kind=kind, noncol=noncol))

def kbox(label, folder, cx, cy, z0, sx_plan, sy_plan, h, mat, yaw=0):
    """caja de kit alineada a ejes del plano: sx_plan en x (este) y sy_plan en y (norte)"""
    add(label, folder, BOX, xf(cx, cy, z0, 0, sy_plan, sx_plan, h), [mat])

def lbox(label, folder, o, f, r, yaw, lx0, lx1, ly0, ly1, z0, h, mats, asset=BOX):
    """caja en coordenadas locales del edificio (lx hacia la calle, ly a lo ancho)"""
    cx, cy = P(o, f, r, (lx0 + lx1) / 2, (ly0 + ly1) / 2)
    add(label, folder, asset, xf(cx, cy, z0, yaw, abs(lx1 - lx0) / 1.0, abs(ly1 - ly0) / 1.0, h), mats)

def house_assembly(b, kind, rnd):
    mesh, w0, d0, eave0, roof0 = FRONTS[kind]
    o, f, r, W, D = frame(b["rect"], b["front"])
    yaw = yaw_of(b["front"])
    sy = min(1.1, max(0.9, W / w0))
    sz = 1.1 if (b["fam"] == "AR02" and kind == "house") else 1.0
    eave = eave0 * sz
    depth_mod = min(d0, D - 0.3) if D - 0.3 < d0 else d0
    sx = depth_mod / d0
    folder = "Edificios/" + b["group"]
    mi = FRONT_MI[kind][rnd.randrange(len(FRONT_MI[kind]))]
    brick = BRICK[rnd.randrange(3)]
    add("F_%s_Fachada" % b["id"], folder, mesh, xf(*o, 0, yaw, sx, sy, sz), [mi])
    used = w0 * sy
    if W - used > 0.05:   # pilastras laterales hasta el ancho de la parcela
        g = (W - used) / 2
        for side, (a0, a1) in (("L", (-W / 2, -W / 2 + g)), ("R", (W / 2 - g, W / 2))):
            lbox("F_%s_Pilastra%s" % (b["id"], side), folder, o, f, r, yaw, -depth_mod, 0, a0, a1, 0, eave, [brick])
    if D - depth_mod > 0.3:   # cuerpo hasta el fondo
        lbox("F_%s_Cuerpo" % b["id"], folder, o, f, r, yaw, -D, -depth_mod, -W / 2, W / 2, 0, eave, [brick])
    rh = roof0 if D >= 9 else max(1.6, 0.28 * D)
    cx, cy = P(o, f, r, -D / 2, 0)
    add("F_%s_Cubierta" % b["id"], folder, GABLE, xf(cx, cy, eave, yaw, D + 0.5, W, rh), [SLATE, brick])
    # canalon y bajante (hierro), en la fachada
    lbox("F_%s_Canalon" % b["id"], folder, o, f, r, yaw, 0.0, 0.18, -W / 2, W / 2, eave - 0.18, 0.16, [IRON])
    px, py = P(o, f, r, 0.09, W / 2 - 0.14)
    add("F_%s_Bajante" % b["id"], folder, CYL, xf(px, py, 0, yaw, 0.09, 0.09, eave), [IRON], noncol=True)  # decorativa: sin colision
    return eave + rh

def shed(b, rnd):
    o, f, r, W, D = frame(b["rect"], b["front"]); yaw = yaw_of(b["front"])
    folder = "Edificios/" + b["group"]
    h = 3.2
    lbox("F_%s_Cuerpo" % b["id"], folder, o, f, r, yaw, -D, 0, -W / 2, W / 2, 0, h, [WOOD])
    cx, cy = P(o, f, r, -D / 2, 0)
    add("F_%s_Cubierta" % b["id"], folder, MONO, xf(cx, cy, h, yaw + 180, D + 0.4, W + 0.2, 1.1), [SLATE, WOOD])

SPECIAL = {  # alero, cubierta, material de muro, ventanas en el frente
    "SP-TALLER": (6.5, 3.0, BRICK[1], True), "SP-REFUGIO": (7.5, 2.6, BRICK[2], True),
    "SP-ENFERMERIA": (10.0, 3.0, STONE, True), "SP-INFORME": (8.5, 3.0, BRICK[1], True),
    "SP-ARCH-CENTRAL": (14.0, 4.0, STONE, True), "SP-ARCH-ALA-O": (11.0, 3.5, STONE, True),
    "SP-ARCH-ALA-E": (11.0, 3.5, STONE, True), "SP-ARCH-PORTICO": (10.0, 2.0, STONE, False),
    "CX-ARCH-GALERIA": (6.0, 1.2, STONE, False), "SP-ANEXO": (4.0, 1.4, WOOD, False), "SP-COBERTIZO": (3.2, 1.2, WOOD, False),
}

def special(b, rnd):
    eave, rh, wall, wins = SPECIAL[b["id"]]
    folder = "Especiales/" + b["id"]
    x0, y0, x1, y1 = b["rect"]
    holes = b["interior"] + b["doors"]
    pieces = db.subtract(b["rect"], holes) if holes else [b["rect"]]
    for k, rr in enumerate(pieces):
        kbox("F_%s_Muro%02d" % (b["id"], k), folder, (rr[0] + rr[2]) / 2, (rr[1] + rr[3]) / 2, 0, rr[2] - rr[0], rr[3] - rr[1], eave, wall)
    # dinteles sobre los huecos de puerta (recortados al edificio)
    for k, d in enumerate(b["doors"]):
        dr = (max(d[0], x0), max(d[1], y0), min(d[2], x1), min(d[3], y1))
        if dr[2] - dr[0] > 0.01 and dr[3] - dr[1] > 0.01:
            span = max(dr[2] - dr[0], dr[3] - dr[1])
            zl = 3.0 if span >= 2.8 else 2.6
            if b["id"] == "SP-ARCH-PORTICO" and span > 6: zl = 5.0
            kbox("F_%s_Dintel%d" % (b["id"], k), folder, (dr[0] + dr[2]) / 2, (dr[1] + dr[3]) / 2, zl, dr[2] - dr[0], dr[3] - dr[1], eave - zl, wall)
    # suelo interior (madera en taller, refugio e informe; losa en enfermeria y archivo)
    fmat = FLOOR["flag"] if (wall == STONE) else WOOD
    for k, ir in enumerate(b["interior"]):
        add("F_%s_Suelo%d" % (b["id"], k), folder, BOX, xf((ir[0] + ir[2]) / 2, (ir[1] + ir[3]) / 2, 0.0, 0, ir[3] - ir[1], ir[2] - ir[0], 0.025), [fmat], kind="floor")
    o, f, r, W, D = frame(b["rect"], b["front"]); yaw = yaw_of(b["front"])
    cx, cy = P(o, f, r, -D / 2, 0)
    roofmat = SLATE
    if b["id"] in ("SP-ANEXO", "SP-COBERTIZO"):
        add("F_%s_Cubierta" % b["id"], folder, MONO, xf(cx, cy, eave, yaw + 180, D + 0.4, W + 0.2, rh), [roofmat, wall])
    else:
        add("F_%s_Cubierta" % b["id"], folder, GABLE, xf(cx, cy, eave, yaw, D + 0.6, W + 0.4, rh), [roofmat, wall])
        # cornisa del alero en el frente
        lbox("F_%s_Cornisa" % b["id"], folder, o, f, r, yaw, -0.1, 0.35, -W / 2, W / 2, eave - 0.45, 0.45, [STONE if wall == STONE else BRICK[0]], asset=CORN)
    if wins:   # ventanas en el frente, evitando huecos de puerta
        rows = [1.1, 4.4] + ([7.7] if eave >= 10 else []) + ([10.9] if eave >= 13.5 else [])
        n = max(1, int((W - 2) // 3.2))
        for i in range(n):
            ly = -W / 2 + 1 + (i + 0.5) * (W - 2) / n
            wx, wy = P(o, f, r, 0, ly)
            if any(d[0] - 0.8 <= wx <= d[2] + 0.8 and d[1] - 0.8 <= wy <= d[3] + 0.8 for d in b["doors"]):
                continue
            for zr in rows:
                if zr + 1.7 > eave - 0.5: continue
                px, py = P(o, f, r, 0.04, ly)
                lit = GLASSLIT if rnd.random() < 0.3 else GLASS
                add("F_%s_Ventana_%d_%d" % (b["id"], i, int(zr * 10)), folder, WIN, xf(px, py, zr, yaw, 0.2, 1.1, 1.7), [IRON, lit])
        # puerta de madera en el primer hueco que da a la calle (hoja abierta = no se coloca; solo marco oscuro)

def silhouettes(b, rnd):
    x0, y0, x1, y1 = b["rect"]
    folder = "Fondo/" + b["id"]
    long_x = (x1 - x0) >= (y1 - y0)
    L = (x1 - x0) if long_x else (y1 - y0)
    Dd = (y1 - y0) if long_x else (x1 - x0)
    n = max(1, int(L // 6))
    for i in range(n):
        a0 = (x0 if long_x else y0) + i * L / n; a1 = a0 + L / n
        h = rnd.choice([7.0, 8.0, 9.5, 11.0])
        mat = BRICK[rnd.randrange(3)]
        if long_x:
            rect = (a0, y0, a1, y1); cx, cy = (a0 + a1) / 2, (y0 + y1) / 2; yaw = 0; sx, sy = Dd, a1 - a0
        else:
            rect = (x0, a0, x1, a1); cx, cy = (x0 + x1) / 2, (a0 + a1) / 2; yaw = 90; sx, sy = Dd, a1 - a0
        add("F_%s_%02d_Cuerpo" % (b["id"], i), folder, BOX, xf(cx, cy, 0, yaw, sx, sy, h), [mat])
        if Dd > 4:
            add("F_%s_%02d_Cubierta" % (b["id"], i), folder, GABLE, xf(cx, cy, h, yaw, sx + 0.4, sy, min(3.0, 0.3 * Dd)), [SLATE, mat])
        if rnd.random() < 0.5:
            add("F_%s_%02d_Chimenea" % (b["id"], i), folder, BOX, xf(cx, cy, h, yaw, 0.7, 1.4, min(3.0, 0.3 * Dd) + 1.2), [mat])

def main(outdir):
    rnd = random.Random(1888)
    counts = Counter()
    # 1. suelo base y pavimentos (cajas de kit con material de suelo)
    add("F_Suelo", "Suelo", BOX, xf(120, 90, -0.2, 0, 180, 240, 0.2), [FLOOR["ground"]], kind="floor")
    mat = {"street": "cobble", "plaza": "cobble", "arena-court": "flag", "alley": "cobble", "patio": "flag", "scenic": "cobble"}
    for w in mp.WALK:
        r = w[2]
        add("F_Pav_" + w[0][2:], "Suelo/Pavimentos", BOX, xf((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 0, 0, r[3] - r[1], r[2] - r[0], 0.02), [FLOOR[mat[w[1]]]], kind="floor")
    # aceras con bordillo (dentro del ancho de la calle; escalon de 12 cm)
    for name, rect, side in [("Z01_O", (99, 0, 100.6, 24), "x"), ("Z01_E", (107.4, 0, 109, 14), "x"), ("STE_S", (119, 44, 140, 45.4), "y"),
                             ("STE_N", (109, 50.6, 140, 52), "y"), ("SAV_N", (84, 12.6, 95, 14), "y"), ("SAV_N2", (109, 12.6, 124, 14), "y")]:
        x0, y0, x1, y1 = rect
        add("F_Acera_" + name, "Suelo/Aceras", BOX, xf((x0 + x1) / 2, (y0 + y1) / 2, 0.02, 0, y1 - y0, x1 - x0, 0.10), [FLOOR["flag"]], kind="floor")
    # charcos localizados (planos de 1 cm)
    for i, (x, y, s) in enumerate([(103, 6, 1.6), (106.5, 19, 1.0), (52, 33, 2.2), (93, 62, 1.4), (60, 66, 1.0), (125, 47, 1.8), (175, 63.5, 1.2),
                                   (177, 78, 1.0), (170, 99, 2.0), (180, 120, 1.4), (190, 142, 1.2), (226, 90, 1.0), (88, 90, 1.6), (150, 115, 1.4),
                                   (100, 112, 1.8), (120, 135, 1.2), (210, 152, 1.0), (140, 94, 1.2)]):
        add("F_Charco_%02d" % i, "Suelo/Charcos", BOX, xf(x, y, 0.02, rnd.randrange(0, 90), s * 0.8, s, 0.01), [FLOOR["puddle"]], kind="floor", noncol=True)
    # sumideros (rejilla de hierro enrasada)
    for i, (x, y) in enumerate([(99.4, 8), (99.4, 20), (108.6, 4), (112, 44.3), (130, 44.3), (84.3, 80), (91.7, 98), (172.3, 70), (178.7, 100),
                                (176.3, 130), (190, 139.3), (224.3, 110), (113, 112.3), (150, 117.7), (60, 24.3)]):
        add("F_Sumidero_%02d" % i, "Suelo/Sumideros", BOX, xf(x, y, 0.02, 0, 0.45, 0.8, 0.015), [IRON], kind="floor", noncol=True)
    # 2. edificios
    for b in mp.BUILD:
        if b["group"] == "SIL":
            silhouettes(b, rnd); counts["SIL"] += 1; continue
        if b["interior"] or b["id"] in SPECIAL:
            special(b, rnd); counts["especial"] += 1; continue
        fam = b["fam"]
        if fam == "AR10":
            shed(b, rnd); counts["AR10"] += 1; continue
        o, f, r, W, D = frame(b["rect"], b["front"])
        if fam == "AR05":
            kind = "ware" if W >= 10.8 else "shop"
        elif fam in ("AR03",) or (fam == "AR04" and W >= 7.5):
            kind = "shop"
        else:
            kind = "house"
        house_assembly(b, kind, rnd); counts[kind] += 1
    # 3. muros del layout y cierres automaticos (ladrillo con albardilla de piedra)
    walls = list(mp.WALLS)
    # cierres: reutiliza el calculo del blockout aprobado
    tmp = []
    _items = db.__dict__  # noqa
    for wid, r in walls:
        h = db.wall_h(wid)
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        mat_w = STONE if h < 1.5 else BRICK[1]
        kbox("F_" + wid, "Muros", cx, cy, 0, r[2] - r[0], r[3] - r[1], h, mat_w)
        kbox("F_" + wid + "_Alb", "Muros", cx, cy, h, r[2] - r[0] + 0.08, r[3] - r[1] + 0.08, 0.12, STONE)
    # cierres automaticos: mismos que el blockout (district_placements.json)
    dp = json.load(open(os.path.join(mp.OUT, "district_placements.json"), encoding="utf-8"))
    for it in dp["items"]:
        if it["label"].startswith("MP_Cierre_"):
            r = it["rect"]; cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
            kbox("F_" + it["label"][3:], "Muros/Cierres", cx, cy, 0, r[2] - r[0], r[3] - r[1], 3.0, BRICK[1])
            kbox("F_" + it["label"][3:] + "_Alb", "Muros/Cierres", cx, cy, 3.0, r[2] - r[0] + 0.08, r[3] - r[1] + 0.08, 0.12, STONE)
    # pilares de porton (la hoja y su logica son de C)
    for g in mp.GATES:
        r = g[1]; horiz = (r[2] - r[0]) > (r[3] - r[1])
        ends = [(r[0], (r[1] + r[3]) / 2), (r[2], (r[1] + r[3]) / 2)] if horiz else [((r[0] + r[2]) / 2, r[1]), ((r[0] + r[2]) / 2, r[3])]
        for k, (px, py) in enumerate(ends):
            ox = (-0.3 if k == 0 else 0.3) if horiz else 0
            oy = 0 if horiz else (-0.3 if k == 0 else 0.3)
            kbox("F_Porton_%s_Pilar%d" % (g[0], k), "Portones", px + ox, py + oy, 0, 0.5, 0.5, 2.9, STONE)
        add("F_Porton_%s_Marca" % g[0], "Portones", BOX, xf((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 0.02, 0, r[3] - r[1], r[2] - r[0], 0.02), [FLOOR["kerb"]], kind="floor", noncol=True)
    # 4. props del layout
    for p in mp.PROPS:
        r = p["rect"]; cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2; k = p["kind"]
        if k == "fuente":
            add("F_Fuente_Base", "Props", CYL, xf(cx, cy, 0, 0, 5.0, 5.0, 0.6), [STONE])
            add("F_Fuente_Vaso", "Props", CYL, xf(cx, cy, 0.6, 0, 3.6, 3.6, 0.35), [STONE])
            add("F_Fuente_Pila", "Props", PR + "SM_Fountain_Square/SM_Fountain_Square", xf(cx, cy, 0.95, 0, 1.4, 1.4, 1.4))
        elif k == "puesto":
            yaw = 180 if cy > 48 else 0   # el mostrador mira a la plaza
            add("F_" + p["id"], "Props/Puestos", PR + "SM_MarketStall_01/SM_MarketStall_01", xf(cx, cy, 0, yaw))
        elif k == "carro":
            add("F_" + p["id"], "Props", PR + "SM_Cart_Victorian/SM_Cart_Victorian", xf(cx, cy, 0, 0))
        elif k == "farola":
            add("F_" + p["id"], "Props/Farolas", "/Game/Unscripted/World/BP_GasLamp", xf(cx, cy, 0, 0))
        elif k == "caja":
            add("F_" + p["id"], "Props/Cobertura", PR + "SM_CrateStack_A/SM_CrateStack_A", xf(cx, cy, 0, rnd.choice([0, 15, 90])))
        elif k == "barril":
            add("F_" + p["id"], "Props/Cobertura", PR + "SM_Barrel_A/SM_Barrel_A", xf(cx, cy, 0, rnd.randrange(360)))
        elif k == "carretilla":
            add("F_" + p["id"], "Props/Cobertura", PR + "SM_Handcart_A/SM_Handcart_A", xf(cx, cy, 0, 90, 0.65, 0.65, 0.65))
        elif k == "pilar":
            add("F_" + p["id"], "Props/Pilares", PR + "SM_ArchivePillar_A/SM_ArchivePillar_A", xf(cx, cy, 0, 0))
        elif k == "mesa":
            add("F_" + p["id"], "Interiores", PR + "SM_WorkshopTable_A/SM_WorkshopTable_A", xf(cx, cy, 0.02, 90))
        elif k == "estante":
            add("F_" + p["id"], "Interiores", PR + "SM_Shelf_A/SM_Shelf_A", xf(cx, cy, 0.02, 0))
        elif k == "escritorio":   # escritorio de kit: tablero + 2 costados
            w, d = r[2] - r[0], r[3] - r[1]
            kbox("F_" + p["id"] + "_Tablero", "Interiores", cx, cy, 0.74, w, d, 0.05, WOOD)
            kbox("F_" + p["id"] + "_PataL", "Interiores", r[0] + 0.05, cy, 0.0, 0.06, d, 0.74, WOOD)
            kbox("F_" + p["id"] + "_PataR", "Interiores", r[2] - 0.05, cy, 0.0, 0.06, d, 0.74, WOOD)
            ev = "SM_Ledger_Nursing" if "INF" in p["id"] else "SM_Folder_Report"
            add("F_" + p["id"] + "_Evidencia", "Interiores", PR + ev + "/" + ev, xf(cx, cy, 0.79, 30))
        elif k == "estacion":
            add("F_" + p["id"] + "_Base", "Interiores/Estaciones", BOX, xf(cx, cy, 0.02, 0, d := (r[3] - r[1]), r[2] - r[0], 0.15), [STONE])
            m_ = "SM_RecordStation_Official" if "OFF" in p["id"] else "SM_RecordStation_Authentic"
            add("F_" + p["id"], "Interiores/Estaciones", PR + m_ + "/" + m_, xf(cx, cy, 0.17, 90))
        elif k == "catre":
            add("F_" + p["id"], "Interiores", PR + "SM_Cot_A/SM_Cot_A", xf(cx, cy, 0.02, 0))
    # mobiliario adicional de interiores (fuera de las areas libres del layout)
    extra = [("Refugio_Armario", "SM_Wardrobe_A", 233.9, 152.0, 90), ("Refugio_Silla", "SM_Chair_A", 230.5, 156.0, 200),
             ("Enf_Estante1", "SM_Shelf_A", 207.4, 120.5, 90), ("Enf_Estante2", "SM_Shelf_A", 207.4, 123.0, 90),
             ("Inf_Archivador1", "SM_ArchiveCabinet_A", 208.4, 85.0, 90), ("Inf_Archivador2", "SM_ArchiveCabinet_A", 208.4, 86.0, 90),
             ("Inf_Archivador3", "SM_ArchiveCabinet_A", 216.6, 85.0, -90), ("Taller_Cajas", "SM_CrateStack_A", 141.2, 41.4, 0)]
    for i, y in enumerate([153, 155, 157, 166, 167]):
        extra.append(("Arch_ArchO_%d" % i, "SM_ArchiveCabinet_A", 65.6, y, 90))
        extra.append(("Arch_ArchE_%d" % i, "SM_ArchiveCabinet_A", 88.4, y, -90))
    for n, m_, x, y, yaw in extra:
        add("F_" + n, "Interiores", PR + m_ + "/" + m_, xf(x, y, 0.02, yaw))
    os.makedirs(mp.OUT, exist_ok=True)
    with open(os.path.join(mp.OUT, "district_art_placements.json"), "w", encoding="utf-8") as fh:
        json.dump({"tag": TAG, "count": len(ITEMS), "families": counts, "items": ITEMS}, fh, ensure_ascii=False, indent=1)
    data = json.dumps(ITEMS, ensure_ascii=False)
    with open(os.path.join(outdir, "district_art_mcp_script.py"), "w", encoding="utf-8") as fh:
        fh.write(MCP_TEMPLATE.replace("__DATA__", data))
    print(len(ITEMS), dict(counts), Counter(i["asset"].split("/")[-1] for i in ITEMS).most_common(12))

MCP_TEMPLATE = r'''import json
A='editor_toolset.toolsets.actor.ActorTools.'
S='editor_toolset.toolsets.scene.SceneTools.'
O='editor_toolset.toolsets.object.ObjectTools.'
DATA=json.loads(r"""__DATA__""")
def t(n,a): return execute_tool(n, json.dumps(a))['returnValue']
def run(start=0, count=100000, wipe=True):
    removed=0
    if wipe:
        for tag in ('MP240_PILOT','MP240','MP240_ART','MP240_FINAL'):
            for a in t(S+'find_actors',{'name':'','tag':tag,'collision_channels':[]}):
                rp=a['refPath']
                if 'NavMeshBoundsVolume' in rp: continue
                if t(A+'get_label',{'actor':a}).startswith('MP_Light_'): continue
                t(S+'remove_from_scene',{'actor':a}); removed+=1
    made=0; errs=[]
    for it in DATA[start:start+count]:
        try:
            a=t(S+'add_to_scene_from_asset',{'asset_path':it['asset'],'name':it['label'],'xform':it['xform']})
            t(A+'set_label',{'actor':a,'label':it['label']})
            t(A+'add_tag',{'actor':a,'tag':'MP240_FINAL'})
            t(S+'set_actor_folder',{'actor':a,'folder_path':it['folder']})
            if it['mats'] or it['noncol']:
                c=[q for q in t(A+'get_components',{'actor':a}) if 'StaticMeshComponent' in q['refPath']]
                if c:
                    v={}
                    if it['mats']: v['OverrideMaterials']=it['mats']
                    if it['noncol']: v['BodyInstance']={'collisionEnabled':'NoCollision'}
                    t(O+'set_properties',{'instance':c[0],'values':json.dumps(v)})
            made+=1
        except Exception as e:
            errs.append([it['label'],str(e)[-160:]])
    return {'removed':removed,'made':made,'errors':errs[:20]}
'''

if __name__ == "__main__":
    main(sys.argv[1])
