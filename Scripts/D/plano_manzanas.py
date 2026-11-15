"""Plano de manzanas v3 de Whitechapel (División D).

Lee las zonas, conexiones, coberturas y puntos de SourceData/D/blockout_layout.json
(sin modificarlo) y las casas/luces de SourceData/D/plano_v3/*.csv.
Valida solapes y la regla de altura del lado de cámara, y dibuja
SourceData/D/plano_v3/plano_manzanas_v3.png.

Uso: python -I Scripts/D/plano_manzanas.py
Unidades en metros: u = este (Y de Unreal), v = norte (X de Unreal).
"""
import csv
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "SourceData" / "D"
OUT = SRC / "plano_v3"

UMIN, UMAX, VMIN, VMAX = -6, 66, -6, 60
S = 14          # píxeles por metro
M = 50          # margen
LEG = 420      # ancho de la leyenda
FLOOR_H = {1: 3.5, 2: 6.5, 3: 9.5}  # altura de alero aproximada (m)

# Elementos del plano que no son casas ni zonas.
EXTRA = [
    {"id": "W01", "kind": "fence", "u": [14, 26], "v": [22, 24],
     "note": "Muro bajo con verja Plaza/Tramo (visual, no transitable)"},
    {"id": "P01", "kind": "closed_pass", "u": [38, 40], "v": [18, 22],
     "note": "[PROPUESTA] Paso Callejón/Paso central cerrado (ambiente)"},
]

ARQ = {  # relleno, borde
    "BRICK":    ((122, 62, 48), (60, 28, 20)),
    "SHOP":     ((176, 112, 52), (90, 52, 20)),
    "CORNER":   ((140, 96, 80), (70, 44, 36)),
    "WORKSHOP": ((110, 86, 64), (54, 40, 28)),
    "AGENCY":   ((40, 96, 104), (12, 54, 60)),
    "FILLER":   ((78, 74, 74), (40, 38, 38)),
}
ZONE_FILL = (196, 190, 176)
ZONE_INT = (214, 176, 128)
ZONE_AGENCY = (150, 206, 204)
CONN = {"open": (99, 153, 34), "door": (55, 138, 221),
        "gate_closed": (226, 75, 74), "decor": (239, 159, 39)}
LIGHT = {"ambar": (255, 176, 40), "ambar_tenue": (200, 140, 60),
         "naranja": (255, 110, 30), "cian": (0, 220, 230)}


def px(u, v):
    return (M + (u - UMIN) * S, M + (VMAX - v) * S)


