# -*- coding: utf-8 -*-
"""
Sector piloto Inicio -> Plaza -> Taller (masterplan 240 x 180) para L_Test_D.

Lee las tablas de masterplan240_layout.py (misma fuente que el plano aprobado) y produce:
  SourceData/D/masterplan_240/pilot_placements.json   lista de actores a colocar
  <salida>/pilot_mcp_script.py                         script para ProgrammaticToolset.execute_tool_script

No usa Unreal. Uso:  python -I Scripts/D/pilot240_build.py [carpeta_salida_script]
Las medidas vienen del layout aprobado; este script no las ajusta. Todo actor lleva la etiqueta MP240_PILOT
y va a la carpeta del Outliner "MP240_Pilot/..." para poder borrarlo o rehacerlo sin tocar nada mas.
"""
import importlib.util, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mp", os.path.join(HERE, "masterplan240_layout.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

OFFX, OFFY, _ = mp.OFF["recommended"]
TAG = "MP240_PILOT"
BO = "/Game/Unscripted/Art/Blockout/"
PR = "/Game/Unscripted/Art/Props/"

PILOT_BOX = (26, -2, 174, 90)
INCLUDE_PREFIX = ("MA-0", "MB-", "MC-", "MD-", "MJ-S", "MF-X01", "SP-TALLER", "SP-ANEXO")
WALK_IDS = {"W-SAV", "W-Z01", "W-PS1", "W-PL", "W-STE", "W-PN", "W-PAS", "W-PTW"}
TRIM = {"W-PN": (84, 72, 92, 84)}  # la calle norte se corta en la verja G-PN-S (cerrada en Acto I)
PROP_IDS_EXCLUDE = ("PR-COV-ES", "PR-COV-RF", "PR-PILLAR", "PR-DESK", "PR-ST-", "PR-COT")
WALL_H = 3.0

def ue_box(rect, z0, h):
    """rect del plano (m) -> centro (cm) y escala del cubo de 100 cm en UE (X=norte, Y=este)"""
    x0, y0, x1, y1 = rect
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return {"location": {"x": OFFX + 100 * cy, "y": OFFY + 100 * cx, "z": 100 * (z0 + h / 2)},
            "rotation": {"pitch": 0, "yaw": 0, "roll": 0},
            "scale": {"x": round(y1 - y0, 4), "y": round(x1 - x0, 4), "z": round(h, 4)}}

def ue_point(x, y, z=0.0, yaw=0.0):
    return {"location": {"x": OFFX + 100 * y, "y": OFFY + 100 * x, "z": 100 * z},
            "rotation": {"pitch": 0, "yaw": yaw, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}}

def inside_pt(p, r, eps=1e-6):
    return r[0] - eps <= p[0] <= r[2] + eps and r[1] - eps <= p[1] <= r[3] + eps

def strictly_in(p, r):
    return r[0] < p[0] < r[2] and r[1] < p[1] < r[3]

