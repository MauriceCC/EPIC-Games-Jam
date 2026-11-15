# División C — Relato: narrativa, interacción, objetivos, UI y finales

> **Base confirmada:** Unscripted ? UE 5.8.4 ? Blueprint. Todo contenido para el jugador debe estar en ingl?s, incluidos placeholders visibles. Ver [arranque F0](02_ARRANQUE_F0.md). Las rutas de contenido son relativas a `Unscripted/`; `Scripts/` y `SourceData/` parten del repositorio.

**Persona:** _(nombre)_ · **Rama:** `c/<tarea>` · **Commits:** `[C] …`

## 1. Misión

Que el tema *Director's Cut* **se juegue**: las órdenes aparecen, se reescriben ante el jugador, las pruebas se recogen, los diálogos se leen bien, el HUD informa sin estorbar y el final se decide **registrando físicamente un expediente**. C es la "columna vertebral" que convierte sistemas sueltos en una partida.

**Fuentes de diseño:** `docs/01` (historia, diálogos, finales), `docs/02` (interacción, checkpoints), `docs/05` (fases, objetivos, HUD), `docs/06` (ObjectiveManager, interfaz de interacción), `docs/07` (interfaz).

## 2. Propiedad

- `Content/Unscripted/Narrative/` y `Content/Unscripted/UI/` (incluyen `Test/`)
- Subnivel `Maps/L_Whitechapel_Story` y `Maps/Test/L_Test_C`
- `SourceData/C/` (diálogos y checklist en CSV), `Scripts/C/`, `Source/Unscripted/Narrative/` (si hay C++)
- Este archivo.

**No tocas:** `Core/`, jugador, enemigos, Jack, geometría.

## 3. Lo que provees y lo que consumes

| Provees | A quién |
|---|---|
| `BP_GameState` con `BPI_StoryEvents` y `BP_ObjectiveManager` (fuente única de verdad de la progresión) | Todos |
| Dispatchers `OnStoryPhaseChanged`, `OnChecklistUpdated`, `OnDialogueStarted/Finished`, `OnEndingTriggered` | B, D |
| `BP_GameMode`: respawn y llamada a `OnCheckpointRestore` | A, B |
| `BP_InteractionComponent` (en el jugador): foco por prioridad + prompt | A (lo hospeda) |
| Interactuables: puerta, escondite (`SetHidden`), evidencias, expedientes, checkpoints, triggers | — |
| HUD, checklist, diálogos, pantalla de final, pausa | — |

| Consumes | De quién | Mientras no exista… |
|---|---|---|
| Dispatchers de salud/resistencia/Retoma/Corte | A | Los cascarones existen desde F0; un `BP_TestPlayer_C` que los dispare con teclas |
| `BPI_PlayerControl` | A | Idem |
| `OnDetectionChanged` | B | Idem |
| Eventos `JackFound`, `JackReachedRefuge`, `EnemyNeutralized`, etc. | B | Un actor de prueba que los envíe con teclas |
| Arte de UI (fuentes, papel, sellos), sonidos de UI | D | Fuentes del motor + placeholders `SC_ChecklistRewrite`, `SC_EvidencePickup` |

## 4. Backlog

### F1 — Sistemas aislados en `L_Test_C`

