# 01 — Contratos entre divisiones y propiedad de archivos

> **Versión del contrato: v1.0 (borrador hasta el fin de la Fase 0).**  
> Este documento es la **fuente de verdad** de todo lo que cruza la frontera entre divisiones. Los nombres de `docs/06_UNREAL_ENGINE_5.md` son la base; donde difieran, **manda este archivo**.  
> Dueño del documento: **Integrador**. Cambios: ver `00_PLAN_GENERAL.md §7`. Registrar cada cambio en el historial del final.

## 1. Principio de diseño

Las divisiones **no se llaman por clase concreta** salvo para la jerarquía propia. Se comunican con:

- **Interfaces** (`BPI_*`) en `Core/`: "hazme esto" sin saber qué clase eres.
- **Event Dispatchers** declarados en los componentes: "avísame cuando pase esto".
- **`ReportStoryEvent`** hacia el `BP_GameState`: todo hecho con significado narrativo pasa por ahí.
- **Enums y structs** en `Core/`: el vocabulario común.

Así, A puede rehacer su combate entero, o B su IA, sin que C o D tengan que abrir sus assets.

## 2. Propiedad de carpetas y archivos

Raíz de contenido documentada: `Content/Unscripted/`, relativa al proyecto `Unscripted/`; ruta desde el repositorio: `Unscripted/Content/Unscripted/` y ruta en el editor: `/Game/Unscripted/`. Nombre interno unificado con el título definitivo por autorización explícita del usuario el 2026-11-14. Esta actualización del borrador reemplaza las rutas provisionales anteriores; no cambia propietarios ni firmas.

`Config/`, `Plugins/` y el eventual `Source/` son relativos a `Unscripted/`. `docs/`, `Scripts/` y `SourceData/` son relativos al repositorio. Los comandos Git se ejecutan desde la raíz del repositorio con la ruta completa. El proyecto es Blueprint; las rutas de C++ son reservas condicionales, no módulos existentes.

**Idioma:** todas las salidas al jugador, incluidos `Text` de interfaces y DataTables, deben estar en inglés. Los ejemplos españoles de este contrato explican la intención; no son textos de publicación. No se cambian firmas ni enums por traducir textos de presentación.

| Ruta | Dueño | Contenido |
|---|---|---|
| `Core/Enums/`, `Core/Structs/`, `Core/Interfaces/` | **Integrador** | Contratos de §3–§4. Congelados tras F0 |
| `Player/` | **A** | `BP_PlayerCharacter`, `BP_PlayerController`, componentes de combate, salud, temporal; `ST_RewindSnapshot`; `DT_PlayerBalance` |
| `Player/Input/` | **A** | `IA_*`, `IMC_Default` |
| `Player/Animation/` | **A** | ABP, montages y notifies del agente |
| `Enemies/` | **B** | `BP_GuardBase` y derivados, `BP_StealthComponent`, `BP_PatrolRoute`, coordinador de ataques, `DT_EnemyBalance` |
| `Enemies/Jack/` | **B** | `BP_Jack`, `BP_JackWaypoint` |
| `Enemies/Animation/` | **B** | ABP y montages de enemigos y Jack |
| `Narrative/` | **C** | `BP_GameMode`, `BP_GameState`, `BP_ObjectiveManager`, `BP_InteractionComponent`, interactuables, checkpoints, triggers, `DT_Dialogue`, `DT_Checklist` |
| `UI/` | **C** | `BP_HUD`, `WBP_*` |
| `World/` | **D** | Props y Blueprints de entorno, oclusión de cámara, `BP_CameraRig` si se separa |
| `Art/`, `Materials/`, `VFX/`, `Audio/` | **D** | Mallas, texturas, materiales, Niagara, SoundCues/MetaSounds |
| `Maps/L_Whitechapel` (persistente) | **D** (lock LFS) | Solo contiene subniveles, NavMeshBoundsVolume, PostProcess, luz global |
| `Maps/` subniveles | Ver §6 | Uno por división |
| `Maps/Test/L_Test_A`… `L_Test_D` | Cada división el suyo | Pruebas aisladas |
| `<Carpeta propia>/Test/` | Cada división | Dobles de prueba (muñecos, jugador falso) |
| `Content/Developers/` | Personal | **Ignorado por Git**. Borradores |

