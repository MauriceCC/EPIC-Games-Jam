"""Measure actual Slate layout for all authored C copy and long-text fixtures.

Only transient widget presentation is exercised. Story/player state is untouched;
the current objective/checklist are restored after each visual fixture.
"""
import unreal,asyncio,json,csv,traceback,base64,ast
from pathlib import Path
from toolset_registry._registry_interface import execute_tool
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'measurements':[],'asset_saves_performed':False}
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def getw(owner,name,anchor):
 try:return owner.get_editor_property(name)
 except Exception:pass
 root=owner.get_editor_property(anchor)
 while root.get_parent():root=root.get_parent()
 pending=[root]
 while pending:
  child=pending.pop()
  if child.get_name()==name:return child
  if isinstance(child,unreal.PanelWidget):pending.extend(child.get_all_children())
 raise AssertionError('Missing runtime widget: '+name)
def measure(w):return probe.call_method('MeasureWidget',args=(w,))
def size(w):return measure(w)[1]
def rect(w):
 _,_,a,b=measure(w);return(a.x,a.y,b.x,b.y)
def contained(child,parent,tolerance=2):
 a=rect(child);b=rect(parent);return a[0]>=b[0]-tolerance and a[1]>=b[1]-tolerance and a[2]<=b[2]+tolerance and a[3]<=b[3]+tolerance
def fits(name,text,parent):
 wanted=text.get_desired_size();actual=size(text);out['measurements'].append({'name':name,'text':str(text.get_text()),'desired':[wanted.x,wanted.y],'allocated':[actual.x,actual.y],'parent':list(rect(parent)),'text_bounds':list(rect(text))})
 check(name+' fits its measured text allocation',wanted.x<=actual.x+2 and wanted.y<=actual.y+2 and actual.x>0 and actual.y>0)
 check(name+' remains inside its panel',contained(text,parent))
async def key(name):
 unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport');await asyncio.sleep(.03);r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':name});assert r['returnValue'];await asyncio.sleep(.08)
async def settle():view.force_layout_prepass();await asyncio.sleep(.08)
async def capture(name):
 r=await execute_tool('SlateInspectorToolset.SlateInspectorToolset','Screenshot',{'ref':'w1'});folder=repo/'SourceData/C/Previews';folder.mkdir(exist_ok=True);path=folder/('Block3_'+name+'.png');path.write_bytes(base64.b64decode(r['returnValue']['data']));out.setdefault('captures',[]).append(str(path))
