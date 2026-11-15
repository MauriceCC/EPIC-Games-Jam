# Division C — isolated F1 implementation

Branch: `c/f0-narrative-preparation`, retained by explicit user instruction.
The published C-01/C-02 commits are already in this branch. No branch switch,
commit, push, merge, rebase or pull request was performed for this work.

## Implemented scope

| Task | Saved implementation | Validation |
|---|---|---|
| C-03 | Nearby interface targets; priority then distance; change-only focus notifications; one interaction per use; occupied-hideout focus lock | Priority 100 beats a closer priority 40 target; E works in PIE |
| C-04 | Reusable base, phase-guarded persistent door, reversible hideout using the existing stealth contract | Door reports once, clears Retake history and stays open; hideout enter/leave and checkpoint release work |
| C-05 | Typed evidence, readable scrollable document, idempotent evidence facts and guarded truth report | Duplicate records cannot replace the other evidence; both distinct types unlock the reveal |
| C-06 | All 24 imported dialogue rows, `NextRow`, queued conversations, optional row duration, input/Retake locks and completion signals | Briefing, Jack, future-self, truth, `Correction_Order` and simulated Supervisor chains play in order |
| C-07 | Imported checklist, Tab, completion strikes and timed fade/replacement/reveal | Intermediate animation frames and final four orders verified |
| C-08 | Health, stamina, Retake, Frame Cut cooldown, detection, objective and contextual E prompt | Existing dispatchers only; no connected UI Tick or cast to A/B; native possession notification rebinds replacement pawns |
| C-09 | Checkpoint marker, initial fallback, GameState routing, guarded GameMode restore and all actor listeners | Replacement pawn, two charges in the test double, persistent story facts and interactions, nested input locks |
| C-10 | Three-second `CONTINUITY ALTERED` notice | Existing event; no phase/input side effects; timer expiration observed |

Only C-owned assets and `L_Test_C` were edited, plus the two explicitly
authorized `BPI_Interactable` declarations: `Interact.Interactor` is Actor and
`GetInteractionPriority.Result` is int32. Other interface declarations,
dispatchers, enums, structs, A/B assets and global configuration were preserved.
The earlier `ReportStoryEvent.Source` and `SupervisorEncounterStarted` repairs
were already present and remain intact.

Production copy is loaded from five C-owned DataTables. `DT_Dialogue` and
`DT_Checklist` use their published row structs. `DT_NarrativeText`, `DT_UIStrings`
and `DT_HUDText` reuse `ST_DialogueLine` for text lookup; no shared row schema was
created or changed. All source rows were compared with their imported values.
The original narrative CSV/JSON sources and the three F0 visual previews are
unchanged. `SourceData/C/DT_HUDText.csv` adds the new HUD/objective/prompt copy.

## Run the visual test

1. Open `/Game/Unscripted/Maps/Test/L_Test_C` and press Play. F11 enlarges the
   viewport. The map alone overrides its GameMode with `BP_TestGameMode_C`.
2. Press E five times to finish the briefing. Press E to talk to the simulated
   Jack, then E four times to finish Jack's dialogue and the future-self message.
3. Press E to open the escape door. Press **3** to simulate arrival at the refuge.
4. Press E to read the Nursing Record, E to close it, E to read the Fabricated
   Report, and E to close it. The truth conversation starts and the checklist
   visibly rewrites. Press E six times to finish truth and `Correction_Order`.
5. Press **7** for the simulated Supervisor encounter and E four times for its
   conversation. Press **8** to report defeat, then **9** for the official file
   or **0** for the authentic file. These last keys exercise C-01's existing
   event gate; spatial file mechanisms and ending screens remain F3 work.

Buttons also advance or close their panels. Tab toggles the checklist. Arrow
keys move the C test pawn in swept steps, respecting narrative/hideout locks.

| Test key | Simulated input |
|---|---|
| 1 / 2 / 3 | Jack found / escape route opened / refuge reached |
| 4 / 5 / 6 | Nursing record / fabricated report / guarded truth report |
| 7 / 8 / 9 / 0 | Supervisor encounter / defeat / official file / authentic file |
| H / J / K / L / M | Health / stamina / Retake charges / cut cooldown / detection |
| P / Backspace | Save current test-pawn checkpoint / report player defeat |
| X | Continuity notice |

The map includes physical C door, evidence, hideout and checkpoint actors.
`C_F1_JackReport` is a C-owned event fixture, not B's Jack. The priority-100
finisher fixture is disabled by default so it does not interrupt the narrative
test. It can be enabled in PIE for a focus demonstration; it does not execute
A/B's finisher system.

[PROPUESTA] Isolated defaults are a 220-unit focus radius, a 0.1-second scan,
E-operated checkpoints, a 0.96-second checklist rewrite, placeholder geometry,
and test-pawn health/stamina restoration. These are C-local test/implementation
choices, not additions to a shared contract or approved final balance.

## Verification and remaining work

- C-01/C-02: 217 functional assertions, 23 PIE assertions and preserved private
  phase ownership/dispatcher signatures after reopening the editor.
- C-03 through C-10: 100 PIE assertions across six validators, including pawn
  replacement and restore during dialogue. The real-key run reached phase 5,
  ending 2, after 19 completed dialogue rows.
- Nine additional real-key UI checks cover Tab, resource signals, X and actual
  notice-timer expiration. World prompts stay hidden during modal reading.
- Final asset audit: 22 Blueprint/interface compilations with warnings treated
  as errors, 161 architecture/signature/source-data assertions, five saved tables
  with 69 rows, and no dirty packages.
- F0 preview regression: 173 assertions, without saving the prototype assets.
- Reports: `c_f1_asset_validation.json`, `c_f1_real_input_validation.json`,
  `c03_c04_pie_validation.json`, `c05_pie_validation.json`,
  `c06_pie_validation.json`, `c07_c08_pie_validation.json`,
  `c09_pie_validation.json`, `c_restore_notice_pie_validation.json`,
  `c_f1_real_controls_validation.json`,
  `c_f0_prototype_regression.json` and `c_f1_scope_validation.json`.

The isolated F1 milestone is implemented. Actual A/B movement/combat/resources,
stealth and death integration remain C-21/C-22 in F2; the A/B assets in this
branch are F0 shells. `RequestFinisher.Target` remains ActorComponent and must
be aligned by its owners before real finisher integration. Existing numeric
widths were consumed without editing their declarations. This is not a global
F0 certification. No F2 world placement, F3 final-choice system/ending screen,
or F4 pass was implemented.

Construction scripts are staged editor-authoring records, not startup scripts.
Do not rerun builders over edited assets. The `validate_*` scripts exercise
saved graphs and write reports without saving assets; run PIE validators in a
fresh `L_Test_C` Play session.
