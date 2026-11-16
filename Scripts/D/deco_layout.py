"""Decoración por punto de la historia en L_Test_D — [PROPUESTA] División D.

Genera:
  SourceData/D/masterplan_240/deco_placements.json   (colocación lista para el editor)
  SourceData/D/masterplan_240/deco_propuesta.png     (plano general)
  SourceData/D/masterplan_240/deco_detalle.png       (los 13 lugares ampliados)

Reglas que comprueba para cada objeto (huella real medida en el editor, deco_sizes.json):
  - huella completa dentro de calles/patios navegables (o del interior declarado del lugar);
  - fuera de las zonas que deben quedar libres (arenas, frentes, espera de Jack) con 0,5 m de margen;
  - sin solapar props existentes (deco_existing.json) ni otros nuevos (0,3 m de margen);
  - a 1,5 m o más de cada enemigo y a 1,3 m o más de la ruta principal N01–N20;
  - en calles con ancho mínimo (minFree), el hueco libre más ancho de cada sección sigue >= minFree;
  - regla de cámara (yaw 45: la cámara mira hacia el noreste desde el suroeste): los objetos de más
    de 1,8 m solo van al noreste del centro del lugar, para no tapar al jugador.
Determinista (semilla fija). Uso:  python Scripts/D/deco_layout.py
"""
import importlib.util
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MP = ROOT / "SourceData/D/masterplan_240"
LAYOUT = json.loads((MP / "whitechapel_layout.json").read_text(encoding="utf-8"))
SIZES = json.loads((MP / "deco_sizes.json").read_text(encoding="utf-8"))
# Los props existentes que son suelo (pavimento de acera) se pisan: no cuentan como obstáculo.
FLOOR_MESHES = {"SM_StreetFlagstones"}
EXISTING = [e for e in json.loads((MP / "deco_existing.json").read_text(encoding="utf-8")) if e["mesh"] not in FLOOR_MESHES]
_spec = importlib.util.spec_from_file_location("enc", ROOT / "Scripts/D/encounters_plan.py")
ENC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ENC)

SEED = 1888
TALL_M = 1.8
# Arenas donde se admite cobertura baja en una franja pegada al borde (el centro sigue libre).
BAND = {"4": "Ensanche de escape 17x15"}
BAND_W = 1.2
BAND_MAX_H = 1.3
P = "/Game/Unscripted/Art/Props/"
ASSET = {n: f"{P}{n}/{n}.{n}" for n in SIZES if not n.startswith("SM_Market_")}
ASSET["SM_Market_FlowerCart"] = "/Game/Unscripted/Art/Market/FlowerCart/SM_Market_FlowerCart.SM_Market_FlowerCart"
ASSET["SM_Market_SoupCart"] = "/Game/Unscripted/Art/Market/SoupCart/SM_Market_SoupCart.SM_Market_SoupCart"