| ID | Tarea | Prioridad | Criterio de aceptación |
|---|---|---|---|
| C-01 | `BP_GameMode` + `BP_GameState` + `BP_ObjectiveManager` con `EStoryPhase` y variables de `docs/05` | P0 | `ReportStoryEvent` cambia de fase solo si se cumplen condiciones |
| C-02 | Tabla de transiciones de fase (qué eventos llevan de cada fase a la siguiente) documentada en §5 | P0 | Ningún objeto cambia la fase directamente |
| C-03 | `BP_InteractionComponent`: detectar `BPI_Interactable` cercanos, elegir por prioridad y distancia, `OnFocusChanged`, ejecutar con E | P0 | Con puerta y remate a la vez, gana el remate |
| C-04 | `BP_InteractableBase`, `BP_Door` (persistente), `BP_Hideout` (`SetHidden`) | P0 | |
| C-05 | `BP_Evidence` (tipo `EEvidenceType`) + panel de documento legible | P0 | Recoger 2 evidencias → `TruthRevealed` según condiciones |
| C-06 | `DT_Dialogue` (CSV en `SourceData/C/`) con **todos** los diálogos de `docs/01` + `WBP_Dialogue` | P0 | Diálogos encadenados por `NextRow`; bloquea input y Retoma durante el diálogo |
| C-07 | `DT_Checklist` + `WBP_Checklist` (Tab) con tachado y **animación de reescritura** | P0 | El cambio de órdenes es claramente visible: es el momento temático clave |
| C-08 | `WBP_HUD`: salud, resistencia, cargas de Retoma, cooldown de Corte, detección, objetivo, prompt E | P0 | Todo enlazado por dispatchers, sin `Tick` ni `Cast` a clases ajenas |
| C-09 | `BP_Checkpoint` + respawn en el GameMode (`OnCheckpointRestore` a todos los listeners) | P0 | |
| C-10 | Aviso «CONTINUIDAD ALTERADA» (`ContinuityAltered`) | P1 | |

**Mínimo F1 (hito):** en `L_Test_C`, con teclas de prueba se recorre toda la secuencia de fases, se ven diálogos, checklist reescrito y HUD reaccionando.

### F2 — Vertical slice

| ID | Tarea | Prioridad | Criterio |
|---|---|---|---|
| C-20 | Colocar en `L_Whitechapel_Story`: `PlayerStart`, transmisión inicial, primer checkpoint, puerta lateral | P0 | |
| C-21 | Integrar HUD con el jugador real de A y detección de B | P0 | |
| C-22 | Flujo de muerte y respawn completo con A y B | P0 | |

### F3 — Contenido

| ID | Tarea | Prioridad |
|---|---|---|
| C-30 | Actos I–III completos: triggers, mensaje del yo futuro, evidencias, revelación del Supervisor, fila `Correction_Order` | P0 |
| C-31 | `BP_FinalChoice` x2 (oficial / auténtico) con confirmación, `ClearRetakeHistory`, `OnEndingTriggered` | P0 |
| C-32 | `WBP_Ending`: periódico (Final A) y mensaje al próximo yo (Final B) | P0 |
| C-33 | Menú principal, pausa, créditos (con `CREDITS.md` de D) | P1 |
| C-34 | Subtítulos con nombre del hablante y filtro visual de "transmisión" | P1 |

### F4 — Pulido

Textos revisados (ortografía), legibilidad a 1080p, ritmo de diálogos, comprobar que nunca se puede quedar bloqueada la historia.

## 5. Phase transition table (C-02 preparation)

Status: C-01/C-02 Blueprint state progression implemented and locally validated; full F1 remains incomplete.
Only BP_ObjectiveManager owns phase changes through the existing contract.

| Current phase | Reported event and guard | Next phase | Narrative effects |
|---|---|---|---|
| FindJack | `JackFound` - Current phase is FindJack; ignore a duplicate JackFound. | OpenEscapeRoute | Record bJackFound; queue Jack dialogue and the future-self message. |
| OpenEscapeRoute | `EscapeRouteOpened` - Jack has been found and the route-opening report is valid for this phase. | ProtectJack | Record bEscapeRouteOpen; show the protection/escort objective. |
| ProtectJack | `JackReachedRefuge` - Jack was found and the route was opened before the refuge report. | DiscoverTruth | Record bJackSafe; show the truth-discovery objective. |
| DiscoverTruth | `TruthRevealed` - Jack has reached the refuge; both distinct evidence records have been registered. | FinalChoice | Reveal the Director's fabrication and why innocent Jack was protected until the false case was ready; queue the Supervisor revelation, checklist rewrite and Correction_Order. |
| FinalChoice | `SupervisorDefeated` - Current phase is FinalChoice; do not select an ending. | FinalChoice | Unlock the two final files; Ending remains None. |
| FinalChoice | `FinalDocumentRegistered` - Supervisor gate satisfied; confirm one valid file; ignore repeated registration. | GameEnded | Record one ending: OfficialCut preserves the Director's false version; AuthenticRecord preserves the truth. Block Retake; trigger OnEndingTriggered. |

