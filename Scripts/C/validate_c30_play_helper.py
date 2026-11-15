"""Check the documented C-30 Play setup with native E and the real player.

The helper supplies only missing B prerequisites and safe approach positions.
Evidence, door and dialogue interactions remain production gameplay.
"""
import unreal,asyncio,runpy,json,traceback,base64,time
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'asset_saves_performed':False}
def check(name,ok):
 out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def p(o,n):return o.get_editor_property(n)
def prepare(stage):return runpy.run_path(str(repo/'Scripts/C/prepare_c30_play.py'),init_globals={'C30_STAGE':stage})
async def key(name):
 unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
 await asyncio.sleep(.04)
 r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert r['returnValue']
 await asyncio.sleep(.06)
async def drain(manager):
 for _ in range(90):
  if not p(manager,'bDialogueActive'):return
  await key('E')
 raise AssertionError('The dialogue exceeded its bounded native-E input sequence')
async def run():
 try:
  fixture=prepare('workshop');world,pawn,manager,state,hud,interaction=[fixture[k] for k in ('world','pawn','manager','state','hud','interaction')]
  view=p(hud,'View');unreal.SystemLibrary.execute_console_command(world,'viewmode lit',fixture['pc'])
  check('Workshop setup leaves the real Jack conversation for E',state.call_method('GetCurrentPhase').value==1 and str(p(manager,'CurrentDialogueRow'))=='JackFound_01')
  await drain(manager);interaction.call_method('RefreshFocus');await key('E')
  check('E at the workshop table starts the future message',str(p(manager,'CurrentDialogueRow'))=='FutureMessage_01')
  await drain(manager);check('The future message is completed by native E',p(manager,'bFutureMessageRead'))
  prepare('escape');await key('E');await asyncio.sleep(.5)
  check('The escape setup requires the actual door interaction',state.call_method('GetCurrentPhase').value==2)
  prepare('refuge');check('The refuge setup stops at DiscoverTruth',state.call_method('GetCurrentPhase').value==3 and not p(manager,'bTruthRevelationStarted'))
  for name,point in [('C_NursingRecord',(3460,460,90)),('C_FabricatedReport',(2520,1200,90))]:
   assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(*point),pawn.get_actor_rotation()))
   await asyncio.sleep(.08);interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
   check(name+' is available through the normal E focus',p(interaction,'FocusedActor').get_actor_label()==name)
   await key('E');check(name+' opens a real document',p(hud,'bDocumentOpen'))
   await key('E');check(name+' closes with native E',not p(hud,'bDocumentOpen'))
  check('Both documents start the Supervisor transmission',str(p(manager,'CurrentDialogueRow'))=='Truth_01' and state.call_method('GetCurrentPhase').value==3)
  for _ in range(30):
   if state.call_method('GetCurrentPhase').value==4:break
   await key('E')
  check('The final E confirmation reaches FinalChoice',state.call_method('GetCurrentPhase').value==4 and p(manager,'bTruthRevelationComplete'))
  await asyncio.sleep(.65)
  check('The final notice sits below the transmission header',p(view,'ContinuityText').slot.get_position().y==120 and p(view,'ContinuityText').is_visible())
  await asyncio.sleep(.4)
  check('The revised orders are visibly shown',p(view,'ChecklistDrawer').is_visible() and p(p(view,'ChecklistView'),'bHasRewritten'))
  r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','Screenshot',{'ref':'w1'})
  capture=repo/'SourceData/C/Previews/C30_FinalRewriteAndNotice.png';capture.write_bytes(base64.b64decode(r['returnValue']['data']));out['capture']=str(capture)
  await drain(manager);await asyncio.sleep(2.5)
  check('The short narrative presentation returns to the compact HUD',not p(view,'ContinuityText').is_visible() and not p(view,'bChecklistRequested'))
  check('The procedure does not select an ending',p(manager,'Ending').value==0 and not manager.call_method('IsSupervisorDefeated'))
  out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:
  out['check_count']=len(out['checks']);(repo/'Scripts/C/c30_play_helper_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C30_PLAY_HELPER_TEST '+json.dumps(out))
c30_helper_loop=EditorEventLoopManager();c30_helper_loop.__enter__();c30_helper_task=c30_helper_loop.loop.create_task(run())
