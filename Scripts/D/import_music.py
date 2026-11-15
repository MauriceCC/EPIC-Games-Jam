"""
import_music.py - Division D (Unscripted)

Importa la musica de Mauricio (SourceData/D/Audio/Music, convertida a WAV en
C:/TRABAJOS/JUEGOS/AI_Staging/Audio/Music) a /Game/Unscripted/Audio/Music/ como
SoundWave en bucle:
    SW_Music_Exploration, SW_Music_Combat, SW_Music_CombatAlt, SW_Music_Decision

Uso (en el editor, requiere el Python Editor Script Plugin):
    Tools > Execute Python Script... > este archivo.

- Solo toca /Game/Unscripted/Audio/Music/ (carpeta de D). No sobrescribe lo ya importado.
- Despues, D coloca la musica de exploracion en L_Whitechapel_Light.
"""

import os
import unreal

SRC = "C:/TRABAJOS/JUEGOS/AI_Staging/Audio/Music"
DEST = "/Game/Unscripted/Audio/Music"

eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()


def main():
    tasks = []
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith(".wav"):
            continue
        name = f[:-4]
        if eal.does_asset_exist("%s/%s" % (DEST, name)):
            continue
        t = unreal.AssetImportTask()
        t.filename = "%s/%s" % (SRC, f)
        t.destination_path = DEST
        t.destination_name = name
        t.automated = True
        t.replace_existing = False
        t.save = True
        tasks.append(t)
    if tasks:
        tools.import_asset_tasks(tasks)
    done = []
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith(".wav"):
            continue
        w = unreal.load_asset("%s/%s" % (DEST, f[:-4]))
        if w:
            w.set_editor_property("looping", True)
            eal.save_loaded_asset(w, only_if_is_dirty=False)
            done.append(f[:-4])
    unreal.log("[D_Music] Importadas en bucle: %s" % ", ".join(done))


main()
