"""Isolated real-PIE merge checks; no assets saved, no private story state writes.

Supplies Jack/evidence story events to isolate the merge, then uses real B defeat,
C doors/confirmation, A health/stamina, and main's checkpoint restoration.
This is functional automation, not a complete manual or visual playthrough.
"""
import asyncio
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'))
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager

case = os.environ.get('UNSCRIPTED_ENDING_CASE', 'official')
outdir = repo / 'Unscripted/Saved/PropsHudMerge'
result = {'passed': False, 'case': case, 'checks': [], 'asset_saves_performed': False,
          'mode': 'real PIE; HUD/interaction calls; isolated Jack and evidence prerequisites; not native keyboard or visual QA'}
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)

def check(name, value):
    result['checks'].append({'name': name, 'passed': bool(value)})
    assert value, name

def prop(obj, name):
    return obj.get_editor_property(name)

def cls(path):
    return u.load_asset('/Game/Unscripted/' + path).generated_class()

async def run():
    try:
        deadline = time.monotonic() + 60
        while not worlds.get_game_world():
            assert time.monotonic() < deadline, 'PIE did not start'
            await asyncio.sleep(.1)
        world = worlds.get_game_world()
        while not u.GameplayStatics.get_player_pawn(world, 0):
            assert time.monotonic() < deadline, 'Player did not spawn'
            await asyncio.sleep(.1)
        await asyncio.sleep(1)
        pawn = u.GameplayStatics.get_player_pawn(world, 0)
        pc = u.GameplayStatics.get_player_controller(world, 0)
        hud = pc.get_hud()
        state = u.GameplayStatics.get_game_state(world)
        manager = state.call_method('GetObjectiveManager')
        actors = {a.get_actor_label(): a for a in u.GameplayStatics.get_all_actors_of_class(world, u.Actor)}
        health = pawn.get_component_by_class(cls('Player/BP_HealthComponent'))
        combat = pawn.get_component_by_class(cls('Player/BP_CombatComponent'))
        check('Real player starts with 100 health and stamina',
              prop(health, 'CurrentHealth') == 100 and prop(combat, 'CurrentStamina') == 100)
        check('Both branch placements are reconciled in PIE',
              all(n in actors for n in ['B_Jack_Workshop', 'B_Interventor', 'B_Supervisor',
                  'C_FutureMessage', 'C_OfficialRecord', 'C_AuthenticRecord'])
              and not any(n in actors for n in ['B_WorkshopEscapeDoor', 'B_ArchiveGate', 'B_RecordsDoor']))

        def drain():
            for _ in range(150):
                if not prop(manager, 'bDialogueActive'):
                    break
                hud.call_method('UseNarrativeInteraction')
            check('Dialogue drains through production HUD', not prop(manager, 'bDialogueActive'))

        def approach(location):
            check('Collision-safe test approach', pawn.call_method('K2_TeleportTo', args=(location, pawn.get_actor_rotation())))
            pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()

        drain()
        # The live player's animation component and controller are initialized,
        # unlike the worldless A fixture. Verify stamina gates with real timers.
        pawn.call_method('DoParry')
        check('Live parry spends A stamina', prop(pawn, 'bParryWindow') and prop(combat, 'CurrentStamina') == 90)
        pawn.call_method('EndParry')
        combat.call_method('SetStamina', args=(0.,))
        pawn.call_method('DoParry')
        check('Live parry rejects empty stamina', not prop(pawn, 'bParryWindow'))
        await asyncio.sleep(1.2)
        check('Stamina regenerates in real PIE', prop(combat, 'CurrentStamina') > 0)

        checkpoint = actors['C_Closure_CP0']
        approach(checkpoint.get_actor_location() + u.Vector(0, -100, 100))
        checkpoint.call_method('Interact', args=(pawn,))
        before_restore = prop(u.GameplayStatics.get_game_mode(world), 'RestoreCount')
        pawn.call_method('TakeHit', args=(1000.,))
        await asyncio.sleep(.2)
        check('main checkpoint restoration survives the A health merge',
              prop(u.GameplayStatics.get_game_mode(world), 'RestoreCount') == before_restore + 1
              and not prop(pawn, 'bDead') and prop(health, 'CurrentHealth') == 100)
        check('Restored player can still move', pawn.get_component_by_class(u.CharacterMovementComponent).movement_mode == u.MovementMode.MOVE_WALKING)

        side = actors['C_SideDoor']
        check('Side door starts phase-locked', not side.call_method('CanInteract', args=(pawn,)))
        statics = u.get_default_object(u.GameplayStatics)
        transform = u.Transform()
        source = statics.call_method('BeginDeferredActorSpawnFromClass', args=(world,
            cls('Narrative/Test/BP_StoryEventTestSource_C'), transform,
            u.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, u.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        source = statics.call_method('FinishSpawningActor', args=(source, transform, u.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        event_type = type(prop(source, 'EventToReport'))

        def report(index, param=''):
            source.set_editor_property('EventToReport', event_type.cast(index))
            source.set_editor_property('EventParam', param)
            source.call_method('ReportConfiguredEvent')
            drain()

        report(0)
        approach(u.Vector(2735, 4780, 100))
        check('JackFound unlocks the single side door', side.call_method('CanInteract', args=(pawn,)))
        side.call_method('Interact', args=(pawn,))
        await asyncio.sleep(.9)
        check('Animated door opens and reports the real escape event',
              prop(side, 'bIsOpen') and state.call_method('GetCurrentPhase').value == 2)
        report(2)
        report(3, 'NursingRecord')
        report(3, 'FabricatedReport')
        manager.call_method('TryStartTruthRevelation')
        drain()
        await asyncio.sleep(.3)
        drain()
        check('C revelation reaches FinalChoice without choosing an ending',
              state.call_method('GetCurrentPhase').value == 4 and manager.call_method('GetRegisteredEnding').value == 0)

        archive = actors['C_ArchiveGate']
        check('Archive still requires B Interventor defeat', not archive.call_method('CanInteract', args=(pawn,)))
        actors['B_Interventor'].call_method('B_ApplyHealthDamage', args=(10000.,))
        result['interventor_diagnostics'] = {
            'health': prop(actors['B_Interventor'], 'B_Health'),
            'correction_done': prop(actors['B_Interventor'], 'bB_CorrectionDone'),
            'can_run': actors['B_Interventor'].call_method('B_CanRunEncounter'),
            'defeated': actors['B_Interventor'].call_method('IsDefeated'),
            'archive_can_interact': archive.call_method('CanInteract', args=(pawn,))}
        check('Defeating the actual Interventor unlocks the C archive gate', archive.call_method('CanInteract', args=(pawn,)))
        records = actors['C_RecordsDoor']
        check('Records still requires Supervisor defeat', not records.call_method('CanInteract', args=(pawn,)))
        actors['B_Supervisor'].call_method('B_ApplyHealthDamage', args=(10000.,))
        drain()
        check('Actual B Supervisor defeat reaches the C objective manager', manager.call_method('IsSupervisorDefeated'))
        approach(u.Vector(4620, 3000, 100))
        records.call_method('Interact', args=(pawn,))
        await asyncio.sleep(.9)
        check('Records door opens after real boss-defeat event', prop(records, 'bIsOpen'))

        station = actors['C_OfficialRecord' if case == 'official' else 'C_AuthenticRecord']
        other = actors['C_AuthenticRecord' if case == 'official' else 'C_OfficialRecord']
        selected = 1 if case == 'official' else 2
        approach(u.Vector(5060, 2600 if case == 'official' else 3400, 100))
        check('Unconfirmed final cannot register', not station.call_method('ConfirmRegistration', args=(pawn,)))
        station.call_method('Interact', args=(pawn,))
        check('C modal opens without choosing an ending',
              prop(hud, 'bFinalConfirmationOpen') and manager.call_method('GetRegisteredEnding').value == 0)
        hud.call_method('CancelFinalChoice')
        check('Cancellation restores movement input', not prop(hud, 'bFinalConfirmationOpen') and not pc.is_move_input_ignored())
        station.call_method('Interact', args=(pawn,))
        await asyncio.sleep(.5)
        hud.call_method('ConfirmFinalChoice')
        await asyncio.sleep(.15)
        check('Confirmed record selects the intended C ending exactly once',
              manager.call_method('GetRegisteredEnding').value == selected
              and state.call_method('GetCurrentPhase').value == 5
              and prop(station, 'RegistrationCount') == 1 and prop(hud, 'bEndingPresented'))
        check('Terminal ending pauses gameplay and shows its widget',
              u.GameplayStatics.is_game_paused(world) and prop(hud, 'FinalView').is_in_viewport())
        other.call_method('Interact', args=(pawn,))
        check('Opposite record cannot replace the final',
              not other.call_method('CanInteract', args=(pawn,))
              and manager.call_method('GetRegisteredEnding').value == selected)
        result['passed'] = True
    except Exception:
        result['error'] = traceback.format_exc()
        u.log_error(result['error'])
    finally:
        (outdir / ('play_' + case + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
        print('PROPS_HUD_PLAY ' + json.dumps(result))
        levels.editor_request_end_play()
        await asyncio.sleep(.5)
        u.SystemLibrary.quit_editor()

assert not worlds.get_game_world()
u.EditorPythonScripting.set_keep_python_script_alive(True)
assert levels.load_level('/Game/Unscripted/Maps/L_Whitechapel')
levels.editor_request_begin_play()
merge_loop = EditorEventLoopManager()
merge_loop.__enter__()
merge_task = merge_loop.loop.create_task(run())
