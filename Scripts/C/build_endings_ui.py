"""Build only C's final-record presentation, using existing narrative copy and fonts.

Run with PIE stopped. The two endings share one responsive cinematic frame.
No foreign asset, shared struct, input mapping or game configuration is edited.
"""
import unreal,sys,csv,json,traceback
from pathlib import Path
sys.dont_write_bytecode=True
repo=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
sys.path.insert(0,str(repo/'Scripts/C'))
import blueprint_helpers_c as h,umg_helpers_c as u
from toolset_registry._asyncio.editor_event_loop_manager import EditorEventLoopManager
out={'passed':False,'saved':[]}
def color(code,alpha=1):
 v=[int(code[i:i+2],16)/255 for i in (0,2,4)]
 return unreal.LinearColor(*[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v],alpha)
INK=color('14191C');GOLD=color('BDA16E');IVORY=color('ECE3CF');PAPER=color('D8CCAE');DARK=color('252720');MUTED=color('A5AAA4');TEAL=color('90B8AE')
def graph(bp,name,inputs=(),outputs=()):
 g=h.edit(bp,name)
 if g:h.clear_body(g);return g
 return h.function(bp,name,inputs,outputs)
async def label(bp,parent,name,text,size,x,y,w,ht,tint=IVORY,bold=False,tracking=0):
 obj=await u.label(bp,parent,name,text,size,tint,True);u.place(obj,x,y,w,ht)
 font=obj.get_editor_property('font');font.set_editor_property('typeface_font_name','Bold' if bold else 'Regular');font.set_editor_property('letter_spacing',tracking);obj.set_font(font)
 return obj
async def rule(bp,parent,name,x,y,w,tint=GOLD):
 obj=await u.widget(bp,unreal.Border,name,parent);obj.set_brush_color(tint);obj.set_padding(unreal.Margin(0));u.place(obj,x,y,w,1)
async def framed(bp,parent,name,x,y,w,ht,background):
 frame=await u.widget(bp,unreal.Border,name+'Frame',parent,True);frame.set_padding(unreal.Margin(1));frame.set_brush_color(GOLD);u.place(frame,x,y,w,ht)
 inside=await u.widget(bp,unreal.Border,name+'Fill',frame,True);inside.set_padding(unreal.Margin(0));inside.set_brush_color(background)
 return await u.widget(bp,unreal.CanvasPanel,name,inside,True)
async def copy_label(bp,parent,name,row,size,x,y,w,ht,tint=IVORY,bold=False,tracking=0):
 obj=await label(bp,parent,name,copy[row],size,x,y,w,ht,tint,bold,tracking);bindings[name]=('Narrative/DT_EndingText',row);return obj
