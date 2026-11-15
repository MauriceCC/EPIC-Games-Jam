"""Calcula aceras, bordillos y pequeños props de las calles del plano v3 (División D).

Lee blockout_layout.json (zonas, conexiones, coberturas) y plano_v3/manzanas.csv, y escribe
SourceData/D/plano_v3/calles.json, que coloca Scripts/D/place_houses_v3.py en L_Whitechapel_Geo
(carpeta Streets_v3, etiqueta D_Streets_v3).

- Acera de losa (MI_Flagstone_York) con bordillo de granito a lo largo de cada fachada que da a
  una zona exterior, cortada en las aberturas y puertas. Solo en zonas de 8 m o más de ancho:
  el Callejón y el Rincón (4 m) se quedan sin acera para no estrechar el paso.
- Barril y pila de cajas junto a cada tienda cuya fachada da a una zona exterior, lejos de las
  puertas y de las coberturas de B.

Uso: python -I Scripts/D/vestir_calles_v3.py
Convenciones: u = este = +Y, v = norte = +X (metros); el cubo básico mide 1 m y tiene el pivote
en el centro.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "SourceData" / "D"
CUBE = "/Engine/BasicShapes/Cube"
MAT = "/Game/Unscripted/Materials/Blockout/"
BARREL = "/Game/Unscripted/Art/Props/SM_Barrel_A/SM_Barrel_A"
CRATES = "/Game/Unscripted/Art/Props/SM_CrateStack_A/SM_CrateStack_A"
INTERIOR = {"Z_Refuge", "Z_Workshop", "Z_Archive", "Z_RecordsRoom"}
PAVE_TOP = 0.12     # m; por encima de las losas antiguas (0,10) para evitar parpadeo
KERB_W, KERB_TOP = 0.22, 0.17
OPENING_MARGIN = 0.5  # m de holgura a cada lado de una abertura


def overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


def subtract(seg, cuts):
    """Resta intervalos `cuts` del intervalo `seg`."""
    parts = [seg]
    for c0, c1 in cuts:
        nxt = []
        for p0, p1 in parts:
            if c1 <= p0 or c0 >= p1:
                nxt.append((p0, p1))
                continue
            if c0 > p0:
                nxt.append((p0, c0))
            if c1 < p1:
                nxt.append((c1, p1))
        parts = nxt
    return [(a, b) for a, b in parts if b - a >= 1.0]


def box(label, u0, u1, v0, v1, top, mat):
    return {
        "label": label, "asset": CUBE, "material": MAT + mat,
        "location": {"x": round((v0 + v1) * 50, 1), "y": round((u0 + u1) * 50, 1), "z": round(top * 50, 1)},
        "rotation": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
        "scale": {"x": round(v1 - v0, 3), "y": round(u1 - u0, 3), "z": round(top, 3)},
    }


def main():
    layout = json.loads((D / "blockout_layout.json").read_text(encoding="utf-8"))
    with open(D / "plano_v3" / "manzanas.csv", encoding="utf-8") as f:
        houses = list(csv.DictReader(f))
    for h in houses:
        for k in ("u0", "u1", "v0", "v1"):
            h[k] = float(h[k])
    covers = [(c["center"][0], c["center"][1], max(c["size"][0], c["size"][1])) for c in layout["cover"]]
    # PlayerStart, checkpoints, ruta de Jack, estaciones: nada a menos de 1,5 m
    points = [v for k, v in layout["check_points"].items() if not k.startswith("_")]
    actors = []
    n_pave = n_prop = 0
    for z in layout["zones"]:
        if z["id"] in INTERIOR:
            continue
        (zu0, zu1), (zv0, zv1) = z["u"], z["v"]
        width = min(zu1 - zu0, zv1 - zv0)
        w = 1.5 if width >= 10 else (1.0 if width >= 8 else 0.0)
        # bordes: (eje fijo, valor, dirección hacia dentro, rango a lo largo)
        edges = [("v", zv0, +1, (zu0, zu1)), ("v", zv1, -1, (zu0, zu1)),
                 ("u", zu0, +1, (zv0, zv1)), ("u", zu1, -1, (zv0, zv1))]
        for axis, at, inward, (r0, r1) in edges:
            cuts = []
            for c in layout["connections"]:
                if c["line"] == axis and abs(c["at"] - at) < 0.01:
                    cuts.append((c["range"][0] - OPENING_MARGIN, c["range"][1] + OPENING_MARGIN))
            for h in houses:
                if axis == "v":
                    touches = (h["v1"] == at and inward > 0) or (h["v0"] == at and inward < 0)
                    o0, o1 = max(r0, h["u0"]), min(r1, h["u1"])
                else:
                    touches = (h["u1"] == at and inward > 0) or (h["u0"] == at and inward < 0)
                    o0, o1 = max(r0, h["v0"]), min(r1, h["v1"])
                if not touches or o1 - o0 < 1.0:
                    continue
                segs = subtract((o0, o1), cuts)
                for s0, s1 in segs if w else []:
                    n_pave += 1
                    a, b = (at, at + inward * w) if inward > 0 else (at + inward * w, at)
                    ka, kb = ((at + inward * w - KERB_W, at + inward * w) if inward > 0
                              else (at + inward * w, at + inward * w + KERB_W))
                    if axis == "v":
                        actors.append(box("SW_%s_%s_%d" % (z["id"][2:], h["id"], n_pave), s0, s1, a, b, PAVE_TOP, "MI_Flagstone_York"))
                        actors.append(box("KB_%s_%s_%d" % (z["id"][2:], h["id"], n_pave), s0, s1, ka, kb, KERB_TOP, "MI_Kerb_Granite"))
                    else:
                        actors.append(box("SW_%s_%s_%d" % (z["id"][2:], h["id"], n_pave), a, b, s0, s1, PAVE_TOP, "MI_Flagstone_York"))
                        actors.append(box("KB_%s_%s_%d" % (z["id"][2:], h["id"], n_pave), ka, kb, s0, s1, KERB_TOP, "MI_Kerb_Granite"))
                # props junto a tiendas que dan a esta zona
                if h["arquetipo"] != "SHOP" or not segs or not w:
                    continue
                s0, s1 = max(segs, key=lambda s: s[1] - s[0])
                if s1 - s0 < 3.0:
                    continue
                d = (w or 0.6) * 0.5 + 0.4
                for k, (asset, t, yaw) in enumerate(((BARREL, 0.18, 0.0), (CRATES, 0.30, 90.0))):
                    along = s0 + (s1 - s0) * t
                    pu, pv = (along, at + inward * d) if axis == "v" else (at + inward * d, along)
                    if any(abs(pu - cu) < cs / 2 + 1.5 and abs(pv - cv) < cs / 2 + 1.5 for cu, cv, cs in covers):
                        continue
                    if any(abs(pu - p[0]) < 1.5 and abs(pv - p[1]) < 1.5 for p in points):
                        continue
                    n_prop += 1
                    actors.append({
                        "label": "PR_%s_%d" % (h["id"], k), "asset": asset,
                        "location": {"x": round(pv * 100, 1), "y": round(pu * 100, 1), "z": round(PAVE_TOP * 100 if w else 0.0, 1)},
                        "rotation": {"pitch": 0.0, "yaw": yaw + 17 * k, "roll": 0.0},
                        "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
                    })
    out = D / "plano_v3" / "calles.json"
    out.write_text(json.dumps({"folder": "Streets_v3", "tag": "D_Streets_v3", "actors": actors},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print("%d tramos de acera, %d props -> %s" % (n_pave, n_prop, out))


if __name__ == "__main__":
    main()
