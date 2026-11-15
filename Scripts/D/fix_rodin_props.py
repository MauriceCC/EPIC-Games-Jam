"""
fix_rodin_props.py - Division D (Unscripted)

Corrige escala y pivote de los props generados con Hyper3D Rodin. Rodin exporta los modelos
normalizados (~1,9 m) con el pivote en el centro; aqui se reimportan desde su FBX original
con escala real y la base en Z = 0 (pivote en el suelo, como pide ART_BIBLE §10).

Uso (dentro del editor; requiere el Python Editor Script Plugin):
    Herramientas > Ejecutar script de Python... > este archivo.

- Reimporta SOLO los 3 assets de /Game/Unscripted/Art/Props/ listados abajo (carpetas de D).
- Conserva el material ya corregido (M_*) y regenera la colision convexa.
- Es idempotente: siempre parte del FBX original, asi que puede ejecutarse varias veces.
"""

import unreal

STAGING = "C:/TRABAJOS/JUEGOS/AI_Staging/Rodin"

# nombre: (escala uniforme, traslacion Z en cm tras escalar, hulls de colision)
# Medidas originales (cm) tomadas por MCP el 2026-11-14:
#   GasLamp  z [-95.03, 94.93]  -> objetivo 3,2 m de alto -> escala 1.685
#   Official z [-79.53, 78.85]  -> escala 0.85 (~1,6 x 1,1 x 1,35 m)
#   Authentic z [-84.20, 83.90] -> escala 0.85 (~1,6 x 1,0 x 1,43 m)
PROPS = {
    "SM_GasLamp_A": (1.685, 95.03 * 1.685, 4),
    "SM_RecordStation_Official": (0.85, 79.53 * 0.85, 6),
    "SM_RecordStation_Authentic": (0.85, 84.20 * 0.85, 6),
    # P1 (2026-11-14): Fountain z [-95, 95] -> 1,3 m; Pillar z [-95, 95] -> 4 m
    "SM_Fountain_Square": (0.684, 95.0 * 0.684, 4),
    "SM_ArchivePillar_A": (2.105, 95.0 * 2.105, 4),
}


def reimport(name, scale, tz, hulls):
    folder = "/Game/Unscripted/Art/Props/" + name
    mesh_path = "%s/%s" % (folder, name)
    base = name[3:]
    material = unreal.load_asset("%s/M_%s" % (folder, base))

    ui = unreal.FbxImportUI()
    ui.import_mesh = True
    ui.import_as_skeletal = False
    ui.import_materials = False
    ui.import_textures = False
    ui.import_animations = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    data = ui.static_mesh_import_data
    data.import_uniform_scale = scale
    data.import_translation = unreal.Vector(0.0, 0.0, tz)
    data.combine_meshes = True
    data.auto_generate_collision = False

    task = unreal.AssetImportTask()
    task.filename = "%s/%s/base_basic_pbr.fbx" % (STAGING, name)
    task.destination_path = folder
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = False
    task.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        unreal.log_error("[D_FixRodin] No se pudo reimportar " + name)
        return False
    if material:
        mesh.set_material(0, material)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    sms.set_convex_decomposition_collisions(mesh, hulls, 16, 100000)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)

    box = mesh.get_bounding_box()
    unreal.log("[D_FixRodin] %s: min=(%.0f, %.0f, %.0f) max=(%.0f, %.0f, %.0f) cm" % (
        name, box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z))
    return True


def main():
    ok = 0
    for name, (scale, tz, hulls) in PROPS.items():
        try:
            if reimport(name, scale, tz, hulls):
                ok += 1
        except Exception as exc:  # noqa: BLE001
            unreal.log_error("[D_FixRodin] FALLO %s: %s" % (name, exc))
    unreal.log("[D_FixRodin] Resumen: %d de %d props corregidos" % (ok, len(PROPS)))


main()