Archivos de texto del repositorio:

| Ruta | Dueño |
|---|---|
| `Config/*.ini`, `Unscripted.uproject`, `Plugins/` (dentro de `Unscripted/`) | Integrador |
| `Source/Unscripted/Player/` · `Enemies/` · `Narrative/` · `World/` (si D0.2 = C++) | A · B · C · D |
| `SourceData/A/` … `SourceData/D/` (CSV/JSON fuente de DataTables) | Cada división |
| `Scripts/A/` … `Scripts/D/`, `Scripts/INT/` (Python del editor) | Cada división / integrador |
| `docs/0*.md` (diseño) | Todos, **solo vía PR revisado** por el dueño del área (tabla de `AGENTS.md`) |
| `docs/plan/00_*`, `docs/plan/01_*`, `AGENTS.md`, `README.md` | Integrador |
| `docs/plan/A_*` … `D_*` | Cada división el suyo |
| `CREDITS.md` | D |

**Regla:** se pueden *referenciar* assets ajenos (por ejemplo, A hace `Spawn System` del Niagara `NS_TemporalCut` de D), pero **no guardarlos**.

## 3. Enums y structs (`Core/`)

> Añadir valores **solo al final**. No reordenar ni renombrar.

```text
ECombatState        Idle, Attacking, Dodging, Parrying, Stunned, TemporalFrozen, Rewinding, Defeated
EEnemyAIState       Patrol, Suspicious, Chase, Combat, Return, Stunned, Defeated
EAttackType         Light1, Light2, Light3, Heavy, Finisher, Stealth, EnemyBasic, EnemyCharged, EnemySweep, EnemyTemporal
EHitResult          Hit, Blocked, Parried, Dodged, Ignored
EStoryPhase         FindJack, OpenEscapeRoute, ProtectJack, DiscoverTruth, FinalChoice, GameEnded
EStoryEvent         JackFound, EscapeRouteOpened, JackReachedRefuge, EvidenceCollected, TruthRevealed,
                    InterventorTurnedHostile, SupervisorDefeated,
                    FinalDocumentRegistered, EnemyNeutralized, PlayerDefeated, CheckpointReached,
                    ContinuityAltered, FutureMessageRead, SupervisorEncounterStarted
EEvidenceType       NursingRecord, FabricatedReport
EEndingType         None, OfficialCut, AuthenticRecord
ESpeaker            Agent, Jack, Supervisor, Director, FutureSelf, Interventor, System
```

```text
ST_HitInfo
  Damage            float
  PostureDamage     float
  AttackType        EAttackType
  Instigator        Actor
  HitLocation       Vector
  HitDirection      Vector     (normalizado, del atacante al objetivo)
  bParryable        bool
  bNonLethal        bool       (true por defecto en ataques del jugador a civiles)

ST_DialogueLine     (fila de DT_Dialogue, dueño de datos: C)
  Speaker           ESpeaker
  Text              Text
  Duration          float      (0 = esperar input)
  NextRow           Name       (None = fin)

ST_ChecklistRow     (fila de DT_Checklist, dueño de datos: C)
  Phase             EStoryPhase
  Items             Array<Text>
  CompletedMask     Array<bool>
  bIsRewritten      bool       (estilo "!" de la versión reescrita)
```

`ST_RewindSnapshot` **no** es contrato: es interno de A (`Player/`).

## 4. Interfaces (`Core/Interfaces/`)

### `BPI_Damageable` — implementan: `BP_PlayerCharacter` (A), `BP_GuardBase` (B), dobles de prueba

**Corrección aprobada A-CON-01 (2026-11-14):** usar `ReceiveCombatHit`, nunca el nombre anterior `ReceiveHit`, que colisiona con el evento nativo de Actor mostrado como `Hit` (incluye `MyComp`). La entrada sigue siendo `HitInfo: ST_HitInfo` y la salida se denomina `Result: EHitResult`. Migrar también llamadas e implementaciones de A/B ya creadas en el editor; no modificar el evento nativo de colisión. Ver [guía de migración](../../Scripts/INT/A_CON_01_RECEIVE_COMBAT_HIT.md).

