# 06 — Diseño técnico propuesto para Unreal Engine 5

> **Norma de producto:** Unscripted, UE 5.8.4, Blueprint. Todo contenido visible o audible al jugador debe estar en ingl?s. Los ejemplos en espa?ol de este documento son referencias de dise?o que deben adaptarse antes de incorporarse al juego; documentaci?n y comentarios internos pueden seguir en espa?ol.

> **Advertencia:** esta es una arquitectura **sugerida** a partir de la conversación. No describe archivos ya existentes, Blueprints compilados ni componentes comprobados en un proyecto real.
>
> **Contratos:** los nombres, firmas, interfaces, dispatchers, carpetas y subniveles que comparten varias divisiones están fijados en [`plan/01_CONTRATOS_Y_PROPIEDAD.md`](plan/01_CONTRATOS_Y_PROPIEDAD.md). Si algo de este documento difiere, **prevalece el contrato**. Este archivo sigue siendo la referencia de *cómo* implementar cada sistema.

## Proyecto

- Unreal Engine **5.8.4**, Desktop; proyecto existente `Unscripted/Unscripted.uproject`.
- Base existente: **Top Down**, proyecto creado como **Blueprint**. No crear un segundo proyecto; variante exacta pendiente de verificar en el editor.
- Cámara isométrica/elevada; ajustar Pitch -55°, Yaw 45° como punto inicial.
- Movimiento y habilidades con **Enhanced Input**.
- Vista isométrica 3D y orientación hacia cursor.
- Nivel único `L_Whitechapel` (nombre sugerido).
- Para guardar el diseño visual, evitar dependencia de sistemas avanzados de iluminación, física o mundos abiertos.

## Mapa de Blueprints propuestos

```text
L_Whitechapel (persistente + subniveles _Geo, _Light, _AI, _Story)
├── BP_GameMode / BP_GameState (+ BP_ObjectiveManager) / BP_HUD      [C]
├── BP_PlayerController                                              [A]
├── BP_PlayerCharacter                                               [A]
│   ├── BP_CombatComponent                                           [A]
│   ├── BP_TemporalComponent                                         [A]
│   ├── BP_HealthComponent  (también en enemigos)                    [A]
│   ├── BP_InteractionComponent                                      [C]
│   └── BP_StealthComponent                                          [B]
├── BP_GuardBase                                                     [B]
│   ├── BP_Pursuer
│   ├── BP_Interventor
│   └── BP_Supervisor
├── BP_Jack, BP_JackWaypoint, BP_PatrolRoute                         [B]
├── BP_InteractableBase (clase base)                                 [C]
│   ├── BP_Door, BP_Hideout, BP_Evidence, BP_FinalChoice
├── BP_Checkpoint, BP_StoryTrigger                                   [C]
├── Interfaces: BPI_Interactable, BPI_Damageable, BPI_TimeAffectable,
│   BPI_PlayerControl, BPI_StoryEvents, BPI_CheckpointListener       [Core]
└── Widgets: WBP_HUD, WBP_Dialogue, WBP_Checklist, WBP_Ending        [C]
```

Entre corchetes, la división dueña. `BPI_Interactable` ofrece un contrato común a puertas, documentos, escondites, personajes, enemigos aturdidos (remate) y mecanismos de elección. Las firmas exactas de todas las interfaces están en el documento de contratos.

## Entradas sugeridas

| Input Action | Evento |
|---|---|
| `IA_Move` | WASD (Vector2D) |
| `IA_LookMouse` | Localizar cursor en plano del mundo para orientación |
| `IA_LightAttack` | Clic izquierdo |
| `IA_HeavyAttack` | Clic derecho |
| `IA_Dodge` | Espacio |
| `IA_Parry` | Q |
| `IA_TemporalCut` | F |
| `IA_Retake` | R |
| `IA_Interact` | E |
| `IA_Crouch` | Ctrl |
| `IA_Checklist` | Tab |

## Estados de combate

```text
ECombatState
  Idle
  Attacking
  Dodging
  Parrying
  Stunned
  TemporalFrozen
  Rewinding
  Defeated
```

**Contrato básico:** las habilidades solo se inician desde estados permitidos; una salida de habilidad debe restaurar un estado válido. Los golpes no deben solaparse arbitrariamente. Si un actor queda aturdido, su entrada ofensiva queda cancelada según reglas de la animación.

## Ataques y detección de impacto

- Utilizar **Animation Montages** para combo ligero, pesado, esquiva, parry y remate.
- Utilizar **Animation Notifies** para abrir/cerrar ventanas de daño, ventana de parry y transición de combos.
- Detectar enemigos mediante `Sphere Trace`/overlap en un arco frontal, en ventanas de impacto.
- Llevar un conjunto de actores impactados durante cada ataque para impedir múltiples daños del mismo golpe.
- Calcular orientación hacia el punto del cursor en el plano del suelo.
- Resistencias, daño, tiempo de animación y postura deben poder modificarse mediante variables/data assets o estructuras.

## IA de enemigos

Para un prototipo, `NavMeshBoundsVolume` y `AI Move To` pueden gestionar patrullas por waypoints. La percepción puede implementarse con `AI Perception` o comprobaciones de ángulo + distancia + line trace si resultan más simples.

Estados sugeridos:

