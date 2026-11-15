# Division C narrative source data

Status: F0 preparation only. These files have not been imported as Unreal assets.

Sources: README.md, docs/01_VISION_Y_NARRATIVA.md, docs/02_JUGABILIDAD_GENERAL.md,
docs/05_NIVEL_MISIONES_Y_HUD.md, docs/06_UNREAL_ENGINE_5.md,
docs/07_ARTE_AUDIO_ALCANCE.md and docs/plan/01_CONTRATOS_Y_PROPIEDAD.md.
The final product name is Unscripted.

## Files and intended destinations

| File | Purpose | Intended row struct / destination |
|---|---|---|
| DT_Dialogue.csv | English adaptations of every quoted dialogue, transmission and ending line in docs/01 | ST_DialogueLine; /Game/Unscripted/Narrative/DT_Dialogue |
| DT_Checklist.csv | Initial orders, progress masks and rewritten orders | ST_ChecklistRow; /Game/Unscripted/Narrative/DT_Checklist |
| NarrativeText.csv | English document titles, design summaries, ending summaries and continuity notice | Source text inventory only; no shared row struct has been requested |

Only the first two files are DataTable candidates. Do not import NarrativeText.csv
as a DataTable or create a new shared struct for it. Document summaries are
adaptations of the design, not authored historical records or finished newspaper
layouts. No exact alibi time, witness name or murderer identity has been invented.

## Import gate

F0 is incomplete. Live MCP inspection now finds nine enums, three structs,
six interfaces and six component assets. The two C components are empty and
lack the required dispatcher declarations. Four shared interface pin types do
not match the contract; base shells and division test maps are still pending.
See Scripts/C/MCP_SHARED_ASSET_AUDIT.md for the current evidence.

The integrator must finish and validate the existing F0 contract before F1.
Before importing either table, verify the actual reflected member names,
member types, enum values and DataTable compatibility of its row struct.
A matching asset name does not prove a compatible struct.

CSV headers match the documented contract, not a verified successful import.
Name is the row key. Items and CompletedMask use Unreal array text syntax.
The import must report zero field, enum or conversion errors. Re-export and
compare the values before accepting an imported table. Save only C assets.

## Dialogue playback preparation

All durations are 0: wait for player input, as allowed by ST_DialogueLine.
No untested automatic timing has been selected. NextRow terminates at None.

Entry rows:
- Briefing_01
- JackFound_01
- FutureMessage_01
- Truth_01
- Correction_Order
- SupervisorEncounter_01
- EndingOfficial_01
- EndingAuthentic_01
- ContinuityAltered_01
- CombatWarning_01

Correction_Order is intentionally a single terminal row with its exact agreed
name. B depends on OnDialogueFinished(Row = Correction_Order) to turn the
Interventor hostile. Do not rename it or report a different row as its completion.

[PROPUESTA] System is used for unattributed procedure messages, the official
ending quotation and the combat warning. This avoids assigning a new named
speaker where docs/01 does not name one. Confirm attribution before final audio.

Other row identifiers are internal C working names. They do not introduce new
shared contracts. The narrative order and playback are still to be implemented
in F1; the CSV does not trigger events or block input by itself.

## Checklist preparation

Rows cover FindJack through FinalChoice. The first orders always include
locating Jack, protecting him and keeping his identity secret. In FinalChoice,
the previous two objectives are struck through and the two new orders are
framing Jack and eliminating him without exposing his identity.

[PROPUESTA] Intermediate completion masks use bJackFound and bJackSafe to
represent progress while keeping identity protection ongoing. These are draft
display snapshots for C-07, not a new progression rule. Confirm them during
F1. No GameEnded row claims that the Director's orders were fulfilled in the
authentic ending; ending presentation belongs to F3.

The final file is registered spatially after the Supervisor gate. Defeating
the Supervisor alone never selects an ending. No runtime checklist rewrite,
dialogue, Widget Blueprint or final-choice mechanism has been implemented.

## Validation

Run from the repository root:

    python -B Scripts/C/validate_source_data.py

The validator checks schemas, row uniqueness, speaker and phase tokens, linked
dialogue rows, cycles, correction-row stability and checklist array lengths.
This is source-data validation, not an Unreal import or gameplay test.

## Independent F0 review

NarrativeSequences.json maps all 24 source quotations to ten separate English
sequences. Exact NextRow and source-fingerprint checks reject cross-scene
dialogue and flag design edits needing translation review.
Fingerprints do not certify translation quality.

StoryTransitions.json prepares six rules and policies for all 14 existing
events. It references the shared documentation read-only and is not imported
or used as a substitute ObjectiveManager.

UIStrings.csv contains 16 labels; Proposal status means [PROPUESTA].
WidgetPreviewCases.json references four dialogue cases and two checklist
snapshots. Neither is a new shared type or a DataTable.
Completed checklist wording is preserved; the title is Fabricated Report.

C-06/C-07 creation remains gated by F0. See
[the unexecuted widget guide](../../Scripts/C/WIDGET_PROTOTYPE_PREPARATION.md).
Validation also rejects six deliberately invalid in-memory examples.
No Unreal import, visual preview or runtime behavior has been tested.

## Confirmed premise review

Jack is innocent in this fiction. The Department keeps him alive while it
fabricates evidence to frame him as Jack the Ripper, then plans his secret
disappearance without revealing his identity. The official file preserves the
Director's manufactured version; the authentic file preserves the truth.

The Supervisor's preservation language is his justification, challenged by the
agent. It is not an objective claim that the agency protects historical truth.
bJackSafe is the refuge milestone, not a promise of survival in the endings.

The earlier premise pass clarified two dialogue adaptations and six narrative summaries to state the
confirmed motive precisely. Source-quotation fingerprints remain unchanged;
NarrativeSequences.json records the adaptation notes. The long-dialogue case
now exercises the expanded truth revelation. No new plot fact, event or shared
type is introduced. See [the editorial review](../../Scripts/C/NARRATIVE_PREMISE_REVIEW.md).

## Live MCP dependency check

The shared dialogue/checklist struct schemas expose the documented field shapes
and ESpeaker/EStoryPhase choices. This is not a successful DataTable import or
a check of native numeric widths/default values. Keep the existing CSV headers
until an actual import/round-trip is validated.

Runtime progression and interaction remain gated: ObjectiveManager/Interaction
dispatchers are absent, and Core contains the four type mismatches described
in [the audit](../../Scripts/C/MCP_SHARED_ASSET_AUDIT.md). C recorded correction
requests without changing shared declarations or adding conversion workarounds.

## Final narrative copy

The source progression remains protection -> doubt -> evidence -> revelation
and rewritten agency orders -> Supervisor access gate -> archival choice.
The final player objective is "Choose which account to archive." The Director's
framing/elimination orders are not mandatory conditions for AuthenticRecord.

NarrativeMotto is the English adaptation of the definitive theme:
"History belongs not to those who lived it, but to those who decide how it is told."
Its speaker and presentation placement have not been assigned.

Four dialogue adaptations now have editorial notes in NarrativeSequences.json.
The ending records and evidence summaries were retained after review. No plot
outcome, phase condition, shared signature or runtime system changed. Reading
pace and staging still require implemented-game testing.
