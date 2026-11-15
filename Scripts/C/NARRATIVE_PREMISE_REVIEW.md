# Narrative premise review

Date: 2026-11-14
Branch: c/f0-narrative-preparation
Scope: Division C source data and preparation documents, during F0.
Authority: the user's confirmed premise, docs/01_VISION_Y_NARRATIVA.md,
docs/05_NIVEL_MISIONES_Y_HUD.md and the existing shared contract vocabulary.

## Confirmed narrative facts

1. Jack is innocent within this alternate fiction.
2. The Department protects him temporarily while fabricating evidence to cast
   him as Jack the Ripper.
3. Once the false case is ready, the Department intends to make him disappear
   without making his identity public.
4. The Director imposes a fabricated history and presents that work as preservation.
5. Registering the official file preserves that false version; registering the
   authentic file preserves the truth. Supervisor defeat only unlocks the files.
6. The documented authentic ending preserves evidence for the agent's next self
   after memory erasure. It does not promise that Jack survives.

## Findings and corrections

The prepared story did not reverse Jack's innocence or turn the final choice
into a combat outcome. Several English summaries left key motives implicit.

| Data | Finding / resolution |
|---|---|
| Briefing_01-05 and initial checklist | Coherent covert instructions: locate Jack, protect him from capture, conceal his identity. Keep the real purpose concealed until the reveal. |
| JackFound_01-03 | Jack's fear and his question about being kept alive fit the instrumental protection. They are not confessions. |
| Truth_02-05 | Keep the evidence of innocence and the Supervisor's convenient-culprit logic. Keep the confirmed reason for temporary protection, false case and secret disappearance in a concise spoken reveal. |
| SupervisorEncounter_02 | Replace the ambiguous expression about fabricating a murderer with framing an innocent man as Jack the Ripper. No actual murderer is created or identified by this line. |
| FinalChoice checklist | Explicitly order framing Jack as Jack the Ripper; retain elimination without revealing his identity. Preserve both completed objectives verbatim. |
| NursingRecord_Summary | Clarify that the time/signature contradict the accusation and support Jack's innocence; add no invented time, witness or location. |
| FabricatedReport_Summary | Make the protection -> fabricated case -> secret disappearance sequence explicit. |
| OfficialFile_Summary / OfficialEnding_Summary | The file falsely accuses an innocent man. Its registration preserves the Director's version and authorizes the documented secret elimination. His identity is not published. |
| AuthenticFile_Summary / AuthenticEnding_Summary | The file preserves innocence and evidence of fabrication. Retain the documented memory erasure, Jack's death and surviving copy; do not invent a guaranteed rescue. |
| StoryTransitions.json and C plan section 5 | Clarify the reveal and ending meanings without changing phase order, events, flags, guards or interfaces. bJackSafe records reaching the refuge at that stage, not permanent survival. |
| UIStrings.csv and future preview fixtures | Labels do not assert guilt. Exercise the expanded reveal in the long-dialogue fixture. No widgets are created. |

The false accusation inside the Department's record does not require publishing
Jack's real identity. The official ending's public version keeps it concealed.
The actual killer's identity remains undisclosed.

## Speaker perspective retained

The Supervisor's "Your job was to preserve history" is an antagonist's
justification, immediately challenged by the agent. It is not a statement
that the Department is objectively protecting historical truth.

The official-ending quotation, procedure warnings and continuity notice also
retain their agency perspective. They do not override the confirmed premise.

## Data traceability and phase limits

Twenty-four dialogue rows still map to twenty-four source quotations in ten
separate sequences. The four edited English adaptations retain their source
anchors and are recorded in NarrativeSequences.json. No row identifier, NextRow link,
speaker token or Correction_Order identifier is changed.

Review covers five checklist rows, twelve narrative entries, sixteen UI
strings, six transition/access rules, fourteen event policies and the C
implementation/preview preparation documents. Proposed speaker labels and
presentation choices remain proposals.

This is editorial review plus structural data validation. Automated checks
validate coverage, links, masks and transition consistency; they do not prove
natural-language meaning. No new semantic keyword test is presented as proof.

No new shared type, gameplay event, asset, widget, integration or phase was
implemented. Unreal import, rendering, runtime flow and F1 acceptance remain
pending. The content review does not mark F0 complete.

## Final editorial pass against the definitive premise

The complete source progression was reviewed: protective briefing -> Jack's
question and the future-self warning -> the two records -> confirmation of the
fabricated case and rewritten orders -> the Supervisor obstacle -> physical
file registration -> the documented official/authentic endings.

Four dialogue lines were refined:
- JackFound_03: a direct, natural question retains the reason-for-protection
  mystery without changing what Jack knows.
- Truth_05: four short sentences retain the convenient culprit, the false case
  as the reason for keeping Jack alive, disappearance and identity secrecy.
  The evidence/report and rewritten checklist identify the fabricated Ripper
  accusation explicitly; the reveal no longer repeats their whole explanation.
- SupervisorEncounter_02: present-progressive framing keeps the official
  archive decision pending while acknowledging the Department's wrongdoing.
- SupervisorEncounter_04: challenge the Director's final word rather than
  imply a new objective to replace the Director.

The English motto is:
"History belongs not to those who lived it, but to those who decide how it is told."

NarrativeMotto is presentation copy with no assumed speaker or placement.
FinalChoiceObjective reads "Choose which account to archive." It distinguishes
the player's decision from the Department's rewritten demands.

The framing/elimination checklist entries remain the Director's orders.
Their completion is not required to select AuthenticRecord; the existing
registration guard already permits that choice without either act.
This clarification changes no phase guard, event, interface or runtime rule.

The two evidence summaries remain complementary: one contradicts Jack's guilt,
the other exposes fabrication. File attribution stays inside the Department's
record; it does not publish Jack's real identity. The official ending preserves
the manufactured version; the authentic ending preserves evidence for the
agent's next self without inventing a rescue or changing the documented deaths.

The twenty-four dialogue rows, ten separate sequences, five checklist rows,
twelve narrative entries and six transition/access rules remain intact.
UI copy now has sixteen entries, including the motto and final-choice objective.
Source quotation anchors, Correction_Order, speaker tokens and row links stay
unchanged. No timing, fixed evidence order or cross-scene playback link is added.

Semantic and dramatic coherence were reviewed manually. Structural checks cover
the source files only. Document bodies are still marked DesignSummary; staging,
reading pace, rewrite animation and both complete endings still need Unreal
playtesting after their implementation. This pass creates no runtime content.
