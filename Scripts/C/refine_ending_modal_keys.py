"""Use native key-repeat rejection for the C-only registration modal."""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'));import blueprint_helpers_c as h
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
bp=h.asset('UI/WBP_Ending');g=h.edit(bp,'OnKeyDown');h.clear_body(g)
key=h.call(g,'/Script/Engine.KismetInputLibrary:GetKey',Input=h.param(g,'InKeyEvent')).find_result_pin()
def equal(value):return h.call(g,'/Script/Engine.KismetInputLibrary:EqualEqual_KeyKey',A=key,B=value).find_result_pin()
repeat=h.call(g,'/Script/Engine.KismetInputLibrary:InputEvent_IsRepeat',Input=h.param(g,'InKeyEvent')).find_result_pin()
yes,no=h.branch(g,g.find_graph_entry_pin(),h.all_true(g,h.get(g,'bConfirmationMode'),equal('E'),h.not_(g,repeat)));confirmed=h.invoke(g,yes,bp,'RequestConfirm').find_then_pin();yes,no=h.branch(g,no,h.all_true(g,h.get(g,'bConfirmationMode'),equal('BackSpace')));cancelled=h.invoke(g,yes,bp,'RequestCancel').find_then_pin()
n=g.add_branch_node();h.literal(n.find_input_pin('Condition'),True)
for p in (confirmed,cancelled):h.connect(p,n.find_execute_pin())
h.result(g,n.find_output_pin('then'),ReturnValue=h.call(g,'/Script/UMG.WidgetBlueprintLibrary:Handled').find_result_pin())
h.result(g,no,ReturnValue=h.call(g,'/Script/UMG.WidgetBlueprintLibrary:Unhandled').find_result_pin());h.layout(bp,['OnKeyDown']);h.save(bp);print('C_ENDING_MODAL_KEYS_REFINED')