[StoryTransitions.json](../../SourceData/C/StoryTransitions.json) is C-owned
preparation data. Its six rules and fourteen event policies keep the existing
contract tokens and phase behavior. GameEnded has no outgoing transition.
Premature, duplicate and invalid reports cannot skip phases.

The truth reveal exposes the Director's fabrication and the Department's
temporary reason for protecting innocent Jack. Supervisor defeat unlocks the
two files. Confirmed registration chooses the false official version or the
truth-preserving authentic record. Personal Retake does not undo narrative facts.
bJackSafe means that Jack reached the refuge at that stage; it does not guarantee
his survival after the final choice.

[PROPUESTA] Evidence order, Param encoding and private preview presentation
remain open. No shared interface, dispatcher, enum or struct was changed.
See [the premise review](../../Scripts/C/NARRATIVE_PREMISE_REVIEW.md) and
[widget preparation](../../Scripts/C/WIDGET_PROTOTYPE_PREPARATION.md).

## 6. Notas técnicas

- **Una sola fuente de verdad:** solo `BP_ObjectiveManager` cambia la fase. Puertas, evidencias, Jack y enemigos **solo reportan eventos**.
- Los textos van en DataTables (no en nodos) para poder corregirlos con el agente vía CSV.
- El HUD solo se entera por dispatchers enlazados en `BeginPlay` (obtener componentes por clase/interfaz desde el pawn).
- La elección final debe ser **espacial** (`docs/01`): caminar al mecanismo y pulsar E, con confirmación.

## 7. Decisiones abiertas de la división

- ¿Retoma automática o elegida al morir? — con A.
- ¿Pelea del Interventor opcional u obligatoria? — con B.
- Orden flexible de las evidencias (`docs/05` lo permite) vs. orden fijo.

## 8. Prompt de arranque para tu agente

```text
Trabajo en la División C (Relato: narrativa, interacción, objetivos, UI y finales) del proyecto Unscripted (UE 5.8.4, Blueprint).
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/C_NARRATIVA_INTERACCION_UI.md y después docs/01, docs/02, docs/05, docs/06 y docs/07.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: solo puedo modificar Content/Unscripted/Narrative/, Content/Unscripted/UI/,
Maps/L_Whitechapel_Story, Maps/Test/L_Test_C, SourceData/C/, Scripts/C/ y mi archivo de división.
Respeta exactamente las firmas del contrato v<versión>.
Entrégame: (1) los pasos para construirlo en Blueprint/UMG, nodo a nodo, indicando en qué asset va cada cosa;
(2) los datos de DataTable en CSV si aplica (diálogos, checklist); (3) cómo probarlo en L_Test_C;
(4) si necesitas algo fuera de mis carpetas, redáctalo como solicitud de contrato y no lo implementes.
```

## 9. Solicitudes de contrato

| # | Fecha | Petición | A quién | Estado |
|---|---|---|---|---|
| C-F0-01 | 2026-11-14 | Complete and validate the pending F0 bases/maps. Interfaces and six component assets are delivered; signature and dispatcher conformance remain pending under C-F0-02/03/04. | Integrator | Partially delivered; F1 remains gated |
| C-F0-02 | 2026-11-14 | Align existing Core signatures with the documented contract: ReportStoryEvent.Source and Interact.Interactor are ActorActionUtility instead of Actor; GetInteractionPriority.Result is Text instead of int; RequestFinisher.Target is ActorComponent instead of Actor. See the MCP audit. No new signature is requested. | Integrator (Core) | Pending; C does not implement a workaround |
| C-F0-03 | 2026-11-14 | Deliver the existing F0 dispatcher declarations: five ObjectiveManager signals and OnFocusChanged are absent; Health, Combat, Temporal and Stealth dependency signals are also absent. Stealth has no custom function graphs. Exact existing names/signatures are in contracts section 5 and the MCP audit. | Integrator (F0 delivery) | Pending; no shared declaration changed by C |
| C-F0-04 | 2026-11-14 | Review ApplyTemporalFreeze: Duration, PostureDamage and Result are double-precision graph pins while the contract says float. Confirm the intended precision or align the pins before freezing F0. | Integrator (Core) | Precision review pending |

