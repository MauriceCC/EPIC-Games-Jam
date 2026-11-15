"""Calcula la colocación de las casas del plano v3 (División D).

Lee SourceData/D/plano_v3/manzanas.csv y escribe SourceData/D/plano_v3/colocacion.json con un
actor por casa (o varios cuando la huella es más larga que la malla). El JSON lo consume la
colocación por MCP en L_Whitechapel_Geo (carpeta Houses_v3, etiqueta D_Houses_v3).

Uso: python -I Scripts/D/colocar_casas_v3.py

Convenciones: u = este = +Y de Unreal, v = norte = +X (como blockout_layout.json).
Las mallas SM_House_* tienen la base en Z = 0 y la fachada hacia +Y local (comprobado en el
editor el 2026-11-15).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "SourceData" / "D" / "plano_v3"
ART = "/Game/Unscripted/Art/Buildings"

# ancho (x local), fondo (y local), alto en metros tras fix_house_scale.py
MESH = {
    "Brick": (8.2, 8.3, 12.0),
    "Shop": (6.8, 6.8, 10.0),
    "Corner": (7.4, 8.4, 6.0),
    "Workshop": (17.3, 10.8, 11.0),
    "Agency": (17.5, 13.1, 16.0),
    "Filler": (13.5, 7.5, 12.5),
    "ShopLow": (6.7, 5.8, 4.5),
}
YAW = {"N": -90.0, "S": 90.0, "E": 0.0, "O": 180.0}
# Casas con fundido=si (sur/oeste de un espacio): con la cámara a −55° un volumen tapa al
# jugador si supera ~1 m + 1,4 × distancia; a 3 m del borde eso son ~5 m.
CAMERA_SIDE_MAX_M = 4.8
PERIMETER_MAX_M = 3.0
SHOP_PERIMETER_M = 3.8
# Estirar el fondo hasta 2,2× rellena las manzanas profundas sin dejar huecos entre casas.
MAX_DEPTH_SCALE = 2.2


def fit(length, width):
    """Número de copias y escala a lo ancho para cubrir `length` con mallas de `width`."""
    n = max(1, round(length / width))
    sx = length / (n * width)
    if sx > 1.4:
        n += 1
        sx = length / (n * width)
    return n, sx


def pick(arq, floors):
    """Malla y altura objetivo (m) según arquetipo y plantas."""
    if arq == "SHOP":
        return "Shop", {1: 7.0, 2: 10.0}.get(floors, 11.0)
    if arq == "WORKSHOP":
        return "Workshop", {1: 7.0, 2: 11.0}.get(floors, 12.5)
    if arq == "AGENCY":
        return ("Agency", 14.5) if floors >= 3 else ("Corner", 6.0)
    if arq == "CORNER" or floors == 1:
        return "Corner", 6.0
    if arq == "FILLER":
        return "Filler", 12.5
    return "Brick", {2: 9.6}.get(floors, 12.0)


def main():
    actors = []
    with open(PLAN / "manzanas.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        u0, u1, v0, v1 = (float(r[k]) for k in ("u0", "u1", "v0", "v1"))
        floors = int(r["plantas"])
        face = r["fachada"]
        if face == "-":
            face = "S" if (u1 - u0) >= (v1 - v0) else "O"
        mesh, height = pick(r["arquetipo"], floors)
        if r["fundido"] == "si":
            # Lado de cámara (LEVEL_DESIGN §4): casita baja, nunca más de CAMERA_SIDE_MAX_M.
            shop = r["arquetipo"] == "SHOP"
            mesh, height = ("ShopLow" if shop else "Corner"), min(height, CAMERA_SIDE_MAX_M)
            if v1 <= 0 or u1 <= 0:
                # borde exterior sur/oeste: PlayerStart queda a 3 m; 4,8 m taparían 3,4 m de suelo.
                # Las tiendas bajan algo menos para que la puerta siga teniendo altura de paso.
                height = SHOP_PERIMETER_M if shop else PERIMETER_MAX_M
        along_u = face in ("N", "S")          # la fachada corre a lo largo de u (eje Y)
        length = (u1 - u0) if along_u else (v1 - v0)
        depth = (v1 - v0) if along_u else (u1 - u0)
        n, sx = fit(length, MESH[mesh][0])
        if sx < 0.75 and mesh != "Corner":
            # huella demasiado estrecha para esta malla: la casita aguanta mejor el ajuste
            mesh, height = "Corner", min(height, 7.0)
            n, sx = fit(length, MESH[mesh][0])
        w, d, h = MESH[mesh]
        sy = min(max(depth / d, 0.5), MAX_DEPTH_SCALE)
        real_depth = d * sy
        sz = height / h
        step = length / n
        for i in range(n):
            # centro a lo largo de la fachada
            c = (u0 if along_u else v0) + step * (i + 0.5)
            # centro en profundidad: pegado a la fachada
            if face == "N":
                cu, cv = c, v1 - real_depth / 2
            elif face == "S":
                cu, cv = c, v0 + real_depth / 2
            elif face == "E":
                cu, cv = u1 - real_depth / 2, c
            else:
                cu, cv = u0 + real_depth / 2, c
            mirror = -1.0 if (i + len(actors)) % 2 else 1.0
            jitter = 1.0 + 0.04 * ((hash(r["id"] + str(i)) % 5) - 2) / 2
            actors.append({
                "label": "%s_%d" % (r["id"], i + 1) if n > 1 else r["id"],
                "asset": "%s/SM_House_%s/SM_House_%s" % (ART, mesh, mesh),
                "location": {"x": round(cv * 100, 1), "y": round(cu * 100, 1), "z": 0.0},
                "rotation": {"pitch": 0.0, "yaw": YAW[face], "roll": 0.0},
                "scale": {"x": round(sx * mirror, 3), "y": round(sy, 3), "z": round(sz * jitter, 3)},
                "fundido": r["fundido"] == "si",
            })
    out = PLAN / "colocacion.json"
    out.write_text(json.dumps({"folder": "Houses_v3", "tag": "D_Houses_v3", "actors": actors},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    print("%d actores para %d casas -> %s" % (len(actors), len(rows), out))


if __name__ == "__main__":
    main()
