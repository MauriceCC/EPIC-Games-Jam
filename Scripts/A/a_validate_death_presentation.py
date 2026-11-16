"""Reloaded asset/graph checks and sampled motion evidence for A/B death polish."""
import json
import math
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.path[:0] = [str(repo/'Scripts/C'), str(repo/'Scripts/A'), str(Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h
from a_build_death_motion import SUPPORT

checks, samples = [], {}


def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})


def main():
    for name in ('Player/BP_PlayerCharacter', 'Enemies/BP_GuardBase', 'Enemies/BP_Pursuer', 'Enemies/BP_Interventor', 'Enemies/BP_Supervisor'):
        h.compile_blueprint(h.asset(name), warnings_as_errors=True)
        check(name+' compiles without warnings', True)
    ext = u.AnimPoseExtensions
    for who in ('Agent', 'Pursuer_A', 'Pursuer_B', 'Interventor', 'Supervisor'):
        folder = 'Player' if who == 'Agent' else 'Enemies'
        clip = h.asset(folder+'/Animation/Polish/A_'+who+'_Death')
        idle = h.asset('Art/Characters/SK_'+who+'/Anims/A_SK_'+who+'_Idle')
        check(who+' compatible skeleton', clip.get_editor_property('skeleton') == idle.get_editor_property('skeleton'))
        check(who+' two second nonlooping presentation', abs(clip.get_play_length()-2)<.001)
        bones = list(u.AnimationLibrary.get_animation_track_names(clip))
        frames = []
        for i in range(121):
            p = ext.get_anim_pose_at_time(clip, i/60, u.AnimPoseEvaluationOptions())
            frames.append({str(b): list(ext.get_bone_pose(p,b,u.AnimPoseSpaces.WORLD).translation.to_tuple()) for b in bones})
        neutral = ext.get_anim_pose_at_time(idle, 0, u.AnimPoseEvaluationOptions())
        neutral_hips = ext.get_bone_pose(neutral,'hips',u.AnimPoseSpaces.WORLD).translation
        def distance(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
        check(who+' no imported entry displacement', distance(frames[0]['hips'],neutral_hips.to_tuple())<.15)
        # Early foot support can lift the pelvis a few cm; reject the original
        # 60+ cm launch, while allowing grounded recoil up to 8 cm.
        check(who+' restrained vertical recoil', max(f['hips'][2] for f in frames)<neutral_hips.z+8)
        check(who+' hips finish near ground', frames[-1]['hips'][2]<40)
        check(who+' head finishes near ground', frames[-1]['head'][2]<40)
        check(who+' no joint below floor', min(f[b][2] for f in frames for b in SUPPORT)>-.1)
        check(who+' held final pose', max(distance(frames[-1][b],frames[-7][b]) for b in SUPPORT)<.1)
        maximum_step = max(distance(a['hips'],b['hips']) for a,b in zip(frames,frames[1:]))
        check(who+' continuous pelvis trajectory', maximum_step<8)
        samples[who] = {'max_hip_step_cm_at_60fps':maximum_step,'frames':frames}
    guard = h.asset('Enemies/BP_GuardBase')
    graph = h.edit(guard,'B_ApplyHealthDamage')
    check('Enemy death keeps mesh evaluating', all(str(n.find_input_pin('bEnabled').get_pin_value()).lower()=='true'
          for n in graph.list_all_nodes() if str(n.get_node_title())=='SetComponentTickEnabled'))
    player = h.asset('Player/BP_PlayerCharacter')
    check('Player death defers story event until presentation ends', not any('ReportStoryEvent' in str(n.get_node_title()) for n in h.edit(player,'Die').list_all_nodes()))
    check('Checkpoint cancels pending death notification', any(str(n.get_node_title())=='A_CancelDeathPresentation' for n in h.edit(player,'B_ResumePlayerAtCheckpoint').list_all_nodes()))
    assert all(c['passed'] for c in checks), [c['name'] for c in checks if not c['passed']]
    print('DEATH_ASSETS_VALIDATED', len(checks))


error = None
try:
    main()
except Exception:
    import traceback
    error = traceback.format_exc()
    raise
finally:
    (repo/'Scripts/A/death_asset_validation.json').write_text(json.dumps({'passed':error is None,'error':error,'checks':checks},indent=2))
    Path(u.Paths.project_saved_dir(),'death_pose_samples.json').write_text(json.dumps(samples))