def main():
    items = []
    def add(label, folder, asset, xform, kind, rect=None):
        items.append(dict(label=label, folder="MP240_Pilot/" + folder, asset=asset, xform=xform, kind=kind, rect=rect))

    blds = [b for b in mp.BUILD if b["id"].startswith(INCLUDE_PREFIX)]
    walks = []
    for w in mp.WALK:
        if w[0] in WALK_IDS:
            walks.append((w[0], w[1], TRIM.get(w[0], w[2])))
    rows = {r["ID"]: r for r in mp.building_rows()}

    # 1. suelo base y pavimentos (pavimento 2 cm sobre el suelo base, sin solape de caras)
    add("MP_Ground", "Ground", BO + "SM_BO_Ground", ue_box(PILOT_BOX, -0.2, 0.2), "ground", PILOT_BOX)
    pave = {"W-PL": "SM_BO_Cobble", "W-SAV": "SM_BO_Cobble", "W-Z01": "SM_BO_Cobble", "W-STE": "SM_BO_Cobble",
            "W-PN": "SM_BO_Cobble", "W-PS1": "SM_BO_Flag", "W-PAS": "SM_BO_Flag", "W-PTW": "SM_BO_Flag"}
    for wid, kind, r in walks:
        add("MP_Floor_" + wid[2:], "Floors", BO + pave[wid], ue_box(r, 0.0, 0.02), "floor", r)

    # 2. edificios como volumenes simples (altura del CSV aprobado)
    for b in blds:
        if b["id"] == "SP-TALLER":
            continue
        h = rows[b["id"]]["HeightM"]
        mesh = "SM_BO_BrickDark" if b["fam"] in ("AR03", "AR05") else ("SM_BO_Wood" if b["fam"] == "AR10" else "SM_BO_Brick")
        add("MP_" + b["id"], "Buildings/" + b["group"], BO + mesh, ue_box(b["rect"], 0.0, h), "building", b["rect"])

    # 3. taller de Jack: cascaron de muros de 0,4 m con huecos de puerta, sin cubierta (corte de camara)
    tl = next(b for b in mp.BUILD if b["id"] == "SP-TALLER")
    x0, y0, x1, y1 = tl["rect"]; t = 0.4; H = 6.5
    walls = [  # (rect) con los huecos de las puertas del layout
        ("W_S", (x0, y0, x1, y0 + t)),
        ("W_W1", (x0, y0 + t, x0 + t, 44)), ("W_W2", (x0, 46.5, x0 + t, y1 - t)),
        ("W_N1", (x0, y1 - t, 147.8, y1)), ("W_N2", (150.8, y1 - t, x1, y1)),
        ("W_E1", (x1 - t, y0 + t, x1, 48)), ("W_E2", (x1 - t, 50.5, x1, y1 - t)),
    ]
    for n, r in walls:
        add("MP_Taller_" + n, "Taller", BO + "SM_BO_Brick", ue_box(r, 0.0, H), "wall", r)
    add("MP_Taller_Floor", "Taller", BO + "SM_BO_Wood", ue_box((x0 + t, y0 + t, x1 - t, y1 - t), 0.0, 0.02), "floor",
        (x0 + t, y0 + t, x1 - t, y1 - t))
    # dinteles sobre las puertas (lectura de hueco; no bloquean: empiezan a 2,6-3 m)
    for n, r, z in [("Lintel_W", (x0, 44, x0 + t, 46.5), 2.6), ("Lintel_N", (147.8, y1 - t, 150.8, y1), 3.0),
                    ("Lintel_E", (x1 - t, 48, x1, 50.5), 2.6)]:
        add("MP_Taller_" + n, "Taller", BO + "SM_BO_Brick", ue_box(r, z, H - z), "lintel", None)

    # 4. muros del layout dentro del piloto (patio del taller, barricadas de la avenida)
    for wid, r in mp.WALLS:
        if wid.startswith(("WL-PTW", "WL-SAV")):
            h = 2.5 if wid.startswith("WL-SAV") else WALL_H
            add("MP_" + wid, "Walls", BO + "SM_BO_BrickDark", ue_box(r, 0.0, h), "wall", r)

    # 5. cierres automaticos: todo borde de espacio transitable que no linda con edificio, otro espacio, muro o puerta
    covers = [b["rect"] for b in blds] + [w[2] for w in walks] + [r for wid, r in mp.WALLS if wid.startswith(("WL-PTW", "WL-SAV"))]
    covers += [(x0, y0, x1, y1)] + [g[1] for g in mp.GATES if g[0] in ("G-07",)]
    step, off, T = 0.25, 0.1, 0.3
    auto = []
    for wid, kind, r in walks:
        edges = [("S", (r[0], r[1]), (r[2], r[1]), (0, -1)), ("N", (r[0], r[3]), (r[2], r[3]), (0, 1)),
                 ("W", (r[0], r[1]), (r[0], r[3]), (-1, 0)), ("E", (r[2], r[1]), (r[2], r[3]), (1, 0))]
        for side, a, b_, n in edges:
            L = math.hypot(b_[0] - a[0], b_[1] - a[1]); k = int(round(L / step))
            run = None
            for i in range(k + 1):
                s = i * step
                p = (a[0] + (b_[0] - a[0]) * s / L + n[0] * off, a[1] + (b_[1] - a[1]) * s / L + n[1] * off)
                open_ = not any(inside_pt(p, c) for c in covers) and inside_pt(p, PILOT_BOX)
                if open_ and run is None:
                    run = s
                if (not open_ or i == k) and run is not None:
                    e = s if not open_ else s
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
        add(f"MP_Cierre_{i:02d}_{n}", "Walls/Cierres", BO + "SM_BO_BrickDark", ue_box(rr, 0.0, WALL_H), "wall", rr)

    # 6. props del layout aprobado
    for p in mp.PROPS:
        r = p["rect"]; cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        if p["id"].startswith(PROP_IDS_EXCLUDE) or not strictly_in((cx, cy), PILOT_BOX):
            continue
        if not any(inside_pt((cx, cy), w[2]) for w in walks) and not inside_pt((cx, cy), (x0, y0, x1, y1)):
            continue
        k = p["kind"]
        if k == "fuente":
            add("MP_Fountain_Base", "Props", BO + "SM_BO_Kerb", ue_box(r, 0.0, 0.6), "prop", r)
            add("MP_Fountain_Basin", "Props", PR + "SM_Fountain_Square/SM_Fountain_Square", ue_point(cx, cy, 0.6), "prop", None)
        elif k == "puesto":
            add("MP_" + p["id"], "Props/Puestos", BO + "SM_BO_Wood", ue_box(r, 0.0, 2.6), "prop", r)
        elif k == "carro":
            add("MP_" + p["id"], "Props", BO + "SM_BO_Wood", ue_box(r, 0.0, 1.6), "prop", r)
        elif k == "farola":
            add("MP_" + p["id"], "Props/Farolas", "/Game/Unscripted/World/BP_GasLamp", ue_point(cx, cy), "prop", r)
        elif k == "caja":
            add("MP_" + p["id"], "Props/Cobertura", PR + "SM_CrateStack_A/SM_CrateStack_A", ue_point(cx, cy), "prop", r)
        elif k == "barril":
            add("MP_" + p["id"], "Props/Cobertura", PR + "SM_Barrel_A/SM_Barrel_A", ue_point(cx, cy), "prop", r)
        elif k == "mesa":
            add("MP_" + p["id"], "Taller", PR + "SM_WorkshopTable_A/SM_WorkshopTable_A", ue_point(cx, cy, 0.02, 90), "prop", r)
        elif k == "estante":
            add("MP_" + p["id"], "Taller", PR + "SM_Shelf_A/SM_Shelf_A", ue_point(cx, cy, 0.02, 0), "prop", r)
    # porton lateral del taller (G-07, cerrado en Acto I)
    add("MP_Gate_G07", "Props", PR + "SM_IronGate_A/SM_IronGate_A", ue_point(160, 64, 0, 0), "gate", (159.75, 62.5, 160.25, 65.5))

    # 7. navegacion: NO se crea aqui. Un NavMeshBoundsVolume creado por MCP (add_to_scene_from_class) nace sin
    #    geometria de brocha y el NavMesh sale vacio. Se crea desde la consola del editor con la brocha constructora:
    #      BRUSH MOVETO X=4400 Y=22000 Z=200
    #      BRUSH ADDVOLUME CLASS=NavMeshBoundsVolume
    #    y despues se escala a (9200/256, 14800/256, 800/256), se etiqueta MP240_PILOT y se ejecuta RebuildNavigation.
    #    El script MCP de abajo NO borra los volumenes de navegacion etiquetados.

    os.makedirs(mp.OUT, exist_ok=True)
    with open(os.path.join(mp.OUT, "pilot_placements.json"), "w", encoding="utf-8") as f:
        json.dump({"tag": TAG, "offset_cm": [OFFX, OFFY], "pilot_box_m": PILOT_BOX, "count": len(items), "items": items},
                  f, ensure_ascii=False, indent=1)
    data = json.dumps([{k: v for k, v in it.items() if k != "rect"} for it in items], ensure_ascii=False)
    script = MCP_TEMPLATE.replace("__DATA__", data).replace("__TAG__", TAG)
    outdir = sys.argv[1] if len(sys.argv) > 1 else mp.OUT
    with open(os.path.join(outdir, "pilot_mcp_script.py"), "w", encoding="utf-8") as f:
        f.write(script)
    from collections import Counter
    print(len(items), Counter(i["kind"] for i in items), "cierres:", len(auto))

