"""Presentation-only Block 3 polish for Daniel's existing C widgets.

Preserves all story, input, evidence, final-choice and ability implementations.
Only a notice backdrop mirrors the existing animation and typewriter rate is tuned.
"""
import unreal,sys,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent;sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h,umg_helpers_c as u
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
out={'passed':False,'saved':[]}
def color(value,alpha=1):
 v=[int(value[i:i+2],16)/255 for i in (0,2,4)]
 return unreal.LinearColor(*[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v],alpha)
INK=color('10191D');PAPER=color('F0E8D8');GOLD=color('C8AA75');MUTED=color('B0B8B3');TEAL=color('8ABDB0')
def w(bp,name):
 obj=unreal.find_object(None,bp.get_path_name()+':WidgetTree.'+name);assert obj,name;return obj
def style(obj,size,tint=PAPER,bold=False,wrap=None,tracking=0):
 font=obj.get_editor_property('font');font.set_editor_property('size',size);font.set_editor_property('typeface_font_name','Bold' if bold else 'Regular');font.set_editor_property('letter_spacing',tracking);obj.set_font(font)
 obj.set_color_and_opacity(unreal.SlateColor(specified_color=tint));obj.set_auto_wrap_text(True)
 if wrap is not None:obj.set_editor_property('wrap_text_at',wrap)
def pad(obj,left=0,top=0,right=0,bottom=0):obj.slot.set_padding(unreal.Margin(left,top,right,bottom))
def auto_place(obj,x,y,width,anchor=(0,0),align=(0,0)):
 u.place(obj,x,y,width,0,anchor,align);obj.slot.set_auto_size(True)
def panel_material(obj,material,padding=0):obj.set_brush_from_material(material);obj.set_brush_color(unreal.LinearColor.WHITE);obj.set_padding(unreal.Margin(padding))
def brush(background,edge=GOLD):
 outline=unreal.SlateBrushOutlineSettings(corner_radii=unreal.Vector4(1,5,1,5),color=unreal.SlateColor(specified_color=edge),width=1,rounding_type=unreal.SlateBrushRoundingType.FIXED_RADIUS)
 return unreal.SlateBrush(draw_as=unreal.SlateBrushDrawType.ROUNDED_BOX,tint_color=unreal.SlateColor(specified_color=background),outline_settings=outline)
def button(obj,label,primary=False):
 b=obj.get_editor_property('widget_style')
 for key,shade in [('normal',color('765C35') if primary else color('293535')),('hovered',color('9B7B48') if primary else color('4A5549')),('pressed',color('4E3B24') if primary else color('182222')),('disabled',color('1B2426'))]:b.set_editor_property(key,brush(shade,color('8B7958')))
 obj.set_style(b);obj.set_background_color(unreal.LinearColor.WHITE);style(label,14,PAPER,True);label.set_auto_wrap_text(False);pad(label,18,9,18,9)
def material(name,code,parameters=False):
 path='/Game/Unscripted/UI/Materials/'+name;obj=unreal.load_asset(path)
 if obj and sum(isinstance(e,unreal.MaterialExpressionComponentMask) for e in unreal.MaterialEditingLibrary.get_material_expressions(obj))==2:return obj
 if obj:unreal.MaterialEditingLibrary.delete_all_material_expressions(obj)
 else:obj=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Unscripted/UI/Materials',unreal.Material,unreal.MaterialFactoryNew())
 obj.set_editor_property('material_domain',unreal.MaterialDomain.MD_UI);obj.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
 lib=unreal.MaterialEditingLibrary;uv=lib.create_material_expression(obj,unreal.MaterialExpressionTextureCoordinate,-700,0);expr=lib.create_material_expression(obj,unreal.MaterialExpressionCustom,-350,0);expr.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT4);expr.set_editor_property('code',code)
 inputs=[]
 for n in (('UV','Aspect','Tone','Accent') if parameters else ('UV',)):
  item=unreal.CustomInput();item.set_editor_property('input_name',n);inputs.append(item)
 expr.set_editor_property('inputs',inputs);assert lib.connect_material_expressions(uv,'',expr,'UV')
 if parameters:
  for n,kind,value,y in [('Aspect',unreal.MaterialExpressionScalarParameter,3.4,130),('Tone',unreal.MaterialExpressionVectorParameter,INK,260),('Accent',unreal.MaterialExpressionVectorParameter,GOLD,390)]:
   p=lib.create_material_expression(obj,kind,-700,y);p.set_editor_property('parameter_name',n);p.set_editor_property('default_value',value);assert lib.connect_material_expressions(p,'',expr,n)
 for alpha in (False,True):
  mask=lib.create_material_expression(obj,unreal.MaterialExpressionComponentMask,-80,150 if alpha else 0)
  for ch in ('r','g','b'):mask.set_editor_property(ch,not alpha)
  mask.set_editor_property('a',alpha);assert lib.connect_material_expressions(expr,'',mask,'');assert lib.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY if alpha else unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 errors=list(lib.recompile_material(obj));assert not errors,errors;assert unreal.EditorAssetLibrary.save_loaded_asset(obj,False);out['saved'].append(path);return obj
