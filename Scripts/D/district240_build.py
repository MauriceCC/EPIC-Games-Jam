# -*- coding: utf-8 -*-
"""
Blockout completo del distrito 240 x 180 (masterplan aprobado) para L_Test_D (mapa de pruebas de D).

Misma fuente que el plano aprobado (masterplan240_layout.py) y mismas convenciones que el piloto
(pilot240_build.py, ya aprobado). Produce:
  SourceData/D/masterplan_240/district_placements.json
  <salida>/district_mcp_script.py   para ProgrammaticToolset.execute_tool_script
Etiqueta de todos los actores: MP240 (carpeta del Outliner MP240/...). El script MCP borra los actores
MP240 y MP240_PILOT anteriores salvo los NavMeshBoundsVolume (se crean por consola, ver pilot240_build.py).

Reglas:
- Cubos de 100 cm escalados a la huella exacta del layout; alturas del CSV aprobado.
- Edificios con interior: el rectangulo menos (interiores + puertas) se descompone en cajas solidas
  (compresion de coordenadas). Las puertas se recortan a toda altura (corte de maqueta) salvo en el taller,
  que conserva los dinteles del piloto.
- Portones: solo marcas en el suelo (no bloquean). Su logica es de C (BP_Door); el recorrido se prueba con todo abierto.
- Bordes de espacios transitables que no lindan con nada: muro de cierre automatico de 3 m.
Uso:  python -I Scripts/D/district240_build.py [carpeta_salida_script]
"""
import importlib.util, json, math, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "masterplan240_layout.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

OFFX, OFFY, _ = mp.OFF["recommended"]
TAG = "MP240"
BO = "/Game/Unscripted/Art/Blockout/"
PR = "/Game/Unscripted/Art/Props/"
DISTRICT = (0, 0, 240, 180)
WALL_H = 3.0
WALL_HEIGHTS = {"WL-SAV": 2.5, "WL-REF": 2.6, "WL-PTW": 3.0, "WL-FC-E": 3.0, "WL-FC-STEP": 0.8, "WL-FC-SW": 0.8,
                "WL-ESC": 1.2, "WL-SW": 3.0}

def ue_box(rect, z0, h):
    x0, y0, x1, y1 = rect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return {"location": {"x": OFFX + 100 * cy, "y": OFFY + 100 * cx, "z": 100 * (z0 + h / 2)},
            "rotation": {"pitch": 0, "yaw": 0, "roll": 0},
            "scale": {"x": round(y1 - y0, 4), "y": round(x1 - x0, 4), "z": round(h, 4)}}

def ue_point(x, y, z=0.0, yaw=0.0, s=1.0):
    return {"location": {"x": OFFX + 100 * y, "y": OFFY + 100 * x, "z": 100 * z},
            "rotation": {"pitch": 0, "yaw": yaw, "roll": 0}, "scale": {"x": s, "y": s, "z": s}}

def inside_pt(p, r, eps=1e-6):
    return r[0] - eps <= p[0] <= r[2] + eps and r[1] - eps <= p[1] <= r[3] + eps

