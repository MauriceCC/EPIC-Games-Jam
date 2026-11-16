# División B — Oposición: enemigos, IA, sigilo y Jack

> **Base confirmada:** Unscripted ? UE 5.8.4 ? Blueprint. Todo contenido para el jugador debe estar en ingl?s, incluidos placeholders visibles. Ver [arranque F0](02_ARRANQUE_F0.md). Las rutas de contenido son relativas a `Unscripted/`; `Scripts/` y `SourceData/` parten del repositorio.

**Persona:** _(nombre)_ · **Rama:** `b/<tarea>` · **Commits:** `[B] …`

## 1. Misión

Que los enemigos sean **legibles y justos**: patrullan, sospechan, persiguen, pelean de a uno o dos, telegrafían, se aturden y se neutralizan sin matar a civiles. Además, que Jack recorra su ruta de escape de forma fiable y que el sigilo sea una alternativa real.

**Fuentes de diseño:** `docs/02` (sigilo, Jack), `docs/03` (arquetipos, IA de combate, jefe), `docs/04` (efecto del Corte en enemigos), `docs/06` (IA sugerida).

## 2. Propiedad

- `Content/Unscripted/Enemies/` (incluye `Jack/`, `Animation/`, `Test/`)
- Subnivel `Maps/L_Whitechapel_AI` y `Maps/Test/L_Test_B`
- `SourceData/B/`, `Scripts/B/`, `Source/Unscripted/Enemies/` (si hay C++)
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
| `ReceiveCombatHit` del jugador (parry/esquiva) | A | `BP_TestPlayer_B` en `Enemies/Test/` que implementa `BPI_Damageable` y se mueve con WASD simple |
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
| B-06 | Persecución y combate básico: acercarse, telegrafiar (`OnTelegraphStarted`), atacar con notify → `ReceiveCombatHit` al jugador | P0 | El test player puede recibir golpes |
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

### Implementación concreta recomendada en Blueprint (sin tocar `.uasset`)

A continuación queda la guía de implementación lista para ejecutar en el editor una vez F0 esté validado. Se mantiene dentro de la división B y sigue el contrato v1.0.

#### B-01 — `BP_GuardBase`

- Variables en la clase:
  - `CurrentState` (enum `EEnemyAIState`)
  - `TargetActor` (Actor)
  - `LastKnownPlayerLocation` (Vector)
  - `AlertTimer` (float)
  - `AttackCooldown` (float)
  - `HealthComponent` (tipo `BP_HealthComponent`)
  - `PatrolRoute` (tipo `BP_PatrolRoute` o Array de Waypoints)
  - `bIsTemporalFrozen` (bool)
  - `bCanAttack` (bool)
- Eventos:
  - `BeginPlay`: obtener `HealthComponent`, bind a `OnHealthChanged` y `OnDepleted`, inicializar `CurrentState = Patrol`.
  - `Tick`: si `CurrentState == Suspicious` o `Investigate`, evaluar `AlertTimer`; si `CurrentState == Chase`, `AI Move To` a `TargetActor` o `LastKnownPlayerLocation`.
- Dispatchers:
  - `OnEnemyStateChanged(NewState)`, `OnTelegraphStarted(AttackType, Duration)`
- Nodo clave:
  - `Switch on EEnemyAIState` para entrar en cada rama. B-03 y B-06 reparten la lógica de detección y persecución.

#### B-02 — Patrulla por puntos

- Asset: `BP_PatrolRoute` (ruta editable en mapa)
- Variables:
  - `Waypoints` (Array de `Actor` o `Transform`)
  - `CurrentWaypointIndex` (int)
- Lógica:
  - En `Patrol`, `AI Move To` hacia `Waypoints[CurrentWaypointIndex]`
  - Cuando llega al waypoint: `CurrentWaypointIndex = (CurrentWaypointIndex + 1) % Waypoints.Num()`
  - Si el actor es un `BP_GuardBase` y detecta al jugador, `CurrentState = Suspicious`
- Para editar en editor:
  - añadir `BP_PatrolRoute` como actor de mundo y mover 2–3 puntos de ruta; no se requiere abrir el Blueprint.

#### B-03 — Percepción

- Tipo de detección:
  - `Cone Trace` (ángulo 90–110°) + `Distance` + `Line of Sight`
  - Si no hay trazado complejo, `AI Perception` con un `PerceptionComponent` local
- Variables de percepciones:
  - `VisionRange`
  - `DetectionRange`
  - `SightAngle`
  - `bPlayerHidden`
  - `StealthMultiplier`
