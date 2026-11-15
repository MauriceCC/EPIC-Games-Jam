"""Add a Test-only state fixture; production never references this component.

Worldless state tests cannot drive a viewport dialogue. This fixture supplies
only that completion condition after the unchanged evidence guard succeeds.
Real E confirmation is separately covered by both integrated C-30 Play runs.
"""
import unreal,sys
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
objective=h.asset('Narrative/BP_ObjectiveManager')
bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_C30ProgressionFixture_C')
if not bp:bp=h.create_actor_bp('Narrative/Test','BP_C30ProgressionFixture_C',objective.generated_class())
g=h.edit(bp,'ConfirmRevelationForStateTest')
if g:h.clear_body(g)
else:g=h.function(bp,'ConfirmRevelationForStateTest')
query=h.invoke(g,g.find_graph_entry_pin(),objective,'CanRevealTruth');yes,_=h.branch(g,query.find_then_pin(),query.find_result_pin());h.setvar(g,yes,'bTruthRevelationComplete',True)
h.layout(bp);h.save(bp);print('C30_TEST_STATE_FIXTURE_SAVED')