```text
Patrol → Suspicious → Chase → Combat
    ↘        ↘         ↘
       Return / Patrol
Combat → Stunned → Combat
Combat → Defeated
```

- Patrulla: 2–3 puntos.
- Sospecha: investiga último lugar visto.
- Persecución: movimiento hacia agente.
- Combate: distancia/telegráfica/ataque/reposicionamiento.
- Coordinación de grupos: permitir solo 1–2 ataques simultáneos al principio.
- `TemporalFrozen`: detener temporalmente movimiento y animación, reanudándolos sin conflicto de órdenes.
- Perseguidor, Interventor y Supervisor derivan de una clase base y comparten salud, combate, estados y eventos.

## Interacción: interfaz conceptual

```text
BPI_Interactable
  CanInteract(Interactor) → bool
  GetInteractionText(Interactor) → Text
  GetInteractionPriority() → int
  Interact(Interactor)
```

`BP_InteractionComponent` escoge un objetivo válido cercano, presenta prompt y ejecuta `Interact`. Debe resolver prioridades cuando coinciden remate, puerta y documento.

## Gestión narrativa

```text
EStoryPhase
  FindJack
  OpenEscapeRoute
  ProtectJack
  DiscoverTruth
  FinalChoice
  GameEnded
```

`BP_ObjectiveManager` (componente de `BP_GameState`) administra estado de historia y notifica a `WBP_HUD`/`WBP_Checklist`. Los demás sistemas le comunican hechos con `ReportStoryEvent(EStoryEvent, Source, Param)` vía `BPI_StoryEvents` (ver contratos).

**Eventos tentativos (en el contrato se agrupan en el enum `EStoryEvent`):**

```text
OnJackFound
OnEscapeRouteOpened
OnJackReachedRefuge
OnEvidenceCollected(EvidenceType)
OnTruthRevealed
OnSupervisorEncounterStarted
OnSupervisorDefeated
OnFinalDocumentRegistered(EndingType)
```

Las puertas, pruebas y personajes comunican eventos al gestor, y el gestor valida condiciones para cambiar de fase. Evitar que cada objeto decida directamente toda la historia.

## Implementación del Corte de Fotograma

```text
TryTemporalCut(target):
  if not valid target or out of range or no line of sight: fail
  if cooldown active or current combat state blocks action: fail
  apply target.TemporalFrozen for duration (default 0.8 sec)
  add posture damage (default 10)
  start cooldown (default 10 sec)
  notify HUD / VFX
```

**Precaución:** el Supervisor puede reducir la duración efectiva. Los efectos de congelación deben recuperar correctamente la velocidad de animación/movimiento y no perder estados previos.

## Implementación de Retoma

```text
ST_RewindSnapshot:
  Timestamp
  Transform
  Velocity (optional)
  Health
  Stamina

OnTimerEvery0.1s:
  if valid gameplay state:
    RecordSnapshot()
    KeepLast50Snapshots()

TryRetake():
  require charges > 0 and historical snapshot available
  require not in dialogue/final choice/non-rewindable action
  choose suitable historical snapshot (up to 5s)
  validate destination collision/safe placement
  temporarily disable controls
  restore player's transform/health/stamina
  consume 1 charge (charges not restored)
  play temporal VFX
  resume control
```

El registro almacena **solamente al jugador**, no al conjunto de actores. Enemigos mantienen vida/heridas/estado actual. No deshacer flags narrativos ni duplicar recursos. Vaciar snapshots tras eventos persistentes o al cambiar bruscamente de área.

## Checkpoints

- Guardan progreso narrativo necesario para reiniciar de forma coherente.
- Recuperan las **dos** cargas de Retoma por sección.
- Pueden restablecer salud según balance final.
- En un fallo sin cargas disponibles, reaparecer en checkpoint válido.

## UI e información

`WBP_HUD` muestra salud, resistencia, carga de Retoma, cooldown Corte, objetivo y alerta. `WBP_Dialogue` permite texto de Supervisor/Director/Jack. `WBP_Ending` representa periódico final o mensaje temporal.

## Riesgos técnicos conocidos

1. Sincronización de ataque/impacto y parry con animación real.
2. Colisiones válidas al restaurar la posición de Retoma en un mundo que **no** rebobina.
3. Restablecer IA tras interrupciones temporales.
4. Evitar daño doble por un único hit y estados incompatibles.
5. Evitar pérdida de lectura visual por cámara isométrica/obstáculos.
6. Evitar que el final se active antes de que el jugador registre el documento.

## Criterios funcionales para validar

- El personaje se mueve y orienta ataques de forma coherente.
- El combo golpea una vez por actor por impacto.
- Esquiva y parry actúan en ventanas legibles.
- Los guardias pueden perseguir, combatir y dejar de detectar.
- Corte interrumpe un enemigo y se recupera correctamente.
- Retoma restaura estado **personal** sin modificar enemigos/objetivos narrativos.
- Jack alcanza su refugio al habilitar la ruta.
- El checklist se actualiza con los eventos.
- Los dos mecanismos del archivo disparan finales diferentes.
- Un recorrido desde inicio hasta final no exige intervención manual del editor.

## Qué no está implementado por el mero hecho de figurar aquí

No existe código entregado, ni un proyecto UE, ni assets, ni Animation Montages, ni IA funcional ni niveles probados asociados a este archivo. Es documentación para guiar su construcción.