- Regla de decisión:
  - `Distance < (VisionRange * VisibilityMultiplier)`
  - `Angle <= SightAngle`
  - `LineTraceSingleByChannel` a `Visibility` o `Pawn` sin obstáculos
- Si el jugador está agachado o escondido, aplicar `BP_StealthComponent.GetVisibilityMultiplier()` al rango.
- En `DetectionReachesThreshold`, `CurrentState = Investigate` y `LastKnownPlayerLocation = PlayerLocation`.

#### B-04 — Sospecha → investigar → Return

- `Suspicious`:
  - set `TargetActor = Player`
  - reiniciar `AlertTimer` y disparar `OnEnemyStateChanged`
- `Investigate`:
  - `AI Move To` a `LastKnownPlayerLocation`
  - si el enemigo llega a la posición y no hay visión, `CurrentState = Return`
- `Return`:
  - volver a la ruta del waypoint previo o al punto original
  - si el jugador reaparece o sale de rango, `CurrentState = Patrol`

#### B-05 — `BP_StealthComponent`

- En `BP_PlayerCharacter` o un componente del jugador, con variables:
  - `DetectionLevel` (0–1)
  - `Crouched` (bool)
  - `Hidden` (bool)
  - `DetectedBy` (Array de Actor)
- Funciones del contrato:
  - `SetCrouched(bool)`
  - `SetHidden(bool)`
  - `GetVisibilityMultiplier() -> float`
  - `ReportDetection(Enemy, Level)`
- Lógica:
  - Acumular detección por enemigo + duración del tiempo observado
  - Resolver en `OnDetectionChanged(Level)` para HUD y narativa
  - Reducir `DetectionLevel` si se oculta o se mueve fuera del cono

#### B-06 — Persecución y combate básico

- Transición de `Investigate` a `Chase`:
  - si el jugador sigue visible o la última posición es reciente, mover más rápido y emitir `OnEnemyStateChanged(Chase)`
- En `Combat`:
  - para `BP_Pursuer` y `BP_Interventor`, mantener distancia y preparar telegráfica
- Telegrafía:
  - `OnTelegraphStarted(AttackType, Duration)`
  - disparar al inicio del ataque para que la cámara/VFX lo muestren
- Cuando ataque entra en rango:
  - `Get World Location` del jugador, `Get Actor Forward Vector`, `Line Trace`/`Sphere` a la zona de ataque
  - `ApplyDamage` usando `ReceiveHit` del jugador con `ST_HitInfo`

#### B-07 — Reacción a `EHitResult`

- Si `HitResult == Parried`:
  - activar `Stunned`
  - incrementar `PostureDamage` o aplicar stagger
  - `Set Actor Rotation` para reaccionar hacia el atacante
- Si `HitResult == Blocked`:
  - reducir el daño, mantener `Combat`, no entrar en stagger completo
- Si `HitResult == Dodged`:
  - cancelar ataque, reubicar y mantener `Chase`

#### B-08 — Daño, postura, aturdimiento, remate

- Variables:
  - `CurrentHealth`, `CurrentPosture`
  - `MaxPosture`
  - `StunTimer`
- Reglas:
  - daño > `PostureThreshold` => `CurrentState = Stunned`
  - `CanInteract` devuelve true cuando la unidad está aturdida y el interactor es jugador
  - `Interact` del enemigo llama `RequestFinisher(self)` y aplica `ST_HitInfo` con `AttackType = Finisher`, `bNonLethal = true` para civiles

#### B-09 — `ApplyTemporalFreeze`

- En `BPI_TimeAffectable`:
  - `ApplyTemporalFreeze(Duration, PostureDamage) -> float`
  - si `CanBeTemporalCutTarget == true`, guardar velocidad y animación actual
  - congelar `AI Move To`, `CharacterMovementComponent` y animación
  - usar `M_TemporalFrozen_Overlay` como overlay de material
  - al terminar, reactivar y restaurar el estado previo
- Evitar un estado bloqueado fijo: si el enemigo ya no debe atacar, reanudar `Combat` o `Return`

#### B-10 — Neutralización no letal

- En `BP_GuardBase` o `BP_Jack`, si `ReceiveHit` llega con daño letal pero el enemigo es civil o no agresor:
  - set `CurrentState = Defeated`
  - desactivar el combate
  - `ReportStoryEvent(EnemyNeutralized, self, EncounterName)`
  - poner al actor en posición de inconsciencia mediante animación o `SetActorEnableCollision(false)` si es de pruebas

