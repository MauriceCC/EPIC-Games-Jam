"""One-shot patch: Retake buffer 30 -> 50 samples (0.1 s each = 5 s), as docs/04 specifies.
Approved by Mauricio on 2026-11-15. Changes one literal in the Tick sampling of Player/BP_PlayerCharacter.
"""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, graph
OUT = {'passed': False, 'checks': []}
def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
try:
    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    g = graph(player, 'EventGraph')
    n = {x.get_name(): x for x in g.list_all_nodes()}
    lit, cmp_ = n['K2Node_CallFunction_6'], n['K2Node_PromotableOperator_2']
    pin = lit.find_input_pin('Value')
    check('Literal is the 30-sample cap', 'MakeLiteralInt' in str(L.get_node_title(lit)).replace(' ', '') and pin.get_pin_value() == '30')
    check('Literal feeds Length(PosHistory) > cap', any(p.get_owning_node().get_name() == cmp_.get_name() for p in lit.find_result_pin().list_connected_pins()))
    check('Set to 50', pin.set_pin_value('50'))
    check('Player compiles', L.compile_blueprint(player))
    check('Value saved as 50', pin.get_pin_value() == '50')
    check('Save', unreal.EditorAssetLibrary.save_loaded_asset(player, False))
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    (HERE / 'retake_buffer_5s_result.json').write_text(json.dumps(OUT, indent=2), encoding='utf-8')
    print('RETAKE_BUFFER_PATCH passed=%s' % OUT['passed'])
