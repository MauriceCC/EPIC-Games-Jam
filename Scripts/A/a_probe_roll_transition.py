"""Measure the dodge-to-walk handoff in PIE. Read-only: never saves assets or maps."""
import json
import time
import traceback
from pathlib import Path

import unreal as u

ROOT = '/Game/Unscripted/'
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
loco_cls = u.load_asset(ROOT + 'Art/Characters/Shared/BP_LocomotionAnim').generated_class()
out = Path(u.Paths.project_saved_dir(), 'PropsHudMerge/roll_transition_probe.json')
state = {'started': time.monotonic(), 'samples': [], 'events': [], 'next': 0.0, 'phase': 0}


def finish(error=None):
    out.write_text(json.dumps({'passed': error is None, 'error': error, **state}, indent=2, default=str), encoding='utf8')
    u.unregister_slate_post_tick_callback(handle)
    level.editor_request_end_play()
    u.SystemLibrary.quit_editor()


def sample(player, t, label):
    mesh = player.get_editor_property('mesh')
    instance = mesh.get_anim_instance()
    anim = instance.get_animation_asset() if instance else None
    loco = player.get_component_by_class(loco_cls)
    combat = player.get_editor_property('BP_CombatComponent')
    velocity = player.get_velocity()
    return {
        'label': label,
        't': round(t, 4),
        'location': [round(v, 2) for v in (player.get_actor_location().x, player.get_actor_location().y, player.get_actor_location().z)],
        'velocity': [round(v, 2) for v in (velocity.x, velocity.y, velocity.z)],
        'speed_xy': round((velocity * u.Vector(1, 1, 0)).length(), 2),
        'anim': anim.get_name() if anim else None,
        'busy': bool(loco.get_editor_property('bBusy')) if loco else None,
        'state': int(loco.get_editor_property('CurrentState')) if loco else None,
        'invulnerable': bool(player.get_editor_property('bInvulnerable')),
        'attacking': bool(player.get_editor_property('bAttacking')),
        'dead': bool(player.get_editor_property('bDead')),
        'input_blocked': bool(player.get_editor_property('bGameplayInputBlocked')),
        'stamina': round(float(combat.get_editor_property('CurrentStamina')), 2),
    }


def tick(dt):
    try:
        world = worlds.get_game_world()
        if not world:
            if time.monotonic() - state['started'] > 150:
                finish('PIE startup timeout')
            return
        now = u.GameplayStatics.get_time_seconds(world)
        if 'player' not in state:
            player = u.GameplayStatics.get_player_pawn(world, 0)
            if not player:
                return
            state['player'] = player
            state['t0'] = now
            state['next'] = now
            state['events'].append({'t': 0.0, 'event': 'pawn found', 'anim': None})
            return
        player = state['player']
        player.call_method('DoMove', args=(0.0, 1.0))
        elapsed = now - state['t0']
        if now >= state['next']:
            state['samples'].append(sample(player, elapsed, 'walk'))
            state['next'] = now + 0.1
        if state['phase'] == 0 and elapsed >= 0.6:
            state['phase'] = 1
            state['events'].append({'t': round(elapsed, 3), 'event': 'DoDodge #1'})
            player.call_method('DoDodge')
            state['samples'].append(sample(player, elapsed, 'dodge1 start'))
        elif state['phase'] == 1 and elapsed >= 2.6:
            state['phase'] = 2
            state['events'].append({'t': round(elapsed, 3), 'event': 'DoDodge #2 (cooldown probe)'})
            player.call_method('DoDodge')
            state['samples'].append(sample(player, elapsed, 'dodge2 start'))
        elif elapsed >= 6.0:
            finish()
    except Exception:
        finish(traceback.format_exc())


handle = u.register_slate_post_tick_callback(tick)
level.editor_request_begin_play()
