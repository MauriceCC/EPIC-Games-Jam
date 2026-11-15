# Daniel / C - C-31 and C-32

Implemented locally on `c/hud-hideout-polish`, based on `546c97c`. No merge, commit, push, branch switch or foreign asset edit was performed. The previously detected main/d player conflict remains unresolved; those remote advances are not part of this checkout.

## Production integration

- Existing `BP_FinalChoice`: two Story instances, C_OfficialRecord at (5200,2600,0) and C_AuthenticRecord at (5200,3400,0), reference D's original SM_RecordStation_Official and SM_RecordStation_Authentic. Their colliding meshes remain attached to their C-owned roots.
- The existing ObjectiveManager is still the sole progression owner. Its new read-only queries expose eligibility and the recorded ending; its registration guards, enum values, shared signatures and OnEndingTriggered dispatcher are retained. Eligibility requires FinalChoice, completed C-30, both evidence facts through that phase, SupervisorDefeated, no active document/dialogue and no existing ending. Boss defeat does not select a file.
- E opens a modal naming the selected record and explaining that registration is permanent. A second deliberate E or the registration button confirms it. Backspace or the return button cancels. The modal rejects OS key repeats, very early input and stale/out-of-range targets. Cancellation balances only C's own movement lock, preserves independent locks and restores gameplay input/cursor state.
- Confirmed registration reports the existing FinalDocumentRegistered event with OfficialCut or AuthenticRecord. Only the selected station is consumed. The existing manager enters GameEnded and emits OnEndingTriggered once; stale or opposite reports cannot replace that ending.
- New `WBP_Ending` replaces the gameplay HUD at the terminal boundary, calls SetRetakeBlocked(true), ClearRetakeHistory and SetGameplayInputEnabled(false), disables the pawn's native input and pauses gameplay. Its UI entrance fades/slides using widget time even while gameplay is paused. UI-only focus prevents gameplay behind either modal. Unhandled editor shortcuts remain available.
- OfficialCut presents an aged-paper newspaper, a brass archival frame and a private outcome note. The public newspaper withholds Jack's identity. AuthenticRecord presents a recovered message to the next self: Jack was innocent, the Director fabricated a culprit and the evidence survives the agent's memory erasure. Existing final dialogue quotes and the motto are reused. All player copy is English, with new copy in EndingText.csv / DT_EndingText; the existing HUD prompt table has two additional rows. No external bitmap, font import or camera is required.
- The HUD's prior E chain and Tab behavior are preserved behind bounded final-UI guards. C-30, its records/message, checkpoints, all three doors and the corrected hideout remain in Story. No C-33 menu/restart/credits feature was added.

## Acceptance

- Both final paths passed 28 native-E real-player checks each in L_Whitechapel. These isolated tests use the already authorized C fixture to prepare preceding story facts and missing B prerequisites, never private progression writes or health substitution.
- Coverage includes early rejection, boss-only unlock, real Records-door E interaction, station focus, readable confirmation, native R blocked behind the modal, Backspace cancellation, independent input-lock preservation, stale distance rejection, one ending/one dispatcher emission, correct screen, fade while paused, immutable opposite/repeated reports and native R/F/Tab/E after registration.
- The documented personal setup passed four additional checks. A subsequent continuation test uses the actual native-E C-30 run, then supplies only B's missing SupervisorDefeated report before the real door and final registration.
- Regressions passed: 220 progression assertions, 53 current C-30 native-E checks, 37 door/real-capsule/navigation checks and 39 HUD/Tab/Retake/Frame Cut/checkpoint/hideout checks.
- Saved checks: seven C Blueprints compile with warnings treated as errors; 30 ending-package assertions and 29 C-30/preservation assertions pass. No production asset references Test/Developers. Ending copy matches its source; all content/map packages are saved.
- Native screenshots under SourceData/C/Previews are local diagnostic artifacts. JSON reports and reproduction scripts are in Scripts/C; backups remain outside the repository.

## Remaining owner dependencies

- A-16: this real player still lacks the shared SetRetakeBlocked/ClearRetakeHistory handlers. C emits the existing contract calls and its terminal UI demonstrably prevents native Retake and narrative rollback. Actual clearing of A's internal snapshot arrays still requires A; no player fields or arrays are rewritten by C. Initial real health remains 0/0 and is reported honestly by the HUD. Earlier death/checkpoint integration also remains A's responsibility.
- B: Jack, his natural refuge arrival and the Supervisor encounter/defeat still need the appropriate integrated B actors/events. The test setup does not create or replace any of them.
- D/B: the preexisting Workshop pipe/NavMesh clearance issue remains. The player passes beside the pipe; the Archive and Records openings remain traversable when unlocked.
- A complete unassisted start-to-ending team run cannot be declared until those dependencies and the previously reported player merge conflict are resolved by their owners/integrator.

## Personal Play: each ending

1. Open `/Game/Unscripted/Maps/L_Whitechapel` and start fresh Play. Select **Python** in the editor's bottom command field. Use Shift+F1 to release the Play mouse if needed. Do not use the in-game console for these commands.
2. To test the ending independently, run:

```python
import unreal; C_ENDING_STAGE='records_door'; exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()+'../Scripts/C/prepare_endings_play.py'),encoding='utf-8-sig').read())
```

This shortcut uses the existing authorized C test source to prepare preceding story conditions and the missing boss report. It does not choose or confirm an ending. If you instead completed C-30 through the real evidence/dialogue interactions, finish Correction_Order and use `C_ENDING_STAGE='supervisor'` to supply only B's pending defeat report.

3. Return focus to Play, press E at C_RecordsDoor and wait for it to open. Walk into Records.
4. Approach either station naturally, or repeat the command using `C_ENDING_STAGE='official'` or `'authentic'`. These approach helpers require the real Records door to be open.
5. Press E to examine the chosen file. Read its consequences. Backspace cancels and leaves both stations available; E again deliberately confirms. Mouse buttons offer the same two actions.
6. Official registration shows the newspaper; authentic registration shows the next-self transmission. R cannot undo or replace the registered ending, and the other station cannot select a second ending.
7. Stop Play using the editor's Stop button. Restart from step 1 for the other outcome. The helper and simulated facts vanish when PIE stops; no saved game or authored phase is changed.

Automated reproduction: run `validate_endings_play.py` in fresh Whitechapel PIE with C_ENDING_CASE set to official or authentic. Use `verify_endings_saved.py` with PIE stopped. Build/integration scripts are one-time authoring records; do not rerun them over the working assets.
