# Live MCP audit: Division C readiness

Date: 2026-11-14
Branch: c/f0-narrative-preparation
Revision: 5f269ca6c3df5442d4eff79a4ee7380e3bd8791d
Status: F0 remains incomplete. No F1 gameplay functionality was implemented.

## What was inspected and tested

The running Unreal MCP server was queried for inventory, native parents, graph
nodes/pins, variables, event dispatchers and struct field schemas.
Six interfaces with seventeen function graphs were inspected.

Both C components inherit ActorComponent. Each has only an EventGraph with
unconnected BeginPlay and Tick events, no user variables, no function graphs
and no declared event dispatchers.

BP_ObjectiveManager and BP_InteractionComponent both compiled successfully with
warnings_as_errors=true. Neither was dirty before or after compilation and no
asset-save tool was called. This verifies empty-shell compilation, not gameplay.

## Blocking differences from the existing contract

| Shared interface and pin | Observed graph type | Documented type |
|---|---|---|
| BPI_StoryEvents.ReportStoryEvent.Source | ActorActionUtility object reference | Actor object reference |
| BPI_Interactable.GetInteractionPriority.Result | Text | int |
| BPI_Interactable.Interact.Interactor | ActorActionUtility object reference | Actor object reference |
| BPI_PlayerControl.RequestFinisher.Target | ActorComponent object reference | Actor object reference |

Function names are present, but these four pin types are incompatible with the
documented callers/consumers. C must not add casts, text conversions or
replacement interfaces to accommodate these errors. Corrections belong to
the integrator in Core and are requested in the C division plan.

Pin types above are normalized from the editor's localized display labels.
The native UFunction schema lookup was empty; actual function-graph pins are
the evidence used for this comparison.

ApplyTemporalFreeze reports double-precision Duration, PostureDamage and Result
pins, while the contract documents float. Request C-F0-04 asks the integrator
to confirm the required precision or align those pins before freezing F0.
This precision question is recorded separately from the four confirmed type
mismatches.

## Missing F0 dispatcher declarations

BP_ObjectiveManager is missing:
- OnStoryPhaseChanged(NewPhase: EStoryPhase)
- OnChecklistUpdated()
- OnDialogueStarted(Row: Name)
- OnDialogueFinished(Row: Name)
- OnEndingTriggered(Ending: EEndingType)

BP_InteractionComponent is missing:
- OnFocusChanged(Target: Actor, Prompt: Text)

Read-only inspection of A/B component assets also found no declared dispatchers:
- Health: OnHealthChanged, OnDepleted.
- Combat: OnStaminaChanged, OnCombatStateChanged.
- Temporal: OnRetakeChargesChanged, OnTemporalCutCooldown, OnRetakePerformed.
- Stealth: OnDetectionChanged.

The Stealth component has only its EventGraph, so the documented custom function
graphs are not present either. These are incomplete F0 declarations, not new
contract requests or completed systems for C to consume.

## Structs and enums

ST_DialogueLine, ST_ChecklistRow and ST_HitInfo expose the documented field
shapes. Dialogue and checklist schema reflection includes the expected ESpeaker
and EStoryPhase values; HitInfo includes the documented EAttackType choices.
The existing nine enum assets are present.

Schema keys are normalized by the MCP serializer. Do not rename CSV columns
based only on that normalization. DataTable import/round-trip, native numeric
widths and struct default values were not tested. Other enum value lists were
not independently enumerated during this audit.

## What C can do now

| Work | Present dependency state | Permitted work now |
|---|---|---|
| C-01 phase management | Component and enums exist; shared dispatchers are absent and the story-report Source pin is incompatible | Compile/inspect the shell; prepare guards and test cases |
| C-02 transition decisions | Existing C source data is independent of missing runtime assets | Validate and document source decisions |
| C-03 interaction selection | Component is empty, OnFocusChanged is absent, priority is Text and Interact uses the wrong Interactor class | Document corrections and prepare candidate/priority scenarios |
| C-04/C-05 interactables/evidence | Base shells and test map are absent; Interact is incompatible | Source and acceptance preparation |
| C-06/C-07 dialogue/checklist | Row field shapes are available | Source/schema comparison; F1 import/widgets remain gated |
| C-08 HUD | HUD/GameState and required component signals are missing | Binding design only |
| C-09 checkpoints | Checkpoint interface pin types match; GameMode, checkpoint shell and test map are absent | Acceptance preparation |
| C-10 notice | English source text exists | Source validation |

Plan 00 sections 5.1-5.2 assigns F0 shell/interface declarations to the integrator
and limits other divisions to preparation. Its dependency graph gates C's
isolated runtime systems behind validated F0. The C backlog puts the runtime
tasks above in F1. The current conditional authorization does not waive that
gate or authorize changes to shared declarations.

After F0 is delivered correctly, internal phase guards and numeric interaction
selection are suitable first isolated C implementations. They can use C doubles
without waiting for finished A/B combat. That does not authorize creating D's
missing F0 classes/maps now.

## Remaining base assets

BP_GameMode, BP_GameState, BP_HUD, BP_InteractableBase, BP_Door, BP_Hideout,
BP_Evidence, BP_FinalChoice, BP_Checkpoint, BP_StoryTrigger, L_Test_C and
L_Whitechapel_Story are absent from the live /Game/Unscripted inventory.

The full normalized observations, task readiness and compile checks are in
MCP_SHARED_ASSET_AUDIT.json. Requests C-F0-02/03/04 record the signature,
dispatcher and precision findings in the C plan.

## Scope preserved

No Blueprint graph, variable, interface, dispatcher, enum, struct, map, global
setting or other division's asset was edited. No table/widget/base shell was
created. No explicit compilation of Core or A/B/D assets was performed.
No asset-save tool, Git commit, push, merge, rebase or pull request was used.
