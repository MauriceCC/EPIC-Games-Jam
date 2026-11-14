# División B — Oposición: enemigos, IA, sigilo y Jack

**Persona:** _(nombre)_ · **Rama:** `b/<tarea>` · **Commits:** `[B] …`

## 1. Misión

Que los enemigos sean **legibles y justos**: patrullan, sospechan, persiguen, pelean de a uno o dos, telegrafían, se aturden y se neutralizan sin matar a civiles. Además, que Jack recorra su ruta de escape de forma fiable y que el sigilo sea una alternativa real.

**Fuentes de diseño:** `docs/02` (sigilo, Jack), `docs/03` (arquetipos, IA de combate, jefe), `docs/04` (efecto del Corte en enemigos), `docs/06` (IA sugerida).

## 2. Propiedad

- `Content/CorteFinal/Enemies/` (incluye `Jack/`, `Animation/`, `Test/`)
- Subnivel `Maps/L_Whitechapel_AI` y `Maps/Test/L_Test_B`
- `SourceData/B/`, `Scripts/B/`, `Source/CorteFinal/Enemies/` (si hay C++)
- Este archivo.

**No tocas:** `Core/`, jugador, HUD, interactuables de C, geometría del nivel.

## 3. Lo que provees y lo que consumes

| Provees | A quién |
|---|---|
| `BP_GuardBase` (+ derivados) implementando `BPI_Damageable`, `BPI_TimeAffectable`, `BPI_Interactable` (remate), `BPI_CheckpointListener` | A, C |
| `BP_StealthComponent` (en el jugador): detección agregada, `OnDetectionChanged`, `SetCrouched`, `SetHidden` | A, C |
| `BP_Jack` con `BPI_Interactable` y `BPI_CheckpointListener` | C |
| `ReportStoryEvent`: `EnemyNeutralized`, `JackReachedRefuge`, `JackFound`, `InterventorTurnedHostile`, `SupervisorEncounterStarted`, `SupervisorDefeated` | C |
| Dispatchers `OnEnemyStateChanged`, `OnTelegraphStarted` | D (audio/VFX) |

| Consumes | De quién | Mientras no exista… |
|---|---|---|
| `ReceiveHit` del jugador (parry/esquiva) | A | `BP_TestPlayer_B` en `Enemies/Test/` que implementa `BPI_Damageable` y se mueve con WASD simple |
| `BP_HealthComponent` | A | Existe desde F0 (cascarón); si A aún no lo terminó, usa una variable local temporal |
| `RequestFinisher` | A | Print en test |
| `OnStoryPhaseChanged`, `OnDialogueFinished` | C | Un actor de prueba que dispare las fases con teclas numéricas |
| Geometría y NavMesh de `L_Whitechapel` | D | `L_Test_B` con suelo, cajas y NavMesh propios |

## 4. Backlog

### F1 — Sistemas aislados en `L_Test_B`

| ID | Tarea | Prioridad | Criterio de aceptación |
|---|---|---|---|
| B-01 | `BP_GuardBase`: `BP_HealthComponent`, postura, `EEnemyAIState`, dispatchers | P0 | Cambios de estado visibles con debug text sobre la cabeza |
| B-02 | Patrulla por 2–3 puntos (`BP_PatrolRoute` editable en el mapa) | P0 | Ruta editable moviendo puntos sin abrir el BP |
| B-03 | Percepción: cono de visión + distancia + line trace (o AI Perception) con multiplicador de `BP_StealthComponent` | P0 | Cajas bloquean visión; agacharse reduce distancia |
| B-04 | Sospecha → investigar última posición → Return | P0 | |
| B-05 | `BP_StealthComponent`: agregar `ReportDetection` de varios enemigos, `OnDetectionChanged`, escondido = invisible | P0 | Barra de prueba sube/baja |
| B-06 | Persecución y combate básico: acercarse, telegrafiar (`OnTelegraphStarted`), atacar con notify → `ReceiveHit` al jugador | P0 | El test player puede recibir golpes |
| B-07 | Reacción a `EHitResult`: `Parried` → stagger + postura; `Blocked`/`Dodged` | P0 | |
| B-08 | Recepción de golpes: daño, postura, umbral → `Stunned` → `CanInteract` true para remate | P0 | |
| B-09 | `ApplyTemporalFreeze`: congelar movimiento + animación, overlay `M_TemporalFrozen_Overlay`, restaurar estado previo | P0 | Tras el Corte, el enemigo retoma exactamente lo que hacía (o queda en Combat) sin quedarse bloqueado |
| B-10 | Neutralización no letal + `ReportStoryEvent(EnemyNeutralized)` | P0 | Civiles quedan en el suelo, no "mueren" |
| B-11 | Coordinador de ataques (tokens): máx. 1–2 atacantes simultáneos, el resto rodea | P0 | Con 3 enemigos nunca atacan los 3 a la vez |
| B-12 | `BP_Pursuer` (salud 45, golpes lentos) | P0 | |
| B-13 | `DT_EnemyBalance` + CSV en `SourceData/B/` | P0 | Balance sin tocar nodos |
| B-14 | `BP_Jack`: idle asustado, `Interact` → `JackFound`, avance por `BP_JackWaypoint` cuando el tramo está despejado | P0 | Llega al refugio de forma fiable 10/10 veces |

