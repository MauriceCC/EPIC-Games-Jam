"""Reparto de NPC para L_Test_D (División D) — [PROPUESTA].

Genera SourceData/D/masterplan_240/population_placements.json con:
  - civiles de ambiente (BP_AmbientCivilian, nuevo, de D) por zona de la historia;
  - enemigos y Jack (Blueprints de B, solo instancias) en los puntos de cada acto.

Solo Python estándar. Coordenadas del masterplan (m, x = este, y = norte) y su
conversión a UE con la fórmula del layout: UE_X = 100*y ; UE_Y = 12000 + 100*x.
Los puntos se proyectan al NavMesh al colocarlos en el editor; aquí solo se
evitan las zonas que deben quedar libres (arenas, frentes de interacción).

Uso:  python Scripts/D/population_layout.py
"""
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / "SourceData/D/masterplan_240/whitechapel_layout.json"
OUT = ROOT / "SourceData/D/masterplan_240/population_placements.json"

OFF_X, OFF_Y = 0.0, 12000.0
SEED = 1888

CIV_BP = "/Game/Unscripted/World/NPC/BP_AmbientCivilian.BP_AmbientCivilian_C"
B_BP = {
    "Pursuer": "/Game/Unscripted/Enemies/BP_Pursuer.BP_Pursuer_C",
    "Interventor": "/Game/Unscripted/Enemies/BP_Interventor.BP_Interventor_C",
    "Supervisor": "/Game/Unscripted/Enemies/BP_Supervisor.BP_Supervisor_C",
    "PatrolRoute": "/Game/Unscripted/Enemies/BP_PatrolRoute.BP_PatrolRoute_C",
    "Jack": "/Game/Unscripted/Enemies/Jack/BP_Jack.BP_Jack_C",
}

# Modelos de civil disponibles (Meshy, con Idle/Walk/Run).
LOOKS = {
    "nurse": "SK_Nurse",
    "flower": "SK_FlowerSeller",
    "vagrant": "SK_Vagrant",
    "local_a": "SK_Pursuer_A",  # mismo aspecto que un vecino; sin IA de combate
    "local_b": "SK_Pursuer_B",
}

# (zona, rectángulo del masterplan [x0, y0, x1, y1], lista de (rol, aspecto, cantidad))
# rol: wander = pasea entre puntos de su rect; idle = quieto; flee = idle que huye si hay pelea.
CIVILIANS = [
    ("Z01 Llegada", [99, 2, 109, 24], [("idle", "vagrant", 1), ("wander", "local_a", 2), ("wander", "local_b", 1)]),
    ("Z02 Mercado (borde)", [41, 24, 109, 72], [("idle", "flower", 3), ("wander", "local_a", 4), ("wander", "local_b", 3), ("flee", "nurse", 1)]),
    ("Z02 Fuente (corrillo)", [70, 43, 80, 53], [("flee", "local_a", 2), ("flee", "local_b", 1)]),
    ("Z04 Calle al taller", [109, 44, 140, 52], [("flee", "local_b", 1)]),
    ("Z05 Calle taller-escape", [160, 60, 179, 67], [("flee", "local_a", 1), ("flee", "vagrant", 1)]),
    ("Z06 Escape tramo 2", [176, 113, 183, 139], [("flee", "local_b", 1)]),
    ("Z09 Refugio", [202, 145.5, 222, 162.5], [("idle", "nurse", 1)]),
    ("Z10 Enfermería", [213, 133, 224, 142], [("idle", "nurse", 1), ("idle", "vagrant", 1)]),
    ("Z12 Paso central", [112, 112, 176, 118], [("wander", "local_a", 2), ("flee", "local_b", 2)]),
    ("Z17 Fondo oeste", [23, 14, 29, 100], [("idle", "local_a", 3), ("idle", "local_b", 2), ("idle", "vagrant", 1)]),
]

