"""Check Block 1 interaction clearance against the integrated static world in PIE."""
import unreal,json,traceback,sys
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
out={'passed':False,'points':[],'asset_saves_performed':False}
try:
 world=unreal.EditorLevelLibrary.get_pie_worlds(False)[0]
 own={x.get_actor_label():x for x in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if x.get_actor_label().startswith('C_Closure_')}
 for name,offset in [('C_Closure_CP0',(0,0,110)),('C_Closure_CP1',(0,0,110)),('C_Closure_AlleyHideout',(140,0,110))]:
  point=own[name].get_actor_location()+unreal.Vector(*offset)
  actors=unreal.SystemLibrary.capsule_overlap_actors(world,point,42,65,[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1],unreal.StaticMeshActor,list(own.values())) or []
  blockers=[x.get_actor_label() for x in actors if x.get_component_by_class(unreal.StaticMeshComponent).get_collision_response_to_channel(unreal.CollisionChannel.PAWN)==unreal.CollisionResponse.BLOCK]
  out['points'].append({'name':name,'point':list(point.to_tuple()),'blocking_static_meshes':blockers})
 out['passed']=not any(x['blocking_static_meshes'] for x in out['points'])
except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
finally:
 (repo/'Scripts/C/closure_clearance_validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print('C_CLOSURE_CLEARANCE '+json.dumps(out))
