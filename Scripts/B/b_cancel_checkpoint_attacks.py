"""Discard delayed guard impacts that started before checkpoint restoration."""
from pathlib import Path
import sys
import unreal as u

repo = Path(u.Paths.project_dir()).resolve().parent
sys.path[:0] = [str(repo / 'Scripts/C'), str(Path(u.Paths.engine_dir()).resolve() /
    'Plugins/Experimental/ToolsetRegistry/Content/Python')]
import blueprint_helpers_c as h

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
guard = h.asset('Enemies/BP_GuardBase')
g = h.edit(guard, 'EventGraph')
names = ('B_LastAttackResetAt', 'B_MeleeStartedAt', 'B_PulseStartedAt', 'B_MeleePendingUntil')
assert not any(str(n) in names for n in u.BlueprintEditorLibrary.list_member_variable_names(guard))
for name in names:
    h.variable(guard, name, h.basic('real'), -1.0, category='Combat')
assert u.BlueprintEditorLibrary.compile_blueprint(guard)
g = h.edit(guard, 'EventGraph')
nodes = {n.get_name(): n for n in g.list_all_nodes()}
now = h.call(g, '/Script/Engine.GameplayStatics:GetTimeSeconds').find_result_pin()


def successor(source):
    next_pin, = source.list_connected_pins()
    source.break_pin_links()
    return next_pin


def previous(target):
    prior, = target.list_connected_pins()
    target.break_pin_links()
    return prior


def custom_event(name):
    return next(n for n in nodes.values() if isinstance(n, u.K2Node_CustomEvent)
                and str(n.get_node_title()) == name)


reset = custom_event('B_ResetAtCheckpoint').find_then_pin()
resume = successor(reset)
cleared = h.setvar(g, reset, names[0], now)
h.connect(cleared, resume)

# Prevent checkpoint reset from starting a new melee delay while the cancelled
# one still owns Unreal's latent action for this node.
try_melee = custom_event('B_TryMeleeAttack').find_then_pin()
resume = successor(try_melee)
available, _ = h.branch(g, try_melee, h.math(g, 'GreaterEqual_DoubleDouble', now, h.get(g, names[3])))
h.connect(available, resume)
melee = nodes['K2Node_CallFunction_4']
prior = previous(melee.find_execute_pin())
start = h.setvar(g, prior, names[1], now)
duration = h.get(g, 'B_WindupSeconds')
start = h.setvar(g, start, names[3], h.math(g, 'Add_DoubleDouble', now, duration))
h.connect(start, melee.find_execute_pin())

pulse = custom_event('B_SupervisorPulse')
while not pulse.find_input_pin('Duration').is_valid():
    following, = pulse.find_then_pin().list_connected_pins()
    pulse = following.get_owning_node()
start = h.setvar(g, previous(pulse.find_execute_pin()), names[2], now)
h.connect(start, pulse.find_execute_pin())

# Run the native cleanup before testing the timestamp, so the melee tag and
# parry cue are released and the Supervisor's busy flag always clears.
melee_gate = nodes['K2Node_IfThenElse_8'].find_execute_pin()
pulse_clear, = pulse.find_then_pin().list_connected_pins()
pulse_next, = pulse_clear.get_owning_node().find_then_pin().list_connected_pins()
for target, timestamp in ((melee_gate, names[1]), (pulse_next, names[2])):
    valid, _ = h.branch(g, previous(target), h.math(g, 'Greater_DoubleDouble',
        h.get(g, timestamp), h.get(g, names[0])))
    h.connect(valid, target)

h.save(guard)
u.log('B_CHECKPOINT_ATTACK_CANCEL_SAVED')
