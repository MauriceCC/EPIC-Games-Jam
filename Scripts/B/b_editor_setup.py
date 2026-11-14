"""Division B - Enemies, AI, Stealth & Jack editor automation module.

This script provides idempotent setup, node-wiring, and level placement for:
- Content/Unscripted/Enemies/BP_PatrolRoute
- Content/Unscripted/Enemies/BP_StealthComponent
- Content/Unscripted/Enemies/BP_GuardBase (and Pursuer, Interventor, Supervisor)
- Content/Unscripted/Enemies/Jack/BP_Jack
- Maps/Test/L_Test_B
- Maps/L_Whitechapel_AI

Can be run in Unreal Engine via Python console or integration runner:
    import unreal
    from pathlib import Path
    import sys
    sys.path.append(r'C:\\Users\\jalfa\\Documents\\gameJam\\EPIC-Games-Jam\\Scripts\\B')
    import b_editor_setup
    b_editor_setup.build_and_verify_all()
"""

from __future__ import annotations

import csv
from pathlib import Path
import unreal

ROOT = '/Game/Unscripted/'
A = unreal.EditorAssetLibrary
L = unreal.BlueprintEditorLibrary
G = unreal.BlueprintGraphEditor


def get_pin(kind: str) -> unreal.EdGraphPinType:
    """Helper to construct EdGraphPinType instances for blueprint members."""
    if kind.startswith('E'):
        value = unreal.EdGraphPinType()
        enum = A.load_asset(ROOT + 'Core/Enums/' + kind)
        value.import_text(f'(PinCategory="byte",PinSubCategoryObject="{enum.get_path_name()}")')
        return value
    if kind == 'Actor':
        return L.get_object_reference_type(unreal.Actor.static_class())
    if kind == 'Vector':
        return L.get_struct_type(unreal.Vector.static_struct())
    if kind == 'Transform':
        return L.get_struct_type(unreal.Transform.static_struct())
    if kind == 'BP_PatrolRoute':
        bp_class = A.load_blueprint_class(ROOT + 'Enemies/BP_PatrolRoute')
        return L.get_object_reference_type(bp_class)
    if kind == 'float':
        value = unreal.EdGraphPinType()
        value.import_text('(PinCategory="real",PinSubCategory="float")')
        return value
    if kind in ('bool', 'boolean'):
        return L.get_basic_type_by_name('bool')
    if kind in ('int', 'integer'):
        return L.get_basic_type_by_name('int')
    if kind == 'text':
        return L.get_basic_type_by_name('text')
    return L.get_basic_type_by_name(kind)


def ensure_patrol_route() -> None:
    """Ensures BP_PatrolRoute exists with an instance-editable 3D Waypoints array."""
    route_path = ROOT + 'Enemies/BP_PatrolRoute'
    if not A.does_asset_exist(route_path):
        bp = L.create_blueprint_asset_with_parent(route_path, unreal.Actor.static_class())
        assert bp, 'Failed to create BP_PatrolRoute'
        L.add_member_variable(bp, 'Waypoints', L.get_array_type(L.get_struct_type(unreal.Vector.static_struct())))
        L.set_blueprint_variable_instance_editable(bp, 'Waypoints', True)
        L.compile_blueprint(bp)
        A.save_loaded_asset(bp)
        unreal.log('Created BP_PatrolRoute successfully.')


