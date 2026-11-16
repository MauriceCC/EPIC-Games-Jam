"""Fresh-process runtime checks of saved A-04 Blueprint bytecode. No saves."""
import json, traceback
from pathlib import Path
import unreal
HERE=Path(__file__).resolve().parent
OUT={'passed':False,'checks':[]}
actors=[]
def check(name,actual,expected=True):
    ok=actual==expected
    OUT['checks'].append({'name':name,'actual':actual,'expected':expected,'passed':ok})
    assert ok,(name,actual,expected)
def prop(obj,name):return obj.get_editor_property(name)
def invoke(obj,name,*args):return obj.call_method(name,args=args)
try:
    health=unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent')
    player=unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    observer=unreal.load_asset('/Game/Unscripted/Player/Test/BP_HealthObserver_A')
    for bp in (health,player,observer):check(bp.get_name()+' compiles',unreal.BlueprintEditorLibrary.compile_blueprint(bp))
    cdo=unreal.get_default_object(health.generated_class())
    check('Class defaults', [prop(cdo,n) for n in ('CurrentHealth','MaxHealth')],[100,100])
    H=unreal.SubobjectDataBlueprintFunctionLibrary
    templates=[]
    for h in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player):
        obj=H.get_object(H.get_data(h))
        if obj and obj.get_class()==health.generated_class() and obj not in templates:templates.append(obj)
    check('One installed Health',len(templates),1)
    check('Player saved defaults',[prop(templates[0],n) for n in ('CurrentHealth','MaxHealth')],[100,100])
    check('A-03 movement rotation remains disabled',unreal.get_default_object(player.generated_class()).get_editor_property('character_movement').get_editor_property('orient_rotation_to_movement'),False)
    # Transient actor dummies: never save or alter a map or B's assets.
    subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(2):actors.append(subsystem.spawn_actor_from_class(unreal.Actor,unreal.Vector(i*200,0,0),transient=True))
    a=unreal.new_object(health.generated_class(),outer=actors[0])
    b=unreal.new_object(health.generated_class(),outer=actors[1])
    watches=[]
    for i in range(2):
        w=unreal.new_object(observer.generated_class(),outer=actors[0])
        w.set_editor_property('ObservedHealth',a);invoke(w,'BindHealth');watches.append(w)
    def state(label,current,changes,depleted,maximum=100):
        check(label+' stored',[prop(a,'CurrentHealth'),prop(a,'MaxHealth')],[current,maximum])
        for i,w in enumerate(watches):
            check(label+' observer '+str(i),[prop(w,n) for n in ('LastCurrent','LastMax','ChangeCount','DepletedCount')],[current,maximum,changes,depleted])
    invoke(a,'ReceiveBeginPlay');state('BeginPlay initial publish',100,1,0)
    invoke(a,'ApplyHealthDamage',25.0);state('Damage 25 reports 75 (not 50)',75,2,0)
    invoke(a,'SetHealth',25.0);state('Restore 25',25,3,0)
    invoke(a,'ApplyHealthDamage',15.0);state('Remaining 10 is not depleted',10,4,0)
    invoke(a,'ApplyHealthDamage',99.0);state('Overkill',0,5,1)
    invoke(a,'ApplyHealthDamage',10.0);state('No repeated depletion at zero',0,6,1)
    invoke(a,'SetHealth',999.0);state('Upper clamp and revive',100,7,1)
    invoke(a,'ApplyHealthDamage',-20.0);state('Negative damage ignored',100,8,1)
    invoke(a,'SetHealth',-3.0);state('Lower clamp and second depletion',0,9,2)
    invoke(a,'SetHealth',-3.0);state('No repeated depletion on SetHealth',0,10,2)
    invoke(a,'SetHealth',80.0);state('Restore positive',80,11,2)
    watches[0].set_editor_property('bAttemptReentry',True)
    invoke(a,'ApplyHealthDamage',10.0);state('Reentrant notification cannot mutate health',70,12,2)
    watches[0].set_editor_property('bAttemptReentry',False)
    invoke(a,'ApplyHealthDamage',0.0);state('Zero damage',70,13,2)
    a.set_editor_property('MaxHealth',250.0);invoke(a,'SetHealth',999.0);state('Custom max',250,14,2,250)
    a.set_editor_property('MaxHealth',0.0);invoke(a,'SetHealth',1.0);state('Zero max',0,15,3,0)
    a.set_editor_property('MaxHealth',-10.0);invoke(a,'SetHealth',1.0);state('Negative max normalized',0,16,3,0)
    check('Other actor unaffected',[prop(b,'CurrentHealth'),prop(b,'MaxHealth')],[100,100])
    invoke(b,'ApplyHealthDamage',30.0)
    check('Second dummy works independently',prop(b,'CurrentHealth'),70)
    check('Second dummy did not notify first observers',prop(watches[0],'ChangeCount'),16)
    b.set_editor_property('MaxHealth',45.0);invoke(b,'SetHealth',0.0)
    invoke(b,'ReceiveBeginPlay')
    check('Dummy BeginPlay uses its own maximum',prop(b,'CurrentHealth'),45)
    OUT['passed']=True
except Exception:
    OUT['error']=traceback.format_exc();unreal.log_error(OUT['error'])
finally:
    for actor in actors:unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(actor)
    (HERE/'a04_validation_result.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
if not OUT['passed']:raise RuntimeError('A-04 validation failed; inspect report')
