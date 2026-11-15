"""Correct only the new C ending enum comparisons and station attachment."""
import unreal,sys,json
from pathlib import Path
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h
assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
count=0
for rel,specs in [('Narrative/BP_FinalChoice',{'CanInteract':[1,2],'ConfirmRegistration':[1]}),('Narrative/BP_ObjectiveManager',{'CanChooseFinalDocument':[0]}),('UI/WBP_Ending',{'PresentEnding':[1],'PresentConfirmation':[1]}),('UI/BP_HUD',{'PresentFinalEnding':[1,2]})]:
 bp=h.asset(rel)
 for name,expected in specs.items():
  g=h.edit(bp,name)
  nodes=[n for n in g.list_all_nodes() if 'equal' in str(n.get_node_title()).lower() and 'byte' in str(n.get_node_title()).lower()]
  if not nodes:continue
  assert len(nodes)==len(expected),(name,len(nodes))
  for n,index in zip(nodes,expected):
   a=n.find_input_pin('A');b=n.find_input_pin('B');out=n.find_result_pin()
   assert h.valid(a) and h.valid(b) and h.valid(out) and a.list_connected_pins()
   value=a.list_connected_pins()[0]
   links=list(out.list_connected_pins())
   integer=h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=value).find_result_pin();equal=h.math(g,'EqualEqual_IntInt',integer,index);out.break_pin_links()
   for pin in links:h.connect(equal,pin)
   g.remove_nodes([n]);count+=1
 h.save(bp)
bp=h.asset('Narrative/BP_FinalChoice');component=h.add_component(bp,'StationMesh',unreal.StaticMeshComponent);component.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);h.save(bp)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_class()==bp.generated_class():
  component=a.get_editor_property('StationMesh');component.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
  if component.get_attach_parent()!=a.root_component:assert component.attach_to_component(a.root_component,'',unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,unreal.AttachmentRule.KEEP_RELATIVE,False)
  component.set_relative_location(unreal.Vector(),False,True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert levels.set_current_level_by_name('L_Whitechapel_Story');assert levels.save_current_level();print('C_ENDING_BINDINGS_REFINED',count)