def rect_px(u0, u1, v0, v1):
    x0, y1 = px(u0, v0)
    x1, y0 = px(u1, v1)
    return [x0, y0, x1, y1]


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def font(size, bold=False):
    for name in (("arialbd.ttf" if bold else "arial.ttf"), "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def load():
    layout = json.loads((SRC / "blockout_layout.json").read_text(encoding="utf-8"))
    with open(OUT / "manzanas.csv", encoding="utf-8") as f:
        houses = list(csv.DictReader(f))
    for h in houses:
        for k in ("u0", "u1", "v0", "v1"):
            h[k] = float(h[k])
        h["plantas"] = int(h["plantas"])
    with open(OUT / "luces.csv", encoding="utf-8") as f:
        lights = list(csv.DictReader(f))
    return layout, houses, lights


def validate(layout, houses):
    errors, warnings = [], []
    zones = layout["zones"]
    rects = [(h["id"], h["u0"], h["u1"], h["v0"], h["v1"]) for h in houses]
    rects += [(e["id"], *e["u"], *e["v"]) for e in EXTRA]
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            if overlap(a[1], a[2], b[1], b[2]) * overlap(a[3], a[4], b[3], b[4]) > 0:
                errors.append(f"{a[0]} se solapa con {b[0]}")
        for z in zones:
            if overlap(a[1], a[2], *z["u"]) * overlap(a[3], a[4], *z["v"]) > 0:
                errors.append(f"{a[0]} invade la zona {z['id']}")
    # Regla de cámara (LEVEL_DESIGN §4): lo que queda al sur u oeste de un espacio es bajo.
    for h in houses:
        for z in zones:
            south = h["v1"] == z["v"][0] and overlap(h["u0"], h["u1"], *z["u"]) > 0
            west = h["u1"] == z["u"][0] and overlap(h["v0"], h["v1"], *z["v"]) > 0
            if (south or west) and h["plantas"] > 1:
                warnings.append(f"{h['id']} ({h['plantas']} plantas) queda en el lado de cámara de {z['id']}")
            if (south or west) and h["fundido"] != "si":
                warnings.append(f"{h['id']} tapa a {z['id']} desde cámara y no tiene fundido")
    # Huecos dentro de la huella jugable 0..60 x 0..54 que quedarían como muro liso.
    covered = set()
    for _, u0, u1, v0, v1 in rects + [(z["id"], *z["u"], *z["v"]) for z in zones]:
        for u in range(int(u0), int(u1)):
            for v in range(int(v0), int(v1)):
                covered.add((u, v))
    holes = [(u, v) for u in range(UMIN, UMAX) for v in range(VMIN, VMAX) if (u, v) not in covered]
    if holes:
        us = [p[0] for p in holes]
        vs = [p[1] for p in holes]
        warnings.append(f"{len(holes)} m² sin casa ni zona (u {min(us)}–{max(us)+1}, v {min(vs)}–{max(vs)+1})")
    return errors, warnings


def hatch(d, box, color, step=8):
    x0, y0, x1, y1 = box
    for k in range(int(x0 - (y1 - y0)), int(x1), step):
        a = (max(x0, k), y0 + max(0, x0 - k))
        b = (min(x1, k + (y1 - y0)), y0 + min(y1 - y0, x1 - k))
        if a[0] < b[0]:
            d.line([a, b], fill=color, width=1)


def draw(layout, houses, lights, errors, warnings):
    W = M * 2 + (UMAX - UMIN) * S + LEG
    H = M * 2 + (VMAX - VMIN) * S
    img = Image.new("RGB", (W, H), (22, 24, 34))
    d = ImageDraw.Draw(img)
    f_s, f_m, f_b, f_t = font(11), font(13), font(14, True), font(20, True)

    # Rejilla de 4 m y huella jugable
    for u in range(UMIN, UMAX + 1, 4):
        d.line([px(u, VMIN), px(u, VMAX)], fill=(40, 44, 58), width=1)
        if u % 8 == 0:
            d.text((px(u, VMIN)[0] - 6, H - M + 6), str(u), fill=(130, 134, 150), font=f_s)
    for v in range(VMIN, VMAX + 1, 4):
        d.line([px(UMIN, v), px(UMAX, v)], fill=(40, 44, 58), width=1)
        if v % 8 == 0:
            d.text((M - 26, px(UMIN, v)[1] - 6), str(v), fill=(130, 134, 150), font=f_s)
    d.rectangle(rect_px(0, 60, 0, 54), outline=(90, 96, 120), width=1)

    # Zonas
    interior = {"Z_Workshop", "Z_Refuge"}
    agency = {"Z_Archive", "Z_RecordsRoom"}
    for z in layout["zones"]:
        fill = ZONE_AGENCY if z["id"] in agency else ZONE_INT if z["id"] in interior else ZONE_FILL
        d.rectangle(rect_px(*z["u"], *z["v"]), fill=fill, outline=(110, 104, 92))

    # Casas
    for h in houses:
        fill, edge = ARQ[h["arquetipo"]]
        if h["cubierta"] == "teja_roja":
            fill = (150, 58, 46)
        box = rect_px(h["u0"], h["u1"], h["v0"], h["v1"])
        box = [box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1]
        d.rectangle(box, fill=fill, outline=edge, width=2)
        if h["fundido"] == "si":
            hatch(d, box, tuple(min(255, c + 40) for c in fill))
        # cumbrera
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        if h["tejado"] == "dos_aguas_EO":
            d.line([(box[0] + 6, cy), (box[2] - 6, cy)], fill=(230, 220, 200), width=1)
        elif h["tejado"] == "dos_aguas_NS":
            d.line([(cx, box[1] + 6), (cx, box[3] - 6)], fill=(230, 220, 200), width=1)
        elif h["tejado"] == "a_cuatro":
            d.line([(box[0] + 6, box[1] + 6), (cx, cy), (box[2] - 6, box[1] + 6)], fill=(230, 220, 200))
            d.line([(box[0] + 6, box[3] - 6), (cx, cy), (box[2] - 6, box[3] - 6)], fill=(230, 220, 200))
        if h["arquetipo"] == "AGENCY":
            d.rectangle(box, outline=(0, 220, 230), width=2)
        # fachada principal
        side = h["fachada"]
        fc = (255, 214, 120)
        if side == "N":
            d.line([(box[0] + 4, box[1] + 2), (box[2] - 4, box[1] + 2)], fill=fc, width=3)
        elif side == "S":
            d.line([(box[0] + 4, box[3] - 2), (box[2] - 4, box[3] - 2)], fill=fc, width=3)
        elif side == "E":
            d.line([(box[2] - 2, box[1] + 4), (box[2] - 2, box[3] - 4)], fill=fc, width=3)
        elif side == "O":
            d.line([(box[0] + 2, box[1] + 4), (box[0] + 2, box[3] - 4)], fill=fc, width=3)
        # chimeneas
        n = int(h["chimeneas"])
        for k in range(n):
            x = box[0] + (box[2] - box[0]) * (k + 1) / (n + 1)
            d.rectangle([x - 4, box[1] + 5, x + 4, box[1] + 13], fill=(70, 36, 28), outline=(200, 120, 90))
        label = f"{h['id']}·{h['plantas']}P"
        tw = d.textlength(label, font=f_s)
        d.text((cx - tw / 2, cy + 3), label, fill=(245, 240, 230), font=f_s)

    # Extras
    for e in EXTRA:
        box = rect_px(*e["u"], *e["v"])
        if e["kind"] == "fence":
            d.rectangle(box, fill=(60, 58, 60), outline=(20, 20, 20))
            for x in range(int(box[0]) + 4, int(box[2]), 6):
                d.line([(x, box[1] + 3), (x, box[3] - 3)], fill=(15, 15, 18), width=2)
        else:
            d.rectangle(box, fill=(70, 60, 50), outline=CONN["decor"], width=3)

    # Coberturas
    for c in layout["cover"]:
        (u, v), (su, sv, _) = c["center"], c["size"]
        d.rectangle(rect_px(u - su / 2, u + su / 2, v - sv / 2, v + sv / 2), fill=(96, 92, 88), outline=(40, 40, 40))

    # Conexiones (puertas)
    for c in layout["connections"]:
        col = CONN.get(c["type"], CONN["open"])
        a, b = c["range"]
        if c["line"] == "v":
            p0, p1 = px(a, c["at"]), px(b, c["at"])
        else:
            p0, p1 = px(c["at"], a), px(c["at"], b)
        d.line([p0, p1], fill=col, width=7)

    # Ruta de Jack y puntos clave
    cp = layout["check_points"]
    path = [px(*cp[f"Jack_W{i}"]) for i in range(7)]
    for a, b in zip(path, path[1:]):
        d.line([a, b], fill=(160, 90, 200), width=2)
    for k in ("PlayerStart", "Interventor", "Supervisor", "Station_Official", "Station_Authentic"):
        x, y = px(*cp[k])
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255), outline=(0, 0, 0))

    # Luces
    for l in lights:
        x, y = px(float(l["u"]), float(l["v"]))
        col = LIGHT.get(l["color"], (255, 200, 80))
        r = 5 if l["color"] != "cian" else 6
        d.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], outline=col, width=1)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(0, 0, 0))

    # Rótulos de zona
    names = {"Z_Start": "1 Start", "Z_Square": "2 Plaza", "Z_Alley": "3 Callejón", "Z_AlleyNook": "Rincón",
             "Z_WorkshopYard": "4 Patio", "Z_Workshop": "5 Taller", "Z_CentralPass": "6 Paso central",
             "Z_RefugePath": "7 Tramo", "Z_Refuge": "8 Refugio", "Z_Archive": "9 Archivo",
             "Z_RecordsRoom": "10 Registros"}
    for z in layout["zones"]:
        cu = (z["u"][0] + z["u"][1]) / 2
        cv = (z["v"][0] + z["v"][1]) / 2
        if z["id"] == "Z_Square":
            cv = 11.5
        x, y = px(cu, cv)
        t = names.get(z["id"], z["name"])
        tw = d.textlength(t, font=f_b)
        d.text((x - tw / 2, y - 8), t, fill=(30, 26, 22), font=f_b)

    # Cámara (LEVEL_DESIGN §4: suroeste, mirando al noreste)
    x, y = px(-3, -3)
    d.line([(x - 30, y + 30), (x + 10, y - 10)], fill=(255, 255, 255), width=3)
    d.polygon([(x + 14, y - 14), (x + 2, y - 10), (x + 10, y - 2)], fill=(255, 255, 255))
    d.text((x - 44, y + 32), "cámara", fill=(255, 255, 255), font=f_s)

    # Leyenda
    lx = W - LEG + 10
    y = M
    d.text((lx, y), "Whitechapel · plano de manzanas v3", fill=(240, 236, 226), font=f_t); y += 30
    d.text((lx, y), "Rejilla 4 m · u este / v norte · huella 60 × 54 m", fill=(170, 174, 190), font=f_s); y += 24
    for k, (fill, edge) in ARQ.items():
        d.rectangle([lx, y, lx + 22, y + 14], fill=fill, outline=edge, width=2)
        d.text((lx + 30, y), k, fill=(230, 230, 230), font=f_m); y += 20
    d.rectangle([lx, y, lx + 22, y + 14], fill=(150, 58, 46)); d.text((lx + 30, y), "Cubierta de teja roja", fill=(230, 230, 230), font=f_m); y += 20
    b = [lx, y, lx + 22, y + 14]; d.rectangle(b, fill=(122, 62, 48)); hatch(d, b, (170, 110, 90), 5)
    d.text((lx + 30, y), "Rayado: se funde al tapar al jugador", fill=(230, 230, 230), font=f_m); y += 20
    d.line([(lx, y + 7), (lx + 22, y + 7)], fill=(255, 214, 120), width=3); d.text((lx + 30, y), "Fachada principal", fill=(230, 230, 230), font=f_m); y += 20
    d.line([(lx, y + 7), (lx + 22, y + 7)], fill=(230, 220, 200)); d.text((lx + 30, y), "Cumbrera", fill=(230, 230, 230), font=f_m); y += 20
    d.rectangle([lx + 7, y + 3, lx + 15, y + 11], fill=(70, 36, 28), outline=(200, 120, 90)); d.text((lx + 30, y), "Chimenea", fill=(230, 230, 230), font=f_m); y += 26
    for t, c in (("Abertura libre", "open"), ("Puerta de C", "door"), ("Verja cerrada", "gate_closed"), ("Paso cerrado [PROPUESTA]", "decor")):
        d.line([(lx, y + 7), (lx + 22, y + 7)], fill=CONN[c], width=6); d.text((lx + 30, y), t, fill=(230, 230, 230), font=f_m); y += 20
    y += 6
    for t, c in (("Farol / lámpara ámbar", "ambar"), ("Luz tenue", "ambar_tenue"), ("Hogar", "naranja"), ("Tecnología de la agencia", "cian")):
        d.ellipse([lx + 6, y + 2, lx + 16, y + 12], fill=LIGHT[c]); d.text((lx + 30, y), t, fill=(230, 230, 230), font=f_m); y += 20
    d.line([(lx, y + 7), (lx + 22, y + 7)], fill=(160, 90, 200), width=2); d.text((lx + 30, y), "Ruta de Jack", fill=(230, 230, 230), font=f_m); y += 20
    d.ellipse([lx + 6, y + 2, lx + 16, y + 12], fill=(255, 255, 255)); d.text((lx + 30, y), "Inicio, enemigos clave, estaciones", fill=(230, 230, 230), font=f_m); y += 20
    d.rectangle([lx + 4, y + 2, lx + 18, y + 12], fill=(96, 92, 88)); d.text((lx + 30, y), "Cobertura (blockout v1)", fill=(230, 230, 230), font=f_m); y += 28
    d.text((lx, y), "Plantas: 1P ≈ 3,5 m · 2P ≈ 6,5 m · 3P ≈ 9,5 m (alero)", fill=(170, 174, 190), font=f_s); y += 16
    d.text((lx, y), "Lado sur/oeste de cada espacio: 1 planta.", fill=(170, 174, 190), font=f_s); y += 16
    d.text((lx, y), "Zonas y puertas: blockout_layout.json (sin cambios).", fill=(170, 174, 190), font=f_s); y += 24
    d.text((lx, y), f"Validación: {len(errors)} errores, {len(warnings)} avisos", fill=(240, 236, 226), font=f_m); y += 18
    for w in (errors + warnings)[:8]:
        d.text((lx, y), "· " + w[:52], fill=(255, 160, 140) if w in errors else (240, 200, 120), font=f_s); y += 15

    img.save(OUT / "plano_manzanas_v3.png")


def main():
    layout, houses, lights = load()
    errors, warnings = validate(layout, houses)
    for e in errors:
        print("ERROR:", e)
    for w in warnings:
        print("AVISO:", w)
    draw(layout, houses, lights, errors, warnings)
    print(f"{len(houses)} casas, {len(lights)} luces -> {OUT / 'plano_manzanas_v3.png'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