def instance(parent,name,aspect,tone=INK):
 path='/Game/Unscripted/UI/Materials/'+name;obj=unreal.load_asset(path)
 if not obj:obj=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,'/Game/Unscripted/UI/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
 lib=unreal.MaterialEditingLibrary;lib.set_material_instance_parent(obj,parent);lib.set_material_instance_scalar_parameter_value(obj,'Aspect',aspect);lib.set_material_instance_vector_parameter_value(obj,'Tone',tone);lib.set_material_instance_vector_parameter_value(obj,'Accent',GOLD);lib.update_material_instance(obj);assert unreal.EditorAssetLibrary.save_loaded_asset(obj,False);out['saved'].append(path);return obj
async def width_wrapper(bp,root,content,name,width):
 box=unreal.find_object(None,bp.get_path_name()+':WidgetTree.'+name)
 if not box:
  content_name=content.get_name()
  if not isinstance(content.get_parent(),unreal.SizeBox):
   await u.tool('WrapWidgets',widgetBlueprint=u.ref(bp),widgets=[u.ref(content)],wrapperClass=u.ref(unreal.SizeBox.static_class()))
  box=w(bp,content_name).get_parent();assert isinstance(box,unreal.SizeBox)
  await u.tool('RenameWidget',widgetBlueprint=u.ref(bp),widget=u.ref(box),newDisplayName=name)
  box=w(bp,name)
 box.set_width_override(width)
 return box
async def rule(bp,parent,name,x,y,width,height=1,tint=GOLD):
 obj=await u.widget(bp,unreal.Border,name,parent);obj.set_brush_color(tint);obj.set_padding(unreal.Margin(0));obj.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE);u.place(obj,x,y,width,height);return obj
def append_after(g,node,callback):
 pin=node.find_then_pin();targets=list(pin.list_connected_pins());pin.break_pin_links();end=callback(pin)
 for p in targets:h.connect(end,p)