async def build():
 global copy,bindings
 assert not unreal.EditorLevelLibrary.get_pie_worlds(False)
 assert all(p.get_name() in ('/Game/Unscripted/UI/WBP_Ending','/Game/Unscripted/Narrative/DT_EndingText') for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
 rows=list(csv.DictReader((repo/'SourceData/C/EndingText.csv').open(encoding='utf-8-sig',newline='')))
 copy={r['Name']:r['Text'].replace('\\n','\n') for r in rows};bindings={}
 table=unreal.load_asset('/Game/Unscripted/Narrative/DT_EndingText')
 if not table:
  factory=unreal.DataTableFactory();factory.set_editor_property('struct',h.asset('Core/Structs/ST_DialogueLine'));table=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DT_EndingText','/Game/Unscripted/Narrative',unreal.DataTable,factory)
 payload=[{'Name':r['Name'],'Speaker':'NewEnumerator6','Text':copy[r['Name']],'Duration':0,'NextRow':'None'} for r in rows]
 assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table,json.dumps(payload))
 assert unreal.EditorAssetLibrary.save_loaded_asset(table,False);out['saved'].append(table.get_path_name())
 bp=unreal.load_asset('/Game/Unscripted/UI/WBP_Ending')
 if not bp:bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset('WBP_Ending','/Game/Unscripted/UI',unreal.WidgetBlueprint,unreal.WidgetBlueprintFactory())
 canvas=await u.widget(bp,unreal.CanvasPanel,'EndingCanvas')
 backdrop=await u.widget(bp,unreal.Border,'Backdrop',canvas,True);backdrop.set_brush_color(color('070B0E',.94));backdrop.set_padding(unreal.Margin(0))
 slot=backdrop.get_editor_property('slot');slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0,0),maximum=unreal.Vector2D(1,1)));slot.set_offsets(unreal.Margin(0))
 scale=await u.widget(bp,unreal.ScaleBox,'CinematicScale',canvas,True);scale.set_editor_property('stretch',unreal.Stretch.SCALE_TO_FIT);scale.set_editor_property('stretch_direction',unreal.StretchDirection.DOWN_ONLY)
 slot=scale.get_editor_property('slot');slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(.035,.035),maximum=unreal.Vector2D(.965,.965)));slot.set_offsets(unreal.Margin(0))
 size=await u.widget(bp,unreal.SizeBox,'CinematicSize',scale);size.set_width_override(1100);size.set_height_override(760)
 card=await u.widget(bp,unreal.CanvasPanel,'CinematicCard',size,True)
 await copy_label(bp,card,'ArchiveBrand','ArchiveBrand',12,20,10,700,24,GOLD,tracking=130)
 await rule(bp,card,'HeaderRule',20,46,1060)
 official=await framed(bp,card,'OfficialPage',20,76,750,570,PAPER)
 await copy_label(bp,official,'NewspaperMasthead','NewspaperMasthead',35,30,24,690,55,DARK,True,-45)
 await copy_label(bp,official,'NewspaperDateline','NewspaperDateline',11,32,81,680,22,DARK,tracking=90)
 await rule(bp,official,'PaperRuleA',30,111,688,DARK)
 await copy_label(bp,official,'NewspaperHeadline','NewspaperHeadline',35,30,128,688,102,DARK,True)
 await copy_label(bp,official,'NewspaperDeck','NewspaperDeck',17,32,239,682,33,DARK)
 await rule(bp,official,'PaperRuleB',30,281,688,DARK)
 await copy_label(bp,official,'NewspaperLeft','NewspaperLeft',16,32,302,316,188,DARK)
 await rule(bp,official,'PaperColumn',374,302,1,DARK)
 await copy_label(bp,official,'NewspaperRight','NewspaperRight',17,397,302,314,188,DARK)
 await rule(bp,official,'PaperRuleC',30,508,688,DARK)
 await copy_label(bp,official,'NewspaperFootnote','NewspaperFootnote',10,32,527,680,22,DARK,tracking=100)
 authentic=await framed(bp,card,'AuthenticPage',20,76,750,570,color('101C20'))
 await copy_label(bp,authentic,'MessageChannel','MessageChannel',11,32,27,680,29,TEAL,tracking=70)
 await rule(bp,authentic,'MessageRule',32,74,684,TEAL)
 await copy_label(bp,authentic,'MessageTitle','MessageTitle',37,32,95,680,65,IVORY,True)
 await copy_label(bp,authentic,'MessageBody','MessageBody',19,32,180,680,187,IVORY)
 for name,row,y,ht in [('MessageWarning','EndingAuthentic_01',393,68),('MessagePromise','EndingAuthentic_02',473,40)]:
  obj=await label(bp,authentic,name,'',19,32,y,680,ht,TEAL);bindings[name]=('Narrative/DT_Dialogue',row)
 await copy_label(bp,authentic,'MessageSignature','MessageSignature',10,32,535,680,22,TEAL,tracking=110)
 aside=await framed(bp,card,'OutcomeAside',798,76,282,570,color('11171A'))
 await label(bp,aside,'OutcomeNumber','01',62,25,28,230,88,GOLD,True)
 await label(bp,aside,'OutcomeEyebrow','',10,25,128,230,45,GOLD,tracking=100)
 await label(bp,aside,'OutcomeTitle','',25,25,197,230,110,IVORY,True)
 await rule(bp,aside,'OutcomeRule',25,319,230)
 await label(bp,aside,'OutcomeConsequence','',17,25,343,230,135,MUTED)
 await copy_label(bp,aside,'ArchiveSeal','ArchiveSeal',11,25,515,230,28,GOLD,True,90)
 await label(bp,card,'EndingQuote','',20,20,674,1060,52,IVORY)
 bindings['EndingQuote']=('Narrative/DT_Dialogue','EndingOfficial_01')
 await copy_label(bp,card,'EndingFooter','EndingFooter',10,20,738,1060,22,MUTED,tracking=120)
 confirmation=await framed(bp,card,'Confirmation',120,110,860,532,color('151C20'))
 await copy_label(bp,confirmation,'ConfirmationEyebrow','ConfirmationEyebrow',11,32,28,790,30,GOLD,tracking=100)
 await rule(bp,confirmation,'ConfirmationRule',32,79,794)
 await label(bp,confirmation,'ConfirmationTitle','',29,32,105,790,85,IVORY,True)
 await label(bp,confirmation,'ConfirmationBody','',20,32,204,790,154,IVORY)
 await copy_label(bp,confirmation,'PermanentWarning','PermanentWarning',15,32,375,790,42,GOLD)
 for name,x,w,primary in [('CancelButton',32,368,False),('ConfirmButton',424,402,True)]:
  button=await u.widget(bp,unreal.Button,name,confirmation,True);u.place(button,x,449,w,51);button.set_editor_property('is_focusable',False)
  style=button.get_editor_property('widget_style')
  for key,tint in [('normal',color('715937') if primary else color('273135')),('hovered',color('9B7B48') if primary else color('3B4D50')),('pressed',color('4E3E2D'))]:
   brush=style.get_editor_property(key);brush.set_editor_property('tint_color',unreal.SlateColor(specified_color=tint));style.set_editor_property(key,brush)
  button.set_style(style)
  text=await u.label(bp,button,name+'Text',copy['CancelRegistration'] if not primary else copy['OfficialRegister'],13,IVORY,True)
  text.set_editor_property('justification',unreal.TextJustify.CENTER);text.set_auto_wrap_text(False)
 # Declarative widget methods are connected to C's HUD in the bounded integration script.
 boolean=h.basic('bool');real=h.basic('real');ending=h.enum_type('EEndingType')
 for n,t,d in [('DisplayedEnding',ending,'NewEnumerator0'),('bConfirmationMode',boolean,False),('bPresentationAnimating',boolean,False),('PresentationAlpha',real,0),('bConfirmKeyArmed',boolean,False)]:h.variable(bp,n,t,d)
 for name,inputs in [('LoadEndingCopy',()),('RequestConfirm',()),('RequestCancel',()),('PresentConfirmation',[('Ending',ending)]),('PresentEnding',[('Ending',ending)]),('ApplyPresentation',[('Delta',real)])]:graph(bp,name,inputs)
 h.compile_blueprint(bp,warnings_as_errors=True)
 g=h.edit(bp,'LoadEndingCopy');end=g.find_graph_entry_pin()
 for name,(table_name,row_name) in bindings.items():
  row=h.table_row(g,end,h.asset(table_name),row_name);fields=h.break_struct(g,row.find_result_pin());end=u.set_text(g,row.find_then_pin(),name,fields['Text'])
 def begin(g,confirm):
  end=h.setvar(g,g.find_graph_entry_pin(),'DisplayedEnding',h.param(g,'Ending'));end=h.setvar(g,end,'bConfirmationMode',confirm);end=h.setvar(g,end,'bConfirmKeyArmed',False);end=h.setvar(g,end,'PresentationAlpha',0);end=h.setvar(g,end,'bPresentationAnimating',True)
  return h.invoke(g,end,bp,'LoadEndingCopy').find_then_pin()
 def copied(g,end,widget,row,table='Narrative/DT_EndingText'):
  n=h.table_row(g,end,h.asset(table),row);return u.set_text(g,n.find_then_pin(),widget,h.break_struct(g,n.find_result_pin())['Text'])
 g=h.edit(bp,'PresentConfirmation');end=begin(g,True)
 for name in ('OfficialPageFrame','AuthenticPageFrame','OutcomeAsideFrame','EndingQuote','EndingFooter'):end=u.visibility(g,end,h.get(g,name),'Collapsed')
 end=u.visibility(g,end,h.get(g,'ConfirmationFrame'),'Visible')
 official_path,authentic_path=h.branch(g,end,h.math(g,'EqualEqual_IntInt',h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=h.param(g,'Ending')).find_result_pin(),1))
 for path,prefix in [(official_path,'Official'),(authentic_path,'Authentic')]:
  end=copied(g,path,'ConfirmationTitle',prefix+'Confirmation');end=copied(g,end,'ConfirmationBody',prefix+'File_Summary','Narrative/DT_NarrativeText');copied(g,end,'ConfirmButtonText',prefix+'Register')
 g=h.edit(bp,'PresentEnding');end=begin(g,False);end=u.visibility(g,end,h.get(g,'ConfirmationFrame'),'Collapsed')
 for name in ('OutcomeAsideFrame','EndingQuote','EndingFooter'):end=u.visibility(g,end,h.get(g,name),'Visible')
 official_path,authentic_path=h.branch(g,end,h.math(g,'EqualEqual_IntInt',h.call(g,'/Script/Engine.KismetMathLibrary:Conv_ByteToInt',InByte=h.param(g,'Ending')).find_result_pin(),1))
 for path,prefix,number in [(official_path,'Official','01'),(authentic_path,'Authentic','02')]:
  end=u.visibility(g,path,h.get(g,'OfficialPageFrame'),'Visible' if prefix=='Official' else 'Collapsed');end=u.visibility(g,end,h.get(g,'AuthenticPageFrame'),'Visible' if prefix=='Authentic' else 'Collapsed')
  end=u.set_text(g,end,'OutcomeNumber',number)
  for suffix,widget in [('Eyebrow','OutcomeEyebrow'),('Title','OutcomeTitle'),('Consequence','OutcomeConsequence')]:end=copied(g,end,widget,prefix+suffix)
  if prefix=='Authentic':copied(g,end,'EndingQuote','NarrativeMotto','Narrative/DT_UIStrings')
 g=h.edit(bp,'ApplyPresentation');yes,_=h.branch(g,g.find_graph_entry_pin(),h.get(g,'bPresentationAnimating'))
 alpha=h.math(g,'FClamp',h.math(g,'Add_DoubleDouble',h.get(g,'PresentationAlpha'),h.math(g,'Divide_DoubleDouble',h.param(g,'Delta'),.65)),0,1);end=h.setvar(g,yes,'PresentationAlpha',alpha)
 end=h.call(g,'/Script/UMG.Widget:SetRenderOpacity',end,h.get(g,'CinematicCard'),InOpacity=h.get(g,'PresentationAlpha')).find_then_pin()
 translation=h.call(g,'/Script/Engine.KismetMathLibrary:MakeVector2D',X=0,Y=h.math(g,'Multiply_DoubleDouble',h.math(g,'Subtract_DoubleDouble',1,h.get(g,'PresentationAlpha')),16)).find_result_pin();end=h.call(g,'/Script/UMG.Widget:SetRenderTranslation',end,h.get(g,'CinematicCard'),Translation=translation).find_then_pin()
 done,_=h.branch(g,end,h.math(g,'GreaterEqual_DoubleDouble',h.get(g,'PresentationAlpha'),1));h.setvar(g,done,'bPresentationAnimating',False)
 g,tick=h.event(bp,'Tick');h.invoke(g,tick.find_then_pin(),bp,'ApplyPresentation',Delta=tick.find_output_pin('InDeltaTime'))
 await u.bind(bp,'ConfirmButton','RequestConfirm');await u.bind(bp,'CancelButton','RequestCancel')
 bp.set_editor_property('run_construction_script_on_drag',False) if hasattr(bp,'run_construction_script_on_drag') else None
 unreal.get_default_object(bp.generated_class()).set_editor_property('is_focusable',True)
 for name in ('OfficialPageFrame','AuthenticPageFrame','OutcomeAsideFrame','ConfirmationFrame'):unreal.find_object(None,bp.get_path_name()+':WidgetTree.'+name).set_visibility(unreal.SlateVisibility.COLLAPSED)
 h.layout(bp);h.save(bp);out['saved'].append(bp.get_path_name());out['passed']=True
async def guarded():
 try:await build()
 except Exception:out['error']=traceback.format_exc();unreal.log_error(out['error'])
 finally:(repo/'Scripts/C/endings_ui_build.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('C_ENDINGS_UI_BUILD '+json.dumps(out))
c_endings_ui_loop=EditorEventLoopManager();c_endings_ui_loop.__enter__();c_endings_ui_task=c_endings_ui_loop.loop.create_task(guarded())