MCP_TEMPLATE = r'''import json
A='editor_toolset.toolsets.actor.ActorTools.'
S='editor_toolset.toolsets.scene.SceneTools.'
DATA=json.loads(r"""__DATA__""")
def t(n,a): return execute_tool(n, json.dumps(a))['returnValue']
def run():
    old=t(S+'find_actors',{'name':'','tag':'__TAG__','collision_channels':[]})
    old=[a for a in old if 'NavMeshBoundsVolume' not in a['refPath']]
    for a in old: t(S+'remove_from_scene',{'actor':a})
    made=0; errs=[]
    for it in DATA:
        try:
            if it['asset'].startswith('CLASS:'):
                a=t(S+'add_to_scene_from_class',{'actor_type':{'refPath':it['asset'][6:]},'name':it['label'],'xform':it['xform']})
            else:
                a=t(S+'add_to_scene_from_asset',{'asset_path':it['asset'],'name':it['label'],'xform':it['xform']})
            t(A+'set_label',{'actor':a,'label':it['label']})
            t(A+'add_tag',{'actor':a,'tag':'__TAG__'})
            t(S+'set_actor_folder',{'actor':a,'folder_path':it['folder']})
            made+=1
        except Exception as e:
            errs.append([it['label'],str(e)[-160:]])
    return {'removed':len(old),'made':made,'errors':errs[:20]}
'''

if __name__ == "__main__":
    main()
