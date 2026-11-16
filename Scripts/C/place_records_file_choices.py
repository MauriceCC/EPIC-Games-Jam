"""Let the player inspect and confirm one of the two Records Room files."""
import csv
import json
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
world=worlds.get_editor_world()
assert not worlds.get_game_world() and world.get_name()=='L_Whitechapel'
bp=h.asset('Narrative/BP_FinalChoice')
base=h.asset('Narrative/BP_InteractableBase')
guard=h.asset('Enemies/BP_GuardBase')
boss=h.asset('Enemies/BP_Supervisor')
hud=h.asset('UI/BP_HUD')
boolean=h.basic('bool')
h.variable(bp,'bAuthenticFile',boolean,False,True,'Records')
h.variable(bp,'bConfirmFile',boolean,False,category='Records')
mesh=h.add_component(bp,'StationMesh',u.StaticMeshComponent)
mesh.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
mesh.set_editor_property('bCanEverAffectNavigation',False)
h.compile_blueprint(bp,warnings_as_errors=True)

def phase(g,flow,value):
    state=h.call(g,'/Script/Engine.GameplayStatics:GetGameState').find_result_pin()
    ready,missing=h.branch(g,flow,h.is_valid(g,state))
    lookup=h.message(g,ready,'GetCurrentPhase',state)
    index=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=lookup.find_result_pin()).find_result_pin()
    yes,no=h.branch(g,lookup.find_then_pin(),h.math(g,'EqualEqual_IntInt',index,value))
    return yes,(missing,no)

g=h.override(bp,'CanInteract')
h.clear_body(g)
valid=h.all_true(g,h.get(g,'bInteractionEnabled'),h.not_(g,h.get(g,'bConsumed')),h.is_valid(g,h.param(g,'Interactor')))
yes,no=h.branch(g,g.find_graph_entry_pin(),valid)
active,denials=phase(g,yes,4)
find=h.call(g,'/Script/Engine.GameplayStatics:GetActorOfClass',start=active,ActorClass=boss.generated_class().get_path_name())
alive,missing=h.branch(g,find.find_then_pin(),h.is_valid(g,find.find_result_pin()))
defeated=h.invoke(g,alive,guard,'IsDefeated',target=find.find_result_pin())
h.result(g,defeated.find_then_pin(),Result=defeated.find_result_pin())
denied=h.result(g,no,Result=False)
for pin in (*denials,missing):
    h.connect(pin,denied.find_execute_pin())

with (repo/'SourceData/C/NarrativeText.csv').open(encoding='utf-8-sig',newline='') as f:
    phrases={row['Key']:row['Text'] for row in csv.DictReader(f)}

g=h.override(bp,'ExecuteInteraction')
h.clear_body(g)
pc=h.call(g,'/Script/Engine.GameplayStatics:GetPlayerController').find_result_pin()
target=h.call(g,'/Script/Engine.PlayerController:GetHUD',target=pc).find_result_pin()
typed,view,_=h.cast(g,g.find_graph_entry_pin(),target,hud.generated_class())
authentic,official=h.branch(g,typed,h.get(g,'bAuthenticFile'))
for flow,kind,token in [(official,'Official','OfficialCut'),(authentic,'Authentic','AuthenticRecord')]:
    confirm,preview=h.branch(g,flow,h.get(g,'bConfirmFile'))
    label=phrases[kind+'File_Title']
    armed=h.setvar(g,preview,'bConfirmFile',True)
    armed=h.setvar(g,armed,'InteractionPrompt','Confirm '+label.lower())
    h.invoke(g,armed,hud,'OpenDocument',target=view,Title=label,
             Body=phrases[kind+'File_Summary']+' Close this preview, then interact again to confirm.')
    fact=h.invoke(g,confirm,base,'ReportStoryFact',Event='NewEnumerator7',Param=token)
    finished,_=phase(g,fact.find_then_pin(),5)
    end=h.setvar(g,finished,'bConsumed',True)
    h.invoke(g,end,hud,'OpenDocument',target=view,Title=label+' registered',Body=phrases[kind+'Ending_Summary'])

h.layout(bp,{'CanInteract','ExecuteInteraction'})
h.save(bp)
placed={a.get_actor_label():a for a in actors.get_all_level_actors()}
assert levels.set_current_level_by_name('L_Whitechapel_Story')
for kind,y,auth in [('Official',2875,False),('Authentic',3125,True)]:
    label='C_Records_'+kind+'File'
    station=placed.get(label)
    target = u.Vector(5290,y,0)
    if not station:
        station=actors.spawn_actor_from_class(bp.generated_class(),target,u.Rotator(yaw=180))
        assert station and station.get_outermost().get_path_name()=='/Game/Unscripted/Maps/L_Whitechapel_Story'
        station.set_actor_label(label)
    station.modify()
    station.set_editor_property('bAuthenticFile',auth)
    station.set_editor_property('InteractionPrompt','Inspect '+kind.lower()+' file')
    station.set_editor_property('InteractionPriority',75)
    component=station.get_editor_property('StationMesh')
    component.modify()
    asset='SM_RecordStation_'+kind
    component.set_static_mesh(h.asset('Art/Props/'+asset+'/'+asset))
assert u.EditorLoadingAndSavingUtils.save_packages([station.get_outermost()],False)
u.log('B_RECORD_STATIONS saved both authored file choices, preview, and confirmation')
