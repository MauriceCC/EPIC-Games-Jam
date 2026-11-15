"""Place and gate the three late-game encounters in Whitechapel."""
import json
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
dep = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(dep)]
import blueprint_helpers_c as h

worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
world = worlds.get_editor_world()
assert not worlds.get_game_world() and world.get_name() == 'L_Whitechapel'
guard = h.asset('Enemies/BP_GuardBase')
lib = u.BlueprintEditorLibrary
gate_name = 'B_CanRunEncounter'
h.variable(guard, 'B_StoryGate', h.basic('int'), 0, True, 'Encounter')
h.variable(guard, 'bB_CorrectionDone', h.basic('bool'), False, category='Encounter')
h.compile_blueprint(guard, warnings_as_errors=True)

if not h.edit(guard, gate_name):
    g = h.function(guard, gate_name, outputs=[('Result', h.basic('bool'))])
    gate = h.get(g, 'B_StoryGate')
    always, restricted = h.branch(g, g.find_graph_entry_pin(), h.math(g,'EqualEqual_IntInt',gate,0))
    h.result(g, always, Result=True)
    timed, story = h.branch(g, restricted, h.math(g,'EqualEqual_IntInt',gate,2))
    h.result(g, timed, Result=h.get(g,'bB_CorrectionDone'))
    state = h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    valid, missing = h.branch(g, story, h.is_valid(g,state))
    phase = h.message(g, valid, 'GetCurrentPhase', state)
    phase_index = h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=phase.find_result_pin()).find_result_pin()
    boss = h.math(g,'EqualEqual_IntInt',gate,3)
    minimum = h.call(g,'/Script/Engine.KismetMathLibrary:SelectInt',A=4,B=2,bPickA=boss).find_result_pin()
    h.result(g,phase.find_then_pin(),Result=h.math(g,'GreaterEqual_IntInt',phase_index,minimum))
    h.result(g, missing, Result=False)
    h.compile_blueprint(guard,warnings_as_errors=True)

    g = h.edit(guard,'EventGraph')
    tick = next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_Event) and 'Tick' in str(n.get_node_title()))
    output = tick.find_then_pin()
    next_step, = output.list_connected_pins()
    output.break_pin_links()
    check = h.invoke(g,output,guard,gate_name)
    yes,_ = h.branch(g,check.find_then_pin(),check.find_result_pin())
    h.connect(yes,next_step)

    begin = next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_Event) and 'BeginPlay' in str(n.get_node_title()))
    checkpoint, = [n for n in g.list_all_nodes() if isinstance(n,u.K2Node_VariableSet) and n.find_input_pin('B_CheckpointHealth').is_valid()]
    output = checkpoint.find_then_pin()
    listen,_ = h.branch(g,output,h.math(g,'EqualEqual_IntInt',h.get(g,'B_StoryGate'),2))
    state = h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    valid,_ = h.branch(g,listen,h.is_valid(g,state))
    manager = h.message(g,valid,'GetObjectiveManager',state)
    valid,_ = h.branch(g,manager.find_then_pin(),h.is_valid(g,manager.find_result_pin()))
    _, callback = h.bind_assign(g,valid,manager.find_result_pin(),'OnDialogueFinished')
    match = h.call(g,'/Script/Engine.KismetMathLibrary:EqualEqual_NameName',A=callback.find_output_pin('Row'),B='Correction_Order').find_result_pin()
    enter,_ = h.branch(g,callback.find_then_pin(),h.all_true(g,match,h.not_(g,h.get(g,'bB_CorrectionDone'))))
    end = h.setvar(g,enter,'bB_CorrectionDone',True)
    report = h.message(g,end,'ReportStoryEvent',state,Source=h.self_pin(g),Param='RefugeApproach')
    event = report.find_input_pin('Event')
    kinds = json.loads(event.get_pin_type_as_json_schema())['enum']
    h.literal(event,'NewEnumerator'+str(kinds.index('InterventorTurnedHostile')))

    g = h.edit(guard,'B_ApplyHealthDamage')
    entry = g.find_graph_entry_pin()
    previous, = entry.list_connected_pins()
    entry.break_pin_links()
    active = h.invoke(g,entry,guard,gate_name)
    yes,_ = h.branch(g,active.find_then_pin(),active.find_result_pin())
    h.connect(yes,previous)

    g = h.edit(guard,'CanBeTemporalCutTarget')
    entry = g.find_graph_entry_pin()
    result, = entry.list_connected_pins()
    result_node = result.get_owning_node()
    eligibility, = result_node.find_input_pin('Result').list_connected_pins()
    entry.break_pin_links()
    active = h.invoke(g,entry,guard,gate_name)
    h.connect(active.find_then_pin(),result)
    h.connect(h.all_true(g,active.find_result_pin(),eligibility),result_node.find_input_pin('Result'))
    h.layout(guard,{gate_name})
    h.save(guard)

package = '/Game/Unscripted/Maps/L_Whitechapel_AI'
placed = {a.get_actor_label():a for a in actors.get_all_level_actors() if a.get_outermost().get_path_name()==package}
assert levels.set_current_level_by_name('L_Whitechapel_AI')
nav = u.NavigationSystemV1

def project(x,y):
    point = nav.project_point_to_navigation(world,u.Vector(x,y,0),None,None,u.Vector(140,140,180))
    assert point is not None,(x,y)
    return point

def place(label,bp,location):
    actor=placed.get(label)
    if not actor:
        actor=actors.spawn_actor_from_class(bp.generated_class(),location,u.Rotator())
        assert actor and actor.get_outermost().get_path_name()==package
        actor.set_actor_label(label)
    actor.modify()
    assert actor.set_actor_location(location,False,True)
    return actor

pursuer=h.asset('Enemies/BP_Pursuer')
patrol=h.asset('Enemies/BP_PatrolRoute')
finisher=h.asset('Enemies/BP_GuardFinisher')
plans = [
    ('Central_01',pursuer,1,[(2600,3000),(2600,3300)]),
    ('Central_02',pursuer,1,[(3200,3600),(3200,3875)]),
    ('Central_03',pursuer,1,[(2600,4200),(2600,3975)]),
    ('Interventor',h.asset('Enemies/BP_Interventor'),2,[(2450,2000)]),
    ('Supervisor',h.asset('Enemies/BP_Supervisor'),3,[(4200,3000)]),
]
for name,bp,gate,positions in plans:
    points=[project(x,y) for x,y in positions]
    if len(points)>1:
        for src,dst in ((points[0],points[1]),(points[1],points[0])):
            path=nav.find_path_to_location_synchronously(world,src,dst)
            assert path and path.is_valid() and not path.is_partial(),(name,src,dst)
    cap=u.get_default_object(bp.generated_class()).get_editor_property('capsule_component')
    location=points[0]+u.Vector(0,0,cap.get_scaled_capsule_half_height())
    enemy=place('B_'+name,bp,location)
    enemy.set_editor_property('B_StoryGate',gate)
    if len(points)>1:
        route=place('B_'+name+'_Route',patrol,points[0])
        route.set_editor_property('Waypoints',points)
        enemy.set_editor_property('PatrolRoute',route)
        marker=place('B_'+name+'_Finisher',finisher,location)
        marker.set_editor_property('Guard',enemy)
        rule=u.AttachmentRule.SNAP_TO_TARGET
        assert marker.attach_to_actor(enemy,'',rule,rule,u.AttachmentRule.KEEP_WORLD,False)
    u.log('B_ENCOUNTER '+name+' '+str(location))
assert u.EditorLoadingAndSavingUtils.save_packages([enemy.get_outermost()],False)
