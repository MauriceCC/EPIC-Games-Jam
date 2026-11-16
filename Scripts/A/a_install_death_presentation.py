"""[PROPUESTA] Install A/B death presentation through Unreal's Blueprint API.

No Core, shared art, narrative assets, maps, damage or nonlethal rules are saved.
Run with the full editor (Blueprint action menus are unavailable in commandlets).
"""
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.path[:0] = [str(repo/'Scripts/C'), str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h

ROOT = '/Game/Unscripted/'
L = u.BlueprintEditorLibrary
loco = h.asset('Art/Characters/Shared/BP_LocomotionAnim')


def fresh(bp, name):
    graph = h.edit(bp, name)
    if graph:
        h.clear_body(graph)
        return graph
    return h.function(bp, name)


def insert(g, source, bp, name):
    previous = list(source.list_connected_pins())
    if any(str(p.get_owning_node().get_node_title()) == name for p in previous):
        return
    source.break_pin_links()
    call = h.invoke(g, source, bp, name)
    for p in previous:
        h.connect(call.find_then_pin(), p)


def clear_timer(g, start, target, name):
    return h.call(g, '/Script/Engine.KismetSystemLibrary:K2_ClearTimer', start,
                  Object=target, FunctionName=name).find_then_pin()


def main():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    guard = h.asset('Enemies/BP_GuardBase')
    g = fresh(guard, 'B_PlayDeathVisual')
    mesh = h.get(g, 'Mesh')
    comp = h.call(g, '/Script/Engine.Actor:GetComponentByClass',
                  ComponentClass=loco.generated_class().get_path_name()).find_result_pin()
    start = g.find_graph_entry_pin()
    start = h.setvar(g, start, 'bB_AttackVisualActive', False)
    start = h.setvar(g, start, 'bIsTemporalFrozen', False)
    start = clear_timer(g, start, h.self_pin(g), 'B_EndTemporalFreeze')
    start = h.call(g, '/Script/Engine.CharacterMovementComponent:DisableMovement', start,
                   target=h.get(g, 'CharacterMovement')).find_then_pin()
    start = h.call(g, '/Script/Engine.ActorComponent:SetComponentTickEnabled', start,
                   target=mesh, bEnabled=True).find_then_pin()
    start = h.call(g, '/Script/Engine.MeshComponent:SetOverlayMaterial', start,
                   target=mesh, NewOverlayMaterial=None).find_then_pin()
    start = h.call(g, '/Script/Engine.SkeletalMeshComponent:SetPlayRate', start,
                   target=mesh, Rate=1.0).find_then_pin()
    start, _ = h.branch(g, start, h.is_valid(g, comp))
    start = clear_timer(g, start, comp, 'EndOneShot')
    model = h.call(g, '/Script/Engine.SkeletalMeshComponent:GetSkeletalMeshAsset', target=mesh).find_result_pin()
    for who in ('Pursuer_A', 'Pursuer_B', 'Interventor', 'Supervisor'):
        yes, start = h.branch(g, start, h.math(g, 'EqualEqual_ObjectObject', model,
                              ROOT+'Art/Characters/SK_'+who+'/SK_'+who+'.SK_'+who))
        h.invoke(g, yes, loco, 'PlayAndHold', comp,
                 Anim=h.asset('Enemies/Animation/Polish/A_'+who+'_Death').get_path_name())
    h.compile_blueprint(guard, warnings_as_errors=True)

    g = h.edit(guard, 'EventGraph')
    event = next(n for n in g.list_all_nodes() if isinstance(n, u.K2Node_CustomEvent)
                 and str(n.get_node_title()) == 'B_PlayKnockoutFall')
    # Replace the rigid 87-degree fall. Keep a short return from the stagger
    # component tilt while the skeleton itself performs the articulated fall.
    if not any(str(p.get_owning_node().get_node_title()) == 'B_PlayDeathVisual'
               for p in event.find_then_pin().list_connected_pins()):
        event.find_then_pin().break_pin_links()
        move = next(n for n in g.list_all_nodes()
                    if str(n.get_node_title()).replace(' ', '') == 'MoveComponentTo')
        move.find_input_pin('Move').break_pin_links()
        move.find_input_pin('TargetRelativeRotation').break_pin_links()
        h.connect(h.get(g, 'B_StaggerRestRotation'), move.find_input_pin('TargetRelativeRotation'))
        h.literal(move.find_input_pin('OverTime'), .18)
        call = h.invoke(g, event.find_then_pin(), guard, 'B_PlayDeathVisual')
        h.connect(call.find_then_pin(), move.find_input_pin('Move'))
    # Mesh evaluation must remain enabled after the health/story notification.
    g = h.edit(guard, 'B_ApplyHealthDamage')
    for n in g.list_all_nodes():
        if str(n.get_node_title()) == 'SetComponentTickEnabled':
            h.literal(n.find_input_pin('bEnabled'), True)
    h.save(guard)
    for name in ('Pursuer', 'Interventor', 'Supervisor'):
        h.compile_blueprint(h.asset('Enemies/BP_'+name), warnings_as_errors=True)

    player = h.asset('Player/BP_PlayerCharacter')
    u.get_default_object(player.generated_class()).set_editor_property('AnimDeath', h.asset('Player/Animation/Polish/A_Agent_Death'))
    g = fresh(player, 'A_PrepareDeathVisual')
    start = h.call(g, '/Script/Engine.SkeletalMeshComponent:SetPlayRate', g.find_graph_entry_pin(),
                   target=h.get(g, 'Mesh'), Rate=1.0).find_then_pin()
    h.call(g, '/Script/Engine.ActorComponent:SetComponentTickEnabled', start,
           target=h.get(g, 'Mesh'), bEnabled=True)
    g = fresh(player, 'A_FinishDeathPresentation')
    start, _ = h.branch(g, g.find_graph_entry_pin(), h.get(g, 'bDead'))
    state = h.call(g, '/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    event = h.message(g, start, 'ReportStoryEvent', state, Event='NewEnumerator9',
                      Source=h.self_pin(g), Param='None')
    # The existing checkpoint handler clears bDead synchronously when available.
    start, _ = h.branch(g, event.find_then_pin(), h.get(g, 'bDead'))
    h.call(g, '/Script/Engine.KismetSystemLibrary:K2_SetTimer', start,
           Object=h.self_pin(g), FunctionName='RestartLevel', Time=3.0, bLooping=False)
    g = fresh(player, 'A_CancelDeathPresentation')
    start = clear_timer(g, g.find_graph_entry_pin(), h.self_pin(g), 'A_FinishDeathPresentation')
    clear_timer(g, start, h.self_pin(g), 'RestartLevel')
    h.compile_blueprint(player, warnings_as_errors=True)

    g = h.edit(player, 'Die')
    if not any(str(n.get_node_title()) == 'A_PrepareDeathVisual' for n in g.list_all_nodes()):
        insert(g, g.find_graph_entry_pin(), player, 'A_PrepareDeathVisual')
    # Delay only the existing death notification so a checkpoint does not erase
    # the animation in the same frame. Keep its event and checkpoint contract.
    message = next((n for n in g.list_all_nodes() if 'ReportStoryEvent' in str(n.get_node_title())), None)
    if message:
        before, = message.find_execute_pin().list_connected_pins()
        before.break_pin_links()
        h.call(g, '/Script/Engine.KismetSystemLibrary:K2_SetTimer', before,
               Object=h.self_pin(g), FunctionName='A_FinishDeathPresentation', Time=2.05, bLooping=False)
        # Remove the old notification and fallback control flow, preserving
        # the preceding disable-movement / held-animation logic.
        remove = [message]
        for n in g.list_all_nodes():
            if n.get_class().get_name() == 'K2Node_IfThenElse':
                remove.append(n)
            elif str(n.get_node_title()) == 'Set Timer by Function Name' and n.find_input_pin('FunctionName').get_pin_value() == 'RestartLevel':
                remove.append(n)
        g.remove_nodes(remove)
    # Repeated lethal callbacks must not restart the animation/timer.
    entry = g.find_graph_entry_pin()
    linked, = entry.list_connected_pins()
    if linked.get_owning_node().get_class().get_name() != 'K2Node_IfThenElse':
        entry.break_pin_links()
        start, _ = h.branch(g, entry, h.not_(g, h.get(g, 'bDead')))
        h.connect(start, linked)
    g = h.edit(player, 'B_ResumePlayerAtCheckpoint')
    insert(g, g.find_graph_entry_pin(), player, 'A_CancelDeathPresentation')
    h.save(player)
    print('DEATH_PRESENTATION_INSTALLED')


if __name__ == '__main__':
    main()
