"""
toggle_old_dressing.py - Division D (Unscripted)

Oculta en el editor el vestido anterior de L_Whitechapel_Geo para revisar las casas del plano v3
(carpeta Houses_v3) y deja visible todo lo demas. Solo usa la ocultacion temporal del editor:
no cambia el nivel, no lo marca como modificado y no afecta al juego (en juego ese vestido ya
esta oculto con Actor Hidden In Game).

Uso: Tools > Execute Python Script... > este archivo.
Para volver a ver el vestido anterior, cambiar SHOW_OLD a True y ejecutar de nuevo.
"""

import unreal

SHOW_OLD = False
FOLDERS = ("CityBlocks", "Dressing/Facades", "Blockout/Walls", "Blockout/Partitions")


def in_folders(actor):
    path = str(actor.get_folder_path())
    return any(path == f or path.startswith(f + "/") for f in FOLDERS)


def main():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    hidden = shown = 0
    for a in eas.get_all_level_actors():
        old = in_folders(a)
        want_hidden = old and not SHOW_OLD
        if a.is_temporarily_hidden_in_editor() != want_hidden:
            a.set_is_temporarily_hidden_in_editor(want_hidden)
        if want_hidden:
            hidden += 1
        else:
            shown += 1
    unreal.log("[D_OldDressing] %d ocultos en el editor, %d visibles" % (hidden, shown))


main()
