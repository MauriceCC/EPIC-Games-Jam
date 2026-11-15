"""Add a camera-facing cue to the normal, parryable guard attack."""
from pathlib import Path
import sys
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
plugins = Path(u.Paths.engine_dir()) / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(plugins.resolve())]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
lib = u.BlueprintEditorLibrary
component_name = 'B_ParryCue'
active_name = 'bB_ParryCueActive'
impact_name = 'B_ParryCueImpactAt'
ready_name = 'bB_ParryCueReady'

subobjects = u.get_engine_subsystem(u.SubobjectDataSubsystem)
handles = subobjects.k2_gather_subobject_data_for_blueprint(guard)
data_api = u.SubobjectDataBlueprintFunctionLibrary
capsule = template = None
for handle in handles:
    data = subobjects.k2_find_subobject_data_from_handle(handle)
    obj = data_api.get_object_for_blueprint(data, guard)
    if isinstance(obj, u.CapsuleComponent):
        capsule = handle
    if str(data_api.get_variable_name(data)) == component_name:
        template = obj
if template is None:
    assert capsule, 'Guard capsule not found'
    params = u.AddNewSubobjectParams()
    params.set_editor_properties({
        'parent_handle': capsule, 'new_class': u.TextRenderComponent.static_class(),
        'blueprint_context': guard,
    })
    created, reason = subobjects.add_new_subobject(params)
    assert data_api.is_handle_valid(created), reason
    subobjects.rename_subobject_member_variable(guard, created, component_name)
    data = subobjects.k2_find_subobject_data_from_handle(created)
    template = data_api.get_object_for_blueprint(data, guard)
template.set_editor_properties({
    'relative_location': u.Vector(0, 0, 110),
    'horizontal_alignment': u.HorizTextAligment.EHTA_CENTER,
    'vertical_alignment': u.VerticalTextAligment.EVRTA_TEXT_CENTER,
    'world_size': 30.0,
    'visible': False,
    'cast_shadow': False,
})
for name, kind, default in (
    (active_name, 'bool', False), (ready_name, 'bool', False), (impact_name, 'real', 0.0),
):
    h.variable(guard, name, h.basic(kind), default, category='Combat')
assert lib.compile_blueprint(guard)


def engine(graph, method, start=None, target=None, **kwargs):
    return h.call(graph, '/Script/Engine.' + method, start, target, **kwargs)


def now(graph):
    return engine(graph, 'GameplayStatics:GetTimeSeconds').find_output_pin('ReturnValue')


def style(graph, start, cue, text, color, size):
    label = engine(graph, 'KismetTextLibrary:Conv_StringToText', InString=text).find_result_pin()
    text_node = engine(graph, 'TextRenderComponent:K2_SetText', start, cue, Value=label)
    tint = engine(graph, 'TextRenderComponent:SetTextRenderColor', text_node.find_then_pin(), cue, Value=color)
    return engine(graph, 'TextRenderComponent:SetWorldSize', tint.find_then_pin(), cue, Value=size).find_then_pin()


def visibility(graph, start, cue, shown):
    return engine(graph, 'SceneComponent:SetVisibility', start, cue, bNewVisibility=shown).find_then_pin()


def cue_graph(name):
    graph = h.edit(guard, name)
    if graph is None:
        return h.function(guard, name)
    h.clear_body(graph)
    return graph


begin = cue_graph('B_BeginParryCue')
cue = h.get(begin, component_name)
impact = h.math(begin, 'Add_DoubleDouble', now(begin), h.get(begin, 'B_WindupSeconds'))
start = h.setvar(begin, begin.find_graph_entry_pin(), impact_name, impact)
start = h.setvar(begin, start, ready_name, False)
start = style(begin, start, cue, '!', '(R=255,G=184,B=66,A=255)', 40.0)
start = h.setvar(begin, start, active_name, True)

end = cue_graph('B_EndParryCue')
start = h.setvar(end, end.find_graph_entry_pin(), active_name, False)
visibility(end, start, h.get(end, component_name), False)
assert lib.compile_blueprint(guard)

update = cue_graph('B_UpdateParryCue')
active, _ = h.branch(update, update.find_graph_entry_pin(), h.get(update, active_name))
has_windup = engine(update, 'Actor:ActorHasTag', Tag='B.MeleeWindup').find_result_pin()
can_show = h.all_true(update, has_windup, h.not_(update, h.get(update, 'bB_Stunned')),
                      h.not_(update, h.get(update, 'bIsTemporalFrozen')))
show, hide = h.branch(update, active, can_show)
h.invoke(update, hide, guard, 'B_EndParryCue')

cue = h.get(update, component_name)
origin = engine(update, 'SceneComponent:K2_GetComponentLocation', target=cue).find_result_pin()
camera = engine(update, 'GameplayStatics:GetPlayerCameraManager', PlayerIndex=0).find_result_pin()
valid_camera, _ = h.branch(update, show, h.is_valid(update, camera))
eye = engine(update, 'PlayerCameraManager:GetCameraLocation', target=camera).find_result_pin()
# TextRender faces its local +X axis. Keep the lettering upright.
yaw_node = engine(update, 'KismetMathLibrary:BreakRotator',
                  InRot=h.math(update, 'FindLookAtRotation', origin, eye))
rotation = h.math(update, 'MakeRotator', 0.0, 0.0, yaw_node.find_output_pin('Yaw'))
turn = engine(update, 'SceneComponent:K2_SetWorldRotation', valid_camera, cue, NewRotation=rotation)
shown = visibility(update, turn.find_then_pin(), cue, True)

# DoParry keeps its defensive window open for 250 ms. Allow room for a
# reaction and frame ordering by lighting the cue 200 ms before contact.
remaining = h.math(update, 'Subtract_DoubleDouble', h.get(update, impact_name), now(update))
ready = h.all_true(update, h.not_(update, h.get(update, ready_name)),
                   h.math(update, 'LessEqual_DoubleDouble', remaining, 0.20))
flash, _ = h.branch(update, shown, ready)
flash = style(update, flash, cue, 'Q', '(R=106,G=255,B=215,A=255)', 48.0)
h.setvar(update, flash, ready_name, True)
assert lib.compile_blueprint(guard)

events = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
nodes = {n.get_name(): n for n in events.list_all_nodes()}
for predecessor, name in (
    ('K2Node_CallFunction_89', 'B_BeginParryCue'),
    ('K2Node_CallFunction_4', 'B_EndParryCue'),
    ('K2Node_Event_2', 'B_UpdateParryCue'),
):
    source = nodes[predecessor].find_then_pin()
    successor, = source.list_connected_pins()
    if str(lib.get_node_title(successor.get_owning_node())) == name:
        continue
    source.break_pin_links()
    call = h.invoke(events, source, guard, name)
    h.connect(call.find_then_pin(), successor)

h.layout(guard, ('B_BeginParryCue', 'B_EndParryCue', 'B_UpdateParryCue'))
h.save(guard)
print('B_PARRY_CUE_SAVED')
