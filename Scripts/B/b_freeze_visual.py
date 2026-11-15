"""Pause the frozen guard's animation and apply the shared temporal overlay."""
import unreal as u

lib = u.BlueprintEditorLibrary
assets = u.EditorAssetLibrary
root = '/Game/Unscripted/'
guard = u.load_asset(root + 'Enemies/BP_GuardBase')
overlay_asset = root + 'Materials/M_TemporalFrozen_Overlay.M_TemporalFrozen_Overlay'
assert u.load_asset(overlay_asset)


def link(out, inp):
    assert out.is_valid() and inp.is_valid()
    assert out.try_create_connection(inp), inp.get_pin_name()


def call(path):
    node = graph.add_call_function_node('/Script/Engine.' + path)
    assert node, path
    return node


def visual(start, paused):
    mesh = call('Actor.GetComponentByClass')
    assert lib.find_input_pin(mesh, 'ComponentClass').set_pin_value('/Script/Engine.SkeletalMeshComponent')
    target = lib.find_result_pin(mesh)
    overlay = call('MeshComponent.SetOverlayMaterial')
    link(target, lib.find_self_pin(overlay))
    if paused:
        assert lib.find_input_pin(overlay, 'NewOverlayMaterial').set_pin_value(overlay_asset)
    link(start, lib.find_execute_pin(overlay))
    animation = call('ActorComponent.SetComponentTickEnabled')
    link(target, lib.find_self_pin(animation))
    assert lib.find_input_pin(animation, 'bEnabled').set_pin_value('false' if paused else 'true')
    link(lib.find_then_pin(overlay), lib.find_execute_pin(animation))
    return lib.find_then_pin(animation)


graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_graph(guard, 'ApplyTemporalFreeze'))
if not any('setoverlaymaterial' in str(lib.get_node_title(n)).replace(' ', '').lower()
           for n in graph.list_all_nodes()):
    timer = next(n for n in graph.list_all_nodes()
                 if 'settimer' in str(lib.get_node_title(n)).replace(' ', '').lower())
    execute = lib.find_execute_pin(timer)
    stop, = execute.list_connected_pins()
    link(visual(stop, True), execute)

    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(guard))
    end = next(n for n in graph.list_all_nodes() if str(lib.get_node_title(n)) == 'B_EndTemporalFreeze')
    clear, = lib.find_then_pin(end).list_connected_pins()
    visual(lib.find_then_pin(clear.get_owning_node()), False)
    assert lib.compile_blueprint(guard)
    assert assets.save_loaded_asset(guard)
print('B_FREEZE_VISUAL_SAVED')