def setup_variables_and_defaults() -> None:
    """Configures member variables and CDO balance properties across all B blueprints."""
    # 1. BP_StealthComponent
    stealth_bp = A.load_asset(ROOT + 'Enemies/BP_StealthComponent')
    stealth_vars = {
        'DetectionLevel': 'float',
        'bIsCrouched': 'bool',
        'bIsHidden': 'bool',
        'DetectionDecayRate': 'float',
    }
    existing_s = {str(v) for v in L.list_member_variable_names(stealth_bp)}
    for name, kind in stealth_vars.items():
        if name not in existing_s:
            L.add_member_variable(stealth_bp, name, get_pin(kind))
    L.compile_blueprint(stealth_bp)
    A.save_loaded_asset(stealth_bp)

    # 2. BP_GuardBase
    guard_bp = A.load_asset(ROOT + 'Enemies/BP_GuardBase')
    guard_vars = {
        'CurrentAIState': 'EEnemyAIState',
        'TargetActor': 'Actor',
        'LastKnownPlayerLocation': 'Vector',
        'AlertTimer': 'float',
        'AlertDelaySeconds': 'float',
        'VisionRange': 'float',
        'DetectionRange': 'float',
        'SightHalfAngle': 'float',
        'AttackRange': 'float',
        'AttackDamage': 'float',
        'PostureDamage': 'float',
        'CurrentPosture': 'float',
        'MaxPosture': 'float',
        'bCanAttack': 'bool',
        'bIsTemporalFrozen': 'bool',
        'FrozenPreState': 'EEnemyAIState',
        'PatrolRoute': 'BP_PatrolRoute',
        'CurrentWaypointIndex': 'int',
        'bNonLethalCivilian': 'bool',
    }
    existing_g = {str(v) for v in L.list_member_variable_names(guard_bp)}
    for name, kind in guard_vars.items():
        if name not in existing_g:
            L.add_member_variable(guard_bp, name, get_pin(kind))
            if name == 'PatrolRoute':
                L.set_blueprint_variable_instance_editable(guard_bp, name, True)
    L.compile_blueprint(guard_bp)
    A.save_loaded_asset(guard_bp)

    # 3. BP_Jack
    jack_bp = A.load_asset(ROOT + 'Enemies/Jack/BP_Jack')
    jack_vars = {
        'CurrentWaypointIndex': 'int',
        'bJackFound': 'bool',
        'bEscaping': 'bool',
        'bReachedRefuge': 'bool',
    }
    existing_j = {str(v) for v in L.list_member_variable_names(jack_bp)}
    for name, kind in jack_vars.items():
        if name not in existing_j:
            L.add_member_variable(jack_bp, name, get_pin(kind))
    if 'Waypoints' not in existing_j:
        L.add_member_variable(jack_bp, 'Waypoints', L.get_array_type(get_pin('Vector')))
        L.set_blueprint_variable_instance_editable(jack_bp, 'Waypoints', True)
    L.compile_blueprint(jack_bp)
    A.save_loaded_asset(jack_bp)

    # 4. CDO Balance configuration
    repo_root = Path(unreal.Paths.project_dir()).resolve().parent
    csv_path = repo_root / 'SourceData' / 'B' / 'DT_EnemyBalance.csv'
    balance = {}
    if csv_path.exists():
        with open(csv_path, mode='r', encoding='utf-8') as handle:
            for row in csv.DictReader(handle):
                name = row.get('Name', '').strip()
                if name:
                    balance[name] = {k: float(v) for k, v in row.items() if k not in ('Name', 'Notes') and v.replace('.', '', 1).isdigit()}

    # Assign CDO defaults
    def set_cdo(rel: str, prop: str, val):
        bp = A.load_asset(ROOT + rel)
        if bp:
            cdo = unreal.get_default_object(bp.generated_class())
            try:
                cdo.set_editor_property(prop, val)
                L.compile_blueprint(bp)
                A.save_loaded_asset(bp)
            except Exception as exc:
                unreal.log_warning(f"Could not set {rel}.{prop}: {exc}")

    set_cdo('Enemies/BP_StealthComponent', 'DetectionLevel', 0.0)
    set_cdo('Enemies/BP_StealthComponent', 'bIsCrouched', False)
    set_cdo('Enemies/BP_StealthComponent', 'bIsHidden', False)
    set_cdo('Enemies/BP_StealthComponent', 'DetectionDecayRate', 0.3)

    set_cdo('Enemies/BP_GuardBase', 'VisionRange', 1800.0)
    set_cdo('Enemies/BP_GuardBase', 'DetectionRange', 800.0)
    set_cdo('Enemies/BP_GuardBase', 'SightHalfAngle', 50.0)
    set_cdo('Enemies/BP_GuardBase', 'AttackRange', 160.0)
    set_cdo('Enemies/BP_GuardBase', 'AttackDamage', 12.0)
    set_cdo('Enemies/BP_GuardBase', 'PostureDamage', 8.0)
    set_cdo('Enemies/BP_GuardBase', 'CurrentPosture', 30.0)
    set_cdo('Enemies/BP_GuardBase', 'MaxPosture', 30.0)
    set_cdo('Enemies/BP_GuardBase', 'bCanAttack', True)
    set_cdo('Enemies/BP_GuardBase', 'bIsTemporalFrozen', False)
    set_cdo('Enemies/BP_GuardBase', 'bNonLethalCivilian', True)

    set_cdo('Enemies/BP_Pursuer', 'VisionRange', 1800.0)
    set_cdo('Enemies/BP_Pursuer', 'AttackDamage', 12.0)
    set_cdo('Enemies/BP_Pursuer', 'PostureDamage', 8.0)

    set_cdo('Enemies/BP_Interventor', 'VisionRange', 2000.0)
    set_cdo('Enemies/BP_Interventor', 'AttackDamage', 18.0)
    set_cdo('Enemies/BP_Interventor', 'PostureDamage', 12.0)
    set_cdo('Enemies/BP_Interventor', 'MaxPosture', 50.0)
    set_cdo('Enemies/BP_Interventor', 'CurrentPosture', 50.0)

    set_cdo('Enemies/BP_Supervisor', 'VisionRange', 2400.0)
    set_cdo('Enemies/BP_Supervisor', 'AttackDamage', 26.0)
    set_cdo('Enemies/BP_Supervisor', 'PostureDamage', 18.0)
    set_cdo('Enemies/BP_Supervisor', 'MaxPosture', 90.0)
    set_cdo('Enemies/BP_Supervisor', 'CurrentPosture', 90.0)

    set_cdo('Enemies/Jack/BP_Jack', 'bJackFound', False)
    set_cdo('Enemies/Jack/BP_Jack', 'bEscaping', False)
    set_cdo('Enemies/Jack/BP_Jack', 'bReachedRefuge', False)
    unreal.log('Variables and CDO defaults configured.')


