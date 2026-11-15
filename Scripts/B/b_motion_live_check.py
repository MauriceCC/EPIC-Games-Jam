import unreal as u
w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
print('WORLD', w)
if w:
    p = u.GameplayStatics.get_player_character(w, 0)
    if p:
        m = p.get_editor_property('mesh')
        a = m.get_anim_instance()
        print('LIVE', p.get_velocity(), m.get_position(), m.is_playing(), a.get_animation_asset())
        for c in p.get_components_by_class(u.ActorComponent):
            print('COMP', c.get_name(), c.get_class().get_name(), c.is_component_tick_enabled())
lib = u.BlueprintEditorLibrary
bp = u.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
g = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
for n in g.list_all_nodes():
    if isinstance(n, u.K2Node_CustomEvent):
        print('EVENT', lib.get_node_title(n), [(x.get_owning_node().get_name(), str(lib.get_node_title(x.get_owning_node()))) for x in lib.find_then_pin(n).list_connected_pins()])
