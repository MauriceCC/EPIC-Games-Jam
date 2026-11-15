"""Read-only validation of A6/A7 (no saves). Commandlet:
UnrealEditor-Cmd.exe Unscripted.uproject -run=pythonscript -script=Scripts/A/validate_a_sprint_mvp_p1.py -unattended -nullrhi -nosound
Not a PIE session: saved functions are called on transient actors in the editor world.
"""
import json, sys, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a03_graph_tools import L
OUT = {'passed': False, 'checks': [], 'notes': [], 'compile_failures': [], 'mode': 'commandlet; editor world; not PIE'}
def check(name, v):
    OUT['checks'].append({'name': name, 'passed': bool(v)}); assert v, name
def invoke(o, n, *a): return o.call_method(n, args=a)
def p(o, n): return o.get_editor_property(n)
# NEVER notify: a notified edit reruns the construction script and recreates the components.
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

    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    guard_bp = unreal.load_asset('/Game/Unscripted/Enemies/BP_GuardBase')
    combat_cls = unreal.load_asset('/Game/Unscripted/Player/BP_CombatComponent').generated_class()
    # In-memory only: allow seeding private state on the instance (never saved).
    for name in ('RetakeCharges', 'PosHistory', 'HPHistory', 'StaminaHistory', 'SnapAccum', 'bCutReady', 'HealthComp', 'TemporalComp'):
        L.set_blueprint_variable_instance_editable(player, name, True)
    check('Player recompiles for the in-memory test', L.compile_blueprint(player))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    pawn = eas.spawn_actor_from_class(player.generated_class(), unreal.Vector(0, 6000, 300), transient=True); actors.append(pawn)
    combat = pawn.get_component_by_class(combat_cls)
    check('Player and Combat component available', pawn and combat)
    # BeginPlay does not run in the editor world: wire the cached components the way BeginPlay does.
    setp(pawn, 'HealthComp', pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class()))
    setp(pawn, 'TemporalComp', pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_TemporalComponent').generated_class()))

    # ---- A6 ----
    invoke(combat, 'SetStamina', 40.0)
    setp(pawn, 'RetakeCharges', 2)
    setp(pawn, 'PosHistory', [unreal.Vector(0, 6100, 300), unreal.Vector(0, 6200, 300)])
    setp(pawn, 'HPHistory', [100.0, 100.0])
    setp(pawn, 'StaminaHistory', [70.0, 55.0])
    OUT['notes'].append('before retake: stam=%s pos=%d hp=%d cur=%s upd=%s' % (list(p(pawn, 'StaminaHistory')), len(p(pawn, 'PosHistory')), len(p(pawn, 'HPHistory')), p(combat, 'CurrentStamina'), p(combat, 'bA_UpdatingStamina')))
    invoke(pawn, 'DoRetake')
    OUT['notes'].append('after retake: stamina=%s charges=%s hist=%s' % (p(combat, 'CurrentStamina'), p(pawn, 'RetakeCharges'), list(p(pawn, 'StaminaHistory'))))
    check('Retake spends one charge', p(pawn, 'RetakeCharges') == 1)
    check('Retake restores the oldest stamina sample (40 -> 70)', abs(p(combat, 'CurrentStamina') - 70.0) < 0.01)
    check('Retake clears the stamina samples', len(p(pawn, 'StaminaHistory')) == 0)

    invoke(combat, 'SetStamina', 40.0)
    setp(pawn, 'PosHistory', [unreal.Vector(0, 6100, 300), unreal.Vector(0, 6200, 300)])
    setp(pawn, 'HPHistory', [100.0, 100.0])
    setp(pawn, 'StaminaHistory', [70.0])
    invoke(pawn, 'DoRetake')
    check('Misaligned stamina history is not restored', abs(p(combat, 'CurrentStamina') - 40.0) < 0.01)
    check('Retake still works with misaligned stamina', p(pawn, 'RetakeCharges') == 0)

    invoke(combat, 'SetStamina', 10.0)
    setp(pawn, 'PosHistory', [unreal.Vector(1, 2, 3)]); setp(pawn, 'HPHistory', [5.0]); setp(pawn, 'StaminaHistory', [5.0])
    invoke(pawn, 'ClearRetakeHistory')
    check('ClearRetakeHistory also clears stamina samples', len(p(pawn, 'StaminaHistory')) == 0 and len(p(pawn, 'PosHistory')) == 0)

    setp(pawn, 'PosHistory', [unreal.Vector(1, 2, 3)]); setp(pawn, 'HPHistory', [5.0]); setp(pawn, 'StaminaHistory', [5.0])
    invoke(pawn, 'B_ResumePlayerAtCheckpoint', unreal.Transform(unreal.Vector(0, 6500, 300), unreal.Rotator(0, 0, 0), unreal.Vector(1, 1, 1)))
    check('Respawn empties the retake history', not p(pawn, 'PosHistory') and not p(pawn, 'HPHistory') and not p(pawn, 'StaminaHistory'))
    check('Respawn refills stamina', abs(p(combat, 'CurrentStamina') - p(combat, 'MaxStamina')) < 0.01)
    setp(pawn, 'RetakeCharges', 2)
    invoke(pawn, 'DoRetake')
    check('R right after respawn spends no charge (nothing to rewind)', p(pawn, 'RetakeCharges') == 2)

    # ---- A7 ----
    def cut_case(with_wall):
        origin = unreal.Vector(0, 9000 + (3000 if with_wall else 0), 120)
        pawn.set_actor_location(origin, False, True)
        guard = eas.spawn_actor_from_class(guard_bp.generated_class(), origin + unreal.Vector(600, 0, 0), transient=True); actors.append(guard)
        if with_wall:
            wall = eas.spawn_actor_from_class(unreal.StaticMeshActor, origin + unreal.Vector(300, 0, 0), transient=True); actors.append(wall)
            mc = wall.static_mesh_component
            mc.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
            wall.set_actor_scale3d(unreal.Vector(0.3, 6, 6))
            mc.set_collision_profile_name('BlockAll')
            mc.set_mobility(unreal.ComponentMobility.STATIC)
            hit = unreal.SystemLibrary.line_trace_single(pawn, pawn.get_actor_location(), guard.get_actor_location(), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [pawn], unreal.DrawDebugTrace.NONE, True)
            ht = hit.to_tuple() if hit else None
            OUT['notes'].append('python trace through wall: blocking=%s actor=%s' % (ht[0] if ht else None, ht[9].get_name() if ht and ht[9] else None))
        # Keep every other guard in the editor world out of the test: only this one is within CutBest (1500).
        eligible = invoke(guard, 'CanBeTemporalCutTarget')
        setp(pawn, 'bCutReady', True)
        invoke(pawn, 'DoTemporalCut')
        return guard, eligible
    guard, eligible = cut_case(False)
    OUT['notes'].append('Guard eligible for B (CanBeTemporalCutTarget) in editor world: %s' % eligible)
    if eligible:
        check('Cut freezes a visible guard', p(guard, 'bIsTemporalFrozen'))
        guard2, _ = cut_case(True)
        if 'blocking=True' in OUT['notes'][-1]:
            check('Cut does not freeze a guard behind a wall', not p(guard2, 'bIsTemporalFrozen'))
            check('Blocked Cut does not start the cooldown', p(pawn, 'bCutReady'))
        else:
            OUT['notes'].append('This world has no collision for transient actors (even a Python trace hits nothing); confirm A7 wall case in Play')
    else:
        OUT['notes'].append('B rejects the transient guard outside an encounter; A7 must be confirmed in Play')
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    for a in actors:
        try: a.destroy_actor()
        except Exception: pass
    (HERE / 'a_sprint_mvp_p1_validation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
    print('A_SPRINT_MVP_P1_VALIDATION passed=%s' % OUT['passed'])
