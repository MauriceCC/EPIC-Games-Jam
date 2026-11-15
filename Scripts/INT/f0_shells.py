"""Create only missing F0 Blueprint shells through Unreal's editor API.

Existing assets are never overwritten. This stage does not complete F0:
interfaces, signatures, components, maps and verification are separate steps.
Parent classes follow F0_GUIA_EDITOR.md's explicitly labelled proposals.
"""
import json
from pathlib import Path
import unreal

ROOT = '/Game/Unscripted/'
EXPECTED_PROJECT = 'Unscripted'
assert unreal.Paths.get_project_file_path().endswith('/Unscripted.uproject')
assert unreal.SystemLibrary.get_engine_version().startswith('5.8.4-')
lib = unreal.BlueprintEditorLibrary
assets = unreal.EditorAssetLibrary
folders = ['Core/Enums', 'Core/Structs', 'Core/Interfaces', 'Player/Input',
           'Player/Animation', 'Player/Test', 'Enemies/Jack', 'Enemies/Animation',
           'Enemies/Test', 'Narrative/Test', 'UI', 'World/Test', 'Art',
           'Materials', 'VFX', 'Audio', 'Maps/Test']
for folder in folders:
    assets.make_directory(ROOT + folder)

definitions = [
    ('Player/BP_HealthComponent', unreal.ActorComponent),
    ('Player/BP_CombatComponent', unreal.ActorComponent),
    ('Player/BP_TemporalComponent', unreal.ActorComponent),
    ('Enemies/BP_StealthComponent', unreal.ActorComponent),
    ('Narrative/BP_InteractionComponent', unreal.ActorComponent),
    ('Narrative/BP_ObjectiveManager', unreal.ActorComponent),
    ('Player/BP_PlayerCharacter', unreal.Character),
    ('Player/BP_PlayerController', unreal.PlayerController),
    ('Enemies/BP_GuardBase', unreal.Character),
    ('Enemies/BP_Pursuer', 'Enemies/BP_GuardBase'),
    ('Enemies/BP_Interventor', 'Enemies/BP_GuardBase'),
    ('Enemies/BP_Supervisor', 'Enemies/BP_GuardBase'),
    ('Enemies/Jack/BP_Jack', unreal.Character),
    ('Narrative/BP_GameMode', unreal.GameModeBase),
    ('Narrative/BP_GameState', unreal.GameStateBase),
    ('UI/BP_HUD', unreal.HUD),
    ('Narrative/BP_InteractableBase', unreal.Actor),
    ('Narrative/BP_Door', 'Narrative/BP_InteractableBase'),
    ('Narrative/BP_Hideout', 'Narrative/BP_InteractableBase'),
    ('Narrative/BP_Evidence', 'Narrative/BP_InteractableBase'),
    ('Narrative/BP_FinalChoice', 'Narrative/BP_InteractableBase'),
    ('Narrative/BP_Checkpoint', unreal.Actor),
    ('Narrative/BP_StoryTrigger', unreal.Actor),
]
report = []
for relative, parent in definitions:
    path = ROOT + relative
    if isinstance(parent, str):
        parent = assets.load_blueprint_class(ROOT + parent)
    else:
        parent = parent.static_class()
    if assets.does_asset_exist(path):
        bp = assets.load_asset(path)
        assert lib.get_blueprint_parent_class(bp) == parent, 'Unexpected parent: ' + path
        report.append({'asset': path, 'state': 'existing_preserved'})
        continue
    bp = lib.create_blueprint_asset_with_parent(path, parent)
    assert bp, 'Creation failed: ' + path
    assert lib.compile_blueprint(bp), 'Compilation failed: ' + path
    assert assets.save_loaded_asset(bp), 'Save failed: ' + path
    report.append({'asset': path, 'state': 'created_compiled_saved'})

output = Path(unreal.Paths.project_saved_dir()) / 'F0_shells.json'
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('F0 shells: ' + str(output))
