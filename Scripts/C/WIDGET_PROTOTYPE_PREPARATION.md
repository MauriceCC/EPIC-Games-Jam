# Widget prototype preparation

Status: F0 preparation only. No widget asset was created.

## Gate

Plan 00 section 5.2 allows backlog breakdown and data preparation before F0.
Its dependency graph puts C's isolated systems after F0 validation. The C plan
places WBP_Dialogue (C-06) and WBP_Checklist (C-07) in F1. The current conditional
request does not waive that gate. Only fixtures and construction steps are ready.

## Future isolated construction after F0

[PROPUESTA] Private C test paths, control names and presentation:
- /Game/Unscripted/UI/Test/WBP_DialoguePrototype_C
- /Game/Unscripted/UI/Test/WBP_ChecklistPrototype_C

Use native UserWidget parents and primitive preview values only. Do not copy
Core types. WidgetPreviewCases.json references four dialogue cases and two
checklist snapshots; UIStrings.csv supplies display labels, including Future
Self instead of the raw FutureSelf token.

Dialogue: Border -> VerticalBox -> speaker/body TextBlocks and a Continue button.
Local button OnClicked -> advance index -> bounds check -> SetText. Stop at the
terminal row. Check JackMeeting order, TruthRevelation wrapping, Correction
single-row termination and the five-line Briefing.

Checklist: Border -> VerticalBox -> title and item rows. Two local preview
buttons select FindJack and FinalChoice. Preserve the first two strings verbatim;
show counts 3/4 and completed counts 0/2. [PROPUESTA] Experiment with opacity and
a warning accent for rewriting. This is not the production animation.

Read MCP schemas for CreateWidgetBlueprint, AddWidget, GetWidgets,
BindToEventProperty and CompileWidgetBlueprint. They are available.
CreateWidgetBlueprint takes folderPath, assetName and parentClass.
Discover each widget/slot's properties using ObjectTools.list_properties before
get_properties/set_properties; never guess names. Mark button variables before
binding their events. Compile does not save: use AssetTools.save_assets with
explicit C paths, not the singular name mentioned by the UMG description.

No Get Game State, Get Game Mode, player casts, ReportStoryEvent, shared
dispatchers, input mappings, Retake calls or foreign maps. Inspect graphs/text,
compile, save and read back dirty state once F1 permits construction.
720p/1080p cases are prepared, not rendered or visually tested.
No widget interaction, animation, import or gameplay acceptance is claimed.