## 10. Estado

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte C) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

Notas del día:

### 2026-11-14 - F0 preparation

- Active branch: `c/f0-narrative-preparation`. All work is local; no commit, push, merge, rebase or PR.
- MCP smoke test passed in `/Game/Unscripted/Narrative/Test/BP_MCPConnectionTest_C`: Actor, `bMCPVerified` bool, BeginPlay wired to set it true, compile with warnings treated as errors, explicit save and clean dirty-state readback. No map placement or PIE test.
- Prepared English source data: 24 dialogue rows, five checklist phase rows and 12 narrative text entries in [SourceData/C](../../SourceData/C/README.md).
- Source validation passed: 24 dialogue rows, five checklist rows and 12 narrative text entries; schema, enum tokens, dialogue links/cycles and checklist masks checked. git diff --check passed. Import and runtime validation remain pending.
- Prepared the phase/dependency breakdown and future node-level implementation sequence in [Scripts/C/F1_IMPLEMENTATION_PLAN.md](../../Scripts/C/F1_IMPLEMENTATION_PLAN.md).
- Observed nine enum assets and three struct assets in Core. Six interfaces, shared shells and L_Test_C are absent. Request C-F0-01 records this existing dependency; no shared contract was modified.
- [PROPUESTA] Unattributed source lines use System; intermediate checklist masks and flexible evidence ordering remain draft choices.
- No F1 acceptance item is complete. F2-F4 implementation has not started. Continue with C-01 after the integrator validates F0.

### 2026-11-14 - Independent F0 data review

- Same C branch; local changes only. Reviewed 24 source quotations in ten
  sequences; preserved completed checklist wording and the Fabricated Report title.
- Prepared six transition rules covering all 14 existing event tokens, 14 UI
  labels and future presentation cases. No replacement gameplay system or
  shared type was implemented.
- Plan 00 section 5.2 and its F0 dependency graph gate executable C systems;
  C-06/C-07 are F1. The current conditional request does not waive that gate:
  [widget construction remains a guide](../../Scripts/C/WIDGET_PROTOTYPE_PREPARATION.md).
- [Source validation results](../../Scripts/C/data_preparation_validation.json)
  include quotation coverage, exact chain order, contract token spellings,
  transition-table consistency, preview data and six rejected invalid examples.
- MCP inventory/schema reads confirm F0 still lacks interfaces, shared shells
  and L_Test_C. C-F0-01 remains pending. No WBP asset or integration was created.
- Unreal import, rendering, interaction and runtime acceptance remain untested.

### 2026-11-14 - Confirmed premise review

- Reviewed all C dialogue, checklist, evidence/file summaries, ending summaries,
  UI labels, transition decisions and preparation documents against the user's
  confirmed premise and docs/01. [Review](../../Scripts/C/NARRATIVE_PREMISE_REVIEW.md).
- Jack is innocent. His protection is temporary while the Department fabricates
  evidence to frame him as Jack the Ripper; subsequent disappearance is secret.
- Clarified two English dialogue adaptations and six narrative summaries.
  The rewritten framing objective explicitly names the fabricated Ripper role.
  Correction_Order, row links, shared tokens and phase behavior remain unchanged.
- Preserve the Supervisor's preservation claim as antagonist rhetoric, challenged
  by the agent. The authentic ending preserves truth without promising Jack's rescue.
- Expanded-reveal text is included in the future long-dialogue fixture.
  No widget, gameplay integration, shared contract or later phase was implemented.
- Structural validation results are in
  [the C report](../../Scripts/C/data_preparation_validation.json). Semantic
  coherence was reviewed manually; import and gameplay acceptance remain pending.

### 2026-11-14 - Live MCP shared-asset audit

