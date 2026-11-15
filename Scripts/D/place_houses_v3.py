"""
place_houses_v3.py - Division D (Unscripted)

Coloca las casas del plano v3 en L_Whitechapel_Geo a partir de
SourceData/D/plano_v3/colocacion.json y calles.json (los generan
Scripts/D/colocar_casas_v3.py y Scripts/D/vestir_calles_v3.py).

Uso (dentro del editor; requiere el Python Editor Script Plugin):
    Tools > Execute Python Script... > este archivo (con L_Whitechapel abierto; el script hace
    actual L_Whitechapel_Geo por si mismo).

- Se niega a ejecutarse si el nivel actual no es L_Whitechapel_Geo (no toca el persistente).
- Idempotente: borra antes los actores con la etiqueta de cada JSON (D_Houses_v3, D_Streets_v3).
- Carpetas del Outliner: Houses_v3 y Streets_v3. Guarda solo el nivel actual (Geo).
"""

import json
import unreal

PLAN = "C:/TRABAJOS/JUEGOS/EPIC-Games-Jam/SourceData/D/plano_v3/"
LAYOUTS = ("colocacion.json", "calles.json")   # casas; aceras, bordillos y props
EXPECTED = "L_Whitechapel_Geo"


def place(eas, level, path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    tag = data["tag"]
    removed = 0
    for actor in eas.get_all_level_actors():
        if actor.get_level() == level and actor.actor_has_tag(tag):
            eas.destroy_actor(actor)
            removed += 1
    placed = 0
    for a in data["actors"]:
        mesh = unreal.load_asset(a["asset"])
        if not mesh:
            unreal.log_error("[D_HousesV3] Falta la malla " + a["asset"])
            continue
        loc = unreal.Vector(a["location"]["x"], a["location"]["y"], a["location"]["z"])
        rot = unreal.Rotator(roll=a["rotation"]["roll"], pitch=a["rotation"]["pitch"], yaw=a["rotation"]["yaw"])
        actor = eas.spawn_actor_from_object(mesh, loc, rot)
        if not actor:
            continue
        actor.set_actor_scale3d(unreal.Vector(a["scale"]["x"], a["scale"]["y"], a["scale"]["z"]))
        actor.set_actor_label(a["label"])
        actor.tags = [tag]
        actor.set_folder_path(data["folder"])
        if a.get("material"):
            mat = unreal.load_asset(a["material"])
            if mat:
                actor.static_mesh_component.set_material(0, mat)
        placed += 1
    unreal.log("[D_HousesV3] %s: %d actores colocados en %s (%d anteriores borrados)." % (
        tag, placed, data["folder"], removed))


def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.EditorLevelLibrary.get_editor_world()
    streaming = unreal.GameplayStatics.get_streaming_level(world, EXPECTED)
    if streaming:
        unreal.EditorLevelUtils.make_level_current(streaming)
    level = les.get_current_level()
    level_name = level.get_outermost().get_name() if level else ""
    if not level_name.endswith(EXPECTED):
        unreal.log_error("[D_HousesV3] El nivel actual es '%s'. Haz actual %s y repite." % (level_name, EXPECTED))
        return
    for name in LAYOUTS:
        place(eas, level, PLAN + name)
    les.save_current_level()
    unreal.log("[D_HousesV3] %s guardado." % EXPECTED)


main()