# modo: edge = contra el borde de lo navegable (pared); near = cerca del ancla; table = encima de la última mesa
# (id, nombre, centro (m), radio de búsqueda (m), ancla opcional, interior extra, [(asset, n, modo)])
SPOTS = [
    ("1", "Plaza", (95, 48), 14, None, None, [
        ("SM_Market_FlowerCart", 2, "edge"), ("SM_Market_SoupCart", 1, "edge"), ("SM_Cart_Overturned", 1, "near"),
        ("SM_CrateStack_A", 3, "near"), ("SM_Barrel_A", 4, "near"), ("SM_GasLamp_A", 1, "edge")]),
    ("2", "Calle al taller", (125, 48), 10, None, None, [
        ("SM_Drainpipe_A", 2, "edge"), ("SM_Barrel_A", 2, "edge"), ("SM_Handcart_A", 1, "edge")]),
    ("3", "Puerta del taller", (137, 48), 7, None, None, [
        ("SM_WorkshopTable_A", 1, "edge"), ("SM_CrateStack_A", 2, "edge"), ("SM_DebrisPile_A", 1, "edge"), ("SM_Barrel_A", 2, "edge")]),
    ("4", "Ensanche de escape", (175, 98), 10, None, None, [
        ("SM_Cart_Overturned", 1, "edge"), ("SM_LowWall_Stone_A", 1, "edge"), ("SM_DebrisPile_A", 1, "edge"),
        ("SM_CrateStack_A", 3, "edge"), ("SM_Barrel_A", 4, "edge")]),
    ("5", "Estrechamiento 2", (179, 120), 8, None, None, [
        ("SM_DebrisPile_A", 1, "edge"), ("SM_Handcart_A", 1, "edge"), ("SM_Barrel_A", 2, "edge")]),
    ("6", "Registro de enfermería", (218, 137), 7, None, None, [
        ("SM_Cot_A", 3, "edge"), ("SM_WorkshopTable_A", 1, "edge"), ("SM_Ledger_Nursing", 1, "table"),
        ("SM_Chair_A", 2, "near"), ("SM_Shelf_A", 1, "edge")]),
    ("7", "Informe fabricado", (218, 101), 7, None, None, [
        ("SM_CrateStack_A", 3, "edge"), ("SM_Wardrobe_A", 1, "edge"), ("SM_Handcart_A", 1, "edge"),
        ("SM_WorkshopTable_A", 1, "edge"), ("SM_Folder_Report", 1, "table"), ("SM_Barrel_A", 1, "edge")]),
    ("8", "Tránsito al refugio", (195, 142), 10, None, None, [
        ("SM_GasLamp_A", 2, "edge"), ("SM_Barrel_A", 2, "edge"), ("SM_LowWall_Stone_A", 1, "edge")]),
    ("9", "Refugio (barricada)", (212, 152), 10, (206, 148), None, [
        ("SM_Cart_Victorian", 1, "near"), ("SM_Cart_Overturned", 1, "near"), ("SM_CrateStack_A", 3, "near"),
        ("SM_Wardrobe_A", 1, "near"), ("SM_Barrel_A", 3, "near"), ("SM_DebrisPile_A", 1, "near")]),
    ("10", "Paso central", (143, 115), 12, None, None, [
        ("SM_DebrisPile_A", 1, "edge"), ("SM_Barrel_A", 3, "edge"), ("SM_Handcart_A", 1, "edge"), ("SM_CrateStack_A", 1, "edge")]),
    ("11", "Reja del archivo", (122, 134), 8, None, None, [
        ("SM_GasLamp_A", 2, "edge"), ("SM_LowWall_Stone_A", 1, "edge"), ("SM_ArchiveCabinet_A", 2, "edge")]),
    ("12", "Antepatio (jefe)", (94, 122), 18, None, None, [
        ("SM_ArchivePillar_A", 4, "edge"), ("SM_GasLamp_A", 2, "edge"), ("SM_LowWall_Stone_A", 2, "edge")]),
    ("13", "Sala de elección", (77, 157), 12, None, [65.5, 151.5, 88.5, 167.5], [
        ("SM_ArchiveCabinet_A", 4, "edge"), ("SM_Shelf_A", 2, "edge")]),
]


def rect_of(cx, cy, sx, sy, yaw):
    """AABB (m) de una huella sx×sy girada yaw grados (solo 0/90 ± jitter: se usa la caja envolvente)."""
    a = math.radians(yaw)
    w = abs(sx * math.cos(a)) + abs(sy * math.sin(a))
    h = abs(sx * math.sin(a)) + abs(sy * math.cos(a))
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]


def overlap(a, b, m=0.0):
    return a[0] - m < b[2] and b[0] - m < a[2] and a[1] - m < b[3] and b[1] - m < a[3]


def inside_any(pt, rects):
    return any(r[0] <= pt[0] <= r[2] and r[1] <= pt[1] <= r[3] for r in rects)


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def rect_route_dist(r, route):
    pts = [(r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3]), ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)]
    best = 1e9
    for i in range(len(route) - 1):
        a, b = route[i], route[i + 1]
        for p in pts:
            best = min(best, seg_dist(p, a, b))
        # la ruta cruza la caja
        for k in range(21):
            q = (a[0] + (b[0] - a[0]) * k / 20, a[1] + (b[1] - a[1]) * k / 20)
            if r[0] <= q[0] <= r[2] and r[1] <= q[1] <= r[3]:
                return 0
    return best


def _gap(occ, r, ax, s, c0, c1):
    iv = []
    for o in occ:
        a0, a1 = (o[0], o[2]) if ax == "x" else (o[1], o[3])
        if a0 <= s <= a1 and overlap(o, r):
            b0, b1 = (o[1], o[3]) if ax == "x" else (o[0], o[2])
            iv.append((max(c0, b0), min(c1, b1)))
    iv.sort()
    gap, cur = 0.0, c0
    for b0, b1 in iv:
        gap = max(gap, b0 - cur)
        cur = max(cur, b1)
    return max(gap, c1 - cur)


