# Daniel / C - C-30 narrative integration

Local only on `c/hud-hideout-polish`. Scope: closure plan Block 2.4, after the three Block 2.1 doors. No C-31/C-32 final-choice actors, final screens or shared contracts were changed.

## Saved production changes

| C package | Change |
|---|---|
| Narrative/BP_ObjectiveManager | Guarded future-message interaction, distinct evidence availability, Supervisor dialogue completion and one-shot continuity notice |
| Narrative/BP_Evidence | Existing document presentation retained; no premature TruthRevealed report; duplicate kind and phase guards |
| Narrative/BP_FutureMessage_C | Small interactable derived from the existing C base, using the existing future-self dialogue |
| Narrative/DT_HUDText | One additional prompt: Read future message |
| UI/WBP_HUD | Temporarily reveal the existing animated checklist rewrite; timed fade/slide for CONTINUITY ALTERED |
| Maps/L_Whitechapel_Story | The three C interactions below, referencing original D meshes |

| Story actor | World position, cm | Reused D prop |
|---|---|---|
| C_FutureMessage | (2900,5300,0), Workshop table | SM_Folder_Report, mesh height 90 |
| C_NursingRecord | (3340,460,0), Refuge cot | SM_Ledger_Nursing, mesh height 110 |
| C_FabricatedReport | (2400,1200,0), Refuge crates | SM_Folder_Report, mesh height 120 |

Existing English narrative rows are retained: FutureMessage_01, Truth_01 through Truth_05 and Correction_Order. Jack is innocent; the Department protects him until its fabricated case is ready, then intends to erase him without disclosing his identity. The Supervisor revelation is the existing dialogue transmission, not a newly created B character or encounter.

The Workshop message is read once with E after JackFound, rather than playing remotely when Jack is found. Evidence requires JackReachedRefuge and DiscoverTruth. Both distinct records must be collected; closing the second document begins the Supervisor conversation. The phase stays DiscoverTruth until E confirms Truth_05. Only then does the manager report TruthRevealed, enter FinalChoice, queue Correction_Order, rewrite the checklist and report ContinuityAltered once. Premature or repeated reports cannot skip or replay this sequence.

The existing dossier opens for 2.4 seconds if it was closed, preserving crossed-out completed directives and showing the altered orders. Tab takes ownership if the player operates the drawer during that presentation. The notice fades/slides in, holds briefly and fades out over three seconds, below the transmission header. Neither presentation takes movement control.

## Validation

- Two Whitechapel PIE runs using the real A character and native E: 53 checks each, with opposite evidence orders. Only missing B JackFound/JackReachedRefuge prerequisites were simulated. Future message, real side door, both documents, Supervisor lines, checklist, notice, premature reports and duplicates were exercised through production systems.
- The documented three-stage Play helper passed another 17 native-E checks, including the saved final notice position and compact HUD recovery.
- Progression regression: 220 assertions. A test-only ObjectiveManager subclass supplies revelation completion for worldless state tests; no production package references that fixture. Integrated Play tests never set private story state.
- Door regression: 37 checks, including real CharacterMovement passage, colliders, phase locks and Archive/Records navigation.
- Existing HUD/narrative regression: 39 checks, including Tab, real R/F abilities and cooldown, CP0/CP1 and hideout entry/exit/control recovery. Real health remains unchanged at 0/0; no fake health is used.
- Source validation: all 24 dialogue rows, five checklist rows and 12 narrative-text rows validate; six intentionally invalid fixtures are rejected.
- Saved-package inspection: 29 checks, five C Blueprints compiled with warnings treated as errors, no production test dependencies and no dirty content/map packages.

Reports live in `Scripts/C/c30_*_validation.json`, `c01_c02_unit_validation.json`, `closure_doors_validation.json` and `narrative_presentation_validation.json`. Local captures under `SourceData/C/Previews/` are diagnostic only. Backups remain outside the repository.

## External dependencies

- B: no Jack or Supervisor actor is placed in this Whitechapel copy. Natural JackFound/JackReachedRefuge, escort and boss-defeat integration remain B responsibilities. C-30 can be tested through the bounded C helper below without creating or changing B systems.
- D/B: the existing central Workshop pipe leaves the side opening with a partial NavMesh path. The actual player can pass beside it; Archive/Records paths are traversable after opening. Geometry and shared navigation were not changed.
- A: the real player health template remains 0/0; the HUD honestly displays NO VITALS DATA. Earlier death/respawn integration blockers remain outside C-30.
- C-31/C-32: final registration and ending integration are deliberately not started. Reaching FinalChoice here is the C-30 boundary, not a playable completed ending.

## Personal Play procedure

1. Open `/Game/Unscripted/Maps/L_Whitechapel`, ensure Story is loaded and start a fresh Play session. Use the editor's bottom command field, selecting **Python**. If Play captured the mouse, release it with Shift+F1. These are editor Python commands, not commands for the in-game console.
2. Run this command to supply only the missing JackFound prerequisite and position the actual player beside the Workshop table:

```python
import unreal; C30_STAGE='workshop'; exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()+'../Scripts/C/prepare_c30_play.py'),encoding='utf-8-sig').read())
```

3. Return focus to Play. Finish Jack's conversation with E; E first reveals a line, then confirms it. Approach the folder on the Workshop table and press E to read the future-self transmission. Finish that transmission with E. Interacting again must not replay it.
4. Run the same command with `C30_STAGE='escape'`. Press E at the side door and wait for it to open. This real interaction must reach ProtectJack; the helper cannot supply EscapeRouteOpened.
5. Run the command with `C30_STAGE='refuge'`. This supplies only B's pending JackReachedRefuge report after the door is open and positions the player inside the Refuge.
6. Walk to the ledger on the cot, C_NursingRecord, and the folder on the crates, C_FabricatedReport. Press E to open and E to close each document. Either order works. After the first record, the phase must remain DiscoverTruth and no Supervisor conversation should start. Repeated E must not collect the same record twice.
7. Closing the second document starts Truth_01. Read and confirm all five Supervisor lines with E. FinalChoice must not occur before Truth_05 is confirmed. Observe the checklist rewrite, CONTINUITY ALTERED and the Director's altered order. Tab reopens the revised dossier after its temporary presentation closes.
8. Stop Play to remove all test actors and simulated prerequisites. Restart Play for a new order/negative test. Evidence cannot be used before the Refuge prerequisite; Records stays locked until B reports SupervisorDefeated. No ending is selected during this procedure.

The helper never saves assets, changes health, writes private progression flags, collects evidence or completes the revelation for the player. Keep the Unreal window foreground while checking short animations; the editor's existing background throttle runs at a much lower frame rate.
