"""Connect polished action clips and synchronize playback with existing action locks."""
import sys
from pathlib import Path
import unreal as u

repo=Path(u.Paths.project_dir()).resolve().parent
sys.path[:0]=[str(repo/'Scripts/C'),str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h

def main():
    bp=h.asset('Player/BP_PlayerCharacter')
    L=u.BlueprintEditorLibrary
    cdo=u.get_default_object(bp.generated_class())
    for action in ('Attack1','Attack2','Dodge','Parry','Hit','Death'):
        cdo.set_editor_property('Anim'+action,h.asset('Player/Animation/Polish/A_Agent_'+action))
    g=h.edit(bp,'DoLightAttack')
    nodes={n.get_name():n for n in g.list_all_nodes()}
    # The previous pure NOT was evaluated again after flipping the variable.
    # Use the committed choice consistently for clip and both timer durations.
    choice=h.get(g,'bComboAlt')
    for name in ('K2Node_Select_0','K2Node_Select_1','K2Node_Select_2'):
        pin=nodes[name].find_input_pin('Index')
        pin.break_pin_links()
        h.connect(choice,pin)
    for name,seconds in [('K2Node_CallFunction_3',0.6),('K2Node_CallFunction_4',0.75)]:
        assert str(nodes[name].get_node_title())=='Make Literal Float'
        h.literal(nodes[name].find_input_pin('Value'),seconds)
    # Prevent an older one-shot timer from releasing the held death pose.
    g=h.edit(bp,'Die')
    hold=next(n for n in g.list_all_nodes() if str(n.get_node_title())=='PlayAndHold')
    before,=hold.find_execute_pin().list_connected_pins()
    if str(before.get_owning_node().get_node_title())!='Clear Timer by Function Name':
        target,=hold.find_self_pin().list_connected_pins()
        clear=h.call(g,'/Script/Engine.KismetSystemLibrary:K2_ClearTimer',before,Object=target,FunctionName='EndOneShot')
        h.connect(clear.find_then_pin(),hold.find_execute_pin())
    h.save(bp)
    print('A_ANIMATION_POLISH_INSTALLED')

if __name__=='__main__':main()
