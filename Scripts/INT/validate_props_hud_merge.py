"""Fresh-process compilation, preservation and bytecode checks. Never saves assets."""
import json
import hashlib
import os
import sys
import traceback
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
outdir = repo / 'Unscripted/Saved/PropsHudMerge'
sys.dont_write_bytecode = True
sys.path[:0] = [str(repo / 'Scripts/C'), str(repo / 'Scripts/A'),
    str(Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h

result = {'passed': False, 'checks': [], 'compiled': [], 'asset_saves_performed': False}

def check(name, value):
    result['checks'].append({'name': name, 'passed': bool(value)})
    assert value, name

try:
    assets = u.EditorAssetLibrary
    for path in assets.list_assets('/Game/Unscripted', recursive=True, include_folder=False):
        if '/Test/' in path:
            continue
        asset = assets.load_asset(path)
        if isinstance(asset, u.Blueprint):
            h.compile_blueprint(asset, warnings_as_errors=True)
            result['compiled'].append(path)
    check('All production Blueprints compile without warnings or errors', bool(result['compiled']))
    os.environ['UNSCRIPTED_MERGE_SNAPSHOT'] = 'merged'
    script = repo / 'Scripts/INT/inspect_props_hud_merge.py'
    exec(compile(script.read_text(encoding='utf-8'), str(script), 'exec'), {'__file__': str(script)})
    current = json.loads((outdir / 'merged.json').read_text(encoding='utf-8'))
    original = json.loads((repo / 'Scripts/INT/props_hud_merge_baseline.json').read_text(encoding='utf-8'))
    player = current['blueprints']['Player/BP_PlayerCharacter']
    for graph in ['B_ResumePlayerAtCheckpoint', 'Die', 'ReceiveCombatHit', 'GetStealthComponent',
                  'FaceCursor', 'DoMove', 'AttackHit', 'DoRetake']:
        digest = hashlib.sha256(json.dumps(player['graphs'][graph], sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
        check('main player graph retained: ' + graph, digest == original['player_graph_sha256'][graph])
    check('Continuous cursor helper retained', 'A_UpdateCursorFacing' in player['graphs'])
    for name in ['DoLightAttack', 'DoDodge', 'DoParry']:
        check(name + ' uses the merged stamina component',
              any('TryConsumeStamina' in n['title'].replace(' ', '') for n in player['graphs'][name].values()))
    now = {a['label']: a for a in current['actors']}
    removed = {'B_WorkshopEscapeDoor', 'B_ArchiveGate', 'B_RecordsDoor'}
    old_ai = set(original['main_ai_labels'])
    check('Every main AI actor except the three duplicate doors remains', old_ai - removed <= now.keys())
    check('Duplicate doors are absent', not (removed & now.keys()))
    check('Exactly two evidence interactables', len([a for a in now.values() if 'BP_Evidence.' in a['class']]) == 2)
    check('Exactly two final-choice interactables', len([a for a in now.values() if 'BP_FinalChoice.' in a['class']]) == 2)
    check('All C narrative placements retained', all(n in now for n in ['C_Closure_CP0', 'C_Closure_CP1',
          'C_Closure_AlleyHideout', 'C_FutureMessage', 'C_NursingRecord', 'C_FabricatedReport',
          'C_SideDoor', 'C_ArchiveGate', 'C_RecordsDoor', 'C_OfficialRecord', 'C_AuthenticRecord']))
    placed = {a.get_actor_label(): a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
    check('Archive reuses B encounter gating with C door presentation',
          placed['C_ArchiveGate'].get_class() == h.asset('Enemies/BP_ArchiveEncounterDoor').generated_class()
          and not placed['C_ArchiveGate'].get_editor_property('bB_RequiresSupervisor')
          and placed['C_ArchiveGate'].get_editor_property('DoorWidth') == 400.)
    check('HUD retains main objective and new C prompts',
          all(t in current['hud_csv'] for t in ['Defeat the Interventor and Supervisor. Choose a file in Records.',
              'FutureMessagePrompt', 'OfficialFilePrompt', 'AuthenticFilePrompt']))

    # Existing meaningful A suites run against the merged bytecode; report files
    # are redirected into Saved so historic branch evidence stays untouched.
    for name in ['validate_a04', 'validate_a05']:
        path = repo / ('Scripts/A/' + name + '.py')
        source = path.read_text(encoding='utf-8')
        report_name = 'a04_validation_result.json' if name.endswith('04') else 'a05_validation_result.json'
        source = source.replace("HERE/'" + report_name + "'", "Path(" + repr(str(outdir / report_name)) + ")")
        source = source.replace("HERE / '" + report_name + "'", "Path(" + repr(str(outdir / report_name)) + ")")
        exec(compile(source, str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})
        suite = json.loads((outdir / report_name).read_text(encoding='utf-8'))
        check(name + ' passes against merged assets', suite['passed'])
        result[name + '_checks'] = len(suite['checks'])
    result['passed'] = True
except Exception:
    result['error'] = traceback.format_exc()
    u.log_error(result['error'])
finally:
    (outdir / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('PROPS_HUD_VALIDATION ' + json.dumps(result))
if not result['passed']:
    raise RuntimeError('Merge validation failed; inspect Saved/PropsHudMerge/validation.json')
