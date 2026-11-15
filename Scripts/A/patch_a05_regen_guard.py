"""A-05 follow-up (one-shot, already applied): regenerate only when StaminaRegenRate > 0,
so a zero/negative rate never re-broadcasts OnStaminaChanged every frame. Saves only BP_CombatComponent."""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, G, graph, connect
OUT = {'passed': False}
try:
    combat = unreal.load_asset('/Game/Unscripted/Player/BP_CombatComponent')
    g = graph(combat, 'EventGraph')
    # The regen branch is the only one whose condition comes from a float '<' node.
    def source(b):
        links = b.find_condition_pin().list_connected_pins()
        return links[0] if links else None
    found = [(b, source(b)) for b in g.list_all_nodes() if b.get_class().get_name() == 'K2Node_IfThenElse'
             and source(b) and 'Less' in str(L.get_node_title(source(b).get_owning_node())).replace(' ', '') + source(b).get_owning_node().get_name()
             or (b.get_class().get_name() == 'K2Node_IfThenElse' and source(b) and '<' in str(L.get_node_title(source(b).get_owning_node())))]
    assert len(found) == 1, len(found)
    target = found[0]
    b, less_out = target
    assert 'BooleanAND' not in str([str(L.get_node_title(p.get_owning_node())) for p in less_out.list_connected_pins()])
    b.find_condition_pin().break_pin_links()
    rate = g.add_get_member_variable_node('StaminaRegenRate').find_result_pin()
    gt = g.add_call_function_node('/Script/Engine.KismetMathLibrary:Greater_DoubleDouble')
    connect(rate, gt.find_input_pin('A')); assert gt.find_input_pin('B').set_pin_value('0')
    both = g.add_call_function_node('/Script/Engine.KismetMathLibrary:BooleanAND')
    connect(less_out, both.find_input_pin('A')); connect(gt.find_result_pin(), both.find_input_pin('B'))
    connect(both.find_result_pin(), b.find_condition_pin())
    p = L.get_node_pos(b)
    for i, n in enumerate((rate.get_owning_node(), gt, both)): L.set_node_pos(n, unreal.IntPoint(p.x - 300 + i * 200, p.y + 260))
    assert L.compile_blueprint(combat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(combat)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'a05_patch_result.json').write_text(json.dumps(OUT, indent=2), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('patch failed')
