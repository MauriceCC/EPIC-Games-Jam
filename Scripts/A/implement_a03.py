"""One-time A-03 editor migration. Run with the interactive editor CLOSED.

Preserves existing graphs, checks unexpected changes, compiles, saves only A's
PlayerCharacter. Aborts if already applied; never rebuilds authored functions.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
import unreal

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import PATH, FUNCTION, L, G, graph, connect, snapshot, outgoing, find_tick, assert_preserved

ROOT = HERE.parent.parent
FILE = ROOT / 'Unscripted/Content/Unscripted/Player/BP_PlayerCharacter.uasset'
CONTROLLER = FILE.with_name('BP_PlayerController.uasset')
OUT = {'passed': False, 'saved': False, 'checks': [], 'scope': PATH, 'base_commit': 'b2ceb53'}

def check(name, value):
    OUT['checks'].append({'name': name, 'passed': bool(value)})
    assert value, name

try:
    bp = unreal.load_asset(PATH)
    check('Fresh target: helper is not already authored', FUNCTION not in [g.get_name() for g in L.list_graphs(bp)])
    before = snapshot(bp)
    event = graph(bp, 'EventGraph')
    tick = find_tick(event)
    old_links = outgoing(tick.find_then_pin())
    check('Tick has exactly one existing continuation', len(old_links) == 1)
    old_next = old_links[0]
    next_id = (old_next.get_owning_node().get_name(), str(old_next.get_pin_name()))
    check('FaceCursor existing trace and yaw implementation present', 'FaceCursor' in before and len(before['FaceCursor']) == 10)
    check('Required existing bDead field present', 'bDead' in [str(n) for n in L.list_member_variable_names(bp)])
    controller_hash = hashlib.sha256(CONTROLLER.read_bytes()).hexdigest()
    backup = Path(tempfile.mkdtemp(prefix='Unscripted_A03_')) / FILE.name
    shutil.copy2(FILE, backup)
    OUT['backup'] = str(backup)
    OUT['sha256_before'] = hashlib.sha256(FILE.read_bytes()).hexdigest()

    # This internal helper never changes translation or mapping contexts.
    helper = G.create_and_edit_function_graph(bp, FUNCTION)
    helper.set_function_is_private()
    local = helper.add_call_function_node('/Script/Engine.Pawn:IsLocallyControlled')
    dead = helper.add_get_member_variable_node('bDead', '')
    alive = helper.add_call_function_node('/Script/Engine.KismetMathLibrary:Not_PreBool')
    connect(dead.find_result_pin(), alive.find_input_pin('A'))
    allowed = helper.add_call_function_node('/Script/Engine.KismetMathLibrary:BooleanAND')
    connect(local.find_result_pin(), allowed.find_input_pin('A'))
    connect(alive.find_result_pin(), allowed.find_input_pin('B'))
    branch = helper.add_branch_node()
    connect(helper.find_graph_entry_pin(), branch.find_execute_pin())
    connect(allowed.find_result_pin(), branch.find_condition_pin())
    face = helper.add_call_function_node(bp.generated_class().get_path_name() + ':FaceCursor')
    connect(branch.find_then_pin(), face.find_execute_pin())
    for node, x, y in [(local,0,180),(dead,0,330),(alive,220,330),(allowed,440,180),(branch,660,0),(face,900,0)]:
        L.set_node_pos(node, unreal.IntPoint(x,y))
    check('Helper compiles before event hookup', L.compile_blueprint(bp))

    # Reacquire pin handles after compilation, then splice one call into Tick.
    event = graph(bp, 'EventGraph')
    tick = find_tick(event)
    old_next = outgoing(tick.find_then_pin())[0]
    update = event.add_call_function_node(bp.generated_class().get_path_name() + ':' + FUNCTION)
    check('Disconnect only original Tick edge', unreal.BlueprintGraphPinLibrary.break_single_pin_link(tick.find_then_pin(), old_next))
    connect(tick.find_then_pin(), update.find_execute_pin())
    connect(update.find_then_pin(), old_next)
    L.set_node_pos(update, unreal.IntPoint(-300,700))
    check('PlayerCharacter compiles after Tick hookup', L.compile_blueprint(bp))

    # CharacterMovement must not compete with cursor yaw when WASD is held.
    defaults = unreal.get_default_object(bp.generated_class())
    movement = defaults.get_editor_property('character_movement')
    OUT['orient_rotation_to_movement_before'] = movement.get_editor_property('orient_rotation_to_movement')
    movement.set_editor_property('orient_rotation_to_movement', False)
    check('Movement no longer overrides cursor yaw', not movement.get_editor_property('orient_rotation_to_movement'))
    check('Controller yaw already disabled', not defaults.get_editor_property('use_controller_rotation_yaw'))
    after = snapshot(bp)
    assert_preserved(before, after, tick.get_name(), next_id, update.get_name())
    check('Every original graph/pin preserved except the single Tick edge', True)
    check('Controller file unchanged', hashlib.sha256(CONTROLLER.read_bytes()).hexdigest() == controller_hash)
    check('Save only PlayerCharacter', unreal.EditorAssetLibrary.save_loaded_asset(bp))
    OUT['saved'] = True
    OUT['sha256_after'] = hashlib.sha256(FILE.read_bytes()).hexdigest()
    OUT['controller_sha256'] = controller_hash
    OUT['tick_node'] = tick.get_name()
    OUT['original_continuation'] = next_id
    OUT['update_call'] = update.get_name()
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc()
    unreal.log_error(OUT['error'])
finally:
    (HERE/'a03_implementation_result.json').write_text(json.dumps(OUT,indent=2),encoding='utf-8')
if not OUT['passed']:
    raise RuntimeError('A-03 failed; read a03_implementation_result.json. Do not rerun over a saved migration.')