| Función | Firma | Notas |
|---|---|---|
| `ReceiveCombatHit` | `(HitInfo: ST_HitInfo) → EHitResult` | El **receptor** decide: esquiva activa → `Dodged`; parry en ventana → `Parried`; bloqueo → `Blocked`. El atacante reacciona al resultado (p. ej. B entra en stagger si recibe `Parried`) |
| `IsDefeated` | `() → bool` | |

### `BPI_TimeAffectable` — implementan: `BP_GuardBase` (B), dobles de prueba

| Función | Firma | Notas |
|---|---|---|
| `CanBeTemporalCutTarget` | `() → bool` | false si derrotado, ya congelado o inmune |
| `ApplyTemporalFreeze` | `(Duration: float, PostureDamage: float) → float` | Devuelve la duración **efectiva** aplicada (el Supervisor la reduce; 0 = resistido) |

### `BPI_Interactable` — implementan: interactuables de C, `BP_Jack` (B), `BP_GuardBase` aturdido (B, para remate)

| Función | Firma | Notas |
|---|---|---|
| `CanInteract` | `(Interactor: Actor) → bool` | |
| `GetInteractionText` | `(Interactor: Actor) → Text` | Ej. «Interactuar», «Rematar», «Registrar expediente» |
| `GetInteractionPriority` | `() → int` | Remate 100 · Expediente final 90 · Hablar 60 · Evidencia 50 · Puerta 40 · Escondite 30 |
| `Interact` | `(Interactor: Actor) → void` | |

### `BPI_PlayerControl` — implementa: `BP_PlayerCharacter` (A). Lo llaman C y B

| Función | Firma | Quién la llama |
|---|---|---|
| `SetGameplayInputEnabled` | `(bEnabled: bool)` | C (diálogos, final) |
| `SetRetakeBlocked` | `(bBlocked: bool)` | C (diálogos, registro final) |
| `ClearRetakeHistory` | `()` | C (tras eventos irreversibles) |
| `RequestFinisher` | `(Target: Actor)` | B (desde `Interact` del enemigo aturdido) |
| `GetStealthComponent` | `() → BP_StealthComponent` | B, C |

### `BPI_StoryEvents` — implementa: `BP_GameState` (C). Lo llaman todos

| Función | Firma | Notas |
|---|---|---|
| `ReportStoryEvent` | `(Event: EStoryEvent, Source: Actor, Param: Name)` | `Param` opcional: tipo de evidencia, id de checkpoint, etc. |
| `GetCurrentPhase` | `() → EStoryPhase` | |
| `GetObjectiveManager` | `() → BP_ObjectiveManager` | Para enlazar dispatchers |

Uso estándar desde cualquier Blueprint: `Get Game State → ReportStoryEvent (mensaje de interfaz)`.

### `BPI_CheckpointListener` — implementan: `BP_PlayerCharacter` (A), `BP_GuardBase` (B), `BP_Jack` (B)

| Función | Firma | Notas |
|---|---|---|
| `OnCheckpointRestore` | `(CheckpointId: Name, RespawnTransform: Transform)` | Jugador: reaparece, recupera 2 cargas de Retoma y la salud que diga el balance. Enemigos de la sección: vuelven a su estado inicial si B lo decide |

## 5. Event Dispatchers y cascarones (creados en F0, rellenados por el dueño)

Los dispatchers se **declaran en F0** con esta firma exacta para que otros puedan enlazarse desde el día 1, aunque nunca se disparen todavía.

