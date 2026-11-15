# Division C: F0 preparation and F1 handoff

Current branch: c/f0-narrative-preparation.
Current work: C-01/C-02 state progression implemented and locally validated under the explicit user exception for its two indispensable shared corrections.
Implementation steps 1-3 are executed and validated in C01_C02_IMPLEMENTATION.md. Remaining steps and unrelated phase gates are pending.

## Ownership

Allowed content:
- /Game/Unscripted/Narrative/ and /Game/Unscripted/UI/, including Test/.
- /Game/Unscripted/Maps/L_Whitechapel_Story.
- /Game/Unscripted/Maps/Test/L_Test_C.

Allowed repository text:
- SourceData/C/.
- Scripts/C/.
- docs/plan/C_NARRATIVA_INTERACCION_UI.md.

Core assets and signatures are read-only. Player, enemies, Jack, persistent
maps, global settings, plugins and other divisions' files are not editable.
Do not reference C test assets from production assets.

## Phase gates and responsibilities

| Phase | C work | Dependency / exit gate |
|---|---|---|
| F0 | Read design; prepare English data, transition guards and acceptance scenarios; requested MCP smoke test | Integrator delivers and validates interfaces, shared shells and maps |
| F1 | C-01 to C-10: isolated progression, interaction, interactables, evidence, dialogue, checklist, HUD and checkpoint behavior | Full simulated story flow in L_Test_C; rewritten checklist; reactive HUD; clean compilation |
| F2 | C-20 to C-22: Story placement, real HUD binding and death/respawn integration | A/B isolated systems and D blockout; one complete integrated encounter |
| F3 | C-30 to C-34: full acts, spatial file registration, endings, menus and subtitle polish | F2 vertical slice accepted; full playthrough to both endings |
| F4 | Text, readability, dialogue pacing and progression-stall checks | F3 complete; packaged build and delivery remain D's responsibility |

## F0 dependency inventory (historical preparation snapshot)

Live MCP audit: nine enums, three structs, six interfaces and six component
assets exist. The two C components have no custom variables/functions or
declared dispatchers. Both empty shells compile, but four interface pin types
are incompatible with the documented contract. Numeric precision of the
temporal-freeze signature also requires review.

Struct field shapes and the ESpeaker/EStoryPhase/EAttackType choices were
inspected. DataTable import, default values and native numeric widths were
not tested. GameMode, GameState, HUD and L_Test_C remain absent.
Read MCP_SHARED_ASSET_AUDIT.md before treating any F0 dependency as ready.

Required existing interfaces:
BPI_StoryEvents, BPI_Interactable, BPI_PlayerControl,
BPI_CheckpointListener, BPI_Damageable and BPI_TimeAffectable.

Required C shells:
BP_GameMode, BP_GameState, BP_ObjectiveManager, BP_InteractionComponent,
BP_HUD, BP_InteractableBase, BP_Door, BP_Hideout, BP_Evidence,
BP_FinalChoice, BP_Checkpoint and BP_StoryTrigger.

A's Health, Combat and Temporal dispatcher shells and B's Stealth shell are
also needed before HUD binding. C may use its own doubles after F0 instead of
waiting for finished A/B implementations. C must not create competing shared
shells or connect components to A's player.

## F1 implementation order

1. C-01/C-02: inspect the supplied GameState, GameMode and ObjectiveManager
   shells. Confirm parents, interfaces and dispatchers against the contract.
   Get Game State -> ReportStoryEvent (interface message) is the external entry.
   The GameState forwards the report to its ObjectiveManager component.
2. Inside ObjectiveManager, branch on the reported EStoryEvent; record the
   matching narrative flag; validate the current phase and prerequisite flags;
   then change CurrentPhase and broadcast OnStoryPhaseChanged once.
   No interactable or test sender writes CurrentPhase.
3. In BP_GameState, implement GetCurrentPhase and GetObjectiveManager through
   BPI_StoryEvents. Use the same manager instance throughout the session.
4. C-03/C-04: use the supplied BPI_Interactable signatures. Filter CanInteract,
   choose highest priority, break priority ties by distance, notify
   OnFocusChanged and dispatch one Interact for one E input.
   Keep the real input host in A's ownership; use a C test pawn in L_Test_C.
