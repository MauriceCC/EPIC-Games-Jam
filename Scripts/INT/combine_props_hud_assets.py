"""[PROPUESTA] Reconcile the authorized main/props-HUD binary integration in UE.

Base: main's player and B sublevel, C's Story/final assets, Git-merged components.
Run once with the interactive editor closed. Save only the named packages.
"""
import json
import sys
import traceback
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.dont_write_bytecode = True
sys.path[:0] = [str(repo / 'Scripts/C'), str(repo / 'Scripts/A'),
    str(Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h
from a03_graph_tools import snapshot, assert_preserved, find_tick

outdir = repo / 'Unscripted/Saved/PropsHudMerge'
outdir.mkdir(parents=True, exist_ok=True)
report = {'passed': False, 'checks': [], 'saved': [], 'removed_duplicates': []}

def check(name, value):
    report['checks'].append({'name': name, 'passed': bool(value)})
    assert value, name

def save(bp):
    h.save(bp)
    report['saved'].append(bp.get_path_name())

try:
    player = h.asset('Player/BP_PlayerCharacter')
    combat = h.asset('Player/BP_CombatComponent')
    health = h.asset('Player/BP_HealthComponent')
    before = snapshot(player)
    check('Fresh main player has checkpoint restoration and no A-03 yet',
          'B_ResumePlayerAtCheckpoint' in before and 'A_UpdateCursorFacing' not in before)
    h.compile_blueprint(player, warnings_as_errors=True)
    g = h.function(player, 'A_UpdateCursorFacing', private=True)
    local = h.call(g, '/Script/Engine.Pawn:IsLocallyControlled').find_result_pin()
    yes, _ = h.branch(g, g.find_graph_entry_pin(), h.all_true(g, local, h.not_(g, h.get(g, 'bDead'))))
    h.invoke(g, yes, player, 'FaceCursor')
    h.compile_blueprint(player, warnings_as_errors=True)
    g = h.edit(player, 'EventGraph')
    tick = find_tick(g)
    old_next, = tick.find_then_pin().list_connected_pins()
    old_id = (old_next.get_owning_node().get_name(), str(old_next.get_pin_name()))
    tick.find_then_pin().break_pin_links()
    update = h.invoke(g, tick.find_then_pin(), player, 'A_UpdateCursorFacing')
    h.connect(update.find_then_pin(), old_next)
    assert_preserved(before, snapshot(player), tick.get_name(), old_id, update.get_name())
    check('A-03 preserves every main node, including locomotion and checkpoint logic', True)
    cdo = u.get_default_object(player.generated_class())
    cdo.character_movement.set_editor_property('orient_rotation_to_movement', False)
    check('Controller yaw does not compete with cursor', not cdo.use_controller_rotation_yaw)

    before_gates = snapshot(player)
    altered = {}
    for function, cost in [('DoLightAttack', 'LightAttackStaminaCost'),
                           ('DoDodge', 'DodgeStaminaCost'), ('DoParry', 'ParryStaminaCost')]:
        g = h.edit(player, function)
        nodes = {n.get_name(): n for n in g.list_all_nodes()}
        start = nodes['K2Node_IfThenElse_0'].find_then_pin()
        target = nodes['K2Node_VariableSet_0'].find_execute_pin()
        check(function + ' original guard edge', any(p.is_same_native_pin(target) for p in start.list_connected_pins()))
        start.break_pin_links()
        component = h.get(g, 'BP_CombatComponent')
        requested = h.get(g, cost, component, combat.generated_class())
        spend = h.invoke(g, start, combat, 'TryConsumeStamina', target=component, Cost=requested)
        yes, _ = h.branch(g, spend.find_then_pin(), spend.find_output_pin('bConsumed'))
        h.connect(yes, target)
        altered[function] = {('K2Node_IfThenElse_0', 'then'), ('K2Node_VariableSet_0', 'execute')}
    after_gates = snapshot(player)
    for name, nodes in before_gates.items():
        for node_name, node in nodes.items():
            new = after_gates[name][node_name]
            check_detail = (name, node_name)
            assert node['class'] == new['class'] and node['title'] == new['title'], check_detail
            assert node['pins'].keys() == new['pins'].keys(), check_detail
            for pin, old in node['pins'].items():
                actual = new['pins'][pin]
                assert old['value'] == actual['value'] and old['type'] == actual['type'], (*check_detail, pin)
                if (node_name, pin) not in altered.get(name, set()):
                    assert old['links'] == actual['links'], (*check_detail, pin)
    check('A-05 changes only the three authored action guard edges', True)
    helper = u.SubobjectDataBlueprintFunctionLibrary
    for handle in u.get_engine_subsystem(u.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(player):
        obj = helper.get_object(helper.get_data(handle))
        if obj and obj.get_class() == health.generated_class():
            obj.set_editor_property('MaxHealth', 100.0)
            obj.set_editor_property('CurrentHealth', 100.0)
        if obj and obj.get_class() == combat.generated_class():
            for name, value in [('MaxStamina', 100.0), ('CurrentStamina', 100.0),
                ('StaminaRegenRate', 30.0), ('StaminaRegenDelay', .6),
                ('LightAttackStaminaCost', 10.0), ('HeavyAttackStaminaCost', 25.0),
                ('DodgeStaminaCost', 20.0), ('ParryStaminaCost', 10.0)]:
                obj.set_editor_property(name, value)
    save(player)

    levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    check('Whitechapel loads', levels.load_level('/Game/Unscripted/Maps/L_Whitechapel'))
    placed = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    check('B encounters remain', all(n in placed for n in ['B_Jack_Workshop', 'B_Interventor', 'B_Supervisor']))
    story_package = placed['C_ArchiveGate'].get_outermost()
    ai_package = placed['B_ArchiveGate'].get_outermost()
    # B already supplies an encounter-gated subclass of C's BP_Door. Reuse that
    # hierarchy for the Archive, with C's authored mesh/animation configuration.
    # GuardBase has local IsDefeated but does not yet implement BPI_Damageable;
    # keep that compatibility query inside B rather than adding a C -> B cast.
    template = placed['C_ArchiveGate']
    location, rotation = template.get_actor_location(), template.get_actor_rotation()
    check('Replace the Archive instance with the existing B door subclass', actors.destroy_actor(template))
    check('Select Story for the reconciled gate', levels.set_current_level_by_name('L_Whitechapel_Story'))
    gate_bp = h.asset('Enemies/BP_ArchiveEncounterDoor')
    gate = actors.spawn_actor_from_class(gate_bp.generated_class(), location, rotation)
    check('Encounter gate is placed in Story', gate is not None and gate.get_outermost() == story_package)
    gate.set_actor_label('C_ArchiveGate')
    for name, value in [('DoorWidth', 400.), ('bDoubleLeaf', False), ('bReportsEscapeRoute', False),
                        ('bB_RequiresSupervisor', False), ('bRequireSupervisorDefeat', False),
                        ('InteractionPriority', 40), ('InteractionPromptRow', 'None'),
                        ('InteractionPrompt', 'Open archive gate')]:
        gate.set_editor_property(name, value)
    gate.set_editor_property('RequiredPhase', type(gate.get_editor_property('RequiredPhase')).cast(4))
    art = h.asset('Art/Props/SM_IronGate_A/SM_IronGate_A')
    bounds = art.get_bounding_box()
    mesh = gate.get_editor_property('DoorMesh')
    mesh.set_static_mesh(art)
    mesh.set_relative_scale3d(u.Vector(400. / (bounds.max.x - bounds.min.x), 1., 300. / (bounds.max.z - bounds.min.z)))
    mesh.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    secondary = gate.get_editor_property('RightDoorMesh')
    secondary.set_static_mesh(None)
    secondary.set_visibility(False)
    secondary.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    gate.get_editor_property('PassageBlocker').set_box_extent(u.Vector(200, 18, 150))
    gate.get_editor_property('DoorNavigation').set_editor_property('failsafe_extent', u.Vector(200, 20, 300))
    gate.call_method('ApplyDoorPose', args=(0.,))
    # C's animated door owns the physical opening. Both old B and new C doors at
    # the same position would otherwise block one another after interaction.
    for label in ['B_WorkshopEscapeDoor', 'B_ArchiveGate', 'B_RecordsDoor']:
        actor = placed[label]
        check(label + ' is the duplicate in the AI sublevel', actor.get_outermost() == ai_package)
        check(label + ' duplicate removed', actors.destroy_actor(actor))
        report['removed_duplicates'].append(label)
    check('Save reconciled Story and AI only', u.EditorLoadingAndSavingUtils.save_packages([story_package, ai_package], False))
    report['saved'].extend([story_package.get_path_name(), ai_package.get_path_name()])

    # Git merged the English source row from main plus all new C prompt rows.
    table = h.asset('Narrative/DT_HUDText')
    csv = (repo / 'SourceData/C/DT_HUDText.csv').read_text(encoding='utf-8-sig')
    check('Merged HUD CSV imports', u.DataTableFunctionLibrary.fill_data_table_from_csv_string(table, csv))
    check('Save HUD text table', u.EditorAssetLibrary.save_loaded_asset(table, False))
    report['saved'].append(table.get_path_name())
    report['passed'] = True
except Exception:
    report['error'] = traceback.format_exc()
    u.log_error(report['error'])
finally:
    (outdir / 'combine.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('PROPS_HUD_COMBINE ' + json.dumps(report))
    u.SystemLibrary.quit_editor()
