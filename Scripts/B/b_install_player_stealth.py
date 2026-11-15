"""Wire hold-to-crouch input, stealth visibility and Agent pose playback."""
from pathlib import Path
import runpy

import unreal as u

ROOT = '/Game/Unscripted/'
lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
worlds = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not worlds.get_game_world(), 'Stop Play before installing Agent stealth.'
player = assets.load_asset(ROOT + 'Player/BP_PlayerCharacter')
stealth = ROOT + 'Enemies/BP_StealthComponent.BP_StealthComponent_C'
graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(player))
state_name = 'B_StealthPoseState'


def link(output, input_):
    assert output.is_valid() and input_.is_valid()
    assert output.try_create_connection(input_), input_.get_pin_name()


def call(path):
    node = graph.add_call_function_node(path)
    assert node, path
    return node


def engine(path):
    return call('/Script/Engine.' + path)


def get(name, owner=''):
    node = graph.add_get_member_variable_node(name, owner)
    return lib.find_output_pin(node, name)


def branch(start, condition):
    node = graph.add_branch_node()
    link(start, lib.find_execute_pin(node))
    link(condition, lib.find_condition_pin(node))
    return lib.find_then_pin(node), lib.find_output_pin(node, 'else')


def literal_int(value):
    node = engine('KismetSystemLibrary.MakeLiteralInt')
    pin, = lib.list_input_pins(node)
    assert pin.set_pin_value(str(value))
    return lib.find_result_pin(node)


def equal_state(value):
    node = engine('KismetMathLibrary.EqualEqual_IntInt')
    link(get(state_name), lib.find_input_pin(node, 'A'))
    link(literal_int(value), lib.find_input_pin(node, 'B'))
    return lib.find_result_pin(node)


