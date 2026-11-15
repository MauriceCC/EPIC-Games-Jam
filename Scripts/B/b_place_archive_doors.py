"""Gate the Archive and Records Room with the existing story progression."""
import sys
from pathlib import Path
import unreal as u

repo=Path(u.Paths.project_dir()).resolve().parent
dep=Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0]=[str(repo/'Scripts/C'),str(dep)]
import blueprint_helpers_c as h

worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not worlds.get_game_world() and worlds.get_editor_world().get_name()=='L_Whitechapel'

path='/Game/Unscripted/Enemies/BP_ArchiveEncounterDoor'
parent=h.asset('Narrative/BP_Door')
bp=h.asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else h.create_actor_bp(
    'Enemies','BP_ArchiveEncounterDoor',parent.generated_class())
if u.BlueprintEditorLibrary.get_member_variable_type(bp,'bB_RequiresSupervisor') is None:
    h.variable(bp,'bB_RequiresSupervisor',h.basic('bool'),False,True,'Encounter')
    h.compile_blueprint(bp,warnings_as_errors=True)
defaults=u.get_default_object(bp.generated_class())
defaults.set_editor_property('bReportsEscapeRoute',False)
defaults.set_editor_property('InteractionPriority',65)

g=h.override(bp,'CanInteract')
h.clear_body(g)
state=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
ready=h.all_true(g,h.is_valid(g,state),h.is_valid(g,h.param(g,'Interactor')),
                 h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed')))
valid,no=h.branch(g,g.find_graph_entry_pin(),ready)
phase=h.message(g,valid,'GetCurrentPhase',state)
phase_index=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=phase.find_result_pin()).find_result_pin()
final,earlier=h.branch(g,phase.find_then_pin(),h.math(g,'EqualEqual_IntInt',phase_index,4))
requires,archive=h.branch(g,final,h.get(g,'bB_RequiresSupervisor'))
guard=h.asset('Enemies/BP_GuardBase')
denied=h.result(g,no,Result=False)
h.connect(earlier,denied.find_execute_pin())
for entrance, enemy in [(requires,'BP_Supervisor'),(archive,'BP_Interventor')]:
    cls=h.asset('Enemies/'+enemy).generated_class()
    lookup=h.call(g,'/Script/Engine.GameplayStatics:GetActorOfClass',
                  start=entrance,ActorClass=cls.get_path_name())
    available,missing=h.branch(g,lookup.find_then_pin(),h.is_valid(g,lookup.find_result_pin()))
    defeated=h.invoke(g,available,guard,'IsDefeated',target=lookup.find_result_pin())
    h.result(g,defeated.find_then_pin(),Result=defeated.find_result_pin())
    h.connect(missing,denied.find_execute_pin())
h.layout(bp,{'CanInteract'})
h.save(bp)

placed={a.get_actor_label():a for a in actors.get_all_level_actors()}
assert levels.set_current_level_by_name('L_Whitechapel_AI')
for label,location,width,prompt,requires in [
    ('B_ArchiveGate',u.Vector(3600,3600,0),3.4,'Open the archive gate',False),
    ('B_RecordsDoor',u.Vector(4800,3000,0),3.4,'Open the records room',True),
]:
    door=placed.get(label)
    if not door:
        door=actors.spawn_actor_from_class(bp.generated_class(),location,u.Rotator())
        assert door and door.get_outermost().get_path_name()=='/Game/Unscripted/Maps/L_Whitechapel_AI'
        door.set_actor_label(label)
    door.modify()
    door.set_actor_scale3d(u.Vector(1,width,1))
    door.set_editor_property('InteractionPrompt',prompt)
    door.set_editor_property('bB_RequiresSupervisor',requires)
    door.set_editor_property('bReportsEscapeRoute',False)
    mesh=door.get_editor_property('DoorMesh')
    mesh.modify()
    mesh.set_editor_property('bCanEverAffectNavigation',False)
assert u.EditorLoadingAndSavingUtils.save_packages([door.get_outermost()],False)
u.log('B_ARCHIVE_DOORS saved Archive and Records phase gates')
