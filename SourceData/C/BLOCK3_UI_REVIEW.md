# Daniel / C - Block 3 presentation review

Local work on `c/hud-hideout-polish`, preserving the existing C-30/C-31/C-32 implementation and all previous uncommitted work. No branch changes, integration, commits or publication were performed.

## Findings and changes

| Surface | Observed problem | Presentation change |
|---|---|---|
| WBP_HUD | Small, dense status block; long assignments depended on a fixed-height slot | Larger 500 x 136 status plate, clearer vitals/resource grouping and key hints, larger circular agent emblem; primary assignment now wraps in an automatically sized card |
| WBP_Checklist | Long directives could exceed their rows; weak hierarchy | Numbered directives, engraved cut-corner dossier cover, separators, larger type, explicit wrapping and padding; exceptionally long content uses a bounded scroll area while the footer stays visible |
| WBP_Dialogue | Tight reading area and abrupt typographic hierarchy | Wider engraved transmission panel, distinct speaker/channel/body levels, adaptive body height, consistent continue control; typewriter rate tuned from 42 to 34 characters per second |
| WBP_Document | Evidence reading layout was cramped | Larger evidence reader, clearer title/body hierarchy, readable wrapping and scroll area, consistent close button |
| CONTINUITY ALTERED | Text lacked a reliable contrast surface | Centered notice with a framed backplate sharing the existing fade and slide; no new timer or story event |
| WBP_Ending | Presentation used too little of the viewport; some longer copy and button labels clipped at the new type scale | Larger cinematic composition, aged-paper official page, engraved recovered-message frame, archival seal, larger outcome hierarchy, revised text slots and readable confirmation buttons |

All player text is English. Existing dialogue/evidence/ending copy, event guards, input bindings and progression are preserved. The checklist, document and ending Blueprint graph fingerprints are identical to the pre-polish versions. HUD graph changes only mirror the existing notice presentation onto its backplate; the dialogue graph changes only the reveal-rate literal.

New resources are C-owned procedural UI materials under `UI/Materials/`; no external bitmap/font or additional camera was imported. `UI/Test/BP_UIReadabilityProbe_C` is a test-only native layout probe: it keeps Slate geometry inside Blueprint and returns plain vectors to the editor tests. Production widgets have no dependency on it.

## Validation performed

- Native Unreal MCP compilation: all five widgets and the isolated probe compile without errors or warnings. All content and map packages are saved; 18 final saved-resource checks pass.
- Actual Slate measurements: 125 checks pass across every assignment phase, all five checklist rows, all 24 dialogue rows, both evidence documents, the continuity notice, live status labels and deliberately long presentation-only text. Oversized dossier content scrolls within the cover. Fixtures restore the original presentation and do not change progression or health.
- Real Whitechapel pawn and native keyboard: 39 HUD/Tab/E/Retake/Frame Cut/cooldown/checkpoint/hideout checks pass. Entry hides the pawn; exit restores visibility and movement.
- C-30 regression: 53 checks pass through the future message, native-E evidence interactions, Supervisor revelation, checklist rewrite and continuity notice. Only missing B prerequisites use the previously authorized test source.
- Official ending: 47 checks pass. Authentic ending: 46 checks pass. These include actual confirmation/final-page text allocations, cancellation, independent movement locks, real Records-door interaction, one ending dispatch, and resistance to repeated E/R/F/Tab after registration.
- Saved existing systems: 30 ending-package and 29 C-30 checks pass, including production dependency checks and original D mesh references.
- Narrative source validation: 24 dialogue rows, five checklist rows and 12 narrative text rows pass their existing schema/link checks; six intentionally invalid fixtures are rejected. This source-only validator does not claim runtime coverage; the separate PIE suites above provide it.

Native captures use a 1322 x 762 viewport, approximately 1875 x 1081 logical HUD units at the editor's existing DPI. Additional display sizes and packaged Shipping acceptance remain team QA work; no project-wide resolution or DPI setting was changed.

Reports are local under `Scripts/C/*validation.json`; screenshots are diagnostic artifacts under `SourceData/C/Previews/`. Build scripts are authoring records and should not be rerun over the working assets.

## Remaining dependencies and visual limits

- A: the real health template still supplies CurrentHealth=0 and MaxHealth=0. The HUD honestly shows NO VITALS DATA. No false values or player-component changes were introduced.
- A: actual Retake-history clearing and complete death/respawn integration remain owner responsibilities. C's existing terminal modal/input boundary still prevents native Retake after registration.
- B: a complete unassisted story run still requires Jack/escort/Supervisor actors and their real prerequisite reports in the integrated level. Isolated test preparation does not replace them.
- D: `CREDITS.md` still has empty team-name rows, an unconfirmed music tool/license and other attribution confirmations. Final player-facing credits cannot be considered complete from that source. No names or license claims were invented and the D-owned file was not edited.
- The existing agent emblem remains a stylized silhouette, and the legible engine font remains in use. A final illustrated portrait or bespoke licensed typeface would require approved art resources; none was fabricated for this pass.
- Lighting, world/camera occlusion, the existing Workshop pipe/navigation issue, performance and packaged multi-display QA remain outside this UI pass. No A/B/D, Core, map or global configuration changes were made by this pass.

Block 3 is not declared complete for the whole team: credits and the owner integrations above remain pending.

## Personal Play check

1. Open `/Game/Unscripted/Maps/L_Whitechapel`, ensure Story is loaded and start Play. The opening Director transmission remains automatic. E first completes a line, then advances it; later transmissions retain their existing narrative triggers.
2. Inspect the bottom-left status plate and top-left assignment. Use Tab to open/close the dossier, including rapid reversal. R and F should update the real resource/cooldown indicators; the invalid health source should remain explicit. Approach an existing checkpoint/hideout and check the E prompt and control recovery.
3. Follow `CLOSURE_C30_STATUS.md`'s personal procedure to read the Workshop message, open the real side door and collect both Refuge records. Observe the evidence reader, revelation, crossed-out/revised directives and animated continuity notice. The helper only supplies the missing B reports; actual C interactions remain required.
4. For isolated final-screen inspection, start fresh Play, release the mouse with Shift+F1 and use the editor's bottom command field in **Python** mode:

```python
import unreal; C_ENDING_STAGE='records_door'; exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()+'../Scripts/C/prepare_endings_play.py'),encoding='utf-8-sig').read())
```

5. Return focus to Play, press E at the Records door and wait until it opens. Approach a station, or repeat the command with `C_ENDING_STAGE='official'` or `'authentic'`. E opens the confirmation. Backspace cancels; a second deliberate E registers the file. Inspect the corresponding ending and verify R cannot replace it. Stop/restart Play before testing the other ending.
6. If C-30 was completed manually instead, finish the Director's correction and use `C_ENDING_STAGE='supervisor'` only for B's missing defeat report before opening Records. The fuller ending procedure and external integration caveats are in `CLOSURE_ENDINGS_STATUS.md`.

Optional automated reading stress test: in fresh Play execute `Scripts/C/validate_block3_layout.py` through the same editor Python field. It cycles the real UI through existing copy and temporary long text, then restores the original objective/checklist. It never saves gameplay state or substitutes health. Keep Unreal foreground while examining short animations.