def play(start, animation, loop):
    node = engine('SkeletalMeshComponent.PlayAnimation')
    link(get('Mesh', '/Script/Engine.Character'), lib.find_self_pin(node))
    assert lib.find_input_pin(node, 'NewAnimToPlay').set_pin_value(animation.get_path_name())
    assert lib.find_input_pin(node, 'bLooping').set_pin_value(str(loop).lower())
    link(start, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


def change_pose(start, value, animation, loop):
    node = graph.add_set_member_variable_node(state_name)
    link(literal_int(value), lib.find_input_pin(node, state_name))
    link(start, lib.find_execute_pin(node))
    return play(lib.find_then_pin(node), animation, loop)


def sync_stealth(start, crouched):
    component = engine('Actor.GetComponentByClass')
    assert lib.find_input_pin(component, 'ComponentClass').set_pin_value(stealth)
    target = lib.find_result_pin(component)
    valid = engine('KismetSystemLibrary.IsValid')
    link(target, lib.find_input_pin(valid, 'Object'))
    ready, _ = branch(start, lib.find_result_pin(valid))
    set_crouched = call(stealth + '.SetCrouched')
    link(target, lib.find_self_pin(set_crouched))
    inputs = [pin for pin in lib.list_input_pins(set_crouched)
              if str(pin.get_pin_name()) not in ('self', 'execute')]
    crouch_pin, = inputs
    assert crouch_pin.set_pin_value(str(crouched).lower())
    link(ready, lib.find_execute_pin(set_crouched))


def input_event():
    existing = [node for node in graph.list_all_nodes()
                if 'EnhancedInputAction' in node.get_class().get_name()
                and 'IA_Crouch' in str(lib.get_node_title(node))]
    if existing:
        node, = existing
        return node
    choices = [str(name) for name in graph.list_available_nodes([])
               if str(name).endswith('|EnhancedActionEvents|IA_Crouch')]
    assert len(choices) == 1, f'Expected one IA_Crouch event: {choices}'
    node = graph.create_node_from_name(choices[0], u.Vector2D(-1100, 1800), [])
    assert node, choices[0]
    return node


def bind_input(event):
    started = lib.find_output_pin(event, 'Started')
    completed = lib.find_output_pin(event, 'Completed')
    canceled = lib.find_output_pin(event, 'Canceled')
    for pin in (started, completed, canceled):
        assert pin.is_valid() and not pin.list_connected_pins(), 'IA_Crouch is already wired.'
    crouch = engine('Character.Crouch')
    uncrouch = engine('Character.UnCrouch')
    link(started, lib.find_execute_pin(crouch))
    link(completed, lib.find_execute_pin(uncrouch))
    link(canceled, lib.find_execute_pin(uncrouch))


def install_graph(event, idle, crouch_idle, crouch_walk, stand_up):
    bind_input(event)
    update = graph.add_custom_event_node('B_UpdateAgentStealthPose')
    is_crouched = get('bIsCrouched', '/Script/Engine.Character')
    crouched, standing = branch(lib.find_then_pin(update), is_crouched)

    velocity = engine('Actor.GetVelocity')
    speed = engine('KismetMathLibrary.VSizeXY')
    link(lib.find_result_pin(velocity), lib.find_input_pin(speed, 'A'))
    moving = engine('KismetMathLibrary.Greater_DoubleDouble')
    link(lib.find_result_pin(speed), lib.find_input_pin(moving, 'A'))
    assert lib.find_input_pin(moving, 'B').set_pin_value('8.0')
    walk, rest = branch(crouched, lib.find_result_pin(moving))
    for start, index, animation in [(walk, 2, crouch_walk), (rest, 1, crouch_idle)]:
        _, changed = branch(start, equal_state(index))
        sync_stealth(change_pose(changed, index, animation, True), True)

    _, changed = branch(standing, equal_state(0))
    rising, begin_rise = branch(changed, equal_state(3))
    sync_stealth(change_pose(begin_rise, 3, stand_up, False), False)
    active = engine('SkeletalMeshComponent.IsPlaying')
    link(get('Mesh', '/Script/Engine.Character'), lib.find_self_pin(active))
    _, finished = branch(rising, lib.find_result_pin(active))
    change_pose(finished, 0, idle, True)

    assert lib.compile_blueprint(player), 'Could not compile stealth pose event.'
    tick, = [node for node in graph.list_all_nodes()
             if isinstance(node, u.K2Node_Event) and 'Tick' in str(lib.get_node_title(node))]
    tick_out = lib.find_then_pin(tick)
    previous = list(tick_out.list_connected_pins())
    execute = call(ROOT + 'Player/BP_PlayerCharacter.BP_PlayerCharacter_C.B_UpdateAgentStealthPose')
    link(tick_out, lib.find_execute_pin(execute))
    for target in previous:
        link(lib.find_then_pin(execute), target)


def install():
    global graph
    cdo = u.get_default_object(player.generated_class())
    mesh = cdo.get_editor_property('mesh')
    assert mesh.get_editor_property('animation_mode') == u.AnimationMode.ANIMATION_SINGLE_NODE
    installed = any('B_UpdateAgentStealthPose' in str(lib.get_node_title(node))
                    for node in graph.list_all_nodes() if isinstance(node, u.K2Node_CustomEvent))
    if not installed:
        animation_builder = runpy.run_path(str(Path(__file__).with_name('b_player_stealth_pose.py')))
        idle, crouch_idle, crouch_walk, stand_up = animation_builder['build']()
        if state_name not in {str(name) for name in lib.list_member_variable_names(player)}:
            assert lib.add_member_variable(player, state_name, lib.get_basic_type_by_name('int'))
            assert lib.compile_blueprint(player)
            graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(player))
        install_graph(input_event(), idle, crouch_idle, crouch_walk, stand_up)
        assert lib.compile_blueprint(player), 'Could not compile Player stealth.'

    cdo = u.get_default_object(player.generated_class())
    movement = cdo.get_editor_property('character_movement')
    nav = movement.get_editor_property('nav_agent_props')
    nav.set_editor_property('can_crouch', True)
    movement.set_editor_property('nav_agent_props', nav)
    assert movement.get_editor_property('nav_agent_props').get_editor_property('can_crouch')
    movement.set_editor_property('max_walk_speed_crouched', 140)
    movement.set_editor_property('crouched_half_height', 65)
    assert assets.save_loaded_asset(player), 'Could not save BP_PlayerCharacter.'
    u.log('B_AGENT_STEALTH saved Ctrl hold, crouch walk, stand-up and visibility')


install()