def setup_character_meshes() -> None:
    """Assigns skeletal meshes and animation blueprints to enemies and Jack."""
    manny_mesh = A.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    quinn_mesh = A.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple')
    anim_bp = A.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed')
    anim_class = anim_bp.generated_class() if anim_bp else None

    def assign(rel: str, mesh, anim):
        bp = A.load_asset(ROOT + rel)
        if bp:
            cdo = unreal.get_default_object(bp.generated_class())
            comp = cdo.get_editor_property('mesh')
            if comp:
                comp.set_editor_property('skeletal_mesh_asset', mesh)
                if anim:
                    comp.set_editor_property('anim_class', anim)
                comp.set_editor_property('relative_location', unreal.Vector(0.0, 0.0, -90.0))
                comp.set_editor_property('relative_rotation', unreal.Rotator(0.0, -90.0, 0.0))
            L.compile_blueprint(bp)
            A.save_loaded_asset(bp)

    assign('Enemies/BP_GuardBase', manny_mesh, anim_class)
    assign('Enemies/Jack/BP_Jack', quinn_mesh, anim_class)

    for child in ['Enemies/BP_Pursuer', 'Enemies/BP_Interventor', 'Enemies/BP_Supervisor']:
        bp = A.load_asset(ROOT + child)
        if bp:
            L.compile_blueprint(bp)
            A.save_loaded_asset(bp)
    unreal.log('Character meshes and animations assigned.')


