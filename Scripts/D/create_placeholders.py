"""
create_placeholders.py - Division D (Unscripted) - tarea D-01

Crea los placeholders compartidos de docs/plan/01_CONTRATOS_Y_PROPIEDAD.md §8 con su ruta y
nombre DEFINITIVOS, para que A, B y C puedan referenciarlos desde el dia 1. D cambiara despues
su CONTENIDO sin mover ni renombrar los assets.

Uso:
  - Fuera de Unreal:  python Scripts/D/create_placeholders.py   -> imprime la lista (no crea nada).
  - En el editor (requiere "Python Editor Script Plugin"):
        Tools > Execute Python Script... > este archivo.
    Crea solo los que faltan, no toca los existentes y guarda lo creado.
    Cada asset creado lleva el metadato Placeholder=D-01 para auditarlo mas tarde.

Contenido provisional:
  - NS_*  : Niagara System vacio (Spawn System funciona y no muestra nada).
  - SC_*  : Sound Cue vacio (Play Sound funciona y no suena nada).
  - MS_*  : MetaSound Source vacio (requiere el plugin MetaSound, activo por defecto en UE5).
  - M_TemporalFrozen_Overlay : material translucido unlit cian, parametros Tint y Opacity.
  - PP_Retake : material de post-proceso que tine la imagen, parametros Tint e Intensity.
Ningun placeholder contiene texto visible para el jugador.
"""

ROOT = "/Game/Unscripted"
META_KEY = "Placeholder"
META_VALUE = "D-01"

# (carpeta, nombre, tipo) - fuente: 01_CONTRATOS §8
MANIFEST = [
    ("VFX", "NS_TemporalCut", "niagara"),
    ("VFX", "NS_RetakeTrail", "niagara"),
    ("VFX", "NS_ParrySpark", "niagara"),
    ("VFX", "NS_HitImpact", "niagara"),
    ("VFX", "NS_ContinuityGlitch", "niagara"),
    ("VFX", "NS_FinalRegister", "niagara"),
    ("Audio", "SC_StaffHit", "soundcue"),
    ("Audio", "SC_ParrySuccess", "soundcue"),
    ("Audio", "SC_TemporalCut", "soundcue"),
    ("Audio", "SC_Retake", "soundcue"),
    ("Audio", "SC_ChecklistRewrite", "soundcue"),
    ("Audio", "SC_EvidencePickup", "soundcue"),
    ("Audio", "SC_Footstep_Cobble", "soundcue"),
    ("Audio", "MS_Ambience_Whitechapel", "metasound"),
    ("Materials", "M_TemporalFrozen_Overlay", "overlay_material"),
    ("Materials", "PP_Retake", "postprocess_material"),
]

try:
    import unreal
    IN_UNREAL = True
except ImportError:
    IN_UNREAL = False


def asset_path(folder, name):
    return "%s/%s/%s" % (ROOT, folder, name)


# ---------------------------------------------------------------------------
# Creadores (solo Unreal)
# ---------------------------------------------------------------------------

def _factory(class_name):
    cls = getattr(unreal, class_name, None)
    if cls is None:
        return None
    return cls()


def _create(folder, name, asset_class, factory):
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    return tools.create_asset(name, "%s/%s" % (ROOT, folder), asset_class, factory)


def create_niagara(folder, name):
    f = _factory("NiagaraSystemFactoryNew")
    if f is None:
        raise RuntimeError("NiagaraSystemFactoryNew no disponible: activa el plugin Niagara")
    return _create(folder, name, unreal.NiagaraSystem, f)


def create_soundcue(folder, name):
    return _create(folder, name, unreal.SoundCue, unreal.SoundCueFactoryNew())


def create_metasound(folder, name):
    f = _factory("MetaSoundSourceFactory")
    cls = getattr(unreal, "MetaSoundSource", None)
    if f is None or cls is None:
        raise RuntimeError("MetaSoundSourceFactory no disponible: activa el plugin MetaSound")
    return _create(folder, name, cls, f)


def _new_material(folder, name):
    return _create(folder, name, unreal.Material, unreal.MaterialFactoryNew())


def create_overlay_material(folder, name):
    mel = unreal.MaterialEditingLibrary
    mat = _new_material(folder, name)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)

    tint = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(0.0, 0.8, 1.0, 1.0))  # cian de la agencia

    opacity = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 200)
    opacity.set_editor_property("parameter_name", "Opacity")
    opacity.set_editor_property("default_value", 0.35)

    mel.connect_material_property(tint, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    return mat


def create_postprocess_material(folder, name):
    mel = unreal.MaterialEditingLibrary
    mat = _new_material(folder, name)
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)

    scene = mel.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -800, 0)
    scene.set_editor_property("scene_texture_id", unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)

    tint = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -800, 250)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(0.6, 0.95, 1.1, 1.0))

    intensity = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -800, 450)
    intensity.set_editor_property("parameter_name", "Intensity")
    intensity.set_editor_property("default_value", 0.5)

    mult = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -500, 150)
    mel.connect_material_expressions(scene, "Color", mult, "A")
    mel.connect_material_expressions(tint, "", mult, "B")

    lerp = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -250, 50)
    mel.connect_material_expressions(scene, "Color", lerp, "A")
    mel.connect_material_expressions(mult, "", lerp, "B")
    mel.connect_material_expressions(intensity, "", lerp, "Alpha")

    mel.connect_material_property(lerp, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    return mat


CREATORS = {
    "niagara": create_niagara,
    "soundcue": create_soundcue,
    "metasound": create_metasound,
    "overlay_material": create_overlay_material,
    "postprocess_material": create_postprocess_material,
}


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

def run_in_unreal():
    eal = unreal.EditorAssetLibrary
    created, existing, failed = [], [], []
    for folder in sorted({f for f, _, _ in MANIFEST}):
        eal.make_directory("%s/%s" % (ROOT, folder))

    for folder, name, kind in MANIFEST:
        path = asset_path(folder, name)
        if eal.does_asset_exist(path):
            existing.append(path)
            continue
        try:
            asset = CREATORS[kind](folder, name)
            if not asset:
                raise RuntimeError("create_asset devolvio None")
            eal.set_metadata_tag(asset, META_KEY, META_VALUE)
            eal.save_loaded_asset(asset, only_if_is_dirty=False)
            created.append(path)
        except Exception as exc:  # noqa: BLE001 - informar y seguir con el resto
            failed.append((path, str(exc)))

    for p in created:
        unreal.log("[D_Placeholders] Creado: " + p)
    for p in existing:
        unreal.log("[D_Placeholders] Ya existia (sin cambios): " + p)
    for p, err in failed:
        unreal.log_error("[D_Placeholders] FALLO %s: %s" % (p, err))
    unreal.log("[D_Placeholders] Resumen: %d creados, %d ya existian, %d fallos (de %d)" % (
        len(created), len(existing), len(failed), len(MANIFEST)))


def print_manifest():
    print("Placeholders de 01_CONTRATOS §8 (%d):" % len(MANIFEST))
    for folder, name, kind in MANIFEST:
        print("  %-48s %s" % (asset_path(folder, name), kind))
    print("Fuera de Unreal no se crea nada. Ejecuta este script desde el editor (Tools > Execute Python Script).")


if IN_UNREAL:
    run_in_unreal()
elif __name__ == "__main__":
    print_manifest()
