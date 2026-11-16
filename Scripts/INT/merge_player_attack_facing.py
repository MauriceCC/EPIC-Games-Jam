"""Keep movement facing and attack aim on the current A sprint player."""
from pathlib import Path
import sys
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
plugins = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(plugins)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
player = h.asset('Player/BP_PlayerCharacter')
for name in ('B_ResumePlayerAtCheckpoint', 'A_EndHitStop'):
    assert h.edit(player, name), f'Missing merged player function: {name}'

attack = h.edit(player, 'DoLightAttack')
assert any(str(node.get_node_title()) == 'FaceCursor' for node in attack.list_all_nodes())
events = h.edit(player, 'EventGraph')
titles = [str(node.get_node_title()).replace(' ', '').lower() for node in events.list_all_nodes()
          if isinstance(node, u.K2Node_Event)]
for name in ('SetRetakeBlocked', 'SetGameplayInputEnabled', 'ClearRetakeHistory'):
    assert any(name.lower() in title for title in titles), f'Missing merged player event: {name}'
for update in events.list_all_nodes():
    if str(update.get_node_title()) != 'A_UpdateCursorFacing':
        continue
    previous, = update.find_execute_pin().list_connected_pins()
    following, = update.find_then_pin().list_connected_pins()
    events.remove_nodes([update])
    h.connect(previous, following)

movement = u.get_default_object(player.generated_class()).get_editor_property('character_movement')
movement.modify()
movement.set_editor_property('orient_rotation_to_movement', True)
h.save(player)
movement = u.get_default_object(player.generated_class()).get_editor_property('character_movement')
assert movement.get_editor_property('orient_rotation_to_movement')
for asset in ('Enemies/BP_GuardBase', 'Narrative/BP_GameMode'):
    h.compile_blueprint(h.asset(asset), warnings_as_errors=True)
u.log('INT_PLAYER_ATTACK_FACING_MERGED')
