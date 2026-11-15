"""Verify the isolated UI/Test assets in the editor; no gameplay map is run."""
import unreal
import csv
import json
import traceback
from pathlib import Path
from toolset_registry.helpers import compile_blueprint
ROOT = "/Game/Unscripted/UI/Test/"
project = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
report_path = project.parent / "Scripts/C/ui_preview_validation.json"
source = project.parent / "SourceData/C"
report = {"scope": ROOT, "checks": [], "assets": [], "passed": False}
def check(name, condition):
    assert condition, name
    report["checks"].append(name)
def child(widget, name):
    return widget.get_editor_property(name)
def text(widget, name):
    return str(child(widget, name).get_text())
try:
    blueprints = [unreal.load_asset(ROOT + n) for n in ("WBP_DialoguePrototype_C", "WBP_ChecklistPrototype_C", "EUW_NarrativeTestLauncher_C")]
    for bp in blueprints:
        check("Asset loads: " + bp.get_name(), bp is not None)
        compile_blueprint(bp, warnings_as_errors=True)
        deps = [str(x) for x in unreal.AssetRegistryHelpers.get_asset_registry().get_dependencies(bp.get_path_name().split(".")[0], unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True))]
        check("Isolated project dependencies: " + bp.get_name(), all(not d.startswith("/Game/") or d.startswith(ROOT) for d in deps))
        check("Asset saves: " + bp.get_name(), unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False))
        report["assets"].append({"path": bp.get_path_name(), "compile_status": str(bp.get_editor_property("Status")), "dependencies": deps})
    global c_preview_widget
    c_preview_widget = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem).spawn_and_register_tab(blueprints[2])
    dialogue = child(c_preview_widget, "DialoguePreview")
    checklist = child(c_preview_widget, "ChecklistPreview")
    rows = list(csv.DictReader((source / "DT_Dialogue.csv").open(encoding="utf-8-sig", newline="")))
    indices = {r["Name"]: i for i, r in enumerate(rows)}
    speakers = {"System": "Department of Continuity", "FutureSelf": "Future Self", "Agent": "Agent", "Supervisor": "Supervisor", "Jack": "Jack"}
    for i, row in enumerate(rows):
        dialogue.call_method("ShowPreviewLine", args=(i,))
        check("Dialogue body " + row["Name"], text(dialogue, "DialogueBodyText") == row["Text"])
        check("Dialogue speaker " + row["Name"], text(dialogue, "SpeakerText") == speakers[row["Speaker"]])
        next_index = indices.get(row["NextRow"], -1)
        check("Dialogue link " + row["Name"], dialogue.get_editor_property("NextLineIndex") == next_index)
        check("Continue enabled " + row["Name"], child(dialogue, "ContinueButton").get_is_enabled() == (next_index >= 0))
        dialogue.call_method("AdvanceDialoguePreview")
        if next_index >= 0:
            check("Advance " + row["Name"], text(dialogue, "DialogueBodyText") == rows[next_index]["Text"])
        else:
            check("Terminal stays on line " + row["Name"], text(dialogue, "DialogueBodyText") == row["Text"])
    for mode, reset_function, count, initial_count in [(False, "ResetChecklistPreview", 3, 0), (True, "RewriteChecklistPreview", 4, 2)]:
        checklist.call_method(reset_function)
        check("Checklist initial count " + str(mode), checklist.get_editor_property("CompletedCount") == initial_count)
        check("Checklist rewritten state " + str(mode), checklist.get_editor_property("IsRewritten") == mode)
        check("Fourth row visibility " + str(mode), child(checklist, "ObjectiveText3").get_visibility() == (unreal.SlateVisibility.VISIBLE if mode else unreal.SlateVisibility.COLLAPSED))
        for completed in range(initial_count, count + 1):
            for index in range(count):
                check("Checklist marks %s %s %s" % (mode, completed, index), text(checklist, "ObjectiveText" + str(index)).startswith("[x] " if index < completed else "[ ] "))
            check("Checklist status %s %s" % (mode, completed), text(checklist, "ChecklistStatusText") == "%s / %s objectives complete" % (completed, count))
            check("Checklist completion button %s %s" % (mode, completed), child(checklist, "CompleteButton").get_is_enabled() == (completed < count))
            if completed < count:
                checklist.call_method("CompleteNextPreviewObjective")
    checklist.call_method("ResetChecklistPreview")
    original_prefix = [text(checklist, "ObjectiveText" + str(i))[4:] for i in range(2)]
    checklist.call_method("RewriteChecklistPreview")
    check("Rewrite preserves objective prefix", original_prefix == [text(checklist, "ObjectiveText" + str(i))[4:] for i in range(2)])
    check("Rewrite exposes framing", "Frame Jack as Jack the Ripper." in text(checklist, "ObjectiveText2"))
    check("Rewrite exposes disappearance", "Eliminate Jack without revealing his identity." in text(checklist, "ObjectiveText3"))
    dialogue.call_method("ResetDialoguePreview")
    checklist.call_method("ResetChecklistPreview")
    report["passed"] = True
    report["check_count"] = len(report["checks"])
    print("C_UI_VALIDATION_PASSED", report["check_count"])
except Exception:
    report["failure"] = traceback.format_exc()
    unreal.log_error("C_UI_VALIDATION_FAILED " + report["failure"])
finally:
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