| Asset (cascarón) | Dueño | Dispatchers | Lo consume |
|---|---|---|---|
| `BP_HealthComponent` | A (también lo usan los enemigos de B) | `OnHealthChanged(Current, Max: float)`, `OnDepleted()` | C (HUD), B |
| `BP_CombatComponent` | A | `OnStaminaChanged(Current, Max: float)`, `OnCombatStateChanged(NewState: ECombatState)` | C (HUD) |
| `BP_TemporalComponent` | A | `OnRetakeChargesChanged(Current, Max: int)`, `OnTemporalCutCooldown(Remaining, Total: float)`, `OnRetakePerformed()` | C (HUD), D (post-proceso) |
| `BP_StealthComponent` (en el jugador) | B | `OnDetectionChanged(Level: float 0–1)`; funciones `SetCrouched(bool)`, `SetHidden(bool)`, `GetVisibilityMultiplier() → float`, `ReportDetection(Enemy: Actor, Level: float)` | C (HUD, escondites), A (agacharse) |
| `BP_InteractionComponent` (en el jugador) | C | `OnFocusChanged(Target: Actor, Prompt: Text)` | C (HUD) |
| `BP_ObjectiveManager` (componente del GameState) | C | `OnStoryPhaseChanged(NewPhase: EStoryPhase)`, `OnChecklistUpdated()`, `OnDialogueStarted(Row: Name)`, `OnDialogueFinished(Row: Name)`, `OnEndingTriggered(Ending: EEndingType)` | B (Jack, Interventor), D (ambiente/música) |
| `BP_GuardBase` | B | `OnEnemyStateChanged(NewState: EEnemyAIState)`, `OnTelegraphStarted(AttackType: EAttackType, Duration: float)` | D (audio/VFX opcional) |
| `BP_PlayerCharacter`, `BP_PlayerController` | A | — | |
| `BP_GameMode`, `BP_GameState`, `BP_HUD` | C | — | |
| `BP_Jack`, `BP_Pursuer`, `BP_Interventor`, `BP_Supervisor` | B | — | |
| `BP_InteractableBase`, `BP_Door`, `BP_Hideout`, `BP_Evidence`, `BP_FinalChoice`, `BP_Checkpoint`, `BP_StoryTrigger` | C | — | |

### Flujos acordados (quién hace qué)

**Golpe del jugador:** A traza el arco → por cada actor nuevo con `BPI_Damageable` llama `ReceiveCombatHit` → B aplica salud/postura en el enemigo y devuelve el resultado → A reacciona (rebote si `Blocked`).

**Golpe enemigo y parry:** B, en su notify de impacto, llama `ReceiveCombatHit` al jugador → A decide `Parried`/`Dodged`/`Hit` → si `Parried`, B aplica stagger y postura al propio enemigo.

**Corte de Fotograma:** A elige objetivo (cercano, visible, `CanBeTemporalCutTarget`) → `ApplyTemporalFreeze(0.8, 10)` → B congela movimiento/animación y restaura → A inicia cooldown con la duración devuelta → `OnTemporalCutCooldown`.

**Remate:** B, al aturdirse un enemigo, lo hace `CanInteract = true` → C (Interaction) lo prioriza (100) → `Interact` del enemigo llama `RequestFinisher(self)` al jugador → A reproduce el montage y aplica `ST_HitInfo` con `AttackType = Finisher`, `bNonLethal = true` para civiles.

**Muerte del jugador:** `OnDepleted` → A decide si ofrece Retoma (cargas > 0 y no bloqueada) → si no, A llama `ReportStoryEvent(PlayerDefeated)` → C (GameMode) llama `OnCheckpointRestore` a todos los `BPI_CheckpointListener`.

**Diálogo/irreversibles:** C llama `SetGameplayInputEnabled(false)` y `SetRetakeBlocked(true)`; al acabar, los revierte y, si el evento fue irreversible, `ClearRetakeHistory()`.

**Enemigo neutralizado:** B llama `ReportStoryEvent(EnemyNeutralized, self, <Nombre de encuentro>)` → C decide si eso abre algo.

**Jack:** B escucha `OnStoryPhaseChanged`; en `ProtectJack` empieza a avanzar por waypoints cuando la zona está despejada; al llegar llama `ReportStoryEvent(JackReachedRefuge)`. Su `Interact` llama `ReportStoryEvent(JackFound)`; el diálogo lo dispara C.

**Interventor:** B escucha `OnDialogueFinished`; cuando termina la fila `Correction_Order` (nombre de fila acordado con C en `DT_Dialogue`), el Interventor pasa a hostil y B reporta `InterventorTurnedHostile`.

## 6. Mapas y subniveles

`L_Whitechapel` es un mapa persistente que **solo** agrupa subniveles (Level Streaming, todos "Always Loaded"). Cada persona coloca actores únicamente en su subnivel:

