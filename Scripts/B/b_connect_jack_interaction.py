"""Connect the Workshop Jack to the existing interactable and story systems."""
import json
import sys
from pathlib import Path

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.path.insert(0, str(repo / 'Scripts/C'))
toolset_python = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path.insert(0, str(toolset_python))
import blueprint_helpers_c as h

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert not worlds.get_game_world() and worlds.get_editor_world().get_name() == 'L_Whitechapel'
jack_bp = h.asset('Enemies/Jack/BP_Jack')
fallback = 'bB_FollowPlayerWithoutRoute'
if u.BlueprintEditorLibrary.get_member_variable_type(jack_bp, fallback) is None:
    h.variable(jack_bp, fallback, h.basic('bool'), True, True, 'Jack')
    h.compile_blueprint(jack_bp, warnings_as_errors=True)
    g = h.edit(jack_bp, 'EventGraph')
    nodes = {node.get_name(): node for node in g.list_all_nodes()}
    # The prototype follows the player when it has no route. Preserve that
    # behavior in test maps while letting the Workshop instance wait in place.
    unassigned = nodes['K2Node_IfThenElse_7'].find_output_pin('else')
    previous, = unassigned.list_connected_pins()
    assert previous.get_owning_node().get_name() == 'K2Node_IfThenElse_2'
    unassigned.break_pin_links()
    follow, _ = h.branch(g, unassigned, h.get(g, fallback))
    h.connect(follow, previous)
    h.save(jack_bp)
jack_type = jack_bp.generated_class()
parent = h.asset('Narrative/BP_InteractableBase')
asset_path = '/Game/Unscripted/Enemies/Jack/BP_JackInteraction'
existing = u.EditorAssetLibrary.does_asset_exist(asset_path)
bp = h.asset(asset_path) if existing else h.create_actor_bp(
    'Enemies/Jack', 'BP_JackInteraction', parent.generated_class()
)

def build_interaction():
    h.add_component(bp, 'InteractionAnchor', u.SceneComponent)
    if u.BlueprintEditorLibrary.get_member_variable_type(bp, 'Jack') is None:
        h.variable(bp, 'Jack', h.obj_type(jack_type), '', True, 'Jack')
        h.compile_blueprint(bp, warnings_as_errors=True)
    defaults = u.get_default_object(bp.generated_class())
    defaults.set_editor_property('InteractionPrompt', 'Talk to Jack')
    defaults.set_editor_property('InteractionPriority', 60)

    g = h.override(bp, 'CanInteract')
    h.clear_body(g)
    state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    interactor = h.param(g, 'Interactor')
    jack = h.get(g, 'Jack')
    eligible = h.all_true(g, h.is_valid(g, state), h.is_valid(g, interactor),
                          h.is_valid(g, jack), h.get(g, 'bInteractionEnabled'),
                          h.not_(g, h.get(g, 'bConsumed')))
    yes, no = h.branch(g, g.find_graph_entry_pin(), eligible)
    phase = h.message(g, yes, 'GetCurrentPhase', state)
    phase_value = phase.find_result_pin()
    find_jack = 'NewEnumerator' + str(json.loads(phase_value.get_pin_type_as_json_schema())['enum'].index('FindJack'))
    action = next(name for name in h.actions(g, [phase_value])
                  if name.endswith(('|Igual(enumerador)', '|Equal(Enum)')))
    comparison = g.create_node_from_name(action, u.Vector2D(), [phase_value])
    h.connect(phase_value, comparison.find_input_pin('A'))
    h.literal(comparison.find_input_pin('B'), find_jack)
    same_phase = comparison.find_result_pin()
    distance = h.call(g, '/Script/Engine.Actor:GetDistanceTo', target=jack, OtherActor=interactor).find_result_pin()
    near = h.math(g, 'LessEqual_DoubleDouble', distance, 230.0)
    h.result(g, phase.find_then_pin(), Result=h.all_true(g, same_phase, near))
    h.result(g, no, Result=False)

    g = h.override(bp, 'ExecuteInteraction')
    h.clear_body(g)
    state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    jack = h.get(g, 'Jack')
    report = h.message(g, g.find_graph_entry_pin(), 'ReportStoryEvent', state, Source=jack, Param='Workshop')
    story_event = report.find_input_pin('Event')
    names = json.loads(story_event.get_pin_type_as_json_schema())['enum']
    h.literal(story_event, 'NewEnumerator' + str(names.index('JackFound')))
    end = h.setvar(g, report.find_then_pin(), 'bConsumed', True)
    h.setvar(g, end, 'bJackFound', True, target=jack, cls=jack_type)
    h.layout(bp, {'CanInteract', 'ExecuteInteraction'})
    h.save(bp)

build_interaction()

placed = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
jack = placed['B_Jack_Workshop']
jack.modify()
jack.set_editor_property(fallback, False)
assert levels.set_current_level_by_name('L_Whitechapel_AI')
adapter = placed.get('B_Jack_Workshop_Interaction')
if not adapter:
    adapter = actors.spawn_actor_from_class(bp.generated_class(), jack.get_actor_location(), u.Rotator())
    assert adapter and adapter.get_outermost() == jack.get_outermost()
    adapter.set_actor_label('B_Jack_Workshop_Interaction')
adapter.modify()
assert adapter.set_actor_location(jack.get_actor_location(), False, True)
adapter.set_editor_property('Jack', jack)
assert u.EditorLoadingAndSavingUtils.save_packages([jack.get_outermost()], False)
u.log('B_JACK_INTERACTION saved')
