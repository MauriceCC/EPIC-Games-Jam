"""Read-only persistence checks after reopening the editor on the C branch."""
import unreal, json, hashlib, traceback
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'checks':[],'asset_saves_performed':False}
paths=('UI/BP_HUD','UI/WBP_HUD','UI/WBP_Dialogue','UI/WBP_Checklist',
       'UI/Materials/M_UI_AgentVitals_C','UI/Materials/M_UI_DepartmentPlate_C',
       'Narrative/BP_Hideout','Maps/L_Whitechapel_Story')
def asset(rel):return unreal.load_asset('/Game/Unscripted/'+rel)
def check(name,ok):out['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def hashes():
    return {rel:hashlib.sha256((repo/'Unscripted/Content/Unscripted'/(rel+('.umap' if rel.startswith('Maps/') else '.uasset'))).read_bytes()).hexdigest() for rel in paths}
def functions(bp):return {str(g.get_name()) for g in unreal.BlueprintEditorLibrary.list_graphs(bp)}
try:
    check('Persistence inspection runs outside PIE',not unreal.EditorLevelLibrary.get_pie_worlds(False))
    out['disk_hashes']=hashes()
    check('Every saved production package loads',all(asset(rel) for rel in paths))
    hud=asset('UI/BP_HUD');view=asset('UI/WBP_HUD');hide=asset('Narrative/BP_Hideout')
    check('Real-player HUD adapters and fade bridge persist',{'InitializePlayerPresentation','UseNarrativeInteraction','SetHideoutFade'}<=functions(hud))
    check('Dossier and transmission presentation functions persist',{'ToggleChecklist','StepChecklistTransition','CompleteTransmissionEntrance','SetHideoutFade'}<=functions(view))
    check('Progressive dialogue functions persist',{'PresentLine','FinishReveal','ApplyRevealProgress'}<=functions(asset('UI/WBP_Dialogue')))
    check('Controlled wardrobe transition and recovery functions persist',{'BeginEntry','BeginExit','TryHiddenReposition','AbortTransition','ReleaseOccupant','ValidateOccupant'}<=functions(hide))
    for name in ('ChecklistDrawer','HideoutTransitionVeil'):
        widget=unreal.find_object(None,view.get_path_name()+':WidgetTree.'+name)
        check(name+' is saved collapsed',widget and widget.get_visibility()==unreal.SlateVisibility.COLLAPSED)
    check('Compact status panel size persists',unreal.find_object(None,view.get_path_name()+':WidgetTree.StatusPanel').get_editor_property('slot').get_size()==unreal.Vector2D(366,104))
    actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label().startswith('C_Closure_')}
    check('Exactly the existing three Block 1 actors persist',set(actors)=={'C_Closure_CP0','C_Closure_CP1','C_Closure_AlleyHideout'})
    check('All C actors remain in Story',all('/Maps/L_Whitechapel_Story.' in a.get_path_name() for a in actors.values()))
    check('CP0 and CP1 identifiers persist',str(actors['C_Closure_CP0'].get_editor_property('CheckpointId'))=='CP0' and str(actors['C_Closure_CP1'].get_editor_property('CheckpointId'))=='CP1')
    wardrobe=actors['C_Closure_AlleyHideout']
    check('Collision-safe dock and exit persist',wardrobe.get_editor_property('EntryDock').get_world_location().distance(unreal.Vector(1100,3685,90))<.01 and wardrobe.get_editor_property('ExitPoint').get_world_location().distance(unreal.Vector(1100,3750,90))<.01)
    rows=json.loads(unreal.DataTableFunctionLibrary.export_data_table_to_json_string(asset('Narrative/DT_Dialogue')))
    check('All authored dialogue and the Director order persist',len(rows)==24 and next(r for r in rows if r['Name']=='Briefing_05')['Speaker']=='Director')
    check('Read-only inspection leaves saved bytes unchanged',hashes()==out['disk_hashes'])
    check('No content or map packages await saving',not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    out['passed']=True
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
    out['check_count']=len(out['checks'])
    (repo/'Scripts/C/hud_hideout_saved_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('C_HUD_HIDEOUT_SAVED '+json.dumps(out))
