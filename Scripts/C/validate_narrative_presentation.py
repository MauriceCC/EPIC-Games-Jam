"""Staged real-player presentation tests. Never invent or replace health data.

Only C presentation-step functions are advanced for deterministic intermediate frames.
Native E/Tab/R/F events are sent between stages by the editor automation client.
"""
import unreal,json,sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
file=repo/'Scripts/C/narrative_presentation_validation.json';stage=globals().get('C_PRESENT_STAGE','baseline')
out={'checks':[],'external_blockers':[]} if stage=='baseline' else json.loads(file.read_text(encoding='utf-8'))
def p(o,n):return o.get_editor_property(n)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok),'stage':stage});assert ok,name
def focus():unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
try:
 world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0)
 hud=pc.get_hud();view=p(hud,'View');dialogue=p(view,'DialogueView');drawer=p(view,'ChecklistDrawer');state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager');mode=unreal.GameplayStatics.get_game_mode(world)
 health=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Player/BP_HealthComponent').generated_class())
 interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class())
 time=unreal.GameplayStatics.get_time_seconds(world)
 if stage=='baseline':
  check('The real player and saved C HUD are active',pawn.get_class().get_path_name()=='/Game/Unscripted/Player/BP_PlayerCharacter.BP_PlayerCharacter_C' and view.is_in_viewport())
  check('The full dossier starts hidden',drawer.get_visibility()==unreal.SlateVisibility.COLLAPSED and p(view,'ChecklistAlpha')==0)
  check('Only the primary objective is presented permanently',str(p(view,'ObjectiveText').get_text())=='Locate Jack.' and not p(view,'TestHintBackdrop').is_visible())
  out['health_before']={'max':p(health,'MaxHealth'),'current':p(health,'CurrentHealth')}
  if p(health,'MaxHealth')<=0:
   check('Invalid A health is reported honestly',str(p(view,'HealthValueText').get_text())=='NO VITALS DATA' and p(view,'AgentVitalsRing').get_dynamic_material().get_scalar_parameter_value('HealthKnown')==0)
   out['external_blockers'].append('A: the player component template still supplies MaxHealth=0 and CurrentHealth=0; C cannot show valid numeric vitals.')
  check('CP0 remains the initial checkpoint',str(p(mode,'CheckpointId'))=='CP0')
  out['initial_row']=str(p(manager,'CurrentDialogueRow'));check('The automatic opening briefing still starts',out['initial_row']=='Briefing_01')
  # Restart only the view of the current authored line to inspect the incoming state.
  view.call_method('HideDialogue');hud.call_method('SyncDialogue')
  check('New transmission begins with a notice and no abrupt dialogue panel',p(view,'IncomingTransmission').is_visible() and not dialogue.is_visible() and not p(view,'bDialoguePanelReady'))
  check('Restarting presentation does not alter story progress',state.call_method('GetCurrentPhase').value==0 and str(p(manager,'CurrentDialogueRow'))==out['initial_row'])
  focus()
 elif stage=='first_e':
  check('E during incoming transmission reveals the line without skipping it',str(p(manager,'CurrentDialogueRow'))==out['initial_row'] and p(view,'bDialoguePanelReady'))
  check('The revealed body is complete and the incoming notice is gone',str(p(dialogue,'BodyText').get_text())==str(p(dialogue,'FullLine')) and not p(view,'IncomingTransmission').is_visible())
  focus()
 elif stage=='row_two':
  check('The next E advances exactly one authored line',str(p(manager,'CurrentDialogueRow'))=='Briefing_02')
  body=p(dialogue,'FullLine');speaker=p(dialogue,'SpeakerText').get_text()
  dialogue.call_method('PrepareLine',args=(speaker,));dialogue.call_method('PresentLine',args=(speaker,body))
  dialogue.call_method('ApplyRevealProgress',args=(6,))
  partial=str(p(dialogue,'BodyText').get_text());full=str(body)
  check('Text reveal produces a real intermediate substring',0<len(partial)<len(full) and full.startswith(partial))
  start=p(dialogue,'RevealStartTime');hud.call_method('SyncDialogue')
  check('Repeated synchronization does not restart the current line',p(dialogue,'RevealStartTime')==start)
  check('Subsequent lines do not repeat the incoming transmission',not p(view,'IncomingTransmission').is_visible())
  # Inspect a genuine entrance intermediate frame without changing the manager.
  view.call_method('HideDialogue');hud.call_method('SyncDialogue');view.call_method('ApplyTransmissionEntrance',args=(.97,))
  check('Transmission entrance fades and slides rather than snapping',0<dialogue.get_render_opacity()<1 and dialogue.get_editor_property('render_transform').translation.y>0)
  view.call_method('CompleteTransmissionEntrance');dialogue.call_method('FinishReveal')
  focus()
 elif stage=='drawer_open':
  check('Native Tab requests the dossier',p(view,'bChecklistRequested'))
  view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(1.0,));view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(.08,))
  check('Dossier opening has a visible intermediate fade and slide',0<drawer.get_render_opacity()<1 and drawer.get_editor_property('render_transform').translation.x>0)
  view.call_method('StepChecklistTransition',args=(1.0,))
  check('The open dossier settles fully visible',p(view,'ChecklistAlpha')==1 and drawer.get_render_opacity()==1 and drawer.is_visible())
  focus()
 elif stage=='drawer_close':
  check('Native Tab requests closing',not p(view,'bChecklistRequested'))
  view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(1.0,));view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(.08,))
  check('Closing preserves the panel during its fade',0<drawer.get_render_opacity()<1 and drawer.is_visible())
  view.call_method('StepChecklistTransition',args=(1.0,))
  check('The closed dossier collapses completely',drawer.get_visibility()==unreal.SlateVisibility.COLLAPSED and p(view,'ChecklistAlpha')==0)
  view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(.1,));view.call_method('ToggleChecklist');view.call_method('StepChecklistTransition',args=(1.0,))
  check('Rapid reversal cannot leave an invisible blocking drawer',drawer.get_visibility()==unreal.SlateVisibility.COLLAPSED and not p(view,'bChecklistRequested'))
  # A document may cover a transmission without advancing the underlying line.
  row=str(p(manager,'CurrentDialogueRow'));hud.call_method('OpenDocument',args=('Field record','Department of Continuity / recorded observation.'))
  check('Document presentation keeps narrative input ownership',p(hud,'bDocumentOpen') and p(manager,'bDocumentActive'))
  hud.call_method('CloseDocument')
  check('Closing the document preserves the current dialogue row',str(p(manager,'CurrentDialogueRow'))==row and not p(hud,'bDocumentOpen'))
  for _ in range(40):
   if not p(manager,'bDialogueActive'):break
   hud.call_method('UseNarrativeInteraction')
  check('The briefing can be completed without skipping story phases',not p(manager,'bDialogueActive') and state.call_method('GetCurrentPhase').value==0)
  view.call_method('ApplyDialogueExit',args=(1.0,))
  check('Transmission closes cleanly and queues no unrelated conversation',not dialogue.is_visible() and not p(manager,'DialogueQueue'))
  check('No health values were invented during presentation tests',out['health_before']=={'max':p(health,'MaxHealth'),'current':p(health,'CurrentHealth')})
  out['retake_before']=p(pawn,'RetakeCharges');focus()
 elif stage=='retake':
  check('The real R ability still updates the integrated charge display',p(pawn,'RetakeCharges')==out['retake_before']-1 and str(p(view,'RetakeText').get_text()).startswith('Retake 1 / 2'))
  check('Health remains the actual A component state after Retake',out['health_before']=={'max':p(health,'MaxHealth'),'current':p(health,'CurrentHealth')})
  guards=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Enemies/BP_Pursuer').generated_class());check('A real encounter is available for F',bool(guards))
  pawn.set_actor_location(guards[0].get_actor_location()+unreal.Vector(180,0,0),False,True);focus()
 elif stage=='cut':
  check('The real F ability drives the HUD cooldown',not p(pawn,'bCutReady') and p(p(view,'CutCooldownBar'),'percent')>0 and str(p(view,'CutStateText').get_text())!='READY')
  pawn.set_actor_location(unreal.Vector(300,1800,100),False,True)
 elif stage=='ready':
  check('Gameplay and the visual cooldown both become ready',p(pawn,'bCutReady') and p(p(view,'CutCooldownBar'),'percent')==0 and str(p(view,'CutStateText').get_text())=='READY')
  check('Idle gameplay does not start later dialogue automatically',not p(manager,'bDialogueActive') and not p(view,'bDialogueSessionOpen'))
  points=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Checkpoint').generated_class());cp=next(x for x in points if str(p(x,'CheckpointId'))=='CP1')
  pawn.set_actor_location(cp.get_actor_location()+unreal.Vector(100,0,100),False,True);interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
  check('Real world interaction prompt is still connected',p(interaction,'FocusedActor')==cp and 'checkpoint' in str(p(view,'InteractionText').get_text()).lower());focus()
 elif stage=='checkpoint':
  check('Native E still records CP1',str(p(mode,'CheckpointId'))=='CP1')
  hide=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Hideout').generated_class())[0]
  pawn.set_actor_location(p(hide,'ExitPoint').get_world_location(),False,True);interaction.call_method('RefreshFocus');hud.call_method('UseNarrativeInteraction')
  check('The wardrobe starts the real player entry transition',p(hide,'bTransitioning') and p(hide,'Occupant')==pawn)
  focus()
 elif stage=='wardrobe_entered':
  hide=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Hideout').generated_class())[0]
  check('The wardrobe hides the real player after walking in',p(hide,'bOccupied') and not p(hide,'bTransitioning') and p(pawn.get_component_by_class(unreal.SkeletalMeshComponent),'hidden_in_game'))
  focus()
 elif stage=='wardrobe_exited':
  hide=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.load_asset('/Game/Unscripted/Narrative/BP_Hideout').generated_class())[0]
  check('The wardrobe releases the real player after walking out',not p(hide,'bOccupied') and not p(hide,'bTransitioning') and not pc.is_move_input_ignored() and not p(pawn.get_component_by_class(unreal.SkeletalMeshComponent),'hidden_in_game'))
  check('Story progress remains in Act I',state.call_method('GetCurrentPhase').value==0)
  out['finished']=True
 out['last_stage']=stage
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 out['passed']=bool(out.get('finished')) and not out.get('error');out['check_count']=len(out['checks']);file.write_text(json.dumps(out,indent=2),encoding='utf-8')
 print('C_NARRATIVE_PRESENTATION_TEST '+json.dumps(out))