**Mínimo F1 (hito):** en `L_Test_B`, 3 Perseguidores patrullan, detectan, pelean por turnos, se pueden congelar y neutralizar; Jack recorre una ruta de prueba.

### F2 — Vertical slice

| ID | Tarea | Prioridad | Criterio |
|---|---|---|---|
| B-20 | Colocar patrullas del Acto I en `L_Whitechapel_AI` sobre el blockout de D | P0 | 2 Perseguidores en la plaza |
| B-21 | Integrar con el jugador real de A (parry, Corte, remate) | P0 | Pelea completa con A |
| B-22 | `OnCheckpointRestore` para enemigos y Jack (decidir qué se reinicia) | P0 | |
| B-23 | Animaciones reales de enemigos (retarget desde las de A si comparten esqueleto) | P1 | |

### F3 — Contenido

| ID | Tarea | Prioridad |
|---|---|---|
| B-30 | `BP_Interventor` (salud 80, bloquea ligeros, ataque cargado; aliado → hostil con `Correction_Order`) | P0 |
| B-31 | `BP_Supervisor` jefe (salud 180, ataque simple, circular, desplazamiento temporal corto, resistencia al Corte) | P0 |
| B-32 | Encuentros de todas las zonas (`docs/05` tabla de encuentros) en `L_Whitechapel_AI` | P0 |
| B-33 | Ruta completa de Jack taller → refugio en el nivel real | P0 |
| B-34 | Fase 2 del Supervisor (~50 %): repetir ataque desde otra posición | P2 |

### F4 — Pulido

Balance, legibilidad de telegráficas desde la cámara isométrica, bugs de IA atascada.

## 5. Notas técnicas

- **Behavior Tree o máquina de estados en Blueprint:** para una jam, una máquina de estados con `Switch on EEnemyAIState` + `AI Move To` suele ser más rápida de depurar. Decidir en F1 y no mezclar.
- **Congelar sin perder estado:** guardar velocidad de animación/movimiento y estado previo antes de congelar; restaurar en un `Timer`. Cuidado con `AI Move To` en curso: detener y reemitir.
- Las heridas **persisten** con la Retoma del jugador (A no te avisa: no hay nada que hacer).
- Jack **no** es un compañero con IA general: puntos predefinidos y condiciones de "tramo despejado".
- Puertas de C que cambian el NavMesh: probar en F2 juntos.

## 6. Decisiones abiertas de la división

- ¿Al reaparecer en checkpoint los enemigos de la sección reviven o siguen neutralizados? *(propuesta: los neutralizados siguen fuera; los heridos recuperan salud)*.
- ¿La pelea con el Interventor es opcional (`docs/01` la llama «opcional») u obligatoria (`docs/05` la pone en el tramo al refugio)? — decidir con C.
- ¿Ser detectado en una zona de sigilo inicia combate o es fallo inmediato? *(propuesta: inicia combate, coherente con la versión de combate)*.

## 7. Prompt de arranque para tu agente

```text
Trabajo en la División B (Oposición: enemigos, IA, sigilo y Jack) del proyecto CORTE FINAL (UE5).
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/B_ENEMIGOS_IA_SIGILO.md y después docs/02, docs/03, docs/04 y docs/06.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: solo puedo modificar Content/CorteFinal/Enemies/, Maps/L_Whitechapel_AI, Maps/Test/L_Test_B,
SourceData/B/, Scripts/B/ y mi archivo de división. Respeta exactamente las firmas del contrato v<versión>.
Entrégame: (1) los pasos para construirlo en Blueprint, nodo a nodo, indicando en qué asset va cada cosa;
(2) los datos de DataTable en CSV si aplica; (3) cómo probarlo en L_Test_B con mis dobles de prueba;
(4) si necesitas algo fuera de mis carpetas, redáctalo como solicitud de contrato y no lo implementes.
```

## 8. Solicitudes de contrato

| # | Fecha | Petición | A quién | Estado |
|---|---|---|---|---|
| | | | | |

## 9. Estado

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte B) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

Notas del día:
