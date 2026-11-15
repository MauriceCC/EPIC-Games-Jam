"""
build_blockout.py - Division D (Unscripted)

Genera el blockout de Whitechapel a partir de SourceData/D/blockout_layout.json.

Dos modos:

1) Fuera de Unreal (vista previa y validacion, no toca ningun asset):
       python Scripts/D/build_blockout.py --preview SourceData/D/blockout_preview.svg
   Valida el layout (zonas, conexiones, conectividad, puntos de B/C) y dibuja un SVG.

2) Dentro del editor de Unreal (requiere el plugin "Python Editor Script Plugin"):
   - Abrir L_Whitechapel y hacer "current" el subnivel L_Whitechapel_Geo (doble clic en Levels).
   - Tools > Execute Python Script... > elegir este archivo.
   El script borra SOLO los actores con la etiqueta D_Blockout del nivel actual y los vuelve
   a crear (suelos, muros, tabiques, verja, coberturas y etiquetas de zona ocultas en juego).
   Todo queda en una transaccion: Ctrl+Z lo deshace.

Convenciones: unidades del JSON en metros; u = eje Y de Unreal, v = eje X de Unreal.
Dueno: Division D. Ver SourceData/D/LEVEL_DESIGN.md.
"""

import json
import os
import sys

try:
    import unreal  # noqa: F401
    IN_UNREAL = True
except ImportError:
    IN_UNREAL = False


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def default_layout_path():
    candidates = []
    if "__file__" in globals():
        here = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(here, "..", "..", "SourceData", "D", "blockout_layout.json"))
    if IN_UNREAL:
        project_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
        candidates.append(os.path.join(project_dir, "..", "SourceData", "D", "blockout_layout.json"))
    for c in candidates:
        if os.path.isfile(c):
            return os.path.normpath(c)
    raise FileNotFoundError("No se encontro blockout_layout.json en: " + ", ".join(candidates))