#### B-11 — Coordinador de ataques

- Variables:
  - `ActiveAttackers` (Array de Actor)
  - `MaxSimultaneousAttackers` = 1 o 2 según el tipo
- Regla:
  - si `ActiveAttackers.Num() >= MaxSimultaneousAttackers`, los demás se quedan en `Chase` o `Flank`
  - flanqueo: usando waypoint de borde o posición lateral al jugador

#### B-12 — `BP_Pursuer`

- En la subclase de `BP_GuardBase`:
  - `Health = 45`
  - `AttackDamage = 12`
  - `WalkSpeed = 130`, `RunSpeed = 240`
  - `bShouldFlank = true` cuando el jugador está en cobertura
- Añadir `BP_Pursuer` en `Content/Unscripted/Enemies/`

#### B-13 — `DT_EnemyBalance` y data-driven config

- Fichero base:
  - [`SourceData/B/DT_EnemyBalance.csv`](../../SourceData/B/DT_EnemyBalance.csv)
- Fichero de runtime:
  - [`SourceData/B/EnemyAIStateMachine.json`](../../SourceData/B/EnemyAIStateMachine.json)
- Uso recomendado:
  - crear una DataTable en el editor con columnas `Name`, `Health`, etc.
  - leer todos los valores desde `DT_EnemyBalance` y no hardcodear números en nodos.

#### B-14 — `BP_Jack`

- Variables:
  - `Waypoints` (Array de `BP_JackWaypoint`)
  - `CurrentWaypointIndex`
  - `bReachedRefuge`
- Lógica:
  - estado inicial = `Patrol` idle asustado
  - si la zona está despejada y `OnStoryPhaseChanged` llega a `ProtectJack`, `BP_Jack` se mueve por la ruta
  - si `Interact` del jugador: `ReportStoryEvent(JackFound)`
  - al llegar al último waypoint: `ReportStoryEvent(JackReachedRefuge)`
- Asegurar condiciones de camino y no hacer IA general; el movimiento debe estar basado en puntos de ruta predefinidos.

### Validación de implementación recomendada en `L_Test_B`

1. Añadir un `PlayerStart` en `L_Test_B`.
2. Colocar 3 instancias de `BP_Pursuer` y 1 de `BP_Jack`.
3. Crear un `BP_TestPlayer_B` con movimiento básico WASD y `BPI_Damageable`.
4. Conectar un `BP_PatrolRoute` con 3 waypoints.
5. Probar:
   - patrulla sin detectar
   - detección del jugador desde el cono de visión
   - sospecha e investigación por última posición
   - persecución con velocidad alta
   - parry y stagger del jugador
   - corte temporal aplicado a perseguidores
   - remate sobre enemigo aturdido
   - paso de Jack a refugio

## 6. Decisiones abiertas de la división

- ¿Al reaparecer en checkpoint los enemigos de la sección reviven o siguen neutralizados? *(propuesta: los neutralizados siguen fuera; los heridos recuperan salud)*.
- ¿La pelea con el Interventor es opcional (`docs/01` la llama «opcional») u obligatoria (`docs/05` la pone en el tramo al refugio)? — decidir con C.
- ¿Ser detectado en una zona de sigilo inicia combate o es fallo inmediato? *(propuesta: inicia combate, coherente con la versión de combate)*.

## 7. Prompt de arranque para tu agente

```text
Trabajo en la División B (Oposición: enemigos, IA, sigilo y Jack) del proyecto Unscripted (UE 5.8.4, Blueprint).
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/B_ENEMIGOS_IA_SIGILO.md y después docs/02, docs/03, docs/04 y docs/06.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: solo puedo modificar Content/Unscripted/Enemies/, Maps/L_Whitechapel_AI, Maps/Test/L_Test_B,
SourceData/B/, Scripts/B/ y mi archivo de división. Respeta exactamente las firmas del contrato v<versión>.
Entrégame: (1) los pasos para construirlo en Blueprint, nodo a nodo, indicando en qué asset va cada cosa;
(2) los datos de DataTable en CSV si aplica; (3) cómo probarlo en L_Test_B con mis dobles de prueba;
(4) si necesitas algo fuera de mis carpetas, redáctalo como solicitud de contrato y no lo implementes.
```

## 8. Solicitudes de contrato