def corridor_ok(occupied, new):
    """En cada calle con minFree que toca el objeto nuevo, y en cada sección (0,25 m) que ocupa,
    el hueco libre más ancho sigue >= minFree, o al menos no empeora si ya estaba por debajo."""
    for w in LAYOUT["walkable"]:
        mf = w.get("minFree")
        if not mf or not w.get("axis") or not overlap(new, w["rect"]):
            continue
        r, ax = w["rect"], w["axis"]
        c0, c1 = (r[1], r[3]) if ax == "x" else (r[0], r[2])
        lo, hi = (new[0], new[2]) if ax == "x" else (new[1], new[3])
        s = lo
        while s <= hi:
            before = _gap(occupied, r, ax, s, c0, c1)
            after = _gap(occupied + [new], r, ax, s, c0, c1)
            if after + 1e-6 < mf and after + 1e-6 < before:
                return False, w["id"]
            s += 0.25
    return True, None


def main():
    rng = random.Random(SEED)
    walk = [w["rect"] for w in LAYOUT["walkable"]]
    clear = [c["rect"] for c in LAYOUT["mustStayClear"]]
    nodes = LAYOUT["nodes"]
    route = [tuple(nodes[f"N{i:02d}"]["xy"]) for i in range(1, 21)]
    enemies = [(x, y) for g in ENC.GROUPS for (_t, x, y) in g[4]]
    occupied = [e["rect"] for e in EXISTING]
    placed, report = [], []

    for sid, name, center, rad, anchor, extra, items in SPOTS:
        cx, cy = center
        area = walk + ([extra] if extra else [])
        local = [r for r in area if overlap(r, [cx - rad, cy - rad, cx + rad, cy + rad])]
        ok_n, want, last_table = 0, sum(n for _a, n, _m in items), None
        for asset, n, mode in items:
            sz = SIZES[asset]
            tall = sz["h"] > TALL_M
            for _k in range(n):
                if mode == "table":
                    if last_table is None:
                        report.append(f"{sid} {asset}: sin mesa")
                        continue
                    t = last_table
                    placed.append({"spot": sid, "asset": asset, "path": ASSET[asset], "x": t["x"] + 0.15, "y": t["y"],
                                   "z_m": SIZES["SM_WorkshopTable_A"]["h"], "yaw": t["yaw"] + 12, "rect": t["rect"], "tall": False})
                    ok_n += 1
                    continue
                best = None
                for _try in range(1500):
                    base = rng.choice(local)
                    px = rng.uniform(max(base[0], cx - rad), min(base[2], cx + rad))
                    py = rng.uniform(max(base[1], cy - rad), min(base[3], cy + rad))
                    # orientar a lo largo del lado más cercano de su calle/patio
                    dxw = min(px - base[0], base[2] - px)
                    dyw = min(py - base[1], base[3] - py)
                    yaw = (0 if dyw < dxw else 90) + rng.uniform(-8, 8)
                    if asset in ("SM_Barrel_A", "SM_CrateStack_A", "SM_DebrisPile_A"):
                        yaw = rng.uniform(0, 360)
                    r = rect_of(px, py, sz["sx"], sz["sy"], yaw)
                    if math.hypot(px - cx, py - cy) > rad:
                        continue
                    corners = [(r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3])]
                    if not all(inside_any(c, area) for c in corners):
                        continue
                    band = BAND.get(sid)
                    in_band = False
                    if band and sz["h"] <= BAND_MAX_H:
                        br = band_rect = next(c["rect"] for c in LAYOUT["mustStayClear"] if c["name"] == band)
                        inner = [br[0] + BAND_W, br[1] + BAND_W, br[2] - BAND_W, br[3] - BAND_W]
                        in_band = overlap(r, br) and not overlap(r, inner)
                    if any(overlap(r, c, 0.5) for c in clear) and not (in_band and not any(
                            overlap(r, c["rect"], 0.5) for c in LAYOUT["mustStayClear"] if c["name"] != band)):
                        continue
                    if any(overlap(r, o, 0.3) for o in occupied):
                        continue
                    if any(math.hypot(ex - px, ey - py) < 1.5 + max(sz["sx"], sz["sy"]) / 2 for ex, ey in enemies):
                        continue
                    if rect_route_dist(r, route) < 1.3:
                        continue
                    if tall and (px - cx) + (py - cy) < 1.0:
                        continue
                    # puntuación: pegado a pared (edge) o al ancla (near)
                    if mode == "edge":
                        score = min(r[0] - base[0], base[2] - r[2], r[1] - base[1], base[3] - r[3])
                    else:
                        ax_, ay_ = anchor or center
                        score = math.hypot(px - ax_, py - ay_) * 0.4
                    if best is None or score < best[0]:
                        good, _cid = corridor_ok(occupied, r)
                        if good:
                            best = (score, px, py, yaw, r)
                    if best is not None and best[0] < 0.25 and _try > 200:
                        break
                if best is None:
                    report.append(f"{sid} {asset}: sin hueco válido")
                    continue
                _s, px, py, yaw, r = best
                occupied.append(r)
                item = {"spot": sid, "asset": asset, "path": ASSET[asset], "x": round(px, 2), "y": round(py, 2),
                        "z_m": 0.0, "yaw": round(yaw, 1), "rect": [round(v, 2) for v in r], "tall": tall}
                placed.append(item)
                if asset == "SM_WorkshopTable_A":
                    last_table = item
                ok_n += 1
        report.append(f"{sid} {name}: {ok_n}/{want}")

    for it in placed:
        it["ue"] = {"x": round(100 * it["y"], 1), "y": round(12000 + 100 * it["x"], 1), "z": round(100 * it["z_m"], 1)}
    out = {"meta": {"version": "deco v1 [PROPUESTA]", "tag": "MP240_DECO", "folder": "MP240_DECO",
                    "count": len(placed), "report": report}, "items": placed}
    (MP / "deco_placements.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    draw(placed, walk, clear, route)
    print("\n".join(report))
    print(f"total {len(placed)} objetos")


def draw(placed, walk, clear, route):
    try:
        font = ImageFont.truetype("arial.ttf", 15)
        fontb = ImageFont.truetype("arialbd.ttf", 20)
    except OSError:
        font = fontb = ImageFont.load_default()
    cols = {"tall": (240, 150, 40), "low": (250, 220, 120)}

    def render(S, x0, y0, x1, y1, title=None, img_w=None):
        W, H = int((x1 - x0) * S), int((y1 - y0) * S)
        im = Image.new("RGB", (W, H), (24, 24, 28))
        dr = ImageDraw.Draw(im)
        tx = lambda x: (x - x0) * S
        ty = lambda y: (y1 - y) * S
        R = lambda r: [tx(r[0]), ty(r[3]), tx(r[2]), ty(r[1])]
        for r in walk:
            dr.rectangle(R(r), fill=(70, 70, 78))
        for s in SPOTS:
            if s[5]:
                dr.rectangle(R(s[5]), fill=(62, 62, 72))
        for r in clear:
            dr.rectangle(R(r), outline=(60, 170, 90), width=2)
        dr.line([(tx(a), ty(b)) for a, b in route], fill=(230, 200, 80), width=max(2, int(S / 3)))
        for e in EXISTING:
            dr.rectangle(R(e["rect"]), fill=(120, 120, 130))
        for it in placed:
            dr.rectangle(R(it["rect"]), fill=cols["tall" if it["tall"] else "low"], outline=(20, 20, 20))
        for g in ENC.GROUPS:
            col = ENC.COLORS[g[3]]
            for _t, x, y in g[4]:
                rr = max(4, S * 0.45)
                dr.ellipse([tx(x) - rr, ty(y) - rr, tx(x) + rr, ty(y) + rr], fill=col, outline=(255, 255, 255))
        if title:
            dr.text((8, 6), title, fill=(255, 255, 255), font=fontb)
        return im

    full = render(6, 0, 0, 240, 180)
    dr = ImageDraw.Draw(full)
    for sid, name, (cx, cy), rad, *_ in SPOTS:
        dr.text((cx * 6 + 10, (180 - cy) * 6 - 26), sid, fill=(255, 255, 255), font=fontb)
    ly = 10
    for txt, col in [("Prop nuevo bajo", cols["low"]), ("Prop nuevo alto (>1,8 m, solo al NE)", cols["tall"]),
                     ("Prop existente", (120, 120, 130)), ("Enemigo (azul hecho, rojo nuevo)", (220, 40, 40)),
                     ("Ruta principal", (230, 200, 80)), ("Zona libre", (60, 170, 90))]:
        dr.rectangle([12, ly, 26, ly + 14], fill=col)
        dr.text((34, ly - 2), txt, fill=(230, 230, 230), font=font)
        ly += 20
    full.save(MP / "deco_propuesta.png")

    tiles = []
    for sid, name, (cx, cy), rad, *_ in SPOTS:
        r = max(rad, 9) + 2
        tiles.append(render(18, cx - r, cy - r, cx + r, cy + r, f"{sid} · {name}").resize((420, 420)))
    cols_n = 5
    rows = math.ceil(len(tiles) / cols_n)
    sheet = Image.new("RGB", (cols_n * 424, rows * 424), (10, 10, 12))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols_n) * 424, (i // cols_n) * 424))
    sheet.save(MP / "deco_detalle.png")


if __name__ == "__main__":
    main()
