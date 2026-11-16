"""Exercise the documented personal setup using only real E interactions."""
import unreal,asyncio,runpy,json,traceback,base64
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
async def key(name):
 r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert r['returnValue'];await asyncio.sleep(.12)
async def run():
 try:
  await asyncio.sleep(.4)
  continuing=globals().get('C_ENDING_CONTINUE_FROM_C30',False)
  setup=runpy.run_path(str(repo/'Scripts/C/prepare_endings_play.py'),init_globals={'C_ENDING_STAGE':'supervisor' if continuing else 'records_door'});world,pawn,hud,manager=[setup[k] for k in ('world','pawn','hud','manager')]
  check('Personal setup supplies prerequisites without registering a final',manager.call_method('GetRegisteredEnding').value==0 and manager.call_method('IsSupervisorDefeated'))
  await key('E');await asyncio.sleep(.45)
  setup=runpy.run_path(str(repo/'Scripts/C/prepare_endings_play.py'),init_globals={'C_ENDING_STAGE':'official'})
  check('The personal station approach requires the real open Records door',setup['door'].get_editor_property('bIsOpen'))
  await key('E');await asyncio.sleep(.7);check('The first E only opens confirmation',hud.get_editor_property('bFinalConfirmationOpen') and manager.call_method('GetRegisteredEnding').value==0)
  await key('E');await asyncio.sleep(.8);check('The next deliberate E completes the official record',manager.call_method('GetRegisteredEnding').value==1 and hud.get_editor_property('bEndingPresented'))
  r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','Screenshot',{'ref':'w1'});(repo/'SourceData/C/Previews/Ending_official_Final.png').write_bytes(base64.b64decode(r['returnValue']['data']))
  out['continued_from_c30']=continuing;out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:out['check_count']=len(out['checks']);(repo/'Scripts/C/ending_personal_setup_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_ENDING_PERSONAL_SETUP '+json.dumps(out))
c_ending_personal_loop=EditorEventLoopManager();c_ending_personal_loop.__enter__();c_ending_personal_task=c_ending_personal_loop.loop.create_task(run())
