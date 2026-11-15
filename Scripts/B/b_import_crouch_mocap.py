"""Retarget the CC0 Quaternius/KinemIQ crouch clips to SK_Agent in Unreal."""
from pathlib import Path
import unreal as u

ROOT = '/Game/Unscripted/'
SCRATCH = '/Game/Developers/StealthRetarget'
OUTPUT = ROOT + 'Player/Animation'
ASSETS = u.EditorAssetLibrary
TOOLS = u.AssetToolsHelpers.get_asset_tools()
SAVED = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_saved_dir()))
CLIPS = {
    'Idle_crouching': 'A_Agent_CrouchIdle',
    'Walk_crouched_forwards': 'A_Agent_CrouchWalk',
}
CHAINS = (
    ('Spine', ('spine_01', 'spine_03'), ('spine02', 'spine')),
    ('Head', ('neck_01', 'head'), ('neck', 'head')),
    ('LeftClavicle', ('clavicle_l', 'clavicle_l'), ('leftshoulder', 'leftshoulder')),
    ('RightClavicle', ('clavicle_r', 'clavicle_r'), ('rightshoulder', 'rightshoulder')),
    ('LeftArm', ('upperarm_l', 'hand_l'), ('leftarm', 'lefthand')),
    ('RightArm', ('upperarm_r', 'hand_r'), ('rightarm', 'righthand')),
    ('LeftLeg', ('thigh_l', 'ball_l'), ('leftupleg', 'lefttoebase')),
    ('RightLeg', ('thigh_r', 'ball_r'), ('rightupleg', 'righttoebase')),
)


def import_fbx(file, kind, skeleton=None):
    assert file.is_file(), file
    existing = ASSETS.load_asset(f'{SCRATCH}/{file.stem}') if ASSETS.does_asset_exist(f'{SCRATCH}/{file.stem}') else None
    if isinstance(existing, kind):
        return existing

    options = u.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type', False)
    options.set_editor_property('import_as_skeletal', True)
    options.set_editor_property('import_mesh', skeleton is None)
    options.set_editor_property('import_animations', skeleton is not None)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    if skeleton is None:
        options.set_editor_property('mesh_type_to_import', u.FBXImportType.FBXIT_SKELETAL_MESH)
    else:
        options.set_editor_property('mesh_type_to_import', u.FBXImportType.FBXIT_ANIMATION)
        options.set_editor_property('skeleton', skeleton)

    task = u.AssetImportTask()
    for name, value in (
        ('filename', str(file)), ('destination_path', SCRATCH),
        ('automated', True), ('replace_existing', False), ('save', False),
        ('factory', u.FbxFactory()), ('options', options),
    ):
        task.set_editor_property(name, value)
    TOOLS.import_asset_tasks([task])
    imported = [asset for asset in task.get_objects() if isinstance(asset, kind)]
    assert len(imported) == 1, f'Expected one {kind.__name__} from {file.name}, got {imported}'
    return imported[0]


def asset_for(name, cls, factory):
    path = f'{SCRATCH}/{name}'
    return ASSETS.load_asset(path) if ASSETS.does_asset_exist(path) else TOOLS.create_asset(name, SCRATCH, cls, factory())


def make_rig(name, mesh, pelvis, chain_side):
    rig = asset_for(name, u.IKRigDefinition, u.IKRigDefinitionFactory)
    assert rig, name
    controller = u.IKRigController.get_controller(rig)
    assert controller.set_skeletal_mesh(mesh) or controller.get_skeletal_mesh() == mesh
    assert controller.set_retarget_root(pelvis) or str(controller.get_retarget_root()) == pelvis
    present = {str(chain.chain_name) for chain in controller.get_retarget_chains()}
    for chain in CHAINS:
        if chain[0] not in present:
            start, end = chain[chain_side]
            actual = controller.add_retarget_chain(chain[0], start, end, 'None')
            assert str(actual) == chain[0], f'{name}: could not add {chain[0]}'
    return rig