# Encuentros por acto (docs/05 + rutas R-MAIN). Puntos en metros del masterplan.
ENCOUNTERS = [
    {"act": "I", "zone": "Z03 Plaza — primera pelea", "bp": "Pursuer", "points": [[92, 46], [98, 50]]},
    {"act": "I", "zone": "Z04 Calle al taller — patrulla (sigilo opcional)", "bp": "Pursuer",
     "points": [[112, 48]], "patrol": [[112, 48], [138, 48], [138, 50], [112, 50]]},
    {"act": "I", "zone": "Z04 Taller — Jack", "bp": "Jack", "points": [[150, 52]]},
    {"act": "II", "zone": "Z06 Ensanche de escape — grupo", "bp": "Pursuer", "points": [[170, 96], [176, 101], [180, 95]]},
    {"act": "II", "zone": "Z07 Ruta central — patrulla alternativa", "bp": "Pursuer",
     "points": [[115, 115]], "patrol": [[115, 115], [172, 115]]},
    {"act": "II", "zone": "Z08 Tránsito al refugio — Interventor", "bp": "Interventor", "points": [[195, 142]]},
    {"act": "III", "zone": "Z13 Antepatio — Supervisor (jefe)", "bp": "Supervisor", "points": [[94, 124]]},
]

MIN_SPACING_M = 2.2


def to_ue(x, y, z=0.0):
    return {"x": round(OFF_X + 100 * y, 1), "y": round(OFF_Y + 100 * x, 1), "z": z}


def inside(p, r, margin=0.0):
    return r[0] - margin <= p[0] <= r[2] + margin and r[1] - margin <= p[1] <= r[3] + margin


def main():
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    keep_clear = [c["rect"] for c in layout["mustStayClear"]]
    rng = random.Random(SEED)
    taken = []
    civ = []

    def free(p):
        if any(inside(p, r, 0.8) for r in keep_clear):
            return False
        return all(math.dist(p, q) >= MIN_SPACING_M for q in taken)

    for zone, rect, groups in CIVILIANS:
        for role, look, n in groups:
            for _ in range(n):
                for _try in range(400):
                    p = [rng.uniform(rect[0] + 1, rect[2] - 1), rng.uniform(rect[1] + 1, rect[3] - 1)]
                    if free(p):
                        break
                else:
                    print(f"AVISO: sin hueco en {zone} para {role}/{look}")
                    continue
                taken.append(p)
                item = {
                    "zone": zone, "role": role, "look": LOOKS[look], "bp": CIV_BP,
                    "xy_m": [round(p[0], 2), round(p[1], 2)],
                    "location": to_ue(*p), "yaw": rng.choice([0, 45, 90, 135, 180, 225, 270, 315]),
                }
                if role == "wander":
                    pts = []
                    for _w in range(3):
                        for _t in range(200):
                            q = [rng.uniform(rect[0] + 1, rect[2] - 1), rng.uniform(rect[1] + 1, rect[3] - 1)]
                            if not any(inside(q, r, 0.8) for r in keep_clear) and math.dist(q, p) > 4:
                                pts.append(to_ue(*q))
                                break
                    item["wander_points"] = pts
                civ.append(item)

    enemies = []
    for e in ENCOUNTERS:
        for i, p in enumerate(e["points"]):
            item = {"act": e["act"], "zone": e["zone"], "type": e["bp"], "bp": B_BP[e["bp"]],
                    "xy_m": p, "location": to_ue(*p)}
            if e.get("patrol") and i == 0:
                item["patrol_route"] = {"bp": B_BP["PatrolRoute"], "points": [to_ue(*q) for q in e["patrol"]]}
            enemies.append(item)

    out = {
        "meta": {
            "version": "population v1 [PROPUESTA]",
            "map": "/Game/Unscripted/Maps/Test/L_Test_D",
            "folder_civilians": "MP240_POP/Civiles",
            "folder_enemies": "MP240_POP/Enemigos",
            "tag": "MP240_POP",
            "transform": "UE_X = 100*y ; UE_Y = 12000 + 100*x (m -> cm); z se proyecta al NavMesh",
            "counts": {"civilians": len(civ), "enemies_and_jack": len(enemies)},
        },
        "civilians": civ,
        "enemies": enemies,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(civ)} civiles, {len(enemies)} enemigos/Jack -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