def load_layout(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Geometria (Python puro, sin Unreal)
# ---------------------------------------------------------------------------

N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def _rasterize_zones(zones, errors):
    """Devuelve {(i, j): zone_id} con celdas de 1 m (esquina inferior izquierda)."""
    cells = {}
    for z in zones:
        u0, u1 = z["u"]
        v0, v1 = z["v"]
        if any(int(x) != x for x in (u0, u1, v0, v1)):
            errors.append("%s: las coordenadas deben ser enteras (rejilla de 1 m)" % z["id"])
            continue
        if u1 <= u0 or v1 <= v0:
            errors.append("%s: rectangulo vacio o invertido" % z["id"])
            continue
        for i in range(int(u0), int(u1)):
            for j in range(int(v0), int(v1)):
                if (i, j) in cells:
                    errors.append("%s se solapa con %s en la celda (%d, %d)" % (z["id"], cells[(i, j)], i, j))
                    return cells
                cells[(i, j)] = z["id"]
    return cells


def _connection_edges(conn):
    """Aristas unitarias que cubre una conexion. Arista = ('u'|'v', linea, inicio)."""
    a, b = conn["range"]
    return [(conn["line"], int(conn["at"]), k) for k in range(int(a), int(b))]


def _greedy_rects(cells):
    """Agrupa un conjunto de celdas en rectangulos (u0, v0, u1, v1)."""
    remaining = set(cells)
    rects = []
    for (i, j) in sorted(cells, key=lambda c: (c[1], c[0])):
        if (i, j) not in remaining:
            continue
        w = 1
        while (i + w, j) in remaining:
            w += 1
        h = 1
        while all((i + k, j + h) in remaining for k in range(w)):
            h += 1
        for k in range(w):
            for m in range(h):
                remaining.discard((i + k, j + m))
        rects.append((i, j, i + w, j + h))
    return rects


def _merge_edges(edges):
    """Une aristas unitarias contiguas de la misma linea: devuelve (line, at, start, end)."""
    by_line = {}
    for line, at, k in edges:
        by_line.setdefault((line, at), []).append(k)
    segments = []
    for (line, at), ks in sorted(by_line.items()):
        ks.sort()
        start = prev = ks[0]
        for k in ks[1:]:
            if k == prev + 1:
                prev = k
                continue
            segments.append((line, at, start, prev + 1))
            start = prev = k
        segments.append((line, at, start, prev + 1))
    return segments


def build_geometry(layout):
    s = layout["settings"]
    errors, warnings, info = [], [], []
    zones = layout["zones"]
    zone_ids = {z["id"] for z in zones}
    cells = _rasterize_zones(zones, errors)
    if errors:
        return {"errors": errors, "warnings": warnings, "info": info}

    # --- Aristas compartidas entre zonas distintas -------------------------
    shared = {}  # edge -> (zone_a, zone_b)
    for (i, j), zid in cells.items():
        east = cells.get((i + 1, j))
        if east and east != zid:
            shared[("u", i + 1, j)] = (zid, east)
        north = cells.get((i, j + 1))
        if north and north != zid:
            shared[("v", j + 1, i)] = (zid, north)

    # --- Conexiones -------------------------------------------------------
    edge_type = {}
    for c in layout["connections"]:
        if c["type"] not in ("open", "door", "gate_closed"):
            errors.append("%s: tipo desconocido %s" % (c["id"], c["type"]))
            continue
        for e in _connection_edges(c):
            if e not in shared:
                errors.append("%s: el tramo %s no esta en un borde compartido entre dos zonas" % (c["id"], e))
                break
            if e in edge_type:
                errors.append("%s se solapa con otra conexion en %s" % (c["id"], e))
                break
            edge_type[e] = (c["type"], c["id"])

    partition_edges = [e for e in shared if e not in edge_type]
    gate_edges = [e for e, (t, _) in edge_type.items() if t == "gate_closed"]

    # --- Anillo de muros exteriores ---------------------------------------
    if cells:
        min_i = min(c[0] for c in cells) - 1
        max_i = max(c[0] for c in cells) + 1
        min_j = min(c[1] for c in cells) - 1
        max_j = max(c[1] for c in cells) + 1
    low, high = set(), set()
    for i in range(min_i, max_i + 1):
        for j in range(min_j, max_j + 1):
            if (i, j) in cells:
                continue
            if not any((i + di, j + dj) in cells for di, dj in N8):
                continue
            # Lado de camara (la celda esta al sur/oeste de suelo jugable) -> muro bajo.
            if any((i + di, j + dj) in cells for di, dj in ((0, 1), (1, 0), (1, 1))):
                low.add((i, j))
            else:
                high.add((i, j))

    # --- Conectividad -----------------------------------------------------
    def reachable(allowed_types):
        start_zone = "Z_Start" if "Z_Start" in zone_ids else zones[0]["id"]
        seeds = [c for c, z in cells.items() if z == start_zone]
        seen = set(seeds)
        stack = list(seeds)
        while stack:
            i, j = stack.pop()
            for di, dj in N4:
                n = (i + di, j + dj)
                if n not in cells or n in seen:
                    continue
                if cells[n] != cells[(i, j)]:
                    if di:
                        e = ("u", max(i, n[0]), j)
                    else:
                        e = ("v", max(j, n[1]), i)
                    t = edge_type.get(e)
                    if not t or t[0] not in allowed_types:
                        continue
                seen.add(n)
                stack.append(n)
        return {cells[c] for c in seen}

    all_reach = reachable(("open", "door"))
    unreached = sorted(zone_ids - all_reach)
    if unreached:
        errors.append("Zonas inalcanzables desde Z_Start con todas las puertas abiertas: " + ", ".join(unreached))
    info.append("Accesible sin abrir puertas de C: " + ", ".join(sorted(reachable(("open",)))))

    # --- Coberturas -------------------------------------------------------
    cover = []
    for c in layout["cover"]:
        cu, cv = c["center"]
        su, sv, h = c["size"]
        r = (cu - su / 2.0, cv - sv / 2.0, cu + su / 2.0, cv + sv / 2.0)
        owners = {cells.get((int(x), int(y))) for x in _frange(r[0], r[2]) for y in _frange(r[1], r[3])}
        if None in owners or len(owners) != 1:
            warnings.append("%s no cae por completo dentro de una sola zona" % c["id"])
        for conn in layout["connections"]:
            if conn["type"] == "gate_closed":
                continue
            if _rect_hits_connection(r, conn, margin=0.5):
                warnings.append("%s esta a menos de 0,5 m de la conexion %s" % (c["id"], conn["id"]))
        cover.append({"id": c["id"], "rect": r, "h": h, "kind": c.get("kind", "high")})

    # --- Puntos de B/C ----------------------------------------------------
    points = {k: v for k, v in layout.get("check_points", {}).items() if not k.startswith("_")}
    for name, (pu, pv) in points.items():
        if (int(pu), int(pv)) not in cells:
            errors.append("Punto %s (%s, %s) fuera del suelo jugable" % (name, pu, pv))
            continue
        for c in cover:
            x0, y0, x1, y1 = c["rect"]
            if x0 - 0.5 <= pu <= x1 + 0.5 and y0 - 0.5 <= pv <= y1 + 0.5:
                warnings.append("Punto %s choca con la cobertura %s" % (name, c["id"]))

    # --- NavMeshBoundsVolume sugerido ------------------------------------
    zu0 = min(z["u"][0] for z in zones) - 1
    zu1 = max(z["u"][1] for z in zones) + 1
    zv0 = min(z["v"][0] for z in zones) - 1
    zv1 = max(z["v"][1] for z in zones) + 1
    nav = {"center_uv": ((zu0 + zu1) / 2.0, (zv0 + zv1) / 2.0), "size_uv": (zu1 - zu0, zv1 - zv0), "height": 10.0}

    return {
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "zones": zones,
        "cells": cells,
        "floors": [(z["id"], z["u"][0], z["v"][0], z["u"][1], z["v"][1]) for z in zones],
        "walls_low": _greedy_rects(low),
        "walls_high": _greedy_rects(high),
        "partitions": _merge_edges(partition_edges),
        "gates": _merge_edges(gate_edges),
        "doors": [c for c in layout["connections"] if c["type"] == "door"],
        "cover": cover,
        "points": points,
        "nav": nav,
        "settings": s,
    }


def _frange(a, b, step=0.5):
    x = a + step / 2.0
    out = []
    while x < b:
        out.append(x)
        x += step
    return out


def _rect_hits_connection(r, conn, margin):
    a, b = conn["range"]
    at = conn["at"]
    if conn["line"] == "u":
        seg = (at - margin, a - margin, at + margin, b + margin)
    else:
        seg = (a - margin, at - margin, b + margin, at + margin)
    return not (r[2] <= seg[0] or r[0] >= seg[2] or r[3] <= seg[1] or r[1] >= seg[3])


def report(geo):
    for line in geo["info"]:
        print("[INFO] " + line)
    for line in geo["warnings"]:
        print("[AVISO] " + line)
    for line in geo["errors"]:
        print("[ERROR] " + line)
    if not geo["errors"]:
        n = len(geo["floors"]) + len(geo["walls_low"]) + len(geo["walls_high"]) + \
            len(geo["partitions"]) + len(geo["gates"]) + len(geo["cover"])
        print("[INFO] Piezas a generar: %d suelos, %d muros bajos, %d muros altos, %d tabiques, %d verjas, %d coberturas (total %d)" % (
            len(geo["floors"]), len(geo["walls_low"]), len(geo["walls_high"]),
            len(geo["partitions"]), len(geo["gates"]), len(geo["cover"]), n))
        nav = geo["nav"]
        cu, cv = nav["center_uv"]
        su, sv = nav["size_uv"]
        print("[INFO] NavMeshBoundsVolume sugerido (persistente): Location X=%d Y=%d Z=0 cm; Brush X=%d Y=%d Z=%d cm" % (
            cv * 100, cu * 100, sv * 100, su * 100, nav["height"] * 100))


# ---------------------------------------------------------------------------
# Vista previa SVG
# ---------------------------------------------------------------------------

def write_svg(geo, path, px_per_m=14):
    s = geo["settings"]
    pad = 2
    cells = geo["cells"]
    max_u = max(c[0] for c in cells) + 1 + pad
    max_v = max(c[1] for c in cells) + 1 + pad
    min_u = min(c[0] for c in cells) - pad
    min_v = min(c[1] for c in cells) - pad
    W = (max_u - min_u) * px_per_m
    H = (max_v - min_v) * px_per_m
    legend_h = 120

    def X(u):
        return (u - min_u) * px_per_m

    def Y(v):
        return (max_v - v) * px_per_m  # norte arriba

    def rect(u0, v0, u1, v1, fill, stroke="none", sw=0, extra=""):
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="%s" %s/>' % (
            X(u0), Y(v1), (u1 - u0) * px_per_m, (v1 - v0) * px_per_m, fill, stroke, sw, extra)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, Arial, sans-serif">' % (W, H + legend_h),
           '<rect width="100%" height="100%" fill="#1b1d22"/>']
    # rejilla de 2 m
    for u in range(min_u, max_u + 1, 2):
        out.append('<line x1="%.1f" y1="0" x2="%.1f" y2="%.1f" stroke="#262a31" stroke-width="1"/>' % (X(u), X(u), H))
    for v in range(min_v, max_v + 1, 2):
        out.append('<line x1="0" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#262a31" stroke-width="1"/>' % (Y(v), W, Y(v)))
    for _, u0, v0, u1, v1 in geo["floors"]:
        out.append(rect(u0, v0, u1, v1, "#c9c3b4"))
    for (u0, v0, u1, v1) in geo["walls_high"]:
        out.append(rect(u0, v0, u1, v1, "#4a4f5a"))
    for (u0, v0, u1, v1) in geo["walls_low"]:
        out.append(rect(u0, v0, u1, v1, "#8a909c"))
    t = s["partition_thickness_m"]
    for line, at, a, b in geo["partitions"]:
        if line == "u":
            out.append(rect(at - t / 2, a, at + t / 2, b, "#6b707b"))
        else:
            out.append(rect(a, at - t / 2, b, at + t / 2, "#6b707b"))
    for line, at, a, b in geo["gates"]:
        if line == "u":
            out.append(rect(at - t / 2, a, at + t / 2, b, "#b3462f"))
        else:
            out.append(rect(a, at - t / 2, b, at + t / 2, "#b3462f"))
    for d in geo["doors"]:
        a, b = d["range"]
        at = d["at"]
        if d["line"] == "u":
            out.append(rect(at - 0.35, a, at + 0.35, b, "#2f8fd8"))
        else:
            out.append(rect(a, at - 0.35, b, at + 0.35, "#2f8fd8"))
    colors = {"high": "#5b4a3a", "medium": "#7d6650", "low": "#a8916f"}
    for c in geo["cover"]:
        x0, y0, x1, y1 = c["rect"]
        out.append(rect(x0, y0, x1, y1, colors.get(c["kind"], "#5b4a3a"), "#2a2118", 1))
    for z in geo["zones"]:
        cu = (z["u"][0] + z["u"][1]) / 2.0
        cv = (z["v"][0] + z["v"][1]) / 2.0
        out.append('<text x="%.1f" y="%.1f" font-size="12" fill="#3a3a3a" text-anchor="middle" font-weight="600">%s</text>' % (
            X(cu), Y(cv) - 4, z["name"]))
        out.append('<text x="%.1f" y="%.1f" font-size="10" fill="#555" text-anchor="middle">%dx%d m</text>' % (
            X(cu), Y(cv) + 9, z["u"][1] - z["u"][0], z["v"][1] - z["v"][0]))
    for name, (pu, pv) in geo["points"].items():
        col = "#7a2fb3" if name.startswith("Jack") else ("#1f7a3a" if name.startswith(("CP", "PlayerStart")) else "#b36b00")
        out.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (X(pu), Y(pv), col))
        out.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s">%s</text>' % (X(pu) + 5, Y(pv) - 4, col, name))
    # flecha de camara (suroeste mirando al noreste)
    out.append('<text x="8" y="%d" font-size="11" fill="#ddd">N &#8593; (v = X de Unreal) · E &#8594; (u = Y de Unreal) · rejilla 2 m</text>' % (H + 18))
    legend = [("#c9c3b4", "Suelo jugable"), ("#8a909c", "Muro bajo 3 m (lado camara)"), ("#4a4f5a", "Muro alto 9 m"),
              ("#6b707b", "Tabique 4 m"), ("#b3462f", "Verja cerrada"), ("#2f8fd8", "Hueco para puerta de C"),
              ("#5b4a3a", "Cobertura alta"), ("#a8916f", "Cobertura baja")]
    for k, (col, label) in enumerate(legend):
        x = 8 + (k % 4) * (W / 4.0)
        y = H + 38 + (k // 4) * 22
        out.append('<rect x="%.1f" y="%d" width="14" height="14" fill="%s"/>' % (x, y - 11, col))
        out.append('<text x="%.1f" y="%d" font-size="11" fill="#ddd">%s</text>' % (x + 20, y, label))
    out.append('<text x="8" y="%d" font-size="11" fill="#ddd">Puntos: verde = PlayerStart/checkpoints · morado = waypoints de Jack · naranja = otros (sugerencias para B y C)</text>' % (H + 100))
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("[INFO] Vista previa escrita en " + os.path.abspath(path))


# ---------------------------------------------------------------------------
# Unreal
# ---------------------------------------------------------------------------

def spawn_in_unreal(geo):
    s = geo["settings"]
    cm = float(s["unit_cm"])
    tag = s["actor_tag"]
    folder = s["outliner_folder"]

    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = les.get_current_level()
    level_path = level.get_path_name()
    if s.get("expected_level_name") and s["expected_level_name"] not in level_path:
        unreal.log_error("[D_Blockout] El nivel actual es %s. Haz 'current' %s en la ventana Levels y vuelve a ejecutar." % (
            level_path, s["expected_level_name"]))
        return

    mesh = unreal.load_asset(s["mesh"])
    if not mesh:
        unreal.log_error("[D_Blockout] No se pudo cargar la malla " + s["mesh"])
        return
    mats = {}
    fallback = unreal.load_asset(s["materials"]["fallback"])
    for key, p in s["materials"].items():
        m = unreal.load_asset(p) if key != "fallback" else fallback
        if not m:
            unreal.log_warning("[D_Blockout] Material no encontrado (%s), uso el de respaldo" % p)
            m = fallback
        mats[key] = m

    def box(label, sub, u0, v0, u1, v1, z0, z1, mat_key):
        loc = unreal.Vector((v0 + v1) / 2.0 * cm, (u0 + u1) / 2.0 * cm, (z0 + z1) / 2.0 * cm)
        actor = eas.spawn_actor_from_object(mesh, loc, unreal.Rotator(0, 0, 0))
        if not actor:
            unreal.log_error("[D_Blockout] No se pudo crear " + label)
            return
        # Cubo base de 100 cm: escala = tamano en metros. X = v, Y = u.
        actor.set_actor_scale3d(unreal.Vector(v1 - v0, u1 - u0, z1 - z0))
        actor.set_actor_label(label)
        actor.set_folder_path(folder + "/" + sub)
        actor.set_editor_property("tags", [unreal.Name(tag)])
        smc = actor.static_mesh_component
        smc.set_mobility(unreal.ComponentMobility.STATIC)
        smc.set_material(0, mats[mat_key])

    # Borrar la generacion anterior de este mismo nivel.
    old = [a for a in eas.get_all_level_actors()
           if a.actor_has_tag(tag) and a.get_path_name().startswith(level_path + ".")]

    ft = s["floor_thickness_m"]
    tt = s["partition_thickness_m"]
    total = len(geo["floors"]) + len(geo["walls_low"]) + len(geo["walls_high"]) + \
        len(geo["partitions"]) + len(geo["gates"]) + len(geo["cover"]) + len(geo["zones"])

    with unreal.ScopedEditorTransaction("D Build Blockout"):
        if old:
            eas.destroy_actors(old)
        with unreal.ScopedSlowTask(total, "Generando blockout") as task:
            task.make_dialog(True)
            for zid, u0, v0, u1, v1 in geo["floors"]:
                task.enter_progress_frame(1)
                box("BO_Floor_" + zid, "Floors", u0, v0, u1, v1, -ft, 0, "floor")
            for k, (u0, v0, u1, v1) in enumerate(geo["walls_low"]):
                task.enter_progress_frame(1)
                box("BO_WallLow_%02d" % k, "Walls", u0, v0, u1, v1, 0, s["wall_low_height_m"], "wall_low")
            for k, (u0, v0, u1, v1) in enumerate(geo["walls_high"]):
                task.enter_progress_frame(1)
                box("BO_WallHigh_%02d" % k, "Walls", u0, v0, u1, v1, 0, s["wall_high_height_m"], "wall_high")
            for k, (line, at, a, b) in enumerate(geo["partitions"]):
                task.enter_progress_frame(1)
                if line == "u":
                    box("BO_Partition_%02d" % k, "Partitions", at - tt / 2, a, at + tt / 2, b, 0, s["partition_height_m"], "partition")
                else:
                    box("BO_Partition_%02d" % k, "Partitions", a, at - tt / 2, b, at + tt / 2, 0, s["partition_height_m"], "partition")
            for k, (line, at, a, b) in enumerate(geo["gates"]):
                task.enter_progress_frame(1)
                if line == "u":
                    box("BO_GateClosed_%02d" % k, "Partitions", at - tt / 2, a, at + tt / 2, b, 0, s["wall_low_height_m"], "gate")
                else:
                    box("BO_GateClosed_%02d" % k, "Partitions", a, at - tt / 2, b, at + tt / 2, 0, s["wall_low_height_m"], "gate")
            for c in geo["cover"]:
                task.enter_progress_frame(1)
                x0, y0, x1, y1 = c["rect"]
                box("BO_" + c["id"], "Cover", x0, y0, x1, y1, 0, c["h"], "cover")
            if s.get("zone_labels", True):
                for z in geo["zones"]:
                    task.enter_progress_frame(1)
                    cu = (z["u"][0] + z["u"][1]) / 2.0
                    cv = (z["v"][0] + z["v"][1]) / 2.0
                    loc = unreal.Vector(cv * cm, cu * cm, 20.0)
                    actor = eas.spawn_actor_from_class(unreal.TextRenderActor, loc, unreal.Rotator(90, 0, 0))
                    if not actor:
                        continue
                    trc = actor.text_render
                    trc.set_text(unreal.Text(z["name"]))  # Solo editor: oculto en juego.
                    trc.set_editor_property("world_size", 120.0)
                    trc.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
                    actor.set_actor_hidden_in_game(True)
                    actor.set_actor_label("BO_Label_" + z["id"])
                    actor.set_folder_path(folder + "/Labels")
                    actor.set_editor_property("tags", [unreal.Name(tag)])

    unreal.log("[D_Blockout] Listo: %d actores antiguos borrados, %d piezas generadas en %s" % (len(old), total, level_path))
    unreal.log("[D_Blockout] Guarda L_Whitechapel_Geo (Ctrl+S con el subnivel como current). No guardes subniveles ajenos.")


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

def main(argv):
    layout_path = None
    preview = None
    k = 0
    while k < len(argv):
        if argv[k] == "--preview" and k + 1 < len(argv):
            preview = argv[k + 1]
            k += 2
            continue
        layout_path = argv[k]
        k += 1
    layout = load_layout(layout_path or default_layout_path())
    geo = build_geometry(layout)
    report(geo)
    if geo["errors"]:
        print("[ERROR] Layout no valido: no se genera nada.")
        return 1
    if preview:
        write_svg(geo, preview)
    if IN_UNREAL:
        spawn_in_unreal(geo)
    elif not preview:
        print("[INFO] Fuera de Unreal: solo validacion. Usa --preview archivo.svg para ver el plano.")
    return 0


if __name__ == "__main__":
    rc = main(sys.argv[1:] if not IN_UNREAL else [])
    if not IN_UNREAL:
        sys.exit(rc)
