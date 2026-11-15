# C-01 / C-02 local implementation

## Scope and dependencies

Implemented on `c/f0-narrative-preparation`, with no commit, push, merge, rebase, or PR.

The user authorized only the shared changes indispensable to these two tasks:

1. `Core/Interfaces/BPI_StoryEvents.ReportStoryEvent.Source`: ActorActionUtility -> Actor. Event, Param, function names, and all other interface functions retain their signatures.
2. `Core/Enums/EStoryEvent`: append SupervisorEncounterStarted at value 13. Existing values 0 through 12 are preserved.

The existing six EStoryPhase values, EEndingType values, BP_GameMode defaults, BP_GameState parent/interface, installed ObjectiveManager component, five ObjectiveManager dispatcher signatures, and L_Test_C were sufficient. No other shared correction was required.

Combat, AI, navigation, controls, collision, other interfaces, shared structs, foreign components, global configuration, and existing maps were not changed.

## Runtime implementation

- `Narrative/BP_ObjectiveManager`: CurrentPhase, Ending, the documented narrative flags, the supervisor-defeat gate, and an event-processing guard.
- All ten state variables are private and not instance editable.
- `CommitStoryPhase` is private and contains the sole runtime CurrentPhase setter.
- `HandleStoryEvent` rejects terminal-session and synchronous reentrant reports.
- `ProcessStoryEvent` applies the six prepared transition rules and leaves unrelated notifications without phase effects.
- Two distinct evidence facts are required; duplicate or invalid parameters cannot substitute for the other fact. Truth revelation still requires an explicit report.
- Supervisor encounter and defeat reports are idempotent. Defeat unlocks registration and never chooses an ending.
- A valid simulated final-registration report chooses one Ending and enters GameEnded exactly once; later reports cannot change that state.
- Existing OnStoryPhaseChanged, OnChecklistUpdated, and OnEndingTriggered signals are emitted without changing their signatures.
- `Narrative/BP_GameState`: the interface forwards Event, Source, and Param to its existing ObjectiveManager; GetCurrentPhase reads that same manager.
- GetObjectiveManager and BP_GameMode configuration were already correct and were preserved. BP_GameMode did not need an edit.

The dialogue queue, evidence actors, interactables, document confirmation, final-choice mechanisms, ending screens, checkpoint recovery, HUD, input locking, and Retake behavior remain their later C tasks. These systems were not implemented as part of the transition core.

## Provisional C interpretation of Param

[PROPUESTA] Isolated C tests interpret the existing Name Param using existing canonical tokens:

| Event | Param |
|---|---|
| EvidenceCollected | NursingRecord or FabricatedReport |
| FinalDocumentRegistered | OfficialCut or AuthenticRecord |

Other values are rejected. This is a C-owned implementation/testing convention, not a new shared signature or a requirement imposed on A/B/D. Confirm the convention before cross-division integration. The C helper functions isolate this interpretation so it can be adapted locally without changing Core.

[PROPUESTA] The isolated state core records the two evidence facts in either order, consistent with the flexibility allowed by docs/05. No collection actor, spatial sequence, or narrative trigger order is committed by this implementation.

## Test fixtures

- `Narrative/Test/BP_StoryEventTestSource_C`: a normal Actor with EventToReport and EventParam, reporting through the actual BPI_StoryEvents message. It has no input bindings and is not placed in a saved map.
- `Narrative/Test/BP_StoryProgressionObserver_C`: a C-only observer fixture derived from ObjectiveManager, binding real Blueprint multicast callbacks to a separate observed manager. It counts notifications and can attempt a reentrant report for guard testing.

Production Blueprints do not reference either test fixture.

## Validation

- 217/217 Blueprint checks passed, including a phase/event cross-product whose expected transitions come from SourceData/C/StoryTransitions.json, invalid and premature events, duplicates, both evidence orders, explicit revelation, both endings, terminal-state behavior, two multicast subscribers, and reentry protection.
- 23/23 checks passed in L_Test_C PIE through Actor -> interface -> real GameState -> real ObjectiveManager.
- PIE verified exactly five phase notifications and one ending notification for the complete simulated path.
- The new Actor source demonstrates that Source accepts a normal Actor rather than ActorActionUtility.
- CurrentPhase setter inspection found exactly one writer: BP_ObjectiveManager.CommitStoryPhase.
- Source data validation passed for the existing English dialogue/checklist/narrative files. No narrative copy was edited.
- Modified dependencies and C Blueprints compiled with warnings treated as errors and were explicitly saved.
- No existing map was edited or saved. Test actors existed only in PIE.
- Independent UI prototypes and all unrelated pre-existing C work were preserved.

Reports: c01_c02_contract_fix.json, c01_c02_build_result.json, c01_c02_private_state.json, c01_c02_unit_validation.json, c01_c02_pie_validation.json, c01_c02_final_validation.json.

## Reproduce in Unreal

With L_Test_C open and PIE stopped, use the editor Cmd console:

```text
py exec(open(r'C:\Users\user\Desktop\EPIC-Games-Jam\Scripts\C\validate_c01_c02.py',encoding='utf-8-sig').read())
```

For the real interface path, start a fresh Play session in L_Test_C and run:

```text
py exec(open(r'C:\Users\user\Desktop\EPIC-Games-Jam\Scripts\C\validate_c01_c02_pie.py',encoding='utf-8-sig').read())
```

Stop Play afterward. The PIE script exercises a complete simulated session; start a fresh session before rerunning it. These validators do not save assets. The build scripts are one-time construction artifacts and must not be rerun over authored graphs.

## Readiness and remaining work

C-01/C-02 state progression is implemented and locally validated. The full F1 milestone is not complete: C-03 through C-10 remain pending. F2/F3 integrations and final presentation are not implemented.

The known Interact.Interactor, GetInteractionPriority.Result, RequestFinisher.Target, other numeric signatures/structs, input, navigation, and Combat-channel issues were deliberately left untouched. They are not dependencies of this isolated progression core. Global F0 completion and publication to other workstations are not claimed.