| # | Fecha | Petición | A quién | Estado |
|---|---|---|---|---|
| B-CON-01 | 2026-11-14 | Corregir `Source` de `ReportStoryEvent` para que sea una referencia a `Actor`, como exige el contrato. La firma combinada de `BP_GameState` expone `Actor Action Utility` y rechaza los Pawns de B. Verificar el pin tanto en `BPI_StoryEvents` como en su implementación. | C / Integración | Pendiente |

## 9. Estado

### Prioridad de integración de B

Este trabajo corresponde a Jesús (división B). Al integrar en `main`, conserven
estos cambios de `L_Whitechapel`:

- `BP_GuardBase`: los enemigos persiguen al jugador visible mientras se genera
  el NavMesh. El checkpoint invalida los ataques pendientes.
- `BP_Jack`: durante la escolta usa el límite de velocidad actual del
  protagonista y puede seguirlo a la vista mientras se genera el NavMesh.
- `BP_GuardBase` y `BP_PlayerCharacter`: se mantienen las cinco animaciones de
  muerte aportadas por el equipo en `c58a9e6`.

Si hay conflicto en alguno de estos Blueprints binarios, usen como base la
versión integrada de `main` y reapliquen encima los cambios compatibles.
Coordinen con Jesús antes de sustituir el asset y prueben en Play la
persecución, la escolta y el checkpoint.


### Caídas articuladas — 2026-11-15

Autorización puntual de integración A/B. **[PROPUESTA]** Se sustituye el giro
rígido de muerte por clips adaptados a Perseguidor A/B, Interventor y Supervisor.
Se conserva la neutralización no letal y la pose final, incluso tras atacar,
congelarse o quedar aturdido. Detalles, pruebas y límites en
[`Scripts/A/DEATH_PRESENTATION.md`](../../Scripts/A/DEATH_PRESENTATION.md).

### Ataques animados — 2026-11-15

Autorización puntual del usuario para A y B. **[PROPUESTA]** `BP_GuardBase` reproduce un golpe adaptado a la malla de Perseguidor A/B, Interventor o Supervisor al comenzar la telegráfica. El contacto se sincroniza con `B_WindupSeconds`; interrupciones por congelación, aturdimiento y caída liberan la reproducción pendiente. Clips propios en `Enemies/Animation/Polish/`, sin modificar originales de D, contratos, daño ni mapas. Implementación y límites: [`Scripts/A/ANIMATION_POLISH.md`](../../Scripts/A/ANIMATION_POLISH.md). Compilación y compatibilidad verificadas; valoración visual integrada pendiente. No declara B-23 ni F4 cerrados por la sola existencia de clips.

**Git LFS (2026-11-14):** se liberó el bloqueo de `L_Whitechapel.umap`. La consulta posterior a `origin` confirmó que el repositorio no tenía bloqueos activos. D/Integración puede volver a bloquear el mapa persistente cuando vaya a editarlo.

### Revisión documental 2026-11-14 (`main` @ `4afcd57`)

La prueba descrita abajo procede de la revisión de B; ahora el checkout revisado es `main`. Se conservan sus resultados como pruebas reportadas, pendientes de repetición después de los merges. Existen CSV, scripts y assets; no se localizó `DT_EnemyBalance.uasset`, por lo que B-13 no se cierra solo con valores aplicados a los Blueprints.

**[PROPUESTA] Prioridad inmediata:** resolver B-CON-01 con INT/C y enlazar las interfaces de GuardBase/Jack con la lógica local existente. Después repetir el mínimo F1 con tres perseguidores y Jack 10/10; validar con A parry/Corte/remate y con C eventos/checkpoint. Jefe, hostilidad narrativa del Interventor y ruta real de Jack siguen pendientes según el reporte de B. Ver [informe conjunto](03_ESTADO_Y_SIGUIENTES_PASOS.md).

### Auditoría de integración (2026-11-14)

Verificación posterior con UnrealEditor-Cmd, sin guardar mapas: L_Whitechapel_AI y L_Whitechapel solo contienen 2 Perseguidores y 1 ruta de B, cerca del origen y fuera de la Plaza propuesta por D. Jack solo está en L_Test_B. Faltan colocación de Jack/ruta real, patrullas de Callejón/Patio, 3 Perseguidores del Paso central, Interventor y Supervisor. Evidencia: `SourceData/B/placement_audit.json`. Carga terminada con 0 errores y warning de RecastNavMesh; no equivale a Play validado.

