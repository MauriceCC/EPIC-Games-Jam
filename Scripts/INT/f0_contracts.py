"""Declare F0 interfaces and dispatchers using Unreal 5.8 editor APIs.

Proposed pin names where the contract omits them: Result, bCrouched, bHidden.
No gameplay logic is implemented here.
"""
import unreal

ROOT = '/Game/Unscripted/'
L = unreal.BlueprintEditorLibrary
G = unreal.BlueprintGraphEditor
A = unreal.EditorAssetLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()

def pin(kind):
    if kind.startswith('E'):
        value = unreal.EdGraphPinType()
        enum = A.load_asset(ROOT+'Core/Enums/'+kind)
        value.import_text('(PinCategory="byte",PinSubCategoryObject="'+enum.get_path_name()+'")')
        return value
    if kind.startswith('ST_'):
        return L.get_struct_type(A.load_asset(ROOT+'Core/Structs/'+kind))
    if kind == 'Actor':
        return L.get_object_reference_type(unreal.Actor.static_class())
    if kind == 'Transform':
        return L.get_struct_type(unreal.Transform.static_struct())
    if kind.startswith('BP_'):
        folder = 'Enemies/' if kind == 'BP_StealthComponent' else 'Narrative/'
        return L.get_object_reference_type(A.load_blueprint_class(ROOT+folder+kind))
    if kind == 'float':
        value = unreal.EdGraphPinType()
        value.import_text('(PinCategory="real",PinSubCategory="float")')
        return value
    return L.get_basic_type_by_name(kind)

interfaces = {
    'BPI_Damageable': [('ReceiveHit', [('HitInfo','ST_HitInfo')], 'EHitResult'), ('IsDefeated', [], 'bool')],
    'BPI_TimeAffectable': [('CanBeTemporalCutTarget', [], 'bool'), ('ApplyTemporalFreeze', [('Duration','float'),('PostureDamage','float')], 'float')],
    'BPI_Interactable': [('CanInteract',[('Interactor','Actor')],'bool'),('GetInteractionText',[('Interactor','Actor')],'text'),('GetInteractionPriority',[],'int'),('Interact',[('Interactor','Actor')],None)],
    'BPI_PlayerControl': [('SetGameplayInputEnabled',[('bEnabled','bool')],None),('SetRetakeBlocked',[('bBlocked','bool')],None),('ClearRetakeHistory',[],None),('RequestFinisher',[('Target','Actor')],None),('GetStealthComponent',[],'BP_StealthComponent')],
    'BPI_StoryEvents': [('ReportStoryEvent',[('Event','EStoryEvent'),('Source','Actor'),('Param','name')],None),('GetCurrentPhase',[],'EStoryPhase'),('GetObjectiveManager',[],'BP_ObjectiveManager')],
    'BPI_CheckpointListener': [('OnCheckpointRestore',[('CheckpointId','name'),('RespawnTransform','Transform')],None)],
}
for name, functions in interfaces.items():
    path = ROOT+'Core/Interfaces/'+name
    if A.does_asset_exist(path):
        bp = A.load_asset(path)
    else:
        factory = unreal.BlueprintInterfaceFactory()
        bp = T.create_asset(name, ROOT+'Core/Interfaces', unreal.Blueprint, factory)
    assert bp
    for graph in list(L.list_graphs(bp)):
        if str(graph.get_name()) == 'NewFunction':
            L.remove_graph(bp, graph)
    for func, inputs, output in functions:
        existing_graph = L.find_graph(bp, func)
        graph = G.get_graph_editor(existing_graph) if existing_graph else G.create_and_edit_function_graph(bp, func)
        input_names = {str(p.get_pin_name()) for n in graph.list_all_nodes() if isinstance(n, unreal.K2Node_FunctionEntry) for p in L.list_output_pins(n)}
        for field, kind in inputs:
            if field not in input_names:
                assert graph.add_graph_input_parameter(field, pin(kind)).is_valid()
        if output:
            output_names = {str(p.get_pin_name()) for n in graph.list_all_nodes() if isinstance(n, unreal.K2Node_FunctionResult) for p in L.list_input_pins(n)}
            if 'Result' not in output_names:
                assert graph.add_graph_output_parameter('Result', pin(output))
    assert L.compile_blueprint(bp), name
    assert A.save_loaded_asset(bp), name
    print('Interface compiled and saved: '+name)

dispatchers = {
    'Player/BP_HealthComponent': [('OnHealthChanged',[('Current','float'),('Max','float')]),('OnDepleted',[])],
    'Player/BP_CombatComponent': [('OnStaminaChanged',[('Current','float'),('Max','float')]),('OnCombatStateChanged',[('NewState','ECombatState')])],
    'Player/BP_TemporalComponent': [('OnRetakeChargesChanged',[('Current','int'),('Max','int')]),('OnTemporalCutCooldown',[('Remaining','float'),('Total','float')]),('OnRetakePerformed',[])],
    'Enemies/BP_StealthComponent': [('OnDetectionChanged',[('Level','float')])],
    'Narrative/BP_InteractionComponent': [('OnFocusChanged',[('Target','Actor'),('Prompt','text')])],
    'Narrative/BP_ObjectiveManager': [('OnStoryPhaseChanged',[('NewPhase','EStoryPhase')]),('OnChecklistUpdated',[]),('OnDialogueStarted',[('Row','name')]),('OnDialogueFinished',[('Row','name')]),('OnEndingTriggered',[('Ending','EEndingType')])],
    'Enemies/BP_GuardBase': [('OnEnemyStateChanged',[('NewState','EEnemyAIState')]),('OnTelegraphStarted',[('AttackType','EAttackType'),('Duration','float')])],
}
for relative, declarations in dispatchers.items():
    bp = A.load_asset(ROOT+relative)
    existing = {str(n) for n in L.list_event_dispatchers(bp)}
    for name, parameters in declarations:
        if name in existing:
            continue
        assert L.add_event_dispatcher(bp, name)
        for field, kind in parameters:
            assert L.add_event_dispatcher_parameter(bp, name, field, pin(kind))
    assert L.compile_blueprint(bp), relative
    assert A.save_loaded_asset(bp), relative

bp = A.load_asset(ROOT+'Enemies/BP_StealthComponent')
for func, inputs, output in [('SetCrouched',[('bCrouched','bool')],None),('SetHidden',[('bHidden','bool')],None),('GetVisibilityMultiplier',[],'float'),('ReportDetection',[('Enemy','Actor'),('Level','float')],None)]:
    if L.find_graph(bp, func):
        continue
    graph = G.create_and_edit_function_graph(bp, func)
    for field, kind in inputs:
        assert graph.add_graph_input_parameter(field, pin(kind)).is_valid()
    if output:
        ret = graph.add_graph_output_parameter('Result', pin(output))
        assert L.find_input_pin(ret, 'Result').set_pin_value('1.0')
        assert graph.find_graph_entry_pin().try_create_connection(L.find_execute_pin(ret))
assert L.compile_blueprint(bp)
assert A.save_loaded_asset(bp)
print('F0 declarations complete')

