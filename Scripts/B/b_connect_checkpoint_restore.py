"""Connect B's checkpoint state to Whitechapel's existing restore operation."""
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
dep = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(dep)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
jack = h.asset('Enemies/Jack/BP_Jack')
guard = h.asset('Enemies/BP_GuardBase')
player = h.asset('Player/BP_PlayerCharacter')
mode = h.asset('Narrative/BP_GameMode')
health = h.asset('Player/BP_HealthComponent')
animation = h.asset('Art/Characters/Shared/BP_LocomotionAnim')
transform_type = u.BlueprintEditorLibrary.get_struct_type(u.Transform.static_struct())

if u.BlueprintEditorLibrary.get_member_variable_type(jack,'B_LastReachedTransform') is None:
    h.variable(jack,'B_LastReachedTransform',transform_type,'',category='Jack')
    h.compile_blueprint(jack,warnings_as_errors=True)
    g = h.edit(jack,'EventGraph')
    nodes = {n.get_name():n for n in g.list_all_nodes()}
    advance = nodes['K2Node_VariableSet_0']
    incoming, = advance.find_execute_pin().list_connected_pins()
    save = h.setvar(g,incoming,'B_LastReachedTransform',
                    h.call(g,'/Script/Engine.Actor:GetTransform').find_result_pin())
    h.connect(save,advance.find_execute_pin())

    reset = nodes['K2Node_VariableSet_6']
    incoming, = reset.find_execute_pin().list_connected_pins()
    resume, = reset.find_then_pin().list_connected_pins()
    g.remove_nodes([reset])
    h.connect(incoming,resume)
    original = nodes['K2Node_CallFunction_29']
    after_stop, = original.find_execute_pin().list_connected_pins()
    after_stop.break_pin_links()
    progress = h.math(g,'Greater_IntInt',h.get(g,'CurrentWaypointIndex'),0)
    reached, initial = h.branch(g,after_stop,progress)
    h.connect(initial,original.find_execute_pin())
    h.call(g,'/Script/Engine.Actor:K2_SetActorTransform',start=reached,
           NewTransform=h.get(g,'B_LastReachedTransform'),bSweep=False,bTeleport=True)
    h.save(jack)

revive = 'B_ResumePlayerAtCheckpoint'
if not any(revive in str(n.get_node_title()) for n in h.edit(mode,'RestoreCheckpoint').list_all_nodes()):
    g = h.edit(player,revive) or h.function(player,revive,[('Respawn',transform_type)])
    h.clear_body(g)
    start = g.find_graph_entry_pin()
    for field in ('bDead','bAttacking','bParryWindow','bInvulnerable'):
        start=h.setvar(g,start,field,False)
    movement = h.get(g,'CharacterMovement')
    run = h.call(g,'/Script/Engine.CharacterMovementComponent:SetMovementMode',start=start,
                 target=movement,NewMovementMode='MOVE_Walking')
    moved = h.call(g,'/Script/Engine.Actor:K2_SetActorTransform',start=run.find_then_pin(),
                   NewTransform=h.param(g,'Respawn'),bSweep=False,bTeleport=True)
    component = h.get(g,'HealthComp')
    maximum = h.get(g,'MaxHealth',target=component,cls=health.generated_class())
    refill = h.invoke(g,moved.find_then_pin(),health,'SetHealth',target=component)
    amount, = [pin for pin in refill.list_input_pins() if str(pin.get_pin_name()) not in ('self','execute')]
    h.connect(maximum,amount)
    loco = h.get(g,'LocomotionAnim')
    valid,_ = h.branch(g,refill.find_then_pin(),h.is_valid(g,loco))
    h.invoke(g,valid,animation,'EndOneShot',target=loco)
    h.compile_blueprint(player,warnings_as_errors=True)

    g = h.edit(player,'Die')
    report, = [n for n in g.list_all_nodes() if 'ReportStoryEvent' in str(n.get_node_title()).replace(' ','')]
    end = report.find_then_pin()
    timer, = end.list_connected_pins()
    end.break_pin_links()
    failed,_ = h.branch(g,end,h.get(g,'bDead'))
    h.connect(failed,timer)
    h.layout(player,{revive})
    h.save(player)

g = h.edit(mode,'RestoreCheckpoint')
if not any(revive in str(n.get_node_title()) for n in g.list_all_nodes()):
    count, = [n for n in g.list_all_nodes() if isinstance(n,u.K2Node_VariableSet) and n.find_input_pin('RestoreCount').is_valid()]
    count_in = count.find_execute_pin()
    prior, = count_in.list_connected_pins()
    prior.break_pin_links()
    pawn = h.call(g,'/Script/Engine.GameplayStatics:GetPlayerCharacter').find_result_pin()
    typed,target,other = h.cast(g,prior,pawn,player.generated_class())
    respawn = h.invoke(g,typed,player,revive,target=target,Respawn=h.get(g,'RespawnTransform'))
    current = [respawn.find_then_pin(),other]
    for bp in (guard,jack):
        fetch=h.call(g,'/Script/Engine.GameplayStatics:GetAllActorsOfClass',
                     ActorClass=bp.generated_class().get_path_name())
        for start in current:
            h.connect(start,fetch.find_execute_pin())
        body,item,done=h.foreach(g,fetch.find_then_pin(),fetch.find_output_pin('OutActors'))
        h.invoke(g,body,bp,'B_ResetAtCheckpoint',target=item)
        current=[done]
    h.connect(current[0],count_in)
    h.layout(mode,{'RestoreCheckpoint'})
    h.save(mode)
u.log('B_CHECKPOINT saved player, guard, and last-reached Jack restore')
