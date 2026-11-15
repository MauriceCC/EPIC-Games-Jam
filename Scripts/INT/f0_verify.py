"""Read-only F0 asset and class-reference audit."""
import json
from pathlib import Path
import unreal

ROOT = '/Game/Unscripted/'
A = unreal.EditorAssetLibrary
L = unreal.BlueprintEditorLibrary
report = {
    'engine': unreal.SystemLibrary.get_engine_version(),
    'project': unreal.Paths.get_project_file_path(),
    'assets': {},
    'blueprints': {},
}
report['blueprint_api_search'] = {}
for name in dir(unreal):
    if 'blueprint' not in name.lower():
        continue
    cls = getattr(unreal, name, None)
    if cls:
        methods = [method for method in dir(cls)
                   if 'interface' in method.lower() or 'implemented' in method.lower()]
        if methods:
            report['blueprint_api_search'][name] = methods
report['available_interface_descriptors'] = [
    name for name in dir(unreal)
    if 'interface' in name.lower() and 'blueprint' in name.lower()
]

expected = [
    'Core/Enums/ECombatState', 'Core/Enums/EEnemyAIState',
    'Core/Enums/EAttackType', 'Core/Enums/EHitResult',
    'Core/Enums/EStoryPhase', 'Core/Enums/EStoryEvent',
    'Core/Enums/EEvidenceType', 'Core/Enums/EEndingType',
    'Core/Enums/ESpeaker', 'Core/Structs/ST_HitInfo',
    'Core/Structs/ST_DialogueLine', 'Core/Structs/ST_ChecklistRow',
    'Core/Interfaces/BPI_Damageable', 'Core/Interfaces/BPI_TimeAffectable',
    'Core/Interfaces/BPI_Interactable', 'Core/Interfaces/BPI_PlayerControl',
    'Core/Interfaces/BPI_StoryEvents', 'Core/Interfaces/BPI_CheckpointListener',
    'Player/BP_HealthComponent', 'Player/BP_CombatComponent',
    'Player/BP_TemporalComponent', 'Player/BP_PlayerCharacter',
    'Player/BP_PlayerController', 'Enemies/BP_StealthComponent',
    'Enemies/BP_GuardBase', 'Enemies/BP_Pursuer', 'Enemies/BP_Interventor',
    'Enemies/BP_Supervisor', 'Enemies/Jack/BP_Jack',
    'Narrative/BP_InteractionComponent', 'Narrative/BP_ObjectiveManager',
    'Narrative/BP_GameMode', 'Narrative/BP_GameState', 'UI/BP_HUD',
    'Narrative/BP_InteractableBase', 'Narrative/BP_Door',
    'Narrative/BP_Hideout', 'Narrative/BP_Evidence',
    'Narrative/BP_FinalChoice', 'Narrative/BP_Checkpoint',
    'Narrative/BP_StoryTrigger', 'Player/Input/IMC_Default',
    'Maps/L_Whitechapel', 'Maps/L_Whitechapel_Geo',
    'Maps/L_Whitechapel_Light', 'Maps/L_Whitechapel_AI',
    'Maps/L_Whitechapel_Story', 'Maps/Test/L_Test_A',
    'Maps/Test/L_Test_B', 'Maps/Test/L_Test_C', 'Maps/Test/L_Test_D',
]
for relative in expected:
    report['assets'][relative] = A.does_asset_exist(ROOT + relative)

blueprints = [
    'Player/BP_PlayerCharacter', 'Player/BP_PlayerController',
    'Enemies/BP_GuardBase', 'Enemies/BP_Pursuer',
    'Enemies/BP_Interventor', 'Enemies/BP_Supervisor',
    'Enemies/Jack/BP_Jack', 'Narrative/BP_InteractableBase',
    'Narrative/BP_GameState', 'Narrative/BP_GameMode',
    'Narrative/BP_Checkpoint', 'Narrative/BP_StoryTrigger',
]
interface_assignments = {
    'Player/BP_PlayerCharacter': ['BPI_Damageable', 'BPI_PlayerControl', 'BPI_CheckpointListener'],
    'Enemies/BP_GuardBase': ['BPI_Damageable', 'BPI_TimeAffectable', 'BPI_Interactable', 'BPI_CheckpointListener'],
    'Enemies/Jack/BP_Jack': ['BPI_Interactable', 'BPI_CheckpointListener'],
    'Narrative/BP_InteractableBase': ['BPI_Interactable'],
    'Narrative/BP_GameState': ['BPI_StoryEvents'],
}
for relative in blueprints:
    bp = A.load_asset(ROOT + relative)
    if not bp:
        continue
    data = {}
    for prop in ('simple_construction_script',):
        try:
            value = bp.get_editor_property(prop)
            data[prop] = str(value)
        except Exception as exc:
            data[prop + '_error'] = str(exc)
    try:
        generated_class = bp.generated_class()
        data['parent_class'] = str(L.get_blueprint_parent_class(bp))
        data['generated_class_api'] = [
            name for name in dir(generated_class) if 'interface' in name.lower()
        ]
        checker = getattr(unreal.SystemLibrary, 'does_class_implement_interface', None)
        if checker:
            data['requested_interfaces'] = {
                name: bool(checker(
                    generated_class,
                    A.load_asset(ROOT + 'Core/Interfaces/' + name).generated_class()
                ))
                for name in interface_assignments.get(relative, [])
            }
        else:
            data['interface_check_api_missing'] = True
    except Exception as exc:
        data['generated_class_error'] = str(exc)
    try:
        handles = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(bp)
        helper = unreal.SubobjectDataBlueprintFunctionLibrary
        data['subobject_helper_api'] = [name for name in dir(helper) if 'component' in name.lower()]
        data['components'] = [
            {'name': str(helper.get_variable_name(helper.get_data(handle))),
             'fields': [name for name in dir(helper.get_data(handle)) if not name.startswith('_')]}
            for handle in handles
        ]
    except Exception as exc:
        data['components_error'] = str(exc)
    report['blueprints'][relative] = data

report['interfaces'] = {}
for relative in [item for item in expected if item.startswith('Core/Interfaces/')]:
    bp = A.load_asset(ROOT + relative)
    report['interfaces'][relative] = {
        'graphs': [str(name) for name in L.list_graph_names(bp)] if bp else []
    }

game_mode = A.load_asset(ROOT + 'Narrative/BP_GameMode')
if game_mode:
    defaults = unreal.get_default_object(game_mode.generated_class())
    report['game_mode_defaults'] = {}
    for prop in ('default_pawn_class', 'player_controller_class',
                 'game_state_class', 'hud_class'):
        try:
            report['game_mode_defaults'][prop] = str(defaults.get_editor_property(prop))
        except Exception as exc:
            report['game_mode_defaults'][prop + '_error'] = str(exc)

output = Path(unreal.Paths.project_saved_dir()) / 'F0_verification.json'
output.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
print('F0 read-only audit: ' + str(output))
