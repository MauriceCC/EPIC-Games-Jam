"""Create F0 input assets; gameplay handlers belong to A in F1."""
import unreal
A = unreal.EditorAssetLibrary
T = unreal.AssetToolsHelpers.get_asset_tools()
root = '/Game/Unscripted/Player/Input/'
definitions = {'Move':None,'LookMouse':'Mouse2D','LightAttack':'LeftMouseButton','HeavyAttack':'RightMouseButton','Dodge':'SpaceBar','Parry':'Q','TemporalCut':'F','Retake':'R','Interact':'E','Crouch':'LeftControl','Checklist':'Tab','Pause':'Escape'}
actions = {}
def key_value(name):
    key = unreal.Key()
    key.import_text('(KeyName="'+name+'")')
    return key
for name in definitions:
    path = root+'IA_'+name
    if A.does_asset_exist(path):
        actions[name] = A.load_asset(path)
        continue
    factory = unreal.DataAssetFactory()
    factory.set_editor_property('data_asset_class', unreal.InputAction)
    action = T.create_asset('IA_'+name, root, unreal.InputAction, factory)
    action.set_editor_property('value_type', unreal.InputActionValueType.AXIS2D if name in ['Move','LookMouse'] else unreal.InputActionValueType.BOOLEAN)
    if name == 'Move':
        action.set_editor_property('accumulation_behavior', unreal.InputActionAccumulationBehavior.CUMULATIVE)
    assert A.save_loaded_asset(action)
    actions[name] = action
if not A.does_asset_exist(root+'IMC_Default'):
    factory = unreal.DataAssetFactory()
    factory.set_editor_property('data_asset_class', unreal.InputMappingContext)
    context = T.create_asset('IMC_Default', root, unreal.InputMappingContext, factory)
else:
    context = A.load_asset(root+'IMC_Default')
if not context.get_editor_property('default_key_mappings').get_editor_property('mappings'):
    mappings = []
    for name, key in definitions.items():
        if key:
            mappings.append(unreal.EnhancedActionKeyMapping(action=actions[name],key=key_value(key)))
    for key in ['D','A','W','S']:
        modifiers = []
        if key in ['A','S']:
            negate = unreal.InputModifierNegate(outer=context)
            negate.set_editor_properties({'x':True,'y':False,'z':False})
            modifiers.append(negate)
        if key in ['W','S']:
            swizzle = unreal.InputModifierSwizzleAxis(outer=context)
            swizzle.set_editor_property('order',unreal.InputAxisSwizzle.YXZ)
            modifiers.append(swizzle)
        mappings.append(unreal.EnhancedActionKeyMapping(action=actions['Move'],key=key_value(key),modifiers=modifiers))
    data = context.get_editor_property('default_key_mappings')
    data.set_editor_property('mappings', mappings)
    context.set_editor_property('default_key_mappings', data)
    assert A.save_loaded_asset(context)
print('F0 input assets created')
