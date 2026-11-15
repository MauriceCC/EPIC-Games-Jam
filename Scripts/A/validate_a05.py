"""Fresh-process runtime checks of saved A-05 Blueprint bytecode. No saves.
Run as a commandlet (see Scripts/A/A05_RESISTENCIA.md)."""
import json, traceback
from pathlib import Path
import unreal
HERE = Path(__file__).resolve().parent
OUT = {'passed': False, 'checks': []}
actors = []
def check(name, actual, expected=True):
    if isinstance(actual, float): actual = round(actual, 4)
    if isinstance(actual, list): actual = [round(x, 4) if isinstance(x, float) else x for x in actual]
    ok = actual == expected
    OUT['checks'].append({'name': name, 'actual': actual, 'expected': expected, 'passed': ok})
    assert ok, (name, actual, expected)
def prop(o, n): return o.get_editor_property(n)
def invoke(o, n, *a): return o.call_method(n, args=a)
try:
    combat = unreal.load_asset('/Game/Unscripted/Player/BP_CombatComponent')
    player = unreal.load_asset('/Game/Unscripted/Player/BP_PlayerCharacter')
    hud = unreal.load_asset('/Game/Unscripted/Player/Test/BP_StaminaHUDTest_A')
    for bp in (combat, player, hud): check(bp.get_name() + ' compiles', unreal.BlueprintEditorLibrary.compile_blueprint(bp))
    for bp in (combat, player, hud):
        bad = []
        for raw in unreal.BlueprintEditorLibrary.list_graphs(bp):
            ed = unreal.BlueprintGraphEditor.get_graph_editor(raw)
            bad += [raw.get_name() + ':' + n.get_name() for n in list(ed.list_nodes_with_errors()) + list(ed.list_nodes_with_warnings())]
        check(bp.get_name() + ' has no node errors/warnings', bad, [])
    tun = ['MaxStamina', 'CurrentStamina', 'StaminaRegenRate', 'StaminaRegenDelay', 'LightAttackStaminaCost', 'HeavyAttackStaminaCost', 'DodgeStaminaCost', 'ParryStaminaCost']
    expected = [100, 100, 30, 0.6, 10, 25, 20, 10]
    check('Class defaults (docs/03)', [prop(unreal.get_default_object(combat.generated_class()), n) for n in tun], expected)
    H = unreal.SubobjectDataBlueprintFunctionLibrary
    tpl = [H.get_object(H.get_data(h)) for h in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player)]
    tpl = list({o.get_path_name(): o for o in tpl if o and o.get_class() == combat.generated_class()}.values())
    check('One installed Combat on player', len(tpl), 1)
    check('Player template values', [prop(tpl[0], n) for n in tun], expected)
    ht = [o for o in (H.get_object(H.get_data(h)) for h in unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player)) if o and o.get_class().get_name() == 'BP_HealthComponent_C']
    check('A-04 Health template preserved', [prop(ht[0], n) for n in ('MaxHealth', 'CurrentHealth')], [100, 100])
    check('A-03 rotation setting preserved', unreal.get_default_object(player.generated_class()).get_editor_property('character_movement').get_editor_property('orient_rotation_to_movement'), False)

    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(2): actors.append(eas.spawn_actor_from_class(unreal.Actor, unreal.Vector(i * 300, 0, 0), transient=True))
    a = unreal.new_object(combat.generated_class(), outer=actors[0])
    b = unreal.new_object(combat.generated_class(), outer=actors[1])
    watches = []
    for i in range(2):
        w = unreal.new_object(hud.generated_class(), outer=actors[0])
        w.set_editor_property('bPrintToScreen', False); w.set_editor_property('ObservedCombat', a)
        invoke(w, 'BindCombat'); watches.append(w)
    # BindCombat publishes the current value immediately (1 call per observer), before BeginPlay.
    base = 1
    def state(label, current, changes, pause=None, maximum=100):
        check(label + ' stored', [prop(a, 'CurrentStamina'), prop(a, 'MaxStamina')], [current, maximum])
        for i, w in enumerate(watches):
            check(label + ' observer ' + str(i), [prop(w, n) for n in ('LastCurrent', 'LastMax', 'ChangeCount')], [current, maximum, base + changes])
        if pause is not None: check(label + ' regen pause', prop(a, 'A_RegenPauseRemaining'), pause)
    def tick(dt): invoke(a, 'ReceiveTick', dt)
    def consume(cost): return invoke(a, 'TryConsumeStamina', cost)
    check('Bind shows current value', [prop(watches[0], n) for n in ('LastCurrent', 'LastMax', 'ChangeCount')], [100, 100, 1])
    invoke(a, 'ReceiveBeginPlay'); state('BeginPlay fills and publishes', 100, 1, 0)
    check('Light attack cost accepted', consume(10.0), True); state('Light attack 100-10', 90, 2, 0.6)
    tick(0.25); state('No regen during pause', 90, 2, 0.35)
    tick(0.36); state('Pause expires', 90, 2, 0)
    tick(0.1); state('Regen 30/s after pause', 93, 3, 0)
    check('Dodge accepted', consume(20.0), True); state('Dodge 93-20', 73, 4, 0.6)
    check('Heavy accepted', consume(25.0), True); state('Heavy 73-25', 48, 5, 0.6)
    check('Parry accepted', consume(10.0), True); state('Parry 48-10', 38, 6, 0.6)
    check('Dodge accepted again', consume(20.0), True); state('38-20', 18, 7, 0.6)
    tick(0.3)
    check('HasStamina(20) false at 18', invoke(a, 'HasStamina', 20.0), False)
    check('HasStamina(18) true at 18', invoke(a, 'HasStamina', 18.0), True)
    check('Dodge refused without full cost', consume(20.0), False); state('Refusal changes nothing (no notify, pause kept)', 18, 7, 0.3)
    check('Exact cost accepted', consume(18.0), True); state('Drained to zero', 0, 8, 0.6)
    for c in (10.0, 20.0, 25.0): check('Refused at zero: ' + str(c), consume(c), False)
    state('Zero stays zero', 0, 8, 0.6)
    check('Zero cost accepted, no spend', consume(0.0), True); check('Negative cost accepted, no spend', consume(-5.0), True)
    state('Free actions do not notify or reset pause', 0, 8, 0.6)
    tick(0.6); tick(1.0); state('One second of regen from zero', 30, 9, 0)
    trace = []
    for _ in range(5):
        tick(1.0); trace.append((prop(a, 'CurrentStamina'), prop(watches[0], 'ChangeCount')))
    OUT['regen_trace'] = trace
    state('Regen clamps at max', 100, 12, 0)
    tick(1.0); state('No notifications while full', 100, 12, 0)
    invoke(a, 'SetStamina', 250.0); state('SetStamina upper clamp', 100, 13)
    invoke(a, 'SetStamina', -4.0); state('SetStamina lower clamp', 0, 14)
    invoke(a, 'SetStamina', 50.0); state('SetStamina restore', 50, 15)
    watches[0].set_editor_property('bAttemptReentry', True, unreal.PropertyAccessChangeNotifyMode.NEVER)
    check('Spend during notification target', consume(10.0), True)
    check('Reentrant TryConsume refused', prop(watches[0], 'LastReentryResult'), False)
    watches[0].set_editor_property('bAttemptReentry', False, unreal.PropertyAccessChangeNotifyMode.NEVER); state('Reentry did not mutate', 40, 16, 0.6)
    a.set_editor_property('StaminaRegenRate', -10.0); tick(0.6); tick(1.0); state('Negative rate never drains nor re-notifies', 40, 16, 0)
    a.set_editor_property('StaminaRegenRate', 0.0); tick(1.0); tick(1.0); state('Zero rate never re-notifies', 40, 16, 0)
    a.set_editor_property('StaminaRegenRate', 30.0)
    a.set_editor_property('MaxStamina', 150.0); invoke(a, 'SetStamina', 999.0); state('Custom max', 150, 17, None, 150)
    check('Other component untouched', [prop(b, 'CurrentStamina'), prop(b, 'MaxStamina')], [100, 100])
    check('Second component independent', invoke(b, 'TryConsumeStamina', 30.0), True)
    check('Second component value', prop(b, 'CurrentStamina'), 70)
    check('First observers not notified by second', prop(watches[0], 'ChangeCount'), base + 17)

    # Real player gates: spawn a transient PlayerCharacter in the editor world and call its actions.
    pawn = eas.spawn_actor_from_class(player.generated_class(), unreal.Vector(0, 2000, 300), transient=True); actors.append(pawn)
    comp = pawn.get_component_by_class(combat.generated_class())
    check('Spawned player has Combat', comp is not None)
    # Player flags are not writable from Python on instances: reset them with the player's own End* functions.
    def act(fn, flag, cost, reset):
        check(fn + ' flag starts clear', pawn.get_editor_property(flag), False)
        invoke(comp, 'SetStamina', 100.0)
        invoke(pawn, fn)
        check(fn + ' starts with stamina and spends its cost', [pawn.get_editor_property(flag), prop(comp, 'CurrentStamina')], [True, 100 - cost])
        check(fn + ' pauses regeneration', prop(comp, 'A_RegenPauseRemaining'), 0.6)
        invoke(pawn, reset); check(reset + ' clears flag', pawn.get_editor_property(flag), False)
        invoke(comp, 'SetStamina', cost - 1)
        invoke(pawn, fn)
        check(fn + ' blocked without full stamina', [pawn.get_editor_property(flag), prop(comp, 'CurrentStamina')], [False, cost - 1])
        invoke(comp, 'SetStamina', 0.0); invoke(pawn, fn)
        check(fn + ' blocked at zero', [pawn.get_editor_property(flag), prop(comp, 'CurrentStamina')], [False, 0])
    act('DoParry', 'bParryWindow', 10, 'EndParry')
    act('DoDodge', 'bInvulnerable', 20, 'EndDodge')
    act('DoLightAttack', 'bAttacking', 10, 'EndAttack')
    invoke(comp, 'SetStamina', 100.0); invoke(pawn, 'DoLightAttack'); invoke(pawn, 'DoLightAttack')
    check('Second click during an attack spends nothing (existing guard first)', prop(comp, 'CurrentStamina'), 90)
    invoke(pawn, 'EndAttack')
    OUT['passed'] = True
except Exception:
    OUT['error'] = traceback.format_exc(); unreal.log_error(OUT['error'])
finally:
    for x in actors:
        try: unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(x)
        except Exception: pass
    (HERE / 'a05_validation_result.json').write_text(json.dumps(OUT, indent=2, default=str), encoding='utf-8')
if not OUT['passed']: raise RuntimeError('A-05 validation failed; inspect report')