**No cerrado para entrega.** Ver [auditoría y criterios de cierre](../../Scripts/B/AUDITORIA_INTEGRACION.md). Revisión estática: validadores CSV/JSON pasan, pero no equivalen a validación de Blueprints. No se ejecutó Play en esta revisión (editor cerrado). Siguen pendientes interfaces, remate, eventos/fases narrativos, Supervisor completo, encuentros/ruta real de Jack, balance conectado y pruebas integradas. B-CON-01 continúa pendiente de verificación/corrección por C/integración. No se modificaron contratos ni assets ajenos.

### Prueba actual de B

En el checkout `codex/unscripted-integration`, abrir `/Game/Unscripted/Maps/Test/L_Test_B` y elegir **Play** en el visor. El mapa usa el controlador Top Down y una cámara ortográfica isométrica fija. **[PROPUESTA]** El jugador de prueba de B usa clic izquierdo para moverse, Espacio para el golpe de corto alcance, F para congelar al primer Perseguidor durante dos segundos, Ctrl izquierdo para activar el multiplicador de sigilo y E cerca de Jack para iniciar los tres puntos del refugio.

Se comprobó en Play la cámara activa, el daño nativo, la neutralización, el máximo de dos ataques simultáneos, el aturdimiento y su recuperación, el recorrido de Jack y la restauración local de un Perseguidor herido. La decisión de prueba para checkpoints conserva las unidades neutralizadas y los objetivos completados. La copia combinada añade sospecha e investigación de la última posición, el efecto de aviso de D al preparar un ataque y la pausa visual del Corte.

Las funciones de B están en sus propios Blueprints. Sigue pendiente asignar y cablear `BPI_Damageable`, `BPI_TimeAffectable`, `BPI_Interactable` y `BPI_CheckpointListener` en `BP_GuardBase`. Los grafos locales con nombres que coinciden con una función de interfaz deben migrarse antes de asignarla. `B_ReceiveCombatHit` y `B_ResetAtCheckpoint` contienen la lógica local que deben invocar las implementaciones. Jack tiene `B_StartEscape` y `B_ResetAtCheckpoint`; falta enlazarlos con la fase, la interacción y los eventos de historia. Quedan pendientes el encuentro completo del Supervisor, el disparo narrativo del Interventor y la ruta real de Jack en Whitechapel.

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte B) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

### Estado actual de preparación (2026-11-14)

- [x] Se revisó el inventario actual del proyecto y los assets B existentes (`BP_GuardBase`, `BP_Pursuer`, `BP_Interventor`, `BP_Supervisor`, `BP_Jack`, `BP_StealthComponent`).
- [x] Se preparó la base de datos de balance B en texto: [`SourceData/B/DT_EnemyBalance.csv`](../../SourceData/B/DT_EnemyBalance.csv).
- [x] Se añadió la validación de balance en [`Scripts/B/b_enemy_balance.py`](../../Scripts/B/b_enemy_balance.py).
- [x] Se estructuró y validó la máquina de estados de IA en [`SourceData/B/EnemyAIStateMachine.json`](../../SourceData/B/EnemyAIStateMachine.json) y [`Scripts/B/b_ai_machine.py`](../../Scripts/B/b_ai_machine.py).
- [x] Se creó y compiló `BP_PatrolRoute` en `Content/Unscripted/Enemies/` con soporte de waypoints editables 3D.
- [x] Se crearon y asignaron todas las variables de contrato y balance en `BP_GuardBase`, `BP_Pursuer`, `BP_Interventor`, `BP_Supervisor`, `BP_Jack` y `BP_StealthComponent`.
- [x] Se programó y compiló el grafo de lógica de `BP_StealthComponent` (`SetCrouched`, `SetHidden`, `GetVisibilityMultiplier` con ramificaciones de retorno y `ReportDetection`).
- [x] Se pobló y guardó `Maps/Test/L_Test_B` con la ruta de patrulla, 2 Perseguidores y Jack configurado.
- [x] Se pobló y guardó `Maps/L_Whitechapel_AI` con el encuentro de patrulla del Acto I (plaza con 2 Perseguidores).
- [x] Se redactó la guía completa nodo a nodo de Blueprint para todos los assets de B en [`Scripts/B/B_GUIA_BLUEPRINT.md`](../../Scripts/B/B_GUIA_BLUEPRINT.md).

Notas del día:
La división B ha sido implementada directamente en el editor de Unreal Engine 5.8.4 mediante la pasarela de automatización: variables creadas, grafos de funciones de sigilo cableados y compilados, balance aplicado a los CDO y actores colocados en los niveles `L_Test_B` y `L_Whitechapel_AI`.