| Subnivel | Dueño | Contiene |
|---|---|---|
| `L_Whitechapel` (persistente) | D | Subniveles, `NavMeshBoundsVolume`, PostProcess global, luz direccional/cielo, `BP_CameraRig` si existe |
| `L_Whitechapel_Geo` | D | Blockout, después arte final, colisiones, cobertura |
| `L_Whitechapel_Light` | D | Luces locales (faroles), niebla, audio ambiente |
| `L_Whitechapel_AI` | B | Enemigos, rutas de patrulla, Jack y sus waypoints |
| `L_Whitechapel_Story` | C | `PlayerStart`, interactuables, evidencias, puertas, checkpoints, triggers, expedientes finales |

Notas:

- **NavMesh**: `Runtime Generation = Dynamic` (Project Settings → Navigation Mesh) para que el `RecastNavMesh` no ensucie el mapa al mover geometría. Solo D guarda el persistente.
- **Iluminación**: Lumen dinámico; nadie hace *Build Lighting* (evita `_BuiltData` gigantes).
- **Puertas que bloquean NavMesh** (C) deben usar `Nav Modifier` o desactivar colisión de navegación al abrirse; coordinar con B en F2.
- A no tiene subnivel: el jugador lo genera el GameMode en el `PlayerStart` de C.

## 7. Configuración del proyecto (F0, integrador)

| Ajuste | Valor |
|---|---|
| Default GameMode | `BP_GameMode` (C) con `BP_PlayerCharacter`, `BP_PlayerController`, `BP_GameState`, `BP_HUD` |
| Mapa por defecto (editor y juego) | `L_Whitechapel` |
| Canales de traza | `Interaction` (Trace, ignore por defecto), `Combat` (Trace, overlap Pawn) |
| Canal de objeto | `Enemy` (si B lo necesita para filtrar trazas de A) |
| Enhanced Input | `IMC_Default` añadido por `BP_PlayerController` (A) |
| Plugins | Enhanced Input, Niagara, Python Editor Script Plugin (+ MCP si D0.5) |

## 8. Placeholders compartidos (para no bloquearse por arte)

D crea en F0/F1 assets **vacíos o provisionales con su nombre definitivo**; el resto los referencia desde el día 1 y D cambia su *contenido* más tarde sin mover la ruta:

```text
VFX/NS_TemporalCut         VFX/NS_RetakeTrail       VFX/NS_ParrySpark
VFX/NS_HitImpact           VFX/NS_ContinuityGlitch  VFX/NS_FinalRegister
Audio/SC_StaffHit          Audio/SC_ParrySuccess    Audio/SC_TemporalCut
Audio/SC_Retake            Audio/SC_ChecklistRewrite Audio/SC_EvidencePickup
Audio/SC_Footstep_Cobble   Audio/MS_Ambience_Whitechapel
Materials/M_TemporalFrozen_Overlay  (overlay que B aplica al congelar)
Materials/PP_Retake        (post-proceso que A/D activan en Retoma)
```

Si alguien necesita otro placeholder, lo pide en "Solicitudes de contrato" de D.

## 9. Historial de versiones del contrato

| Versión | Fecha | Cambio | Pedido por |
|---|---|---|---|
| v1.0 | | Contrato inicial (esqueleto F0) | Integrador |
| v1.0 borrador, reparación de enum | 2026-11-14 | El asset existente omitía SupervisorEncounterStarted. Se añade al final, sin cambiar índices anteriores, por autorización explícita del usuario. El orden de §3 refleja el asset | Usuario / integrador temporal |
| v1.0 borrador, aclaración documental | 2026-11-14 | Nombre Unscripted, base de rutas y norma de inglés; sin cambios de firmas ni congelación de F0 | Usuario / integrador temporal |
| v1.0 borrador, unificación de rutas | 2026-11-14 | Raíz propia `Content/Unscripted/` y reserva condicional `Source/Unscripted/`; guías y planes actualizados. No se encontraron assets guardados bajo la raíz provisional que requirieran migración | Usuario / integrador temporal |
| v1.0 borrador, A-CON-01 | 2026-11-14 | Renombrar operación de daño a `ReceiveCombatHit` para evitar colisión con Actor; entrada HitInfo y salida Result conservadas. Aprobado por el usuario; validación de assets pendiente | Usuario / integrador temporal |
