"""Run the staged C presentation suite in fresh integrated Whitechapel PIE.

Uses native keyboard events and real player components. Runtime-only actor
placement isolates encounters; no gameplay asset or health data is changed.
"""
import unreal, asyncio, runpy, sys, json, traceback
from pathlib import Path
sys.dont_write_bytecode = True
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
suite = repo / 'Scripts/C/validate_narrative_presentation.py'
report = repo / 'Scripts/C/narrative_presentation_validation.json'

def stage(name):
    runpy.run_path(str(suite), init_globals={'C_PRESENT_STAGE': name})
    result = json.loads(report.read_text(encoding='utf-8'))
    assert not result.get('error'), result.get('error')

async def key(name):
    unreal.get_default_object(unreal.load_class(None, '/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
    await asyncio.sleep(.1)
    result = await execute_tool('SlateInspectorToolset.SlateInspectorToolset', 'PressKey', {'key': name})
    assert result['returnValue'], name
    await asyncio.sleep(.08)

async def run():
    try:
        await asyncio.sleep(.2)
        stage('baseline')
        await key('E'); stage('first_e')
        await key('E'); stage('row_two')
        await key('Tab'); stage('drawer_open')
        await key('Tab'); stage('drawer_close')
        await key('R'); await asyncio.sleep(.15); stage('retake')
        await key('F'); await asyncio.sleep(.1); stage('cut')
        world = unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        deadline = asyncio.get_running_loop().time() + 20
        while not pawn.get_editor_property('bCutReady'):
            assert asyncio.get_running_loop().time() < deadline, 'Frame Cut cooldown did not finish'
            await asyncio.sleep(.1)
        await asyncio.sleep(.15); stage('ready')
        await key('E'); stage('checkpoint')
        await asyncio.sleep(3); stage('wardrobe_entered')
        await key('E'); await asyncio.sleep(3); stage('wardrobe_exited')
        print('C_PRESENTATION_AUTOMATION_PASSED')
    except Exception:
        unreal.log_error('C_PRESENTATION_AUTOMATION_FAILED ' + traceback.format_exc())

c_presentation_loop = EditorEventLoopManager()
c_presentation_loop.__enter__()
c_presentation_task = c_presentation_loop.loop.create_task(run())