async def build():
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
 assert all(p.get_name().startswith('/Game/Unscripted/UI/') for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
 frame=material('M_UI_CutBrassFrame_C',r'''
float a=max(Aspect,1.0);float2 q=float2(UV.x*a,UV.y);float cut=.075;
float edge=min(min(q.x,a-q.x),min(q.y,1-q.y));
float bevel=min(q.x+q.y-cut,(a-q.x)+(1-q.y)-cut)*.7071;
float sd=min(edge,bevel),aa=max(fwidth(sd),.001);
float mask=smoothstep(-aa,aa,sd);
float grain=frac(sin(dot(floor(UV*float2(1100,320)),float2(12.9898,78.233)))*43758.5453);
float3 col=Tone.rgb+(1-UV.y)*.006+(grain-.5)*.004;
float rim=1-smoothstep(.008,.016,sd);col=lerp(col,Accent.rgb*.70,rim);
float etched=(1-smoothstep(.0015,.0035,abs(sd-.030)))*.24;col+=etched*Accent.rgb;
float pin=min(length(q-float2(.10,.065)),length(q-float2(a-.10,.935)));
col=lerp(col,Accent.rgb*.75,1-smoothstep(.011,.017,pin));
float top=step(.34,q.x)*step(q.x,a-.12)*(1-smoothstep(.004,.010,abs(q.y-.014)));
col+=top*Accent.rgb*.22;
return float4(col,.98*mask);
''',True)
 paper=material('M_UI_ArchivePaper_C',r'''
float n=frac(sin(dot(floor(UV*float2(1500,1200)),float2(12.9898,78.233)))*43758.5453);
float edge=min(min(UV.x,1-UV.x),min(UV.y,1-UV.y));
float aged=1-smoothstep(.001,.075,edge);
float fiber=sin(UV.y*2800+sin(UV.x*40))*.0015;
float3 col=float3(.70,.625,.465)+(n-.5)*.010+fiber-aged*float3(.07,.065,.045);
return float4(col,1);
''')
 mats={k:instance(frame,'MI_UI_'+k+'_C',a,t) for k,a,t in [('AgentPlate',3.68,INK),('ObjectivePlate',4.0,INK),('DossierPlate',1.12,color('1B211F')),('TransmissionPlate',3.6,INK),('NoticePlate',9.3,color('1A2020')),('PromptPlate',10.55,INK),('DocumentPlate',1.57,color('181E1E')),('EndingAside',.50,color('111A1D')),('ConfirmationPlate',1.61,color('151D20'))]}
 view=h.asset('UI/WBP_HUD');canvas=w(view,'HUDCanvas');status=w(view,'StatusPanel');panel_material(status,mats['AgentPlate']);u.place(status,28,-28,500,136,(0,1),(0,1))
 positions=[('AgentVitalsRing',14,13,110,110),('HealthCaption',138,13,192,20),('HealthValueText',138,36,192,30),('HealthArea',138,73,192,5),('DetectionCaption',138,93,72,20),('DetectionArea',236,103,94,4),('RetakeText',362,15,126,26),('RetakePip0',364,50,27,5),('RetakePip1',403,50,27,5),('RetakeKeyHint',456,44,30,22),('CutCooldownCaption',362,75,126,20),('CutStateText',362,96,126,28),('CutCooldownArea',362,126,124,3)]
 for name,x,y,sx,sy in positions:u.place(w(view,name),x,y,sx,sy)
 for name,size,tint,bold in [('HealthCaption',11,MUTED,False),('HealthValueText',17,PAPER,True),('DetectionCaption',11,MUTED,False),('RetakeText',16,PAPER,True),('RetakeKeyHint',13,GOLD,True),('CutCooldownCaption',12,GOLD,False),('CutStateText',17,TEAL,True)]:style(w(view,name),size,tint,bold)
 for name,height in [('HealthArea',5),('DetectionArea',4),('CutCooldownArea',3)]:w(view,name).set_height_override(height)
 await rule(view,w(view,'VitalsLayout'),'AbilityDivider',344,15,1,109,color('867353',.65))
 for i in range(3):
  rivet=await rule(view,w(view,'VitalsLayout'),'AgentPlateMark'+str(i),17+i*8,124,3,3,color('C8AA75',.8));rivet.set_render_transform_angle(45)
 objective=w(view,'ObjectiveCard');panel_material(objective,mats['ObjectivePlate']);objective.set_padding(unreal.Margin(20,15,20,15));auto_place(objective,28,28,440)
 await width_wrapper(view,objective,w(view,'ObjectiveCardContent'),'ObjectiveMeasure',400)
 style(w(view,'ObjectiveEyebrow'),10,GOLD,True,tracking=90);w(view,'ObjectiveEyebrow').set_auto_wrap_text(False);pad(w(view,'ObjectiveEyebrow'),0,0,0,6)
 style(w(view,'ObjectiveText'),20,PAPER,False,392);w(view,'ObjectiveText').set_editor_property('line_height_percentage',1.12);pad(w(view,'ObjectiveText'))
 # Existing drawer, row widgets, completion strikes and rewrite animation remain.
 checklist=h.asset('UI/WBP_Checklist');root=w(checklist,'ChecklistPanel');panel_material(root,mats['DossierPlate']);root.set_padding(unreal.Margin(26,25,26,22));await width_wrapper(checklist,root,w(checklist,'ChecklistPanelContent'),'DossierMeasure',380)
 for name,size,tint,bold,wrap in [('ChecklistEyebrow',11,GOLD,True,380),('ChecklistTitle',28,PAPER,True,380),('RewriteStatus',12,TEAL,False,380),('ChecklistHint',12,MUTED,False,380)]:style(w(checklist,name),size,tint,bold,wrap)
 pad(w(checklist,'ChecklistEyebrow'),0,0,0,8);pad(w(checklist,'ChecklistTitle'),0,0,0,15);pad(w(checklist,'RewriteStatus'),0,0,0,15);pad(w(checklist,'ChecklistHint'),0,14,0,0)
 content=w(checklist,'ChecklistPanelContent');rows=w(checklist,'ChecklistRows');area=await u.widget(checklist,unreal.SizeBox,'DossierReadingArea',content);area.set_min_desired_height(180);area.set_max_desired_height(450)
 scroll=await u.widget(checklist,unreal.ScrollBox,'DossierScroll',area)
 if rows.get_parent()!=scroll:rows.remove_from_parent();scroll.add_child(rows)
 await u.tool('MoveWidget',widgetBlueprint=u.ref(checklist),widget=u.ref(area),newParent=u.ref(content),childIndex=3)
 for i in range(4):
  row=w(checklist,'ItemRow'+str(i));text=w(checklist,'ItemText'+str(i));style(text,18,PAPER,False,320);text.set_editor_property('line_height_percentage',1.12);pad(text,38,12,8,15);pad(row,0,0,0,7)
  number=await u.label(checklist,row,'DirectiveNumber'+str(i),f'{i+1:02}',11,GOLD);number.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE);number.slot.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_LEFT);number.slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_TOP);pad(number,0,15,0,0)
  line=await u.widget(checklist,unreal.SizeBox,'DirectiveRule'+str(i),row);line.set_height_override(1);line.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE);line.slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_BOTTOM);pad(line,38,0,0,0)
  ink=await u.widget(checklist,unreal.Border,'DirectiveRuleInk'+str(i),line);ink.set_brush_color(color('796B51',.5));ink.set_padding(unreal.Margin(0))
  strike=w(checklist,'Strike'+str(i));strike.set_width_override(316);pad(strike,38,0,8,0)
 drawer=w(view,'ChecklistDrawer');drawer.set_width_override(448);drawer.clear_height_override();auto_place(drawer,-28,62,448,(1,0),(1,0));style(w(view,'DossierKeyHint'),12,MUTED,True);u.place(w(view,'DossierKeyHint'),-29,23,240,25,(1,0),(1,0))
 # Stable width and adaptive height prevent typewriter text escaping its panel.
 dialogue=h.asset('UI/WBP_Dialogue');root=w(dialogue,'DialoguePanel');panel_material(root,mats['TransmissionPlate']);root.set_padding(unreal.Margin(28,20,28,18));await width_wrapper(dialogue,root,w(dialogue,'DialoguePanelContent'),'TransmissionMeasure',824)
 for name,size,tint,bold in [('DialogueEyebrow',11,MUTED,False),('SpeakerText',19,GOLD,True),('BodyText',22,PAPER,False),('AdvanceButtonLabel',14,PAPER,True)]:style(w(dialogue,name),size,tint,bold,812 if name=='BodyText' else None)
 pad(w(dialogue,'DialogueEyebrow'),0,0,0,8);pad(w(dialogue,'SpeakerText'),0,0,0,13);pad(w(dialogue,'BodyText'),0,0,0,10);w(dialogue,'BodyText').set_editor_property('line_height_percentage',1.12)
 w(dialogue,'DialogueArea').clear_height_override();w(dialogue,'DialogueArea').set_min_desired_height(132);button(w(dialogue,'AdvanceButton'),w(dialogue,'AdvanceButtonLabel'));w(dialogue,'AdvanceButton').slot.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_RIGHT)
 auto_place(w(view,'DialogueView'),0,-184,880,(.5,1),(.5,1))
 g=h.edit(dialogue,'AdvanceReveal')
 for n in g.list_all_nodes():
  for p in n.list_input_pins():
   if not p.list_connected_pins() and str(p.get_pin_value()) in ('42','42.0','42.000000'):h.literal(p,34)
 panel_material(w(view,'IncomingTransmission'),mats['TransmissionPlate']);w(view,'IncomingTransmission').set_padding(unreal.Margin(20,16,20,16));u.place(w(view,'IncomingTransmission'),0,32,430,64,(.5,0),(.5,0));style(w(view,'IncomingTransmissionText'),14,GOLD,True,tracking=75);w(view,'IncomingTransmissionText').set_auto_wrap_text(False)
 panel_material(w(view,'InteractionBackdrop'),mats['PromptPlate']);u.place(w(view,'InteractionBackdrop'),0,-28,570,54,(.5,1),(.5,1));u.place(w(view,'InteractionText'),0,-40,526,30,(.5,1),(.5,1));style(w(view,'InteractionText'),16,PAPER,True)
 # Give the existing animated notice contrast without replacing its public text widget.
 notice=w(view,'ContinuityText');style(notice,25,PAPER,True,tracking=110);notice.set_editor_property('justification',unreal.TextJustify.CENTER);u.place(notice,0,120,600,44,(.5,0),(.5,0));notice.set_shadow_color_and_opacity(color('020405',.95));notice.set_shadow_offset(unreal.Vector2D(1,2))
 back=await u.widget(view,unreal.Border,'ContinuityBackdrop',canvas,True);panel_material(back,mats['NoticePlate']);u.place(back,0,108,600,68,(.5,0),(.5,0));back.slot.set_z_order(notice.slot.get_z_order()-1);back.set_visibility(unreal.SlateVisibility.COLLAPSED);back.set_render_opacity(0)
 if not any(str(n.get_node_title()).replace(' ','')=='SetRenderOpacity' and any(str(p.get_owning_node().get_node_title()).replace(' ','')=='GetContinuityBackdrop' for p in n.find_self_pin().list_connected_pins()) for n in h.edit(view,'ShowContinuityNotice').list_all_nodes() if n.get_class().get_name()=='K2Node_CallFunction' and h.valid(n.find_self_pin())):
  g=h.edit(view,'ShowContinuityNotice');tail=next(n for n in g.list_all_nodes() if 'SetTimer' in str(n.get_node_title()).replace(' ',''));append_after(g,tail,lambda end:h.call(g,'/Script/UMG.Widget:SetRenderOpacity',u.visibility(g,end,h.get(g,'ContinuityBackdrop'),'HitTestInvisible'),h.get(g,'ContinuityBackdrop'),InOpacity=0).find_then_pin())
  g=h.edit(view,'StepContinuityNotice');opacity=next(n for n in g.list_all_nodes() if 'SetRenderOpacity' in str(n.get_node_title()).replace(' ',''));transform=next(n for n in g.list_all_nodes() if 'SetRenderTranslation' in str(n.get_node_title()).replace(' ',''));a=opacity.find_input_pin('InOpacity').list_connected_pins()[0];translation=transform.find_input_pin('Translation').list_connected_pins()[0]
  def mirror(end):
   end=h.call(g,'/Script/UMG.Widget:SetRenderOpacity',end,h.get(g,'ContinuityBackdrop'),InOpacity=a).find_then_pin();return h.call(g,'/Script/UMG.Widget:SetRenderTranslation',end,h.get(g,'ContinuityBackdrop'),Translation=translation).find_then_pin()
  append_after(g,transform,mirror)
  g=h.edit(view,'HideContinuityNotice');tail=next(n for n in g.list_all_nodes() if 'SetVisibility' in str(n.get_node_title()).replace(' ',''));append_after(g,tail,lambda end:u.visibility(g,end,h.get(g,'ContinuityBackdrop'),'Collapsed'))
 # Evidence shares the same typography and roomy reading area.
 document=h.asset('UI/WBP_Document');root=w(document,'DocumentPanel');panel_material(root,mats['DocumentPlate']);root.set_padding(unreal.Margin(28));u.place(w(view,'DocumentView'),0,0,820,520,(.5,.5),(.5,.5))
 style(w(document,'DocumentEyebrow'),11,GOLD,True,740);style(w(document,'DocumentTitle'),30,PAPER,True,740);style(w(document,'DocumentBody'),22,PAPER,False,730);w(document,'DocumentBody').set_editor_property('line_height_percentage',1.15);w(document,'ReadingArea').set_height_override(310);button(w(document,'CloseButton'),w(document,'CloseButtonLabel'));w(document,'CloseButton').slot.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_RIGHT)
 ending=h.asset('UI/WBP_Ending');w(ending,'CinematicScale').set_editor_property('stretch_direction',unreal.StretchDirection.BOTH)
 style(w(ending,'NewspaperHeadline'),34,color('252720'),True);u.place(w(ending,'NewspaperHeadline'),30,128,688,110);u.place(w(ending,'NewspaperDeck'),32,245,682,32);u.place(w(ending,'NewspaperDateline'),32,88,680,20)
 u.place(w(ending,'OutcomeNumber'),25,22,230,100);style(w(ending,'OutcomeTitle'),24,PAPER,True);u.place(w(ending,'OutcomeTitle'),25,197,230,120);u.place(w(ending,'OutcomeRule'),25,334,230,1);style(w(ending,'OutcomeConsequence'),16,MUTED);u.place(w(ending,'OutcomeConsequence'),25,355,230,128)
 w(ending,'OfficialPageFill').set_brush_from_material(paper);w(ending,'OfficialPageFill').set_brush_color(unreal.LinearColor.WHITE)
 for frame_name,fill_name,mat in [('AuthenticPageFrame','AuthenticPageFill',mats['TransmissionPlate']),('OutcomeAsideFrame','OutcomeAsideFill',mats['EndingAside']),('ConfirmationFrame','ConfirmationFill',mats['ConfirmationPlate'])]:
  w(ending,frame_name).set_brush_color(unreal.LinearColor(0,0,0,0));panel_material(w(ending,fill_name),mat)
 style(w(ending,'MessageBody'),20,PAPER,False,670);w(ending,'MessageBody').set_editor_property('line_height_percentage',1.10);style(w(ending,'ConfirmationBody'),21,PAPER,False,778)
 u.place(w(ending,'MessageBody'),32,180,680,218);u.place(w(ending,'MessageWarning'),32,414,680,68);u.place(w(ending,'MessagePromise'),32,491,680,36);u.place(w(ending,'MessageSignature'),32,540,680,20)
 for name in ('CancelButton','ConfirmButton'):
  button(w(ending,name),w(ending,name+'Text'),primary=name=='ConfirmButton');pad(w(ending,name+'Text'),12,9,12,9)
 seal=await u.widget(ending,unreal.Border,'ArchiveStamp',w(ending,'OutcomeAside'));seal.set_brush(brush(color('131D1C'),GOLD));seal.set_brush_color(unreal.LinearColor.WHITE);u.place(seal,18,493,246,60);seal.slot.set_z_order(-1);seal.set_render_transform_angle(-3);seal.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
 stamp=w(ending,'ArchiveSeal');u.place(stamp,27,514,228,25);style(stamp,12,GOLD,True,tracking=70);stamp.set_editor_property('justification',unreal.TextJustify.CENTER);stamp.set_render_transform_angle(-3)
 for bp in (checklist,dialogue,document,ending,view):h.save(bp);out['saved'].append(bp.get_path_name())
 out['passed']=True
async def guarded():
 try:await build()
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:(repo/'Scripts/C/block3_ui_build.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_BLOCK3_UI_BUILD '+json.dumps(out))
c_block3_loop=EditorEventLoopManager();c_block3_loop.__enter__();c_block3_task=c_block3_loop.loop.create_task(guarded())
