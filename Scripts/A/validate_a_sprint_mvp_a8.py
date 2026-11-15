"""Read-only validation of A8 (no saves). Full editor: run_validate_a_sprint_mvp_a8_editor.py.
Not a PIE session: saved functions are called on transient actors in the editor world (timers do not tick,
so A_EndHitStop is called directly).
"""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L, snapshot
OUT = {'passed': False, 'checks': [], 'notes': [], 'compile_failures': [], 'mode': 'full editor; editor world; not PIE'}
def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
def invoke(o, n, *a): return o.call_method(n, args=a)
def p(o, n): return o.get_editor_property(n)
def setp(o, n, v): o.set_editor_property(n, v, unreal.PropertyAccessChangeNotifyMode.NEVER)
actors = []
try:
    count = 0
    for path in unreal.EditorAssetLibrary.list_assets('/Game/Unscripted', recursive=True, include_folder=False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.Blueprint):
            count += 1
            if not L.compile_blueprint(asset): OUT['compile_failures'].append(path)
    check('All %d Unscripted Blueprints compile' % count, not OUT['compile_failures'])

    shake = unreal.load_asset('/Game/Unscripted/Player/CS_PlayerHit_A')
    cdo = unreal.get_default_object(shake.generated_class())
    check('Shake is a LegacyCameraShake', isinstance(cdo, unreal.LegacyCameraShake))
    check('Shake duration saved (0.18 s)', abs(cdo.get_editor_property('oscillation_duration') - 0.18) < 1e-4)
    check('Shake location amplitude saved', abs(cdo.get_editor_property('loc_oscillation').get_editor_property('x').get_editor_property('amplitude') - 4.0) < 1e-4)
    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    snap = snapshot(player)
    shakes = [n for n in snap['TakeHit'].values() if 'ClientStartCameraShake' in n['title'].replace(' ', '')]
    check('TakeHit starts CS_PlayerHit_A', len(shakes) == 1 and 'CS_PlayerHit_A' in shakes[0]['pins']['Shake']['value'])

    for name in ('HealthComp', 'A_HitStopTargets'):
        L.set_blueprint_variable_instance_editable(player, name, True)  # in memory only
    check('Player recompiles for the in-memory test', L.compile_blueprint(player))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    guard_bp = unreal.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
    pawn = eas.spawn_actor_from_class(player.generated_class(), unreal.Vector(0, 20000, 120), unreal.Rotator(0, 0, 0), transient=True); actors.append(pawn)
    guard = eas.spawn_actor_from_class(guard_bp.generated_class(), unreal.Vector(110, 20000, 120), unreal.Rotator(0, 180, 0), transient=True); actors.append(guard)
    far = eas.spawn_actor_from_class(guard_bp.generated_class(), unreal.Vector(900, 20000, 120), transient=True); actors.append(far)
    health0 = p(guard, 'B_Health')
    invoke(pawn, 'AttackHit')
    OUT['notes'].append('guard health %s -> %s' % (health0, p(guard, 'B_Health')))
    check('Hit enemy slows to 0.05', abs(guard.get_editor_property('custom_time_dilation') - 0.05) < 1e-4)
    check('Enemy out of range is not slowed', abs(far.get_editor_property('custom_time_dilation') - 1.0) < 1e-4)
    check('Player itself is not slowed (no global hit-stop)', abs(pawn.get_editor_property('custom_time_dilation') - 1.0) < 1e-4)
    check('Hit enemy remembered once', [a.get_name() for a in p(pawn, 'A_HitStopTargets')] == [guard.get_name()])
    invoke(pawn, 'AttackHit')
    check('A second hit does not duplicate the target', len(p(pawn, 'A_HitStopTargets')) == 1)
    invoke(pawn, 'A_EndHitStop')
    check('A_EndHitStop restores 1.0', abs(guard.get_editor_property('custom_time_dilation') - 1.0) < 1e-4)
    check('A_EndHitStop forgets the targets', len(p(pawn, 'A_HitStopTargets')) == 0)
    setp(pawn, 'A_HitStopTargets', [guard, far]); far.destroy_actor()
    invoke(pawn, 'A_EndHitStop')
    check('A destroyed target is skipped safely', len(p(pawn, 'A_HitStopTargets')) == 0)

    health_cls = unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class()
    hc = pawn.get_component_by_class(health_cls); setp(pawn, 'HealthComp', hc)
    h0 = p(hc, 'CurrentHealth')
    invoke(pawn, 'TakeHit', 10.0)
    check('TakeHit still applies damage with no player controller (shake skipped)', abs(p(hc, 'CurrentHealth') - (h0 - 10.0)) < 0.01)
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    for a in actors:
        try: a.destroy_actor()
        except Exception: pass
    (HERE / 'a_sprint_mvp_a8_validation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
    print('A8_VALIDATION passed=%s' % OUT['passed'])
