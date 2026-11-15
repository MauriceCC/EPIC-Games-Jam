"""Create correctly typed empty placeholders under the approved final paths."""
import unreal
A = unreal.EditorAssetLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
root = '/Game/Unscripted/'
specs = [
    ('VFX/'+name, unreal.NiagaraSystem, unreal.NiagaraSystemFactoryNew)
    for name in ['NS_TemporalCut','NS_RetakeTrail','NS_ParrySpark','NS_HitImpact','NS_ContinuityGlitch','NS_FinalRegister']
] + [
    ('Audio/'+name, unreal.SoundCue, unreal.SoundCueFactoryNew)
    for name in ['SC_StaffHit','SC_ParrySuccess','SC_TemporalCut','SC_Retake','SC_ChecklistRewrite','SC_EvidencePickup','SC_Footstep_Cobble']
] + [('Audio/MS_Ambience_Whitechapel',unreal.MetaSoundSource,unreal.MetaSoundSourceFactory),
     ('Materials/M_TemporalFrozen_Overlay',unreal.Material,unreal.MaterialFactoryNew),
     ('Materials/PP_Retake',unreal.Material,unreal.MaterialFactoryNew)]
for relative, cls, factory in specs:
    path = root+relative
    if A.does_asset_exist(path):
        assert isinstance(A.load_asset(path), cls), path
        continue
    folder, name = path.rsplit('/',1)
    obj = T.create_asset(name, folder, cls, factory())
    assert obj, path
    if name == 'PP_Retake':
        obj.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
        node = unreal.MaterialEditingLibrary.create_material_expression(obj, unreal.MaterialExpressionSceneTexture, -200, 0)
        node.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
        assert unreal.MaterialEditingLibrary.connect_material_property(node,'Color',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(obj)
    assert A.save_loaded_asset(obj), path
print('F0 placeholders created; audio and VFX intentionally empty')
