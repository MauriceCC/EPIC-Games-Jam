"""Preserve shared knockout delivery and the Interventor's light-hit defense."""
import sys
from pathlib import Path
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
dep = Path(u.Paths.engine_dir()).resolve() / 'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0] = [str(repo / 'Scripts/C'), str(dep)]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
bp = h.asset('Enemies/BP_GuardBase')
g = h.edit(bp, 'B_ApplyHealthDamage')
nodes = g.list_all_nodes()
messages = {str(n.find_input_pin('Param').get_pin_value()): n for n in nodes
            if 'ReportStoryEvent' in str(n.get_node_title()).replace(' ', '')}
generic = messages['NonLethal']
boss = messages['Archive']
gate, = generic.find_execute_pin().list_connected_pins()
gate_input = gate.get_owning_node().find_execute_pin()
boss_valid, = boss.find_execute_pin().list_connected_pins()
boss_outer, = boss_valid.get_owning_node().find_execute_pin().list_connected_pins()
h.connect(boss_outer.get_owning_node().find_output_pin('else'), gate_input)
h.connect(boss_valid.get_owning_node().find_output_pin('else'), gate_input)
h.connect(boss.find_then_pin(), gate_input)

g = h.edit(bp,'EventGraph')
damage, = [n for n in g.list_all_nodes() if 'B_ApplyHealthDamage' in str(n.get_node_title())]
if not any('bB_BlocksLight' in str(n.get_node_title()) for n in g.list_all_nodes()):
    before, = damage.find_execute_pin().list_connected_pins()
    before.break_pin_links()
    can_take_damage = h.any_true(g,h.not_(g,h.get(g,'bB_BlocksLight')),h.get(g,'bB_Stunned'))
    yes,_ = h.branch(g,before,can_take_damage)
    h.connect(yes,damage.find_execute_pin())

g = h.edit(bp,'B_ApplyPostureDamage')
if not any('B_CanRunEncounter' in str(n.get_node_title()) for n in g.list_all_nodes()):
    start=g.find_graph_entry_pin()
    original,=start.list_connected_pins()
    start.break_pin_links()
    check=h.invoke(g,start,bp,'B_CanRunEncounter')
    yes,_=h.branch(g,check.find_then_pin(),check.find_result_pin())
    h.connect(yes,original)

h.save(bp)
u.log('B_ENCOUNTER_POLISH saved shared knockout report and Interventor defense')
