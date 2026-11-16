"""Reload/compile A-03 and verify saved wiring; never saves any package."""
import hashlib
import json
from pathlib import Path
import sys
import traceback
import unreal

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import PATH, FUNCTION, L, graph, find_tick, outgoing, snapshot

OUT = {'passed': False, 'checks': [], 'mode': 'fresh commandlet; no mouse/PIE validation'}
def check(name, value):
    OUT['checks'].append({'name':name,'passed':bool(value)})
    assert value, name

try:
    build = json.loads((HERE/'a03_implementation_result.json').read_text(encoding='utf-8'))
    root = HERE.parent.parent
    bp = unreal.load_asset(PATH)
    check('Reloaded saved character', bool(bp))
    check('PlayerCharacter compiles after reload', L.compile_blueprint(bp))
    defaults = unreal.get_default_object(bp.generated_class())
    movement = defaults.get_editor_property('character_movement')
    check('Saved movement cannot rotate toward WASD', not movement.get_editor_property('orient_rotation_to_movement'))
    check('Controller yaw cannot override cursor yaw', not defaults.get_editor_property('use_controller_rotation_yaw'))
    event = graph(bp,'EventGraph')
    tick = find_tick(event)
    links = outgoing(tick.find_then_pin())
    check('Tick has one update call', len(links)==1 and links[0].get_owning_node().get_name()==build['update_call'])
    update = links[0].get_owning_node()
    check('Tick invokes correct private helper', str(L.get_node_title(update)).replace(' ','') == FUNCTION)
    links = outgoing(update.find_then_pin())
    check('Existing snapshot chain still follows helper', len(links)==1 and [links[0].get_owning_node().get_name(),str(links[0].get_pin_name())]==build['original_continuation'])
    nodes = list(graph(bp,FUNCTION).list_all_nodes())
    titles = [str(L.get_node_title(n)).replace(' ','') for n in nodes]
    check('Local control is required', 'IsLocallyControlled' in titles)
    check('Dead guard retained', 'GetbDead' in titles)
    check('Exactly one FaceCursor call in helper', titles.count('FaceCursor')==1)
    face_graph = snapshot(bp)['FaceCursor']
    check('Existing hit-test based cursor function retained', len(face_graph)==10 and any(n['title']=='GetHitResultUnderCursorByChannel' for n in face_graph.values()))
    check('Existing FaceCursor rotates yaw only', any(n['title']=='MakeRotator' and n['pins']['Pitch']['value']=='0.0' and n['pins']['Roll']['value']=='0.0' for n in face_graph.values()))
    check('Movement graph retained', len(snapshot(bp)['DoMove'])==8)
    controller_file = root/'Unscripted/Content/Unscripted/Player/BP_PlayerController.uasset'
    check('Entire controller asset unchanged', hashlib.sha256(controller_file.read_bytes()).hexdigest()==build['controller_sha256'])
    # Exercise the guard on the real generated class with no controller/world.
    # If it falls through, FaceCursor would try to use a missing controller.
    before_rotation = defaults.get_actor_rotation()
    before_location = defaults.get_actor_location()
    defaults.call_method(FUNCTION)
    check('Unpossessed character leaves orientation unchanged', defaults.get_actor_rotation()==before_rotation)
    check('Orientation helper never moves an unpossessed character', defaults.get_actor_location()==before_location)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc()
    unreal.log_error(OUT['error'])
finally:
    OUT['check_count'] = len(OUT['checks'])
    (HERE/'a03_validation.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A-03 validation failed; see a03_validation.json')
