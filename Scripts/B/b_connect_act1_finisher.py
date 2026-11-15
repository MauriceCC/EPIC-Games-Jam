"""Enable the existing interaction system to neutralize a stunned Act I guard."""
import json
import sys
from pathlib import Path

import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
tools = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(tools)]
import blueprint_helpers_c as h

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
assert not worlds.get_game_world() and worlds.get_editor_world().get_name() == 'L_Whitechapel'
guard_bp = h.asset('Enemies/BP_GuardBase')
guard_class = guard_bp.generated_class()
base = h.asset('Narrative/BP_InteractableBase')
path = '/Game/Unscripted/Enemies/BP_GuardFinisher'
existing = u.EditorAssetLibrary.does_asset_exist(path)
bp = h.asset(path) if existing else h.create_actor_bp('Enemies', 'BP_GuardFinisher', base.generated_class())
h.add_component(bp, 'FinisherAnchor', u.SceneComponent)
if u.BlueprintEditorLibrary.get_member_variable_type(bp, 'Guard') is None:
    h.variable(bp, 'Guard', h.obj_type(guard_class), '', True, 'Finisher')
    h.compile_blueprint(bp, warnings_as_errors=True)
defaults = u.get_default_object(bp.generated_class())
defaults.set_editor_property('InteractionPrompt', 'Subdue')
defaults.set_editor_property('InteractionPriority', 100)

g = h.override(bp, 'CanInteract')
h.clear_body(g)
guard = h.get(g, 'Guard')
interactor = h.param(g, 'Interactor')
can_check = h.all_true(g, h.is_valid(g, guard), h.is_valid(g, interactor),
                       h.get(g, 'bInteractionEnabled'), h.not_(g, h.get(g, 'bConsumed')))
yes, no = h.branch(g, g.find_graph_entry_pin(), can_check)
health = h.get(g, 'B_Health', target=guard, cls=guard_class)
stunned = h.get(g, 'bB_Stunned', target=guard, cls=guard_class)
distance = h.call(g, '/Script/Engine.Actor:GetDistanceTo', target=guard, OtherActor=interactor).find_result_pin()
controller = h.call(g, '/Script/Engine.Pawn:GetController', target=guard).find_result_pin()
visible = h.call(g, '/Script/Engine.Controller:LineOfSightTo', target=controller, Other=interactor).find_result_pin()
eligible = h.all_true(g, stunned, h.math(g, 'Greater_DoubleDouble', health, 0.0),
                      h.math(g, 'LessEqual_DoubleDouble', distance, 170.0), visible)
valid_controller, missing_controller = h.branch(g, yes, h.is_valid(g, controller))
h.result(g, valid_controller, Result=eligible)
denied = h.result(g, no, Result=False)
h.connect(missing_controller, denied.find_execute_pin())

g = h.override(bp, 'ExecuteInteraction')
h.clear_body(g)
guard = h.get(g, 'Guard')
use = h.invoke(g, g.find_graph_entry_pin(), base, 'CanInteract', Interactor=h.param(g, 'Interactor'))
yes, _ = h.branch(g, use.find_then_pin(), use.find_result_pin())
end = h.setvar(g, yes, 'bConsumed', True)
health = h.get(g, 'B_Health', target=guard, cls=guard_class)
neutralize = h.invoke(g, end, guard_bp, 'B_ApplyHealthDamage', target=guard, Damage=health)
state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
valid, _ = h.branch(g, neutralize.find_then_pin(), h.is_valid(g, state))
report = h.message(g, valid, 'ReportStoryEvent', state, Source=guard, Param='NonLethal')
pin = report.find_input_pin('Event')
events = json.loads(pin.get_pin_type_as_json_schema())['enum']
h.literal(pin, 'NewEnumerator' + str(events.index('EnemyNeutralized')))
h.layout(bp, {'CanInteract', 'ExecuteInteraction'})
h.save(bp)

package = '/Game/Unscripted/Maps/L_Whitechapel_AI'
placed = {a.get_actor_label(): a for a in actors.get_all_level_actors()
          if a.get_outermost().get_path_name() == package}
assert levels.set_current_level_by_name('L_Whitechapel_AI')
for guard in placed.values():
    if guard.get_class().get_name() != 'BP_Pursuer_C':
        continue
    label = guard.get_actor_label() + '_Finisher'
    anchor = placed.get(label)
    if not anchor:
        anchor = actors.spawn_actor_from_class(bp.generated_class(), guard.get_actor_location(), u.Rotator())
        assert anchor and anchor.get_outermost() == guard.get_outermost()
        anchor.set_actor_label(label)
    anchor.modify()
    anchor.set_editor_property('Guard', guard)
    rule = u.AttachmentRule.SNAP_TO_TARGET
    assert anchor.attach_to_actor(guard, '', rule, rule, u.AttachmentRule.KEEP_WORLD, False)
assert u.EditorLoadingAndSavingUtils.save_packages([placed['BP_Pursuer'].get_outermost()], False)
u.log('B_FINISHER saved and attached to the four Act I Pursuers')
