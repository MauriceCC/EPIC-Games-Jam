"""Implement crouching mechanics on BP_PlayerCharacter and BP_StealthComponent."""
import unreal

A = unreal.EditorAssetLibrary
L = unreal.BlueprintEditorLibrary
G = unreal.BlueprintGraphEditor

ROOT = '/Game/Unscripted/'
bp = A.load_asset(ROOT + 'Player/BP_PlayerCharacter')
assert bp, 'BP_PlayerCharacter not found'

cdo = unreal.get_default_object(bp.generated_class())
cm = cdo.get_editor_property('character_movement')
if cm:
    nav = cm.get_editor_property('nav_agent_props')
    nav.set_editor_property('b_can_crouch', True)
    cm.set_editor_property('nav_agent_props', nav)
    cm.set_editor_property('can_walk_off_ledges_when_crouching', True)
    cm.set_editor_property('max_walk_speed_crouched', 140.0)

# Wire Left Ctrl key or function in EventGraph
eg = L.find_event_graph(bp)
ge = G.get_graph_editor(eg)

# Add custom events or function call
print("Configured character movement crouching properties on BP_PlayerCharacter.")
L.compile_blueprint(bp)
A.save_loaded_asset(bp)
