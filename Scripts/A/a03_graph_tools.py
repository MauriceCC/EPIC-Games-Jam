"""A-owned helpers for the limited cursor-facing change; no import side effects."""
import unreal

PATH = '/Game/Unscripted/Player/BP_PlayerCharacter'
FUNCTION = 'A_UpdateCursorFacing'
L = unreal.BlueprintEditorLibrary
G = unreal.BlueprintGraphEditor

def graph(bp, name):
    return G.get_graph_editor(next(g for g in L.list_graphs(bp) if g.get_name() == name))

def connect(a, b):
    assert a.is_valid() and b.is_valid()
    if not any(p.is_same_native_pin(b) for p in a.list_connected_pins()):
        assert a.try_create_connection(b), (str(a.get_pin_name()), str(b.get_pin_name()))

def snapshot(bp):
    result = {}
    for raw in L.list_graphs(bp):
        nodes = {}
        for node in G.get_graph_editor(raw).list_all_nodes():
            nodes[node.get_name()] = {
                'class': node.get_class().get_name(), 'title': str(L.get_node_title(node)),
                'pins': {str(p.get_pin_name()): {
                    'value': str(p.get_pin_value()), 'type': p.get_pin_type().export_text(),
                    'links': sorted((x.get_owning_node().get_name(), str(x.get_pin_name())) for x in p.list_connected_pins())
                } for p in L.list_all_pins(node)}
            }
        result[raw.get_name()] = nodes
    return result

def outgoing(pin):
    return list(pin.list_connected_pins())

def find_tick(editor):
    return next(n for n in editor.list_all_nodes() if n.get_class().get_name() == 'K2Node_Event' and 'Tick' in str(L.get_node_title(n)))

def assert_preserved(before, after, tick_name, original_next, new_call):
    # Only the Tick execution edge may change in any pre-existing graph.
    for name, nodes in before.items():
        assert name in after, name
        for node_name, node in nodes.items():
            assert node_name in after[name], (name, node_name)
            current = after[name][node_name]
            assert current['class'] == node['class'] and current['title'] == node['title']
            assert current['pins'].keys() == node['pins'].keys()
            for pin_name, old_pin in node['pins'].items():
                new_pin = current['pins'][pin_name]
                assert new_pin['value'] == old_pin['value'] and new_pin['type'] == old_pin['type']
                expected = old_pin['links']
                if name == 'EventGraph' and node_name == tick_name and pin_name == 'then':
                    expected = [(new_call, 'execute')]
                elif name == 'EventGraph' and node_name == original_next[0] and pin_name == original_next[1]:
                    expected = [(new_call, 'then')]
                assert new_pin['links'] == expected, (name, node_name, pin_name)
        added = set(after[name]) - set(nodes)
        assert added == ({new_call} if name == 'EventGraph' else set()), (name, added)
    assert set(after) - set(before) == {FUNCTION}
