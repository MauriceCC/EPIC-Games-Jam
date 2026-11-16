"""Place the existing story evidence that unlocks the Archive encounter."""
import unreal as u

worlds=u.get_editor_subsystem(u.UnrealEditorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=worlds.get_editor_world()
assert not worlds.get_game_world() and world.get_name()=='L_Whitechapel'
package='/Game/Unscripted/Maps/L_Whitechapel_Story'
placed={a.get_actor_label():a for a in actors.get_all_level_actors()}
evidence=u.load_asset('/Game/Unscripted/Narrative/BP_Evidence').generated_class()
kind=type(u.get_default_object(evidence).get_editor_property('EvidenceType'))
nav=u.NavigationSystemV1
assert levels.set_current_level_by_name('L_Whitechapel_Story')
for i,label,prompt,x,y in [
    (0,'C_Refuge_NursingRecord','Read the nursing record',3400,400),
    (1,'C_Refuge_FabricatedReport','Read the fabricated report',2480,1150),
]:
    location=nav.project_point_to_navigation(world,u.Vector(x,y,0),None,None,u.Vector(125,125,160))
    assert location is not None,label
    obj=placed.get(label)
    if not obj:
        obj=actors.spawn_actor_from_class(evidence,location,u.Rotator())
        assert obj and obj.get_outermost().get_path_name()==package
        obj.set_actor_label(label)
    obj.modify()
    obj.set_editor_property('EvidenceType',kind.cast(i))
    obj.set_editor_property('InteractionPrompt',prompt)
assert u.EditorLoadingAndSavingUtils.save_packages([obj.get_outermost()],False)
u.log('B_REFUGE_EVIDENCE two existing narrative records placed')
