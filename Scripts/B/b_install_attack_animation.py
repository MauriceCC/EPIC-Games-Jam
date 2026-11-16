"""[PROPUESTA] Connect skeleton-specific attacks to existing windup; no damage changes."""
import sys
from pathlib import Path
import unreal as u

repo=Path(u.Paths.project_dir()).resolve().parent
sys.path[:0]=[str(repo/'Scripts/C'),str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h

ROOT='/Game/Unscripted/'
L=u.BlueprintEditorLibrary
guard=h.asset('Enemies/BP_GuardBase')
loco=h.asset('Art/Characters/Shared/BP_LocomotionAnim')

def component(g):
    return h.call(g,'/Script/Engine.Actor:GetComponentByClass',ComponentClass=loco.generated_class().get_path_name()).find_result_pin()

def fresh(name):
    g=h.edit(guard,name)
    if g: h.clear_body(g)
    else: g=h.function(guard,name)
    return g

def insert(g,source,name):
    targets=list(source.list_connected_pins())
    if any(str(p.get_owning_node().get_node_title())==name for p in targets):return
    source.break_pin_links()
    n=h.invoke(g,source,guard,name)
    for p in targets:h.connect(n.find_then_pin(),p)

def main():
    h.variable(guard,'bB_AttackVisualActive',h.basic('bool'),False,category='Animation')
    assert L.compile_blueprint(guard)
    g=fresh('B_PlayAttackVisual')
    comp=component(g)
    start,_=h.branch(g,g.find_graph_entry_pin(),h.is_valid(g,comp))
    mesh=h.get(g,'Mesh')
    model=h.call(g,'/Script/Engine.SkeletalMeshComponent:GetSkeletalMeshAsset',target=mesh).find_result_pin()
    duration=h.math(g,'Divide_DoubleDouble',h.math(g,'FMax',h.get(g,'B_WindupSeconds'),0.05),0.6)
    for who in ('Pursuer_A','Pursuer_B','Interventor','Supervisor'):
        yes,start=h.branch(g,start,h.math(g,'EqualEqual_ObjectObject',model,ROOT+'Art/Characters/SK_'+who+'/SK_'+who+'.SK_'+who))
        yes=h.setvar(g,yes,'bB_AttackVisualActive',True)
        clip=h.asset('Enemies/Animation/Polish/A_'+who+'_Attack')
        h.invoke(g,yes,loco,'PlayOneShot',comp,Anim=clip.get_path_name(),Duration=duration)
    g=fresh('B_HoldAttackVisual')
    start,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bB_AttackVisualActive'))
    comp=component(g)
    start,_=h.branch(g,start,h.is_valid(g,comp))
    h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=comp,FunctionName='EndOneShot')
    g=fresh('B_CancelAttackVisual')
    start,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bB_AttackVisualActive'))
    start=h.setvar(g,start,'bB_AttackVisualActive',False)
    comp=component(g)
    start,_=h.branch(g,start,h.is_valid(g,comp))
    clear=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',start,Object=comp,FunctionName='EndOneShot')
    h.invoke(g,clear.find_then_pin(),loco,'EndOneShot',comp)
    assert L.compile_blueprint(guard)
    g=fresh('B_CheckAttackVisual')
    interrupted=h.any_true(g,h.get(g,'bB_Stunned'),h.math(g,'LessEqual_IntInt',h.get(g,'B_Health'),0))
    start,_=h.branch(g,g.find_graph_entry_pin(),interrupted)
    h.invoke(g,start,guard,'B_CancelAttackVisual')
    assert L.compile_blueprint(guard)
    g=h.edit(guard,'B_BeginParryCue')
    insert(g,g.find_graph_entry_pin(),'B_PlayAttackVisual')
    g=h.edit(guard,'B_UpdateStaggerPose')
    insert(g,g.find_graph_entry_pin(),'B_CheckAttackVisual')
    g=h.edit(guard,'ApplyTemporalFreeze')
    # Run only on an accepted freeze, after the frozen flag is set.
    flag=next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_VariableSet) and n.find_input_pin('bIsTemporalFrozen').is_valid())
    insert(g,flag.find_then_pin(),'B_HoldAttackVisual')
    g=h.edit(guard,'EventGraph')
    for name,method in [('B_EndTemporalFreeze','B_CancelAttackVisual'),('B_PlayKnockoutFall','B_CancelAttackVisual')]:
        event=next(n for n in g.list_all_nodes() if isinstance(n,u.K2Node_CustomEvent) and str(n.get_node_title())==name)
        insert(g,event.find_then_pin(),method)
    h.save(guard)
    print('B_ATTACK_ANIMATION_INSTALLED')

if __name__=='__main__':main()