def ensure_levels_populated() -> None:
    """Ensures test map L_Test_B and L_Whitechapel_AI have required actors placed."""
    route_class = A.load_blueprint_class(ROOT + 'Enemies/BP_PatrolRoute')
    pursuer_class = A.load_blueprint_class(ROOT + 'Enemies/BP_Pursuer')
    jack_class = A.load_blueprint_class(ROOT + 'Enemies/Jack/BP_Jack')

    # 1. L_Test_B
    unreal.EditorLevelLibrary.load_level(ROOT + 'Maps/Test/L_Test_B')
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    has_route = any(a.get_class() == route_class for a in actors)
    has_jack = any(a.get_class() == jack_class for a in actors)
    pursuer_count = sum(1 for a in actors if a.get_class() == pursuer_class)

    route_actor = None
    for a in actors:
        if a.get_class() == route_class:
            route_actor = a
            break

    if not has_route and route_class:
        route_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(route_class, unreal.Vector(0.0, 0.0, 50.0), unreal.Rotator(0.0, 0.0, 0.0))
        if route_actor:
            route_actor.set_editor_property('Waypoints', [unreal.Vector(-400.0, 200.0, 0.0), unreal.Vector(400.0, 200.0, 0.0), unreal.Vector(0.0, -400.0, 0.0)])

    if pursuer_count < 2 and pursuer_class and route_actor:
        for i in range(2 - pursuer_count):
            p = unreal.EditorLevelLibrary.spawn_actor_from_class(pursuer_class, unreal.Vector(-200.0 + (i * 400.0), 100.0, 110.0), unreal.Rotator(0.0, 0.0, 0.0))
            if p:
                p.set_editor_property('PatrolRoute', route_actor)

    if not has_jack and jack_class:
        j = unreal.EditorLevelLibrary.spawn_actor_from_class(jack_class, unreal.Vector(300.0, -300.0, 110.0), unreal.Rotator(0.0, 90.0, 0.0))
        if j:
            j.set_editor_property('Waypoints', [unreal.Vector(300.0, -100.0, 0.0), unreal.Vector(0.0, 300.0, 0.0), unreal.Vector(-400.0, 400.0, 0.0)])
    unreal.EditorLevelLibrary.save_current_level()

    # 2. L_Whitechapel_AI (Act I Plaza encounter)
    unreal.EditorLevelLibrary.load_level(ROOT + 'Maps/L_Whitechapel_AI')
    ai_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    if not ai_actors:
        r = unreal.EditorLevelLibrary.spawn_actor_from_class(route_class, unreal.Vector(0.0, 0.0, 50.0), unreal.Rotator(0.0, 0.0, 0.0))
        if r:
            r.set_editor_property('Waypoints', [unreal.Vector(-300.0, 150.0, 0.0), unreal.Vector(300.0, 150.0, 0.0), unreal.Vector(0.0, -300.0, 0.0)])
            for i in range(2):
                p = unreal.EditorLevelLibrary.spawn_actor_from_class(pursuer_class, unreal.Vector(-150.0 + (i * 300.0), 0.0, 100.0), unreal.Rotator(0.0, 0.0, 0.0))
                if p:
                    p.set_editor_property('PatrolRoute', r)
        unreal.EditorLevelLibrary.save_current_level()

    unreal.EditorLevelLibrary.load_level(ROOT + 'Maps/Test/L_Test_B')
    unreal.log('Levels populated and saved successfully.')


def build_and_verify_all() -> dict[str, bool]:
    """Single master entry point for Division B setup."""
    ensure_patrol_route()
    setup_variables_and_defaults()
    setup_character_meshes()
    ensure_levels_populated()

    report = {
        'BP_PatrolRoute': A.does_asset_exist(ROOT + 'Enemies/BP_PatrolRoute'),
        'BP_StealthComponent': A.does_asset_exist(ROOT + 'Enemies/BP_StealthComponent'),
        'BP_GuardBase': A.does_asset_exist(ROOT + 'Enemies/BP_GuardBase'),
        'BP_Pursuer': A.does_asset_exist(ROOT + 'Enemies/BP_Pursuer'),
        'BP_Interventor': A.does_asset_exist(ROOT + 'Enemies/BP_Interventor'),
        'BP_Supervisor': A.does_asset_exist(ROOT + 'Enemies/BP_Supervisor'),
        'BP_Jack': A.does_asset_exist(ROOT + 'Enemies/Jack/BP_Jack'),
        'L_Test_B': A.does_asset_exist(ROOT + 'Maps/Test/L_Test_B'),
        'L_Whitechapel_AI': A.does_asset_exist(ROOT + 'Maps/L_Whitechapel_AI'),
    }
    unreal.log(f'Division B Verification Report: {report}')
    return report


if __name__ == '__main__':
    build_and_verify_all()
