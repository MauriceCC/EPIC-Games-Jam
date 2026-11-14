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

## 5. Tabla de transiciones de fase (rellenar en C-02)

| Fase actual | Evento(s) requerido(s) | Fase siguiente | Efectos (checklist, diálogo, bloqueos) |
|---|---|---|---|
| FindJack | `JackFound` | OpenEscapeRoute | Diálogo de Jack; mensaje del yo futuro |
| OpenEscapeRoute | `EscapeRouteOpened` | ProtectJack | |
| ProtectJack | `JackReachedRefuge` | DiscoverTruth | |
| DiscoverTruth | `EvidenceCollected` x2 → `TruthRevealed` | FinalChoice | Revelación del Supervisor; **reescritura del checklist**; `Correction_Order` |
| FinalChoice | `SupervisorDefeated` habilita expedientes; `FinalDocumentRegistered` | GameEnded | Bloquear Retoma; final A o B |

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
| | | | | |

## 10. Estado

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte C) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

Notas del día:
