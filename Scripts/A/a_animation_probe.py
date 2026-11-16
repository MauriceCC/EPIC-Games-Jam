import json
from pathlib import Path
import unreal as u
out = {}
root = '/Game/Unscripted/Art/Characters/'
for who in ('Agent', 'Pursuer_A', 'Pursuer_B', 'Interventor', 'Supervisor'):
    base = root+'SK_'+who+'/'
    mesh = u.load_asset(base+'SK_'+who)
    skel = mesh.get_editor_property('skeleton')
    idle = u.load_asset(base+'Anims/A_SK_'+who+'_Idle')
    out[who] = {'bones': [str(n) for n in u.AnimationLibrary.get_animation_track_names(idle)], 'clips': {}}
    for action in ('Idle', 'Walk', 'Run', 'Attack1', 'Attack2', 'Dodge', 'Parry', 'Hit', 'Death'):
        path = base+'Anims/A_SK_'+who+'_'+action
        if not u.EditorAssetLibrary.does_asset_exist(path): continue
        clip = u.load_asset(path)
        out[who]['clips'][action] = {'length':clip.get_play_length(), 'keys':u.AnimationLibrary.get_num_keys(clip)}
        if who == 'Agent' and action in ('Attack1', 'Attack2'):
            ext = u.AnimPoseExtensions
            poses = [ext.get_anim_pose_at_frame(clip,i,u.AnimPoseEvaluationOptions()) for i in range(u.AnimationLibrary.get_num_keys(clip))]
            out[who]['clips'][action]['hands'] = [[round(v,2) for v in (ext.get_bone_pose(p,'righthand',u.AnimPoseSpaces.WORLD).translation-ext.get_bone_pose(p,'hips',u.AnimPoseSpaces.WORLD).translation).to_tuple()] for p in poses]
sub = u.get_engine_subsystem(u.SubobjectDataSubsystem)
api = u.SubobjectDataBlueprintFunctionLibrary
for name in ('BP_GuardBase','BP_Pursuer','BP_Interventor','BP_Supervisor'):
    bp=u.load_asset('/Game/Unscripted/Enemies/'+name)
    out[name]=[]
    for handle in sub.k2_gather_subobject_data_for_blueprint(bp):
        data=sub.k2_find_subobject_data_from_handle(handle)
        obj=api.get_object_for_blueprint(data,bp)
        if obj: out[name].append((str(api.get_variable_name(data)),obj.get_class().get_path_name()))
Path(u.Paths.project_saved_dir(), 'animation_probe.json').write_text(json.dumps(out, indent=2))