async def run():
 global view,probe
 try:
  await asyncio.sleep(.4)
  world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();view=p(hud,'View');manager=unreal.GameplayStatics.get_game_state(world).call_method('GetObjectiveManager');dialogue=p(view,'DialogueView');checklist=p(view,'ChecklistView')
  health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class());health_before=(p(health,'CurrentHealth'),p(health,'MaxHealth'))
  factory=unreal.get_default_object(unreal.GameplayStatics);cls=unreal.load_asset('/Game/Unscripted/UI/Test/BP_UIReadabilityProbe_C').generated_class();probe=factory.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls,unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));probe=factory.call_method('FinishSpawningActor',args=(probe,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
  unreal.SystemLibrary.execute_console_command(world,'viewmode lit',pc)
  # Genuine opening transmission, then native E completes the authored briefing.
  for _ in range(40):
   if not p(manager,'bDialogueActive'):break
   if str(p(manager,'CurrentDialogueRow'))=='Briefing_05':
    await key('E');await settle();await capture('DirectorTransmission')
   await key('E')
  await asyncio.sleep(.35)
  current=manager.call_method('GetStoryPhase');objective=getw(view,'ObjectiveCard','ObjectiveText')
  status=getw(view,'StatusPanel','ObjectiveText')
  for name in ('HealthCaption','HealthValueText','DetectionCaption','RetakeText','RetakeKeyHint','CutCooldownCaption','CutStateText'):
   fits('Live status '+name,getw(view,name,'ObjectiveText'),status)
  for i in range(6):
   view.call_method('SetObjective',args=(type(current).cast(i),));await settle();fits('Objective phase '+str(i),p(view,'ObjectiveText'),objective)
  p(view,'ObjectiveText').set_text('Protect Jack while preserving the nursing record and the fabricated report. Keep his identity secret until the truth can be archived.');await settle();fits('Long objective fixture',p(view,'ObjectiveText'),objective)
  view.call_method('SetObjective',args=(current,));await settle();await capture('Gameplay')
  await key('Tab');await asyncio.sleep(.3);case_root=getw(checklist,'ChecklistPanel','ItemText0')
  rows=list(csv.DictReader((repo/'SourceData/C/DT_Checklist.csv').open(encoding='utf-8-sig',newline='')))
  for row in rows:
   name=row['Name'];checklist.call_method('ApplyChecklistRow',args=(name,));await settle()
   for i in range(4):
    text=p(checklist,'ItemText'+str(i));line=p(checklist,'ItemRow'+str(i))
    if line.is_visible():fits(name+' directive '+str(i+1),text,line)
  for i in range(4):p(checklist,'ItemText'+str(i)).set_text('Keep the nursing record and the fabricated report together. Protect the identity of the innocent man while preserving an authentic account of what the Director ordered. ')
  await settle();area=getw(checklist,'DossierReadingArea','ItemText0');hint=getw(checklist,'ChecklistHint','ItemText0')
  check('Long directives use a bounded scroll area',size(area).y<=451 and size(area).y>0)
  check('The dossier footer stays inside its cover',contained(hint,case_root))
  checklist.call_method('ApplyChecklistRow',args=('FindJack',));await settle();await capture('CaseFile');await key('Tab');await asyncio.sleep(.3)
  # Presenter-only fixtures cover every existing English dialogue line.
  dialogue_rows=list(csv.DictReader((repo/'SourceData/C/DT_Dialogue.csv').open(encoding='utf-8-sig',newline='')))
  root=getw(dialogue,'DialoguePanel','BodyText');view.call_method('ShowDialogue',args=('Director','Layout validation'));view.call_method('CompleteTransmissionEntrance')
  for row in dialogue_rows:
   dialogue.call_method('PresentLine',args=(row['Speaker'],row['Text']));dialogue.call_method('FinishReveal');await settle();fits(row['Name'],p(dialogue,'BodyText'),root)
  long_line='Preserve the nursing record and the fabricated report. Jack is innocent. The Director is manufacturing the history that the Department intends to archive. '*3
  dialogue.call_method('PresentLine',args=('Supervisor',long_line));dialogue.call_method('FinishReveal');await settle();fits('Long transmission fixture',p(dialogue,'BodyText'),root)
  advance=getw(dialogue,'AdvanceButton','BodyText');check('The continue control stays inside long transmissions',contained(advance,root))
  view.call_method('HideDialogue');view.call_method('ApplyDialogueExit',args=(1.0,));await settle()
  # Both actual evidence texts, presented through the existing document path.
  narrative={r['Key']:r['Text'] for r in csv.DictReader((repo/'SourceData/C/NarrativeText.csv').open(encoding='utf-8-sig',newline=''))}
  for prefix in ('NursingRecord','FabricatedReport'):
   hud.call_method('OpenDocument',args=(narrative[prefix+'_Title'],narrative[prefix+'_Summary']));await settle();doc=p(view,'DocumentView');body=p(doc,'DocumentBody');scroll=getw(doc,'DocumentScroll','DocumentBody');root=getw(doc,'DocumentPanel','DocumentBody')
   check(prefix+' wraps within the document reading width',body.get_desired_size().x<=size(scroll).x+2)
   check(prefix+' keeps the close button inside its panel',contained(getw(doc,'CloseButton','DocumentBody'),root));await key('E');check(prefix+' closes through native E',not p(hud,'bDocumentOpen'))
  view.call_method('ShowContinuityNotice');await asyncio.sleep(.11)
  notice=p(view,'ContinuityText');back=p(view,'ContinuityBackdrop');check('The notice backdrop mirrors the existing fade',notice.is_visible() and back.is_visible() and abs(notice.get_render_opacity()-back.get_render_opacity())<.02)
  fits('Continuity notice',notice,back);await capture('ContinuityNotice');view.call_method('HideContinuityNotice');check('The notice backdrop closes with the original notice',not notice.is_visible() and not back.is_visible())
  check('Layout fixtures never change the narrative phase',manager.call_method('GetStoryPhase').value==current.value)
  check('Layout fixtures never substitute player health',health_before==(p(health,'CurrentHealth'),p(health,'MaxHealth')))
  hud.call_method('UpdateChecklist');await settle();out['viewport_size']=list(size(getw(view,'HUDCanvas','ObjectiveText')).to_tuple());out['passed']=True
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:out['check_count']=len(out['checks']);(repo/'Scripts/C/block3_layout_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_BLOCK3_LAYOUT '+json.dumps({k:v for k,v in out.items() if k!='measurements'}))
c_block3_layout_loop=EditorEventLoopManager();c_block3_layout_loop.__enter__();c_block3_layout_task=c_block3_layout_loop.loop.create_task(run())
