"""Apply gameplay balance from SourceData/B/DT_EnemyBalance.csv in Unreal Editor.

Vision ranges in the CSV are metres. Movement speeds are cm/s. The legacy
DetectionRange, AlertDelaySeconds, TemporalFreezeDurationSeconds,
NeutralizeWindowSeconds and Priority columns remain design data.
"""
import sys
from pathlib import Path
import unreal as u

repo=Path(u.Paths.project_dir()).resolve().parent
dep=Path(u.Paths.engine_dir()).resolve()/'Plugins/Experimental/ToolsetRegistry/Content/Python'
sys.path[:0]=[str(repo/'Scripts/C'),str(repo/'Scripts/B'),str(dep)]
import blueprint_helpers_c as h
from b_enemy_balance import validate_balance

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
source=globals().get('balance_csv',repo/'SourceData/B/DT_EnemyBalance.csv')
rows={row['Name']:row for row in validate_balance(source)}
base=h.asset('Enemies/BP_GuardBase')

settings=(
    ('B_BalancePatrolSpeed','WalkSpeed'),
    ('B_BalanceChaseSpeed','RunSpeed'),
    ('B_BalanceStunSeconds','StunDurationSeconds'),
)
for variable,column in settings:
    h.variable(base,variable,h.basic('real'),float(rows['Pursuer'][column]),category='Balance')
h.compile_blueprint(base,warnings_as_errors=True)

g=h.edit(base,'EventGraph')
for movement in [node for node in g.list_all_nodes() if node.find_input_pin('MaxWalkSpeed').is_valid()]:
    following,=movement.find_then_pin().list_connected_pins()
    title=str(following.get_owning_node().get_node_title()).replace(' ','')
    assert 'SimpleMoveTo' in title,title
    variable='B_BalancePatrolSpeed' if 'SimpleMoveToLocation' in title else 'B_BalanceChaseSpeed'
    speed=movement.find_input_pin('MaxWalkSpeed')
    if not any(str(pin.get_pin_name())==variable for pin in speed.list_connected_pins()):
        h.connect(h.get(g,variable),speed)

g=h.edit(base,'B_ApplyPostureDamage')
timer,=[node for node in g.list_all_nodes() if node.find_input_pin('FunctionName').is_valid()
        and str(node.find_input_pin('FunctionName').get_pin_value())=='B_RecoverPosture']
duration=timer.find_input_pin('Time')
if not any(str(pin.get_pin_name())=='B_BalanceStunSeconds' for pin in duration.list_connected_pins()):
    h.connect(h.get(g,'B_BalanceStunSeconds'),duration)

fields=(
    ('B_Health','Health',lambda value:int(float(value))),
    ('AttackDamage','AttackDamage',float),
    ('PostureDamage','PostureDamage',float),
    ('VisionRange','VisionRange',lambda value:float(value)*100.0),
    ('MaxPosture','MaxPosture',float),
    ('CurrentPosture','MaxPosture',float),
    ('B_WindupSeconds','WindupSeconds',float),
    ('B_CutDurationScale','CutDurationPercent',lambda value:int(float(value))),
    *((variable,column,float) for variable,column in settings),
)
for bp, row_name in [(base,'Pursuer')]+[(h.asset('Enemies/BP_'+name),name)
                                     for name in ('Pursuer','Interventor','Supervisor')]:
    defaults=u.get_default_object(bp.generated_class())
    row=rows[row_name]
    defaults.modify()
    for field,column,convert in fields:
        defaults.set_editor_property(field,convert(row[column]))
    movement=defaults.get_editor_property('character_movement')
    movement.modify()
    movement.set_editor_property('max_walk_speed',float(row['RunSpeed']))
    h.save(bp)
    u.log(f'B_BALANCE {row_name}: {row["Health"]} HP, {row["AttackDamage"]} damage')

jack=h.asset('Enemies/Jack/BP_Jack')
movement=u.get_default_object(jack.generated_class()).get_editor_property('character_movement')
movement.modify()
movement.set_editor_property('max_walk_speed',float(rows['Jack']['WalkSpeed']))
h.save(jack)
u.log('B_BALANCE saved from '+str(source))
