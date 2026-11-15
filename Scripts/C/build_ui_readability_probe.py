"""Test-only native Slate measurement; no production package references this actor.

FGeometry is opaque in the Python bridge. Keep it inside a Blueprint and return
only reflected Vector2D values to inspect real painted layout rather than zeros.
"""
import unreal,sys
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'));import blueprint_helpers_c as h
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
bp=unreal.load_asset('/Game/Unscripted/UI/Test/BP_UIReadabilityProbe_C')
if not bp:bp=h.create_actor_bp('UI/Test','BP_UIReadabilityProbe_C')
v=unreal.BlueprintEditorLibrary.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector2D'))
g=h.edit(bp,'MeasureWidget')
if g:h.clear_body(g)
else:g=h.function(bp,'MeasureWidget',[('Widget',h.obj_type(unreal.Widget))],[('Desired',v),('Allocated',v),('TopLeft',v),('BottomRight',v)])
widget=h.param(g,'Widget');geo=h.call(g,'/Script/UMG.Widget:GetCachedGeometry',target=widget).find_result_pin();allocated=h.call(g,'/Script/UMG.SlateBlueprintLibrary:GetLocalSize',Geometry=geo).find_result_pin();desired=h.call(g,'/Script/UMG.Widget:GetDesiredSize',target=widget).find_result_pin()
zero=h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector2D',X=0,Y=0).find_result_pin();a=h.call(g,'/Script/UMG.SlateBlueprintLibrary:LocalToAbsolute',Geometry=geo,LocalCoordinate=zero).find_result_pin();b=h.call(g,'/Script/UMG.SlateBlueprintLibrary:LocalToAbsolute',Geometry=geo,LocalCoordinate=allocated).find_result_pin()
h.result(g,g.find_graph_entry_pin(),Desired=desired,Allocated=allocated,TopLeft=a,BottomRight=b);h.layout(bp);h.save(bp);print('C_UI_READABILITY_PROBE_SAVED')