5. C-05: validate EEvidenceType, record each evidence once, and report events.
   Two reports for the same evidence never replace the two distinct records.
   Door state and collected evidence remain persistent across Retake.
6. C-06: validate/import DT_Dialogue; implement WBP_Dialogue row chaining.
   SetGameplayInputEnabled(false) and SetRetakeBlocked(true) bracket playback.
   Restore these states on completion; clear Retake history after irreversible
   events. Use OnDialogueStarted/Finished with the agreed row names.
7. C-07: validate/import DT_Checklist; implement WBP_Checklist with Tab,
   completion styling and a visibly animated rewrite on the truth transition.
8. C-08: implement WBP_HUD and BP_HUD with dispatcher bindings at BeginPlay.
   Obtain components through the agreed class/interface paths. No per-frame
   polling or Cast to foreign concrete gameplay classes.
9. C-09: checkpoint capture/restore through BPI_CheckpointListener; retain C's
   narrative flags. A decides zero-health/Retake behavior; B decides enemy
   restore policy. Do not fill either open decision on their behalf.
10. C-10: display the English continuity notice from source text.
    Compile every changed C Blueprint with warnings treated as errors.

These steps do not authorize edits outside C or changes to contract signatures.
Any additional private helper identifiers are [PROPUESTA] until implemented and
documented in C's division file.

## Transition and event acceptance scenarios

Progression scenarios are covered by c01_c02_unit_validation.json and c01_c02_pie_validation.json. Interaction, dialogue playback, HUD, checkpoints, and other later scenarios remain pending.

| Case | Input | Expected result |
|---|---|---|
| Phase sequence | JackFound, EscapeRouteOpened, JackReachedRefuge | FindJack -> OpenEscapeRoute -> ProtectJack -> DiscoverTruth |
| Premature event | EscapeRouteOpened before JackFound | No phase skip |
| Duplicate event | Repeat a consumed progression event | No duplicate transition or duplicate narrative sequence |
| Evidence uniqueness | NursingRecord reported twice | Truth remains locked without FabricatedReport |
| Truth prerequisites | TruthRevealed without both evidence flags | No transition to FinalChoice |
| Truth reveal | Both distinct evidence records and valid reveal | FinalChoice; Supervisor revelation, visible rewrite and Correction_Order sequence |
| Correction contract | Finish Correction_Order | OnDialogueFinished reports exactly Correction_Order |
| Supervisor gate | SupervisorDefeated in FinalChoice | Files become available; Ending remains None |
| Final registration | Confirm and register one valid file after the gate | Exactly one ending; phase becomes GameEnded; Retake blocked |
| Invalid registration | Missing boss gate, invalid choice or repeated registration | No unauthorized ending transition |
| Interaction priority | Valid finisher priority 100 and door priority 40 nearby | One finisher interaction; door does not open |
| Dialogue lock | Start, advance and finish a linked conversation | Input/Retake locks bracket the complete sequence |
| HUD events | C doubles broadcast A/B dispatcher values | HUD updates without Tick or foreign-class casts |
| Checkpoint | Restore after persistent interaction and personal Retake | Correct C state; listener restore policy follows A/B decisions |

[PROPUESTA] Accept either evidence order by storing distinct evidence flags.
The division file leaves evidence ordering open; obtain agreement before this
becomes runtime behavior. FinalDocumentRegistered Param encoding and checkpoint
restore policy also need coordination before the relevant F1 implementation.

## Requested MCP smoke-test result

Asset: /Game/Unscripted/Narrative/Test/BP_MCPConnectionTest_C.
Parent: Actor. Member: bMCPVerified (bool).
EventGraph: BeginPlay exec -> Set bMCPVerified, value true.
Created, modified, connected, compiled with warnings_as_errors=true and saved
through MCP. Readback confirmed both connection directions, true input default
and is_dirty=false after saving.

No actor was placed in a map and no PIE execution was performed. This is the
requested creation/compilation smoke test, not the F1 gameplay milestone.
The editor's Spanish localization affects tool-reported display names; custom
asset and variable identifiers are English. No global language setting changed.
