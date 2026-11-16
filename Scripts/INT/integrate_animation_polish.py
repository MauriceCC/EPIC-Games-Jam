"""Integrate remote animation polish into local checkpoint and facing fixes."""
from pathlib import Path
import sys
import json
import traceback
import unreal as u
repo = Path(u.Paths.project_dir()).resolve().parent
result = repo / 'Scripts/INT/animation_merge_validation.json'
try:
    for relative in ('Scripts/A/a_install_animation_polish.py', 'Scripts/B/b_install_attack_animation.py', 'Scripts/INT/merge_player_attack_facing.py', 'Scripts/A/a_validate_animation_polish.py'):
        path = repo / relative
        exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})
    import blueprint_helpers_c as h
    guard = h.asset('Enemies/BP_GuardBase')
    names = {str(n) for n in u.BlueprintEditorLibrary.list_member_variable_names(guard)}
    assert {'B_LastAttackResetAt', 'B_MeleeStartedAt', 'B_PulseStartedAt', 'B_MeleePendingUntil'} <= names
    assert h.edit(guard, 'B_PlayAttackVisual')
    player = h.asset('Player/BP_PlayerCharacter')
    assert h.edit(player, 'B_ResumePlayerAtCheckpoint')
    assert u.get_default_object(player.generated_class()).get_editor_property('character_movement').get_editor_property('orient_rotation_to_movement')
    result.write_text(json.dumps({'passed': True, 'checks': ['Remote animation validation passed', 'Checkpoint attack cancellation variables preserved', 'Enemy attack visuals installed', 'Player checkpoint recovery preserved', 'Movement facing preserved']}, indent=2), encoding='utf-8')
    u.log('ANIMATION_MERGE_OK')
except Exception:
    result.write_text(json.dumps({'passed': False, 'error': traceback.format_exc()}, indent=2), encoding='utf-8')
    u.log_error(traceback.format_exc())
finally:
    u.SystemLibrary.quit_editor()
