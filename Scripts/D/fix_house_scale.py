"""
fix_house_scale.py - Division D (Unscripted)

Reimporta las 6 casas del plano v3 (SourceData/D/plano_v3/modelos) con escala real y la base en
Z = 0. Meshy las exporta normalizadas a ~1 m con el pivote en el centro; la importacion por MCP
no admite escala, por eso se hace aqui.

Uso (dentro del editor; requiere el Python Editor Script Plugin):
    Tools > Execute Python Script... > este archivo.

- Solo toca /Game/Unscripted/Art/Buildings/SM_House_*/ (carpetas de D).
- Conserva MI_House_* (hijas de /Game/Unscripted/Materials/M_House_Master) y pone colision de caja.
- Idempotente: siempre parte del FBX original.
"""

import unreal

SRC = "C:/TRABAJOS/JUEGOS/EPIC-Games-Jam/SourceData/D/plano_v3/modelos"
DST = "/Game/Unscripted/Art/Buildings"

# nombre: (escala uniforme, -Zmin en cm del FBX normalizado)
# Bounds medidos por MCP el 2026-11-15. Alturas objetivo (con tejado):
#   Brick 12 m (3P + buhardilla), Shop 10 m (2P), Corner 6 m (1P), Workshop 11 m (2P alta),
#   Agency 16 m (4P), Filler 12,5 m (3P).
HOUSES = {
    "Brick": (12.0, 50.0),
    "Shop": (10.0, 50.0),
    "Corner": (8.36, 36.16),
    "Workshop": (9.1, 60.37),
    "Agency": (17.45, 46.33),
    "Filler": (13.48, 46.64),
    # Tienda baja de 1 planta para el lado de cámara: 4,5 m (6,7 x 5,8 m de planta).
    "ShopLow": (3.505, 64.32),
}


def reimport(house, scale, zmin):
    name = "SM_House_" + house
    folder = "%s/%s" % (DST, name)
    material = unreal.load_asset("%s/MI_House_%s" % (folder, house))

    ui = unreal.FbxImportUI()
    ui.import_mesh = True
    ui.import_as_skeletal = False
    ui.import_materials = False
    ui.import_textures = False
    ui.import_animations = False
    ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    data = ui.static_mesh_import_data
    data.import_uniform_scale = scale
    data.import_translation = unreal.Vector(0.0, 0.0, zmin * scale)
    data.combine_meshes = True
    data.auto_generate_collision = False

    task = unreal.AssetImportTask()
    task.filename = "%s/house_%s/%s.fbx" % (SRC, house.lower(), name)
    task.destination_path = folder
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = False
    task.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    mesh = unreal.load_asset("%s/%s" % (folder, name))
    if not mesh:
        unreal.log_error("[D_Houses] No se pudo reimportar " + name)
        return False
    if material:
        mesh.set_material(0, material)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    sms.remove_collisions(mesh)
    sms.add_simple_collisions(mesh, unreal.ScriptCollisionShapeType.BOX)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)

    box = mesh.get_bounding_box()
    unreal.log("[D_Houses] %s: %.1f x %.1f x %.1f m (zmin %.0f cm)" % (
        name, (box.max.x - box.min.x) / 100, (box.max.y - box.min.y) / 100,
        (box.max.z - box.min.z) / 100, box.min.z))
    return True


def main():
    ok = 0
    for house, (scale, zmin) in HOUSES.items():
        try:
            if reimport(house, scale, zmin):
                ok += 1
        except Exception as exc:  # noqa: BLE001
            unreal.log_error("[D_Houses] FALLO %s: %s" % (house, exc))
    unreal.log("[D_Houses] Resumen: %d de %d casas a escala real" % (ok, len(HOUSES)))


main()
