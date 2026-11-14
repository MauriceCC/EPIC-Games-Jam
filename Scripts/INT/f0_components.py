"""Attach F0 components and assign the agreed GameMode classes."""
import unreal
A = unreal.EditorAssetLibrary
L = unreal.BlueprintEditorLibrary
S = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
D = unreal.SubobjectDataBlueprintFunctionLibrary
root = '/Game/Unscripted/'
components = {
    'Player/BP_PlayerCharacter': [('Health','Player/BP_HealthComponent'),('Combat','Player/BP_CombatComponent'),('Temporal','Player/BP_TemporalComponent'),('Interaction','Narrative/BP_InteractionComponent'),('Stealth','Enemies/BP_StealthComponent')],
    'Enemies/BP_GuardBase': [('Health','Player/BP_HealthComponent')],
    'Narrative/BP_GameState': [('ObjectiveManager','Narrative/BP_ObjectiveManager')],
}
for relative, items in components.items():
    bp = A.load_asset(root+relative)
    handles = S.k2_gather_subobject_data_for_blueprint(bp)
    names = {str(D.get_variable_name(D.get_data(h))) for h in handles}
    for name, component in items:
        if name in names:
            continue
        params = unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=A.load_blueprint_class(root+component), blueprint_context=bp)
        handle, reason = S.add_new_subobject(params)
        assert D.is_handle_valid(handle), str(reason)
        assert S.rename_subobject(handle, name)
    assert L.compile_blueprint(bp)
    assert A.save_loaded_asset(bp)
bp = A.load_asset(root+'Narrative/BP_GameMode')
defaults = unreal.get_default_object(bp.generated_class())
for prop, relative in [('default_pawn_class','Player/BP_PlayerCharacter'),('player_controller_class','Player/BP_PlayerController'),('game_state_class','Narrative/BP_GameState'),('hud_class','UI/BP_HUD')]:
    defaults.set_editor_property(prop, A.load_blueprint_class(root+relative))
assert L.compile_blueprint(bp)
assert A.save_loaded_asset(bp)
print('F0 components and GameMode classes configured')
