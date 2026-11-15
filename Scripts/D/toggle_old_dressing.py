"""
toggle_old_dressing.py - Division D (Unscripted)

Oculta / muestra en el editor el vestido anterior de L_Whitechapel_Geo para revisar las casas
del plano v3 (carpeta Houses_v3) sin el resto delante. Solo usa la ocultacion temporal del
editor: no cambia el nivel, no lo marca como modificado y no afecta al juego.

Uso: Tools > Execute Python Script... > este archivo. Cada ejecucion alterna oculto/visible.
"""

import unreal

FOLDERS = ("CityBlocks", "Dressing/Facades", "Blockout/Walls", "Blockout/Partitions")


def in_folders(actor):
    path = str(actor.get_folder_path())
    return any(path == f or path.startswith(f + "/") for f in FOLDERS)


def main():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = [a for a in eas.get_all_level_actors() if in_folders(a)]
    if not actors:
        unreal.log_warning("[D_OldDressing] No hay actores en " + ", ".join(FOLDERS))
        return
    hide = not actors[0].is_temporarily_hidden_in_editor()
    for a in actors:
        a.set_is_temporarily_hidden_in_editor(hide)
    unreal.log("[D_OldDressing] %d actores %s" % (len(actors), "ocultos" if hide else "visibles"))


main()
