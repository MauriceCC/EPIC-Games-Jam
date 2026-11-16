"""Position the real player for C-30; simulate only missing B prerequisite events.

Stages: workshop (JackFound), escape (approach the real side door), refuge
(JackReachedRefuge, only after the player opened the side door with E).
Never collects evidence, completes revelation or writes private story state.
"""
import unreal,json
from pathlib import Path
stage=globals().get('C30_STAGE','workshop');assert stage in ('workshop','escape','refuge')
world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0];assert 'L_Whitechapel.' in world.get_path_name()
pawn=unreal.GameplayStatics.get_player_pawn(world,0);pc=unreal.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud();state=unreal.GameplayStatics.get_game_state(world);manager=state.call_method('GetObjectiveManager')
assert state.call_method('GetCurrentPhase').value<4,'The revelation is already complete; restart PIE for a new run.'
def drain():
 for _ in range(100):
  if not manager.get_editor_property('bDialogueActive'):break
  hud.call_method('UseNarrativeInteraction')
if stage=='workshop' and state.call_method('GetCurrentPhase').value==0:
 drain()
 bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C');s=unreal.get_default_object(unreal.GameplayStatics)
 c30_source=s.call_method('BeginDeferredActorSpawnFromClass',args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));c30_source=s.call_method('FinishSpawningActor',args=(c30_source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));c30_source.set_editor_property('EventToReport',type(c30_source.get_editor_property('EventToReport')).cast(0));c30_source.call_method('ReportConfiguredEvent')
if stage=='escape':
 assert state.call_method('GetCurrentPhase').value==1,'Finish Jack dialogue, then open the real side door with E.'
 assert not manager.get_editor_property('bDialogueActive'),'Finish the current dialogue with E first.'
if stage=='refuge':
 assert state.call_method('GetCurrentPhase').value in (2,3),'Open C_SideDoor with E before preparing the refuge.'
 assert not manager.get_editor_property('bDialogueActive'),'Finish the current dialogue with E first.'
 if state.call_method('GetCurrentPhase').value==2:
  bp=unreal.load_asset('/Game/Unscripted/Narrative/Test/BP_StoryEventTestSource_C');s=unreal.get_default_object(unreal.GameplayStatics)
  c30_source=s.call_method('BeginDeferredActorSpawnFromClass',args=(world,bp.generated_class(),unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));c30_source=s.call_method('FinishSpawningActor',args=(c30_source,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT));c30_source.set_editor_property('EventToReport',type(c30_source.get_editor_property('EventToReport')).cast(2));c30_source.call_method('ReportConfiguredEvent')
point={'workshop':(3040,5300,90),'escape':(2735,4780,90),'refuge':(3000,800,90)}[stage]
assert pawn.call_method('K2_TeleportTo',args=(unreal.Vector(*point),pawn.get_actor_rotation())),'The C test approach is blocked.'
interaction=pawn.get_component_by_class(unreal.load_asset('/Game/Unscripted/Narrative/BP_InteractionComponent').generated_class());interaction.call_method('RefreshFocus');hud.call_method('RefreshInteractionPrompt')
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
print('C30_PLAY_READY '+json.dumps({'stage':stage,'phase':state.call_method('GetCurrentPhase').value,'position':list(pawn.get_actor_location().to_tuple()),'dialogue_active':manager.get_editor_property('bDialogueActive')}))
