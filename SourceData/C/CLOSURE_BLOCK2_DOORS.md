# Daniel / C - closure Block 2.1

Local work on `c/hud-hideout-polish`. This handoff records Block 2.1; subsequently authorized C-30 integration is described in `CLOSURE_C30_STATUS.md`. C-31/C-32 are not implemented by either task.

| Story actor | World position (cm) | Unlock | D art |
|---|---|---|---|
| C_SideDoor | (2800,4600,0) | OpenEscapeRoute | SM_Door_Wood_Leaf |
| C_ArchiveGate | (3600,3600,0) | FinalChoice | SM_IronGate_A |
| C_RecordsDoor | (4800,3000,0) | FinalChoice and accepted SupervisorDefeated | SM_Door_Agency_Leaf, double leaf |

All three are instances of C's `BP_Door` in `L_Whitechapel_Story`. They reject premature interactions, open once with E, animate around their hinges, release their passage collider and change their own navigation modifier from Null to Default. Only the side door reports EscapeRouteOpened. Door state remains open through personal Retake. The bounded opening timer never takes control of the player. Existing D mesh files are referenced without modification.

The door task added only the read-only `IsSupervisorDefeated` getter. Its existing fact, guards, transitions and event writers are unchanged. No Core contract is edited. HUD and the locally fixed hideout are preserved.

## Checks

- Real A player in Whitechapel PIE; existing story events supply the test prerequisites.
- Before each unlock, E cannot consume the door and CharacterMovement is stopped by its collider. After E opens it, the real capsule crosses through the doorway without teleporting through it.
- Reject an early boss report; distinguish FinalChoice from SupervisorDefeated; side opening advances to ProtectJack exactly once; other doors never select an ending.
- Archive and Records navigation queries change from partial paths while closed to complete paths while open.
- C Blueprints compile with warnings treated as errors; the C-30 update now passes 220 progression assertions. The 37 real-player door checks also pass after that integration. Saved configuration and ownership checks cover the three instances and the preserved Block 1 actors.

## Dependency for D/B

The Workshop side passage remains a partial NavMesh route after opening, including with C's modifier disabled in a runtime-only isolation check. D's `FA_XPipe_01` is centered at (2800,4565,0) inside the reserved opening. The real capsule (radius 34 cm) passes at X=2735 or X=2865; a centerline capsule sweep hits existing geometry. The current NavMesh agent radius is 35 cm. D/B must review the existing obstruction and baked clearance for Jack/AI. C has not moved the pipe, changed geometry, rebuilt shared navigation or changed global settings.

Normal story access depends on B's Jack/Supervisor events. The door task added no Jack, encounter, evidence, reveal, final document or ending. The subsequent C-30 task supplies evidence and revelation without adding B actors or final registration.

## Personal Play checks

Open L_Whitechapel and start a fresh PIE session for each scenario. In the editor's Cmd field run:

```python
py C_DOOR_SCENARIO='side_open'; exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()+'../Scripts/C/prepare_closure_door_play.py'),encoding='utf-8-sig').read())
```

Change `side_open` to `archive_open` or `records_open`. The helper positions only the live real player near that door and reports existing events; it never saves or rewrites private progression. Press E and walk through. At the Workshop, use the side clearance next to the pipe rather than its centerline. Choose `side_locked`, `archive_locked` or `records_locked` to verify rejection; in `records_locked`, FinalChoice is already reached but the Supervisor has not been defeated. Stop and restart PIE before selecting another scenario; all simulated facts and test actors disappear on stop.

`Scripts/C/validate_closure_doors.py` provides the repeatable physics/event checks. `Scripts/C/verify_closure_doors_saved.py` checks the saved C packages with PIE stopped. Captures and local JSON reports are diagnostic artifacts, not game dependencies.