def retarget_clips(source_mesh, sources, prefix, source_rig_name='IK_KinemIQ', retarget_name='RTG_KinemIQ_Agent'):
    target_mesh = ASSETS.load_asset(ROOT + 'Art/Characters/SK_Agent/SK_Agent')
    assert isinstance(target_mesh, u.SkeletalMesh)
    source_rig = make_rig(source_rig_name, source_mesh, 'pelvis', 1)
    target_rig = make_rig('IK_Agent', target_mesh, 'hips', 2)
    asset = asset_for(retarget_name, u.IKRetargeter, u.IKRetargetFactory)
    assert asset
    controller = u.IKRetargeterController.get_controller(asset)
    side = u.RetargetSourceOrTarget
    for role, rig, mesh in [(side.SOURCE, source_rig, source_mesh), (side.TARGET, target_rig, target_mesh)]:
        controller.set_ik_rig(role, rig)
        controller.set_preview_mesh(role, mesh)
    controller.add_default_ops()
    controller.auto_map_chains(u.AutoMapChainType.EXACT, True)
    controller.auto_align_all_bones(side.TARGET)

    inputs = u.IKRetargetBatchOperationInputs()
    fields = {
        'assets_to_retarget': [ASSETS.find_asset_data(clip.get_path_name()) for clip in sources],
        'source_mesh': source_mesh, 'target_mesh': target_mesh, 'ik_retarget_asset': asset,
        'prefix': prefix, 'target_path': OUTPUT, 'include_referenced_assets': False,
        'overwrite_existing_files': True,
    }
    for name, value in fields.items():
        inputs.set_editor_property(name, value)
    results = [entry.get_asset() for entry in u.IKRetargetBatchOperation.run_batch_retarget(inputs)]
    assert len(results) == len(sources), f'Retarget returned {results}'
    result_by_name = {clip.get_name(): clip for clip in results}
    output = {}
    for source in sources:
        clip = result_by_name[prefix + source.get_name()]
        assert clip.get_editor_property('skeleton') == target_mesh.get_editor_property('skeleton')
        assert u.AnimationLibrary.get_num_keys(clip) > 1
        clip.set_editor_property('enable_root_motion', False)
        assert ASSETS.save_loaded_asset(clip, False)
        output[source.get_name()] = clip
        u.log(f'B_CROUCH_MOCAP retargeted {clip.get_name()}')
    return output


def wire_player(replacements):
    lib = u.BlueprintEditorLibrary
    bp = ASSETS.load_asset(ROOT + 'Player/BP_PlayerCharacter')
    graph = u.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))
    animation_pins = [lib.find_input_pin(node, 'NewAnimToPlay')
                      for node in graph.list_all_nodes()
                      if 'PlayAnimation' in str(lib.get_node_title(node)).replace(' ', '')]
    for old, clip in replacements.items():
        pins = [pin for pin in animation_pins if f'/{old}.' in str(pin.get_pin_value())
                or clip.get_name() in str(pin.get_pin_value())]
        pin, = pins
        assert pin.set_pin_value(clip.get_path_name()), clip.get_name()
    assert lib.compile_blueprint(bp), 'Could not compile BP_PlayerCharacter.'
    assert ASSETS.save_loaded_asset(bp)
    u.log('B_CROUCH_MOCAP saved crouch idle and walk on BP_PlayerCharacter')


if __name__ == '__main__':
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop Play before importing crouch animations.'
    source_mesh = import_fbx(SAVED / 'KinemIQ_Mannequin.fbx', u.SkeletalMesh)
    source_skeleton = source_mesh.get_editor_property('skeleton')
    sources = [import_fbx(SAVED / 'FBX' / f'{name}.fbx', u.AnimSequence, source_skeleton) for name in CLIPS]
    output = retarget_clips(source_mesh, sources, 'A_Agent_Mocap_')
    wire_player({old: output[source.get_name()] for source, old in zip(sources, CLIPS.values())})
