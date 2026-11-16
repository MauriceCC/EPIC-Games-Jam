"""Install A-owned heavy attack through Unreal's Blueprint editor API.

[PROPUESTA] 28 damage, 30 posture, 25 stamina, 190 cm, 120 degree frontal arc.
Uses locomotion one-shot playback and preserves the current damage pipeline.
ReceiveCombatHit is used when implemented; current guards still use AnyDamage.
Run with full editor, Play stopped. Saves only PlayerCharacter/Controller.
"""
import json, sys, shutil, traceback
from pathlib import Path
import unreal as u
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
sys.path[:0]=[str(HERE),str(REPO/'Scripts/C'),str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h
from a_build_uppercut import DURATION,CONTACT,DEST
from a03_graph_tools import snapshot
L=u.BlueprintEditorLibrary

def fresh(bp,name):
    g=h.edit(bp,name)
    if g:h.clear_body(g);return g
    return h.function(bp,name)

def insert(g,pin,bp,name):
    previous=list(pin.list_connected_pins())
    if any(str(p.get_owning_node().get_node_title())==name for p in previous):return
    pin.break_pin_links();n=h.invoke(g,pin,bp,name)
    for p in previous:h.connect(n.find_then_pin(),p)

def timer(g,start,bp,name,seconds):
    return h.call(g,'/Script/Engine.KismetSystemLibrary:K2_SetTimer',start,Object=h.self_pin(g),FunctionName=name,Time=seconds,bLooping=False).find_then_pin()

def main():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    bp=h.asset('Player/BP_PlayerCharacter');controller=h.asset('Player/BP_PlayerController')
    backup=REPO/'Unscripted/Saved/UppercutBackup';backup.mkdir(parents=True,exist_ok=True)
    for name in ('BP_PlayerCharacter','BP_PlayerController'):
        dest=backup/(name+'.uasset')
        if not dest.exists():shutil.copy2(REPO/('Unscripted/Content/Unscripted/Player/'+name+'.uasset'),dest)
    before=snapshot(bp)
    h.variable(bp,'AnimHeavyAttack',h.obj_type(u.AnimSequence),h.asset(DEST).get_path_name(),True,'Heavy Attack')
    h.variable(bp,'bA_HeavyActive',h.basic('bool'),False)
    h.variable(bp,'bA_HeavyHitPending',h.basic('bool'),False)
    for name,value in [('A_HeavyDamage',28.0),('A_HeavyPostureDamage',30.0),('A_HeavyRange',190.0)]:h.variable(bp,name,h.basic('real'),value,True,'Heavy Attack')
    for name in ('DoHeavyAttack','A_HeavyHit','A_EndHeavyAttack','A_CancelHeavyAttack','A_CancelHeavyIfBlocked'):fresh(bp,name)
    fx=h.edit(bp,'A_HeavyImpactFX')
    if fx:h.clear_body(fx)
    else:fx=h.function(bp,'A_HeavyImpactFX',inputs=[('Target',h.obj_type(u.Actor))])
    assert L.compile_blueprint(bp)
    location=h.call(fx,'/Script/Engine.Actor:K2_GetActorLocation',target=h.param(fx,'Target')).find_result_pin()
    impact=h.call(fx,'/Script/Niagara.NiagaraFunctionLibrary:SpawnSystemAtLocation',fx.find_graph_entry_pin(),SystemTemplate=h.asset('VFX/NS_HitImpact').get_path_name(),Location=location)
    h.call(fx,'/Script/Engine.GameplayStatics:PlaySoundAtLocation',impact.find_then_pin(),Sound=h.asset('Audio/SC_StaffHit').get_path_name(),Location=location)
    g=h.edit(bp,'A_CancelHeavyAttack')
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bA_HeavyActive'))
    start=h.setvar(g,yes,'bA_HeavyActive',False)
    start=h.setvar(g,start,'bA_HeavyHitPending',False)
    start=h.setvar(g,start,'bAttacking',False)
    for name in ('A_HeavyHit','A_EndHeavyAttack'):
        start=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=h.self_pin(g),FunctionName=name).find_then_pin()
    # Release ownership before a replacement action is played by TakeHit/Die.
    loco=h.asset('Art/Characters/Shared/BP_LocomotionAnim')
    start=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=h.get(g,'LocomotionAnim'),FunctionName='EndOneShot').find_then_pin()
    h.invoke(g,start,loco,'EndOneShot',h.get(g,'LocomotionAnim'))
    g=h.edit(bp,'A_CancelHeavyIfBlocked')
    yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bGameplayInputBlocked'))
    h.invoke(g,yes,bp,'A_CancelHeavyAttack')
    g=h.edit(bp,'A_EndHeavyAttack')
    h.invoke(g,g.find_graph_entry_pin(),bp,'A_CancelHeavyAttack')

    g=h.edit(bp,'DoHeavyAttack')
    allowed=h.not_(g,h.any_true(g,h.get(g,'bDead'),h.get(g,'bAttacking'),h.get(g,'bGameplayInputBlocked'),h.get(g,'bInvulnerable'),h.get(g,'bParryWindow')))
    yes,_=h.branch(g,g.find_graph_entry_pin(),allowed)
    comp=h.asset('Player/BP_CombatComponent');combat=h.get(g,'BP_CombatComponent')
    cost=h.get(g,'HeavyAttackStaminaCost',combat,comp.generated_class())
    spend=h.invoke(g,yes,comp,'TryConsumeStamina',combat,Cost=cost)
    yes,_=h.branch(g,spend.find_then_pin(),spend.find_output_pin('bConsumed'))
    start=h.setvar(g,yes,'bAttacking',True)
    start=h.setvar(g,start,'bA_HeavyActive',True)
    start=h.setvar(g,start,'bA_HeavyHitPending',True)
    start=h.invoke(g,start,bp,'FaceCursor').find_then_pin()
    start=h.invoke(g,start,loco,'PlayOneShot',h.get(g,'LocomotionAnim'),Anim=h.get(g,'AnimHeavyAttack'),Duration=DURATION).find_then_pin()
    start=timer(g,start,bp,'A_HeavyHit',CONTACT)
    timer(g,start,bp,'A_EndHeavyAttack',DURATION)

    g=h.edit(bp,'A_HeavyHit')
    allowed=h.all_true(g,h.get(g,'bA_HeavyActive'),h.get(g,'bA_HeavyHitPending'),h.get(g,'bAttacking'),h.not_(g,h.get(g,'bDead')),h.not_(g,h.get(g,'bGameplayInputBlocked')))
    yes,_=h.branch(g,g.find_graph_entry_pin(),allowed)
    start=h.setvar(g,yes,'bA_HeavyHitPending',False)
    interface=h.asset('Core/Interfaces/BPI_Damageable')
    # Preserve the target class already used by A's light attack. Do not migrate
    # B's assets or interfaces as part of importing an animation.
    legacy=next(n for n in h.edit(bp,'AttackHit').list_all_nodes() if str(n.get_node_title())=='GetAllActorsOfClass')
    target_class=str(legacy.find_input_pin('ActorClass').get_pin_value())
    actors=h.call(g,'/Script/Engine.GameplayStatics:GetAllActorsOfClass',start,ActorClass=target_class)
    loop,target,done=h.foreach(g,actors.find_then_pin(),actors.find_output_pin('OutActors'))
    origin=h.call(g,'/Script/Engine.Actor:K2_GetActorLocation').find_result_pin()
    location=h.call(g,'/Script/Engine.Actor:K2_GetActorLocation',target=target).find_result_pin()
    delta=h.math(g,'Subtract_VectorVector',location,origin)
    distance=h.math(g,'VSize',delta)
    forward=h.call(g,'/Script/Engine.Actor:GetActorForwardVector').find_result_pin()
    dot=h.math(g,'Dot_VectorVector',h.math(g,'Normal',delta),forward)
    valid=h.all_true(g,h.math(g,'NotEqual_ObjectObject',target,h.self_pin(g)),h.math(g,'LessEqual_DoubleDouble',distance,h.get(g,'A_HeavyRange')),h.math(g,'GreaterEqual_DoubleDouble',dot,0.5))
    yes,_=h.branch(g,loop,valid)
    trace=h.call(g,'/Script/Engine.KismetSystemLibrary:LineTraceSingle',yes,Start=origin,End=location,bIgnoreSelf=True)
    yes,_=h.branch(g,trace.find_then_pin(),h.not_(g,trace.find_output_pin('ReturnValue')))
    implements=h.call(g,'/Script/Engine.KismetSystemLibrary:DoesImplementInterface',TestObject=target,Interface=interface.generated_class().get_path_name()).find_result_pin()
    modern,legacy=h.branch(g,yes,implements)
    message=h.message(g,modern,'ReceiveCombatHit',target)
    hitpin=message.find_input_pin('HitInfo')
    choices=h.actions(g,[hitpin])
    candidates=[x for x in choices if 'hitinfo' in x.lower().replace('_','')]
    key=next(x for x in candidates if any(word in x.lower() for word in ('make','crear')))
    make=g.create_node_from_name(key,u.Vector2D(0,0),[hitpin])
    assert make,'Make ST_HitInfo'
    fields={str(p.get_pin_name()).split('_')[0]:p for p in make.list_input_pins()}
    for key,value in [('Damage',h.get(g,'A_HeavyDamage')),('PostureDamage',h.get(g,'A_HeavyPostureDamage')),('Instigator',h.self_pin(g)),('HitLocation',location),('HitDirection',h.math(g,'Normal',delta)),('bNonLethal',True),('bParryable',True)]:h.value(fields[key],value)
    enum=h.enum_type('EAttackType');values=json.loads(L.pin_type_to_json_schema(enum,u.Actor.static_class()))['enum']
    h.literal(fields['AttackType'],'NewEnumerator'+str(values.index('Heavy')))
    h.connect(make.find_result_pin(),hitpin)
    native=h.call(g,'/Script/Engine.GameplayStatics:ApplyDamage',legacy,DamagedActor=target,BaseDamage=h.get(g,'A_HeavyDamage'),DamageCauser=h.self_pin(g))
    fxcall=h.invoke(g,message.find_then_pin(),bp,'A_HeavyImpactFX',Target=target)
    h.connect(native.find_then_pin(),fxcall.find_execute_pin())

    # Cancel pending hits on accepted damage, death, checkpoint and successful Retake.
    for name in ('TakeHit','Die','B_ResumePlayerAtCheckpoint'):
        g=h.edit(bp,name);insert(g,g.find_graph_entry_pin(),bp,'A_CancelHeavyAttack')
    for name in ('DoDodge','DoParry'):
        g=h.edit(bp,name)
        play=next(n for n in g.list_all_nodes() if str(n.get_node_title())=='PlayOneShot')
        previous,=play.find_execute_pin().list_connected_pins()
        if str(previous.get_owning_node().get_node_title())!='A_CancelHeavyAttack':insert(g,previous,bp,'A_CancelHeavyAttack')
    g=h.edit(bp,'DoRetake')
    node=next(n for n in g.list_all_nodes() if str(n.get_node_title())=='Set Actor Location')
    previous,=node.find_execute_pin().list_connected_pins()
    if str(previous.get_owning_node().get_node_title())!='A_CancelHeavyAttack':insert(g,previous,bp,'A_CancelHeavyAttack')
    g=h.edit(bp,'EventGraph')
    for node in list(g.list_all_nodes()):
        if str(node.get_node_title())=='Set bGameplayInputBlocked':insert(g,node.find_then_pin(),bp,'A_CancelHeavyIfBlocked')
    h.layout(bp,['DoHeavyAttack','A_HeavyHit','A_HeavyImpactFX','A_EndHeavyAttack','A_CancelHeavyAttack','A_CancelHeavyIfBlocked'])
    h.compile_blueprint(bp,warnings_as_errors=True)
    u.get_default_object(bp.generated_class()).set_editor_property('AnimHeavyAttack',h.asset(DEST))
    # Replace just the heavy input's call. Light input and bindings stay intact.
    g=h.edit(controller,'EventGraph');nodes={n.get_name():n for n in g.list_all_nodes()}
    old=nodes.get('K2Node_CallFunction_26')
    if old and str(old.get_node_title())=='DoLightAttack':
        execute,=old.find_execute_pin().list_connected_pins();target,=old.find_self_pin().list_connected_pins()
        old.find_execute_pin().break_pin_links()
        h.invoke(g,execute,bp,'DoHeavyAttack',target)
        g.remove_nodes([old])
    else:assert any(str(n.get_node_title())=='DoHeavyAttack' for n in nodes.values())
    h.save(bp,controller)
    after=snapshot(bp)
    preserved=[name for name in before if before[name]==after[name]]
    (HERE/'uppercut_install.json').write_text(json.dumps({'passed':True,'preserved_graphs':preserved,'changed_graphs':[n for n in before if n not in preserved],'added_graphs':sorted(set(after)-set(before))},indent=2))
    print('UPPERCUT_INSTALLED')

if __name__=='__main__':
    try:main()
    except Exception:
        (HERE/'uppercut_install_error.txt').write_text(traceback.format_exc());raise
    finally:u.SystemLibrary.quit_editor()
