"""
import_audio.py - Division D (Unscripted)

Importa los WAV de C:/TRABAJOS/JUEGOS/AI_Staging/Audio a /Game/Unscripted/Audio/Waves/ y rellena
los Sound Cue de contrato (01_CONTRATOS §8) para que suenen, sin cambiar su nombre ni su ruta.

Uso (en el editor, requiere el Python Editor Script Plugin):
    Herramientas > Ejecutar script de Python... > este archivo.

- Solo toca /Game/Unscripted/Audio/ (carpeta de D).
- Un SC_ solo se rehace si sigue VACIO (placeholder sin nodos); si alguien ya lo edito, se respeta.
- Los pasos usan 3 variaciones (nodo Random). Lluvia y viento quedan en bucle (SC_Rain_Loop, SC_Wind_Loop).
"""

import os
import unreal

SRC = "C:/TRABAJOS/JUEGOS/AI_Staging/Audio"
WAVES = "/Game/Unscripted/Audio/Waves"
AUDIO = "/Game/Unscripted/Audio"

# Sound Cue -> lista de waves (sin extension)
CUES = {
    "SC_StaffHit": ["SW_StaffHit"],
    "SC_ParrySuccess": ["SW_ParrySuccess"],
    "SC_TemporalCut": ["SW_TemporalCut"],
    "SC_Retake": ["SW_Retake"],
    "SC_ChecklistRewrite": ["SW_ChecklistRewrite"],
    "SC_EvidencePickup": ["SW_EvidencePickup"],
    "SC_Footstep_Cobble": ["SW_Footstep_Cobble_01", "SW_Footstep_Cobble_02", "SW_Footstep_Cobble_03"],
    "SC_Rain_Loop": ["SW_Rain_Loop"],
    "SC_Wind_Loop": ["SW_Wind_Loop"],
}
LOOPING = {"SW_Rain_Loop", "SW_Wind_Loop"}

eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()


def import_waves():
    tasks = []
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith(".wav"):
            continue
        name = f[:-4]
        if eal.does_asset_exist("%s/%s" % (WAVES, name)):
            continue
        t = unreal.AssetImportTask()
        t.filename = "%s/%s" % (SRC, f)
        t.destination_path = WAVES
        t.destination_name = name
        t.automated = True
        t.replace_existing = False
        t.save = True
        tasks.append(t)
    if tasks:
        tools.import_asset_tasks(tasks)
    n = 0
    for name in LOOPING:
        w = unreal.load_asset("%s/%s" % (WAVES, name))
        if w:
            w.set_editor_property("looping", True)
            eal.save_loaded_asset(w)
            n += 1
    unreal.log("[D_Audio] Waves importadas: %d nuevas, %d en bucle" % (len(tasks), n))


def cue_is_empty(path):
    cue = unreal.load_asset(path)
    if not cue:
        return True
    try:
        return cue.get_editor_property("first_node") is None
    except Exception:  # noqa: BLE001
        return False


def build_cue(cue_name, wave_names):
    path = "%s/%s" % (AUDIO, cue_name)
    if eal.does_asset_exist(path):
        if not cue_is_empty(path):
            unreal.log("[D_Audio] %s ya tiene contenido, no se toca" % cue_name)
            return False
        eal.delete_asset(path)
    waves = [unreal.load_asset("%s/%s" % (WAVES, w)) for w in wave_names]
    waves = [w for w in waves if w]
    if not waves:
        unreal.log_error("[D_Audio] Sin waves para " + cue_name)
        return False
    f = unreal.SoundCueFactoryNew()
    # UE 5.8: InitialSoundWave esta protegido; se usa el array (varias waves -> nodo Random).
    f.set_editor_property("initial_sound_waves", waves)
    cue = tools.create_asset(cue_name, AUDIO, unreal.SoundCue, f)
    if cue:
        eal.set_metadata_tag(cue, "Placeholder", "D-01 audio (fal ElevenLabs)")
        eal.save_loaded_asset(cue)
        unreal.log("[D_Audio] %s -> %s" % (cue_name, ", ".join(wave_names)))
        return True
    unreal.log_error("[D_Audio] No se pudo crear " + cue_name)
    return False


def main():
    import_waves()
    ok = sum(1 for c, w in CUES.items() if build_cue(c, w))
    unreal.log("[D_Audio] Resumen: %d de %d Sound Cues listos" % (ok, len(CUES)))


main()