- Inspected six interfaces/seventeen function graphs, both C components and
  all three shared structs through the running editor MCP.
- BP_ObjectiveManager and BP_InteractionComponent have native ActorComponent
  parents and empty graphs: no custom variables, functions, connected behavior
  or declared dispatchers. Both compiled with warnings treated as errors;
  neither became dirty and neither was saved.
- Found four shared pin-type mismatches and a separate numeric-precision
  question. Requests C-F0-02/04 record the findings without changing Core.
- The six required C dispatcher declarations and eight A/B dependency signals
  are absent. Read-only inspection found no Stealth custom function graphs.
  Existing F0 delivery request C-F0-03 records these gaps.
- Struct field shapes match the documented C table and hit-info fields.
  ESpeaker, EStoryPhase and EAttackType values are exposed by the schemas.
  Import/round-trip, native numeric widths and default values remain untested.
- No F1 gameplay functionality was implemented. Current permitted work is
  preparation, source/schema inspection and C shell compilation. Missing
  bases/maps and incompatible shared signatures still block runtime work.
- [Detailed audit](../../Scripts/C/MCP_SHARED_ASSET_AUDIT.md) and
  [normalized observations](../../Scripts/C/MCP_SHARED_ASSET_AUDIT.json).
- No missing D asset was created; no graph, shared declaration, global
  configuration or other division's asset was edited. No asset-save tool or
  prohibited Git operation was used.

### 2026-11-14 - Final narrative editorial review

- Reviewed the definitive protective-mission -> fabricated case -> archive-choice
  progression, all dialogue/objective/checklist/evidence/file/ending copy and
  the motto. Refined four dialogue lines for naturalness and dramatic intent.
- Added English NarrativeMotto and FinalChoiceObjective presentation strings.
  The Director's framing/elimination orders are not prerequisites for choosing
  the authentic file; existing phase guards and shared contracts are unchanged.
- Kept source anchors, row names, NextRow links, Correction_Order and all
  documented ending consequences. No additional killer identity or rescue
  outcome was invented.
- Source-only validation and the manual review are documented in
  [the narrative review](../../Scripts/C/NARRATIVE_PREMISE_REVIEW.md).
  No Blueprint, map, contract or other division's system was modified.

### 2026-11-14 - C-01/C-02 implementation and limited dependency repair

- Explicit user exception: corrected only ReportStoryEvent.Source to Actor and appended SupervisorEncounterStarted at value 13. Other Core signatures, enum values, shared structs, A/B systems, configuration, and maps were not changed.
- C-01/C-02 state core is implemented in BP_ObjectiveManager and BP_GameState. BP_GameMode defaults and GetObjectiveManager already met the dependencies and were preserved.
- Ten private state fields, one private phase writer, guarded event routing, idempotent facts, distinct evidence guards, supervisor access gate, terminal ending state, and synchronous reentry protection.
- Existing dispatcher signatures were preserved. Narrative actors, dialogue playback, HUD, final-choice UI, controls, Retake, checkpoint logic, and later integrations remain unimplemented.
- Added C-only Actor source and multicast observer fixtures in Narrative/Test; no saved map placement or production-to-test reference.
- Validation: 217 Blueprint checks and 23 L_Test_C PIE checks passed. Expected phase/event behavior is read independently from the prepared transition table.
- [PROPUESTA] Isolated C Param names use the existing NursingRecord/FabricatedReport and OfficialCut/AuthenticRecord tokens. Evidence facts may arrive in either order. Confirm these local conventions before external integration; no new shared signature was created.
- The historical F0 requests above remain audit history. C-F0-02 is resolved only for ReportStoryEvent.Source; its other three signatures and C-F0-04 are unchanged. The five ObjectiveManager dispatchers required by C-01/C-02 are now verified.
- [Implementation and reproduction](../../Scripts/C/C01_C02_IMPLEMENTATION.md). C-03 through C-10 and the full F1 milestone remain pending.
- Branch c/f0-narrative-preparation; all changes local; no commit, push, merge, rebase, or PR.