def subtract(rect, holes):
    """rect menos la union de holes -> lista de rectangulos (compresion de coordenadas + fusion)"""
    xs = sorted({rect[0], rect[2]} | {min(max(h[i], rect[0]), rect[2]) for h in holes for i in (0, 2)})
    ys = sorted({rect[1], rect[3]} | {min(max(h[i], rect[1]), rect[3]) for h in holes for i in (1, 3)})
    solid = {}
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            c = ((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2)
            solid[(i, j)] = not any(h[0] < c[0] < h[2] and h[1] < c[1] < h[3] for h in holes)
    rows = []
    for j in range(len(ys) - 1):
        i = 0
        while i < len(xs) - 1:
            if solid[(i, j)]:
                k = i
                while k + 1 < len(xs) - 1 and solid[(k + 1, j)]:
                    k += 1
                rows.append([xs[i], ys[j], xs[k + 1], ys[j + 1]])
                i = k + 1
            else:
                i += 1
    merged = []
    for r in rows:
        m = next((q for q in merged if q[0] == r[0] and q[2] == r[2] and abs(q[3] - r[1]) < 1e-9), None)
        if m:
            m[3] = r[3]
        else:
            merged.append(list(r))
    return [tuple(round(v, 4) for v in r) for r in merged if (r[2] - r[0]) > 0.01 and (r[3] - r[1]) > 0.01]

def wall_h(wid):
    for k, v in WALL_HEIGHTS.items():
        if wid.startswith(k):
            return v
    return WALL_H

def main():
    items = []
    def add(label, folder, asset, xform, kind, rect=None):
        items.append(dict(label=label, folder="MP240/" + folder, asset=asset, xform=xform, kind=kind, rect=rect))

    rows = {r["ID"]: r for r in mp.building_rows()}
    walks = [(w[0], w[1], w[2]) for w in mp.WALK]
    nav_walks = [w for w in walks if w[1] != "scenic"]

    # 1. suelo base + pavimentos
    add("MP_Ground", "Ground", BO + "SM_BO_Ground", ue_box(DISTRICT, -0.2, 0.2), "ground", DISTRICT)
    mat = {"street": "SM_BO_Cobble", "plaza": "SM_BO_Cobble", "arena-court": "SM_BO_Flag", "alley": "SM_BO_Flag",
           "patio": "SM_BO_Flag", "scenic": "SM_BO_Cobble"}
    for wid, kind, r in walks:
        add("MP_Floor_" + wid[2:], "Floors/" + kind, BO + mat[kind], ue_box(r, 0.0, 0.02), "floor", r)

    # 2. edificios
    for b in mp.BUILD:
        h = rows[b["id"]]["HeightM"]
        fam = b["fam"]
        mesh = {"AR03": "SM_BO_BrickDark", "AR05": "SM_BO_BrickDark", "AR10": "SM_BO_Wood", "AR09": "SM_BO_Kerb",
                "AR08": "SM_BO_Kerb", "SIL": "SM_BO_BrickDark"}.get(fam, "SM_BO_Brick")
        folder = "Buildings/" + b["group"]
        if b["id"] == "SP-TALLER":
            h = 6.5
        if not b["interior"]:
            add("MP_" + b["id"], folder, BO + mesh, ue_box(b["rect"], 0.0, h), "building", b["rect"])
            continue
        holes = b["interior"] + b["doors"]
        for k, r in enumerate(subtract(b["rect"], holes)):
            add(f"MP_{b['id']}_S{k:02d}", folder, BO + mesh, ue_box(r, 0.0, h), "shell", r)
        for k, r in enumerate(b["interior"]):
            add(f"MP_{b['id']}_Floor{k}", folder, BO + "SM_BO_Wood", ue_box(r, 0.0, 0.02), "floor", r)
        if b["id"] == "SP-TALLER":  # dinteles como en el piloto aprobado
            for n, r, z in [("Lintel_W", (140, 44, 140.4, 46.5), 2.6), ("Lintel_N", (147.8, 57.6, 150.8, 58.0), 3.0),
                            ("Lintel_E", (155.6, 48, 156.0, 50.5), 2.6)]:
                add("MP_Taller_" + n, folder, BO + "SM_BO_Brick", ue_box(r, z, h - z), "lintel", None)

    # 3. muros del layout
    for wid, r in mp.WALLS:
        add("MP_" + wid, "Walls", BO + "SM_BO_BrickDark", ue_box(r, 0.0, wall_h(wid)), "wall", r)

    # 4. marcas de porton (no bloquean)
    for g in mp.GATES:
        add("MP_GateMark_" + g[0], "Gates", BO + "SM_BO_Kerb", ue_box(g[1], 0.02, 0.03), "gatemark", g[1])

    # 5. cierres automaticos de bordes abiertos
    covers = [b["rect"] for b in mp.BUILD if b["group"] != "SIL"] + [w[2] for w in walks] + [r for _, r in mp.WALLS]
    covers += [g[1] for g in mp.GATES] + [r for b in mp.BUILD for r in b["doors"]]
    step, off, T = 0.25, 0.1, 0.3
    auto = []
    for wid, kind, r in nav_walks:
        edges = [("S", (r[0], r[1]), (r[2], r[1]), (0, -1)), ("N", (r[0], r[3]), (r[2], r[3]), (0, 1)),
                 ("W", (r[0], r[1]), (r[0], r[3]), (-1, 0)), ("E", (r[2], r[1]), (r[2], r[3]), (1, 0))]
        for side, a, b_, n in edges:
            L = math.hypot(b_[0] - a[0], b_[1] - a[1]); k = int(round(L / step))
            run = None
            for i in range(k + 1):
                s = i * step
                p = (a[0] + (b_[0] - a[0]) * s / L + n[0] * off, a[1] + (b_[1] - a[1]) * s / L + n[1] * off)
                open_ = not any(inside_pt(p, c) for c in covers) and inside_pt(p, DISTRICT)
                if open_ and run is None:
                    run = s
                if (not open_ or i == k) and run is not None:
                    e = s
                    if e - run >= 0.24:
                        if side in ("S", "N"):
                            yy = r[1] if side == "S" else r[3]
                            rr = (a[0] + run, yy - T if side == "S" else yy, a[0] + e, yy if side == "S" else yy + T)
                        else:
                            xx = r[0] if side == "W" else r[2]
                            rr = (xx - T if side == "W" else xx, a[1] + run, xx if side == "W" else xx + T, a[1] + e)
                        auto.append((wid + side, rr))
                    run = None
    for i, (n, rr) in enumerate(auto):
        add(f"MP_Cierre_{i:03d}_{n}", "Walls/Cierres", BO + "SM_BO_BrickDark", ue_box(rr, 0.0, WALL_H), "wall", rr)

    # 6. props del layout aprobado
    for p in mp.PROPS:
        r = p["rect"]; cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        k = p["kind"]; f = "Props"
        if k == "fuente":
            add("MP_Fountain_Base", f, BO + "SM_BO_Kerb", ue_box(r, 0.0, 0.6), "prop", r)
            add("MP_Fountain_Basin", f, PR + "SM_Fountain_Square/SM_Fountain_Square", ue_point(cx, cy, 0.6), "prop", None)
        elif k == "puesto":
            add("MP_" + p["id"], f + "/Puestos", BO + "SM_BO_Wood", ue_box(r, 0.0, 2.6), "prop", r)
        elif k == "carro":
            add("MP_" + p["id"], f, BO + "SM_BO_Wood", ue_box(r, 0.0, 1.6), "prop", r)
        elif k == "farola":
            add("MP_" + p["id"], f + "/Farolas", "/Game/Unscripted/World/BP_GasLamp", ue_point(cx, cy), "prop", r)
        elif k == "caja":
            add("MP_" + p["id"], f + "/Cobertura", PR + "SM_CrateStack_A/SM_CrateStack_A", ue_point(cx, cy), "prop", r)
        elif k == "barril":
            add("MP_" + p["id"], f + "/Cobertura", PR + "SM_Barrel_A/SM_Barrel_A", ue_point(cx, cy), "prop", r)
        elif k == "carretilla":
            add("MP_" + p["id"], f + "/Cobertura", PR + "SM_Handcart_A/SM_Handcart_A", ue_point(cx, cy, 0, 0, 0.65), "prop", r)
        elif k == "pilar":
            add("MP_" + p["id"], f + "/Pilares", PR + "SM_ArchivePillar_A/SM_ArchivePillar_A", ue_point(cx, cy), "prop", r)
        elif k == "mesa":
            add("MP_" + p["id"], "Interiores", PR + "SM_WorkshopTable_A/SM_WorkshopTable_A", ue_point(cx, cy, 0.02, 90), "prop", r)
        elif k == "estante":
            add("MP_" + p["id"], "Interiores", PR + "SM_Shelf_A/SM_Shelf_A", ue_point(cx, cy, 0.02, 0), "prop", r)
        elif k == "escritorio":
            add("MP_" + p["id"], "Interiores", BO + "SM_BO_Wood", ue_box(r, 0.02, 0.78), "prop", r)
        elif k == "estacion":
            add("MP_" + p["id"] + "_Base", "Interiores/Estaciones", BO + "SM_BO_Kerb", ue_box(r, 0.02, 0.15), "prop", r)
            mesh = "SM_RecordStation_Official" if "OFF" in p["id"] else "SM_RecordStation_Authentic"
            add("MP_" + p["id"], "Interiores/Estaciones", PR + f"{mesh}/{mesh}", ue_point(cx, cy, 0.17, 90), "prop", None)
        elif k == "catre":
            add("MP_" + p["id"], "Interiores", PR + "SM_Cot_A/SM_Cot_A", ue_point(cx, cy, 0.02, 0), "prop", r)

    os.makedirs(mp.OUT, exist_ok=True)
    with open(os.path.join(mp.OUT, "district_placements.json"), "w", encoding="utf-8") as fh:
        json.dump({"tag": TAG, "offset_cm": [OFFX, OFFY], "count": len(items), "items": items}, fh, ensure_ascii=False, indent=1)
    data = json.dumps([{k: v for k, v in it.items() if k != "rect"} for it in items], ensure_ascii=False)
    outdir = sys.argv[1] if len(sys.argv) > 1 else mp.OUT
    with open(os.path.join(outdir, "district_mcp_script.py"), "w", encoding="utf-8") as fh:
        fh.write(MCP_TEMPLATE.replace("__DATA__", data))
    print(len(items), Counter(i["kind"] for i in items), "cierres:", len(auto))

MCP_TEMPLATE = r'''import json
A='editor_toolset.toolsets.actor.ActorTools.'
S='editor_toolset.toolsets.scene.SceneTools.'
DATA=json.loads(r"""__DATA__""")
def t(n,a): return execute_tool(n, json.dumps(a))['returnValue']
def run():
    removed=0
    for tag in ('MP240_PILOT','MP240'):
        for a in t(S+'find_actors',{'name':'','tag':tag,'collision_channels':[]}):
            if 'NavMeshBoundsVolume' in a['refPath']: continue
            t(S+'remove_from_scene',{'actor':a}); removed+=1
    made=0; errs=[]
    for it in DATA:
        try:
            a=t(S+'add_to_scene_from_asset',{'asset_path':it['asset'],'name':it['label'],'xform':it['xform']})
            t(A+'set_label',{'actor':a,'label':it['label']})
            t(A+'add_tag',{'actor':a,'tag':'MP240'})
            t(S+'set_actor_folder',{'actor':a,'folder_path':it['folder']})
            made+=1
        except Exception as e:
            errs.append([it['label'],str(e)[-160:]])
    return {'removed':removed,'made':made,'errors':errs[:20]}
'''

if __name__ == "__main__":
    main()
