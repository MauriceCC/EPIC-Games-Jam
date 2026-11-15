"""One-shot patch after implement_a_sprint_mvp_p1.py (already applied to the saved asset).

The A6 restore condition was (Len(Stamina) == Len(Pos)) AND (Len(Stamina) > 0). The '> 0' literal was lost
when the promotable operator resolved its type, so the branch never restored stamina. DoRetake already requires
Len(PosHistory) > 0 before reaching this point, so equality alone is sufficient: remove the AND and the '>' node.
Saves only Player/BP_PlayerCharacter.
"""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, graph, connect
OUT = {'passed': False, 'checks': []}
def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
try:
    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    g = graph(player, 'DoRetake')
    n = {x.get_name(): x for x in g.list_all_nodes()}
    eq, gt, conj, br = n['K2Node_PromotableOperator_3'], n['K2Node_PromotableOperator_4'], n['K2Node_CommutativeAssociativeBinaryOperator_1'], n['K2Node_IfThenElse_4']
    check('Equality feeds the AND', any(p.get_owning_node().get_name() == conj.get_name() for p in eq.find_result_pin().list_connected_pins()))
    check('AND feeds the restore branch', any(p.get_owning_node().get_name() == conj.get_name() for p in br.find_condition_pin().list_connected_pins()))
    check("'>' is the AND's other input", 'integer > integer' in str(L.get_node_title(gt)))
    len5 = n['K2Node_CallArrayFunction_5']; get16 = n['K2Node_VariableGet_16']
    check('Second Length(StaminaHistory) only feeds the >', [p.get_owning_node().get_name() for p in len5.find_output_pin('ReturnValue').list_connected_pins()] == [gt.get_name()])
    g.remove_nodes([gt, conj, len5, get16])
    connect(eq.find_result_pin(), br.find_condition_pin())
    check('Player compiles', L.compile_blueprint(player))
    check('Save', unreal.EditorAssetLibrary.save_loaded_asset(player, False))
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a6_patch_result.json').write_text(json.dumps(OUT, indent=2), encoding='utf-8')
    print('A6_PATCH passed=%s' % OUT['passed'])
