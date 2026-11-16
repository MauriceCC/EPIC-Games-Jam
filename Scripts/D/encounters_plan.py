"""Plano de encuentros por punto de la historia en L_Test_D — [PROPUESTA] División D.

Dibuja SourceData/D/masterplan_240/encuentros_propuesta.png con:
  - calles/patios navegables del masterplan (gris), zonas que deben quedar libres (verde),
  - ruta principal N01..N20,
  - grupos ya colocados (azul) y grupos propuestos (rojo), numerados como en ENCUENTROS_PROPUESTA.md.

Uso:  python Scripts/D/encounters_plan.py   (requiere Pillow)
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / "SourceData/D/masterplan_240/whitechapel_layout.json"
OUT = ROOT / "SourceData/D/masterplan_240/encuentros_propuesta.png"

# id, acto, nombre, estado, [(tipo, x, y)]  — metros del masterplan (x = este, y = norte)
GROUPS = [
    ("1", "I", "Plaza", "hecho", [("P", 92, 46), ("P", 98, 50)]),
    ("2", "I", "Calle al taller", "hecho", [("Pp", 112, 48)]),
    ("3", "I", "Puerta del taller", "nuevo", [("P", 135, 46), ("P", 138, 50)]),
    ("4", "II", "Ensanche de escape", "hecho", [("P", 170, 96), ("P", 176, 101), ("P", 180, 95)]),
    ("5", "II", "Estrechamiento 2", "nuevo", [("P", 178, 117), ("P", 180, 122)]),
    ("6", "II", "Registro de enfermería", "nuevo", [("P", 215, 136), ("Pp", 220, 139)]),
    ("7", "II", "Informe fabricado", "nuevo", [("P", 216, 99), ("P", 220, 103), ("Pp", 226, 80)]),
    ("8", "II", "Tránsito al refugio", "hecho", [("I", 195, 142)]),
    ("9", "II", "Refugio", "nuevo", [("P", 206, 149), ("P", 210, 148), ("P", 218, 149)]),
    ("10", "III", "Paso central", "hecho+", [("Pp", 115, 115), ("P", 140, 114), ("P", 146, 116)]),
    ("11", "III", "Reja del archivo", "nuevo", [("P", 119, 134), ("P", 125, 134)]),
    ("12", "III", "Antepatio (jefe)", "hecho", [("S", 94, 124)]),
]
COLORS = {"hecho": (40, 110, 220), "hecho+": (150, 60, 200), "nuevo": (220, 40, 40)}
S = 6  # px por metro


def main():
    d = json.loads(LAYOUT.read_text(encoding="utf-8"))
    W, H = 240 * S, 180 * S
    im = Image.new("RGB", (W + 40, H + 40), (24, 24, 28))
    dr = ImageDraw.Draw(im)
    tx = lambda x: 20 + x * S
    ty = lambda y: 20 + (180 - y) * S
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        fontb = ImageFont.truetype("arialbd.ttf", 18)
    except OSError:
        font = fontb = ImageFont.load_default()
    for w in d["walkable"]:
        r = w["rect"]
        dr.rectangle([tx(r[0]), ty(r[3]), tx(r[2]), ty(r[1])], fill=(70, 70, 78))
    for c in d["mustStayClear"]:
        r = c["rect"]
        dr.rectangle([tx(r[0]), ty(r[3]), tx(r[2]), ty(r[1])], outline=(60, 170, 90), width=2)
    for k, z in d["zones"].items():
        r = z["rect"]
        dr.text((tx(r[0]) + 3, ty(r[3]) + 2), k, fill=(150, 150, 160), font=font)
    nodes = d["nodes"]
    order = [f"N{i:02d}" for i in range(1, 21)]
    pts = [(tx(nodes[n]["xy"][0]), ty(nodes[n]["xy"][1])) for n in order]
    dr.line(pts, fill=(230, 200, 80), width=3)
    for n, p in zip(order, pts):
        dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(230, 200, 80))
    for gid, act, name, state, members in GROUPS:
        col = COLORS[state]
        cx = sum(m[1] for m in members) / len(members)
        cy = sum(m[2] for m in members) / len(members)
        for t, x, y in members:
            px, py = tx(x), ty(y)
            rad = 9 if t in ("I", "S") else 7
            dr.ellipse([px - rad, py - rad, px + rad, py + rad], fill=col, outline=(255, 255, 255))
            if t in ("I", "S", "Pp"):
                dr.text((px - 5, py - 9), {"I": "I", "S": "S", "Pp": "p"}[t], fill=(255, 255, 255), font=font)
        dr.text((tx(cx) + 12, ty(cy) - 22), f"{gid}", fill=col, font=fontb)
    # leyenda
    lx, ly = 30, 30
    for txt, col in [("Grupo ya colocado", COLORS["hecho"]), ("Ya colocado + refuerzo", COLORS["hecho+"]),
                     ("Grupo nuevo [PROPUESTA]", COLORS["nuevo"]), ("Ruta principal N01-N20", (230, 200, 80)),
                     ("Zona que debe quedar libre", (60, 170, 90))]:
        dr.rectangle([lx, ly, lx + 14, ly + 14], fill=col)
        dr.text((lx + 22, ly - 2), txt, fill=(230, 230, 230), font=font)
        ly += 22
    dr.text((lx, ly + 4), "p = patrulla   I = Interventor   S = Supervisor", fill=(230, 230, 230), font=font)
    im.save(OUT)
    print("->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
