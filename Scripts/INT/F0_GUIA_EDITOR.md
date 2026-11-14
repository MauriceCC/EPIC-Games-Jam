# F0 en el editor — Unscripted, guía para principiantes

Estado: instrucciones preparadas, no ejecución automática. El usuario confirmó que abrió el proyecto con UE 5.8.4 y que Play funciona. El resto requiere comprobación en el editor. Trabajamos excepcionalmente como integrador.

Fuente de nombres, campos y firmas: [contratos](../../docs/plan/01_CONTRATOS_Y_PROPIEDAD.md). No cambiar los nombres por traducciones. Todo texto para el jugador debe estar en inglés.

## 1. Carpetas

1. Salir de Play con Stop.
2. Abrir Content Drawer con Ctrl+Space. También se puede abrir Content Browser desde Window.
3. Seleccionar la raíz Content del proyecto. `/Game/` en documentación corresponde a esta raíz, no a una carpeta que haya que crear.
4. Clic derecho en el área de assets → New Folder → `Unscripted`.
5. Dentro crear las carpetas siguientes. Para crear una subcarpeta, entrar primero en su carpeta padre.

```text
Content/Unscripted/
  Core/Enums
  Core/Structs
  Core/Interfaces
  Player/Input
  Player/Animation
  Player/Test
  Enemies/Jack
  Enemies/Animation
  Enemies/Test
  Narrative/Test
  UI
  World/Test
  Art
  Materials
  VFX
  Audio
  Maps/Test
```

`Unscripted` es tanto el nombre definitivo del juego como la raíz interna acordada. Esta instrucción sustituye la recomendación anterior de conservar el nombre provisional. No mover los assets de TopDown. Las carpetas vacías pueden no viajar por Git hasta contener assets o un `.gitkeep`.

## 2. Enums: listas de opciones

1. Entrar en `Core/Enums`.
2. Clic derecho → Blueprints → Enumeration (usar la búsqueda del menú si está agrupado de otra manera).
3. Nombrar el asset `ECombatState` y abrirlo con doble clic.
4. Pulsar New para añadir cada entrada. Editar Display Name con los valores siguientes, uno por fila, en este orden.
5. Guardar con Ctrl+S. Un enum no tiene un grafo de nodos que programar.

```text
Idle
Attacking
Dodging
Parrying
Stunned
TemporalFrozen
Rewinding
Defeated
```

Repetir para los otros ocho enums, copiando exactamente las listas de contratos §3: `EEnemyAIState`, `EAttackType`, `EHitResult`, `EStoryPhase`, `EStoryEvent`, `EEvidenceType`, `EEndingType`, `ESpeaker`. No dejar entradas adicionales llamadas NewEnumerator. No reordenarlas después de utilizarlas.

Comprobación: hay nueve assets de tipo Enumeration en esta carpeta; cerrar y reabrir `ECombatState` conserva sus ocho opciones.

## 3. Structs: paquetes de datos

1. Entrar en `Core/Structs` → clic derecho → Blueprints → Structure.
2. Crear `ST_HitInfo` y abrirlo.
3. Renombrar el primer campo y usar New Variable para añadir los demás. En cada fila seleccionar el tipo; escribir el nombre del enum en el buscador de tipos cuando corresponda.

| Campo | Tipo a seleccionar |
|---|---|
| Damage | Float |
| PostureDamage | Float |
| AttackType | EAttackType |
| Instigator | Actor → Object Reference |
| HitLocation | Vector |
| HitDirection | Vector |
| bParryable | Boolean |
| bNonLethal | Boolean |

No seleccionar Actor Class Reference: necesitamos una instancia del actor. Mantener el nombre de campo `bNonLethal` aunque Unreal lo muestre con espacios en ciertos paneles. En Default Values establecer bNonLethal = true como valor inicial; cada ataque debe fijar su intención correctamente. Los demás valores no constituyen todavía balance de combate.

Crear también:

| Asset | Campos y tipos |
|---|---|
| ST_DialogueLine | Speaker: ESpeaker; Text: Text; Duration: Float; NextRow: Name |
| ST_ChecklistRow | Phase: EStoryPhase; Items: Array de Text; CompletedMask: Array de Boolean; bIsRewritten: Boolean |

Para Array, seleccionar primero el tipo base y después el selector de contenedor junto al tipo → Array. Text, String y Name son tipos distintos: respetar la tabla. No crear todavía DataTables ni `ST_RewindSnapshot` (es trabajo interno de A).

Comprobación: guardar, cerrar y reabrir las tres estructuras; comprobar tipos y que no quedaron campos de ejemplo.

## 4. Crear primero los componentes vacíos

Hay dos interfaces que devuelven componentes específicos. Por eso necesitamos crear esos assets antes de definir todas las interfaces: es un ajuste de orden, no un cambio de contrato.

1. En cada carpeta de la tabla, clic derecho → Blueprint Class.
2. Seleccionar Actor Component; si no aparece, abrir All Classes y buscar `ActorComponent`.
3. Nombrar, abrir, pulsar Compile y Save. No agregar lógica aún.

| Carpeta | Blueprints con padre ActorComponent |
|---|---|
| Player | BP_HealthComponent, BP_CombatComponent, BP_TemporalComponent |
| Enemies | BP_StealthComponent |
| Narrative | BP_InteractionComponent, BP_ObjectiveManager |

## 5. Interfaces: declarar operaciones

1. Entrar en `Core/Interfaces` → clic derecho → Blueprints → Blueprint Interface.
2. Crear `BPI_Damageable` y abrirlo.
3. En My Blueprint → Functions, renombrar NewFunction a `ReceiveHit`.
4. Seleccionar la función. En Details → Inputs, pulsar +: nombre `HitInfo`, tipo `ST_HitInfo`.
5. En Outputs pulsar +: tipo `EHitResult`. **[PROPUESTA]** Nombre de salida `Result`, porque el contrato fija su tipo pero no el nombre de ese pin.
6. Añadir otra función con + junto a Functions: `IsDefeated`. Sin Inputs, una salida Boolean.
7. Compile y Save. Las interfaces solo contienen declaraciones; aquí no se conectan nodos para aplicar daño.

Crear las restantes con todas las funciones de contratos §4:

| Interface | Funciones |
|---|---|
| BPI_TimeAffectable | CanBeTemporalCutTarget, ApplyTemporalFreeze |
| BPI_Interactable | CanInteract, GetInteractionText, GetInteractionPriority, Interact |
| BPI_PlayerControl | SetGameplayInputEnabled, SetRetakeBlocked, ClearRetakeHistory, RequestFinisher, GetStealthComponent |
| BPI_StoryEvents | ReportStoryEvent, GetCurrentPhase, GetObjectiveManager |
| BPI_CheckpointListener | OnCheckpointRestore |

Copiar Inputs y Outputs del contrato en el orden escrito. `void` o ausencia de flecha significa que no hay Outputs. `int` significa Integer, no Integer64. Para `BP_StealthComponent` y `BP_ObjectiveManager`, elegir Object Reference del Blueprint creado en el paso anterior. **[PROPUESTA]** Usar `Result` para las demás salidas cuyo nombre no está especificado, documentando cualquier elección distinta antes de compartir.

Comprobación: seis interfaces guardadas y compiladas; ninguna función vacía de ejemplo; todas las entradas y salidas coinciden con el contrato.

## 6. Crear los otros cascarones

Mismo menú Blueprint Class. **[PROPUESTA]** Se concretan estos padres donde el contrato no fija la clase nativa. GameModeBase se combina con GameStateBase.

| Carpeta | Asset | Padre |
|---|---|---|
| Player | BP_PlayerCharacter | Character |
| Player | BP_PlayerController | PlayerController |
| Enemies | BP_GuardBase | Character |
| Enemies | BP_Pursuer, BP_Interventor, BP_Supervisor | BP_GuardBase |
| Enemies/Jack | BP_Jack | Character |
| Narrative | BP_GameMode | GameModeBase |
| Narrative | BP_GameState | GameStateBase |
| UI | BP_HUD | HUD |
| Narrative | BP_InteractableBase | Actor |
| Narrative | BP_Door, BP_Hideout, BP_Evidence, BP_FinalChoice | BP_InteractableBase |
| Narrative | BP_Checkpoint, BP_StoryTrigger | Actor |

Para crear los hijos de un Blueprint, clic derecho sobre el asset padre → Create Child Blueprint Class. Así los enemigos heredan la base, en lugar de ser cuatro personajes independientes. Compilar padres antes que hijos.

Un Character nuevo tiene cápsula y movimiento, pero no personaje visible ni controles configurados. Es esperable en F0; no significa que el asset esté roto.

## 7. Declarar dispatchers y funciones de componentes

1. Abrir `BP_HealthComponent`.
2. En My Blueprint, sección Event Dispatchers, pulsar + y nombrar `OnHealthChanged`.
3. Seleccionarlo → Details → Inputs → añadir `Current` Float y `Max` Float.
4. Crear `OnDepleted` sin Inputs.
5. Compile y Save. No arrastrar Call ni Bind al grafo todavía.

Repetir todas las declaraciones de contratos §5 en Combat, Temporal, Stealth, Interaction, ObjectiveManager y GuardBase. `Current, Max: float` son dos parámetros Float. Los dispatchers no tienen Outputs.

En `BP_StealthComponent`, crear además Functions con +:

- `SetCrouched`: entrada Boolean.
- `SetHidden`: entrada Boolean.
- `GetVisibilityMultiplier`: salida Float.
- `ReportDetection`: entradas Enemy (Actor Object Reference) y Level (Float).

**[PROPUESTA]** Nombrar las entradas Boolean `bCrouched` y `bHidden`, y la salida Float `Result`, donde el contrato no da nombres. Como valor neutro provisional devolver 1.0 en GetVisibilityMultiplier; no implementa sigilo.

## 8. Conectar componentes e interfaces

En `BP_PlayerCharacter`, panel Components → Add → buscar y añadir una vez cada componente: Health, Combat, Temporal, Interaction y Stealth. Los nombres de búsqueda son los Blueprints completos del paso 4. Compile y Save.

Repetir: `BP_GuardBase` incorpora `BP_HealthComponent`; `BP_GameState` incorpora `BP_ObjectiveManager`.

Para añadir una interface a un Blueprint: abrir → Class Settings → Details → Implemented Interfaces → Add → seleccionar la interface → Compile. Aplicar:

| Blueprint | Interfaces |
|---|---|
| BP_PlayerCharacter | BPI_Damageable, BPI_PlayerControl, BPI_CheckpointListener |
| BP_GuardBase | BPI_Damageable, BPI_TimeAffectable, BPI_Interactable, BPI_CheckpointListener |
| BP_Jack | BPI_Interactable, BPI_CheckpointListener |
| BP_InteractableBase | BPI_Interactable |
| BP_GameState | BPI_StoryEvents |

Los hijos heredan las interfaces; no duplicarlas.

**[PROPUESTA] Valores provisionales seguros:** en las funciones con salida dejar CanInteract y CanBeTemporalCutTarget en false, IsDefeated en false, ApplyTemporalFreeze en 0 y ReceiveHit en Ignored. No simular éxitos de sistemas sin implementar. Funciones sin salida pueden permanecer sin comportamiento en F0.

Dos getters deben devolver sus componentes reales para permitir enlazar avisos:

1. En PlayerCharacter, My Blueprint → Interfaces → abrir `GetStealthComponent`.
2. Arrastrar el componente Stealth desde Components al grafo como referencia.
3. Conectar su pin al pin de salida del Return Node; mantener conectado el flujo de ejecución si aparece.
4. En GameState, repetir para `GetObjectiveManager` con el componente ObjectiveManager.
5. En GetCurrentPhase, devolver `FindJack` provisionalmente. C implementará el estado narrativo en F1.

## 9. Configurar clases de juego

Abrir `BP_GameMode` → Class Defaults. Buscar y configurar:

| Propiedad | Valor |
|---|---|
| Default Pawn Class | BP_PlayerCharacter |
| Player Controller Class | BP_PlayerController |
| Game State Class | BP_GameState |
| HUD Class | BP_HUD |

Compile y Save. Edit → Project Settings → Maps & Modes → Default GameMode = BP_GameMode. Una configuración GameMode Override en World Settings de un mapa prevalece sobre este valor; revisar al probar. No guardar cambios sobre el mapa TopDown original.

## 10. Mapas propios y subniveles

1. File → New Level → **Empty Level**, no Open World. Guardar en `Unscripted/Maps` como `L_Whitechapel`.
2. Window → Levels. Este flujo usa subniveles tradicionales, como pide el contrato; no usar el mapa World Partition de la plantilla como base.
3. En el menú del panel Levels → Create New → nivel vacío. Guardar en Maps como `L_Whitechapel_Geo`.
4. Repetir para `L_Whitechapel_Light`, `L_Whitechapel_AI`, `L_Whitechapel_Story`.
5. En Levels, clic derecho sobre cada subnivel → Change Streaming Method → Always Loaded.
6. Doble clic en un subnivel lo vuelve Current: comprobarlo antes de colocar actores.
7. En Geo, añadir un Cube como suelo. **[PROPUESTA]** Scale (20,20,0.2), Location (0,0,-10): una sala provisional de 20 × 20 metros, no el blockout final.
8. En Story, añadir PlayerStart sobre el suelo, por ejemplo Z=120. Sin aviso BADsize.
9. En el persistente, añadir iluminación provisional (Directional Light y Sky Light) y NavMeshBoundsVolume que cubra el suelo. Nada de Build Lighting.
10. Guardar los niveles propios modificados. Crear aparte cuatro Empty Levels y guardar como `Maps/Test/L_Test_A`, B, C y D. En cada uno añadir suelo, luz y PlayerStart propios; no compartir actores por referencia entre mapas de prueba.
11. En Maps & Modes, Editor Startup Map y Game Default Map = L_Whitechapel.

Para inspeccionar la escena antes de que A añada cámara y controles, usar el viewport del editor. Play todavía no demuestra movimiento jugable. No sustituir el PlayerCharacter por otro para ocultar esa tarea pendiente.

## 11. Configuración y tareas que deben quedar registradas

- Edit → Plugins: verificar Enhanced Input, Niagara y Python Editor Script Plugin conforme al plan. Reiniciar si el editor lo solicita, guardando primero el trabajo. No instalar MCP sin decisión del equipo.
- Project Settings → Navigation Mesh → Runtime Generation = Dynamic. P en el viewport muestra la navegación cuando exista geometría navegable y volumen que la cubra.
- Project Settings → Collision → New Trace Channel: `Interaction`, Default Response Ignore.
- **Aclaración pendiente:** el contrato pide `Combat` con respuesta Overlap para Pawn, pero no especifica la respuesta global del canal. **[PROPUESTA]** Ignore por defecto y Overlap para cápsulas relevantes; acordar el comportamiento de obstáculos con A/B antes de verificar impactos. No declarar esta parte resuelta solo por crear un nombre de canal.
- El canal de objeto Enemy es condicional: no crearlo sin necesidad acordada con B.
- Enhanced Input se configura con la guía [A-01](../A/A01_INPUT_BLUEPRINT.md), usando el BP_PlayerController definitivo al existir F0; omitir sus cascarones exclusivos de prueba. La comprobación de input corresponde a A-01, no a combate implementado.
- Placeholders de audio, VFX y materiales de contratos §8 siguen siendo trabajo F0/F1 de D: no crear archivos de otro tipo con el mismo nombre para aparentar que están listos. Registrar su estado antes de que A/B/C los referencien.

## 12. Verificación y entrega

- Compile y Save en todos los Blueprints; corregir errores antes de compartir.
- Reabrir el proyecto y los cinco mapas. Revisar Message Log y Output Log por errores de referencias.
- En Play, revisar World Outliner: aparecen PlayerCharacter, PlayerController, GameMode, GameState y HUD correctos. La ausencia de combate, movimiento o UI terminados es esperable.
- Confirmar getters de componentes y todas las firmas del contrato. Registrar propuestas de nombres de salida y clases padre aceptadas antes de congelar v1.0.
- Registrar pendientes de colisiones/placeholders; no declarar F0 completamente terminado con comprobaciones pendientes.
- Cerrar Unreal antes de operaciones Git que cambien los archivos. Revisar rutas modificadas; agregar solo archivos concretos. Seguir la ventana de integración, sin forzar main.
- Los cuatro integrantes deben abrir y compilar la misma revisión. Solo entonces cada uno desarrolla su carpeta.

Referencias oficiales consultadas: [Blueprint Interfaces](https://dev.epicgames.com/documentation/unreal-engine/blueprint-interface-in-unreal-engine?lang=en-US), [Event Dispatchers](https://dev.epicgames.com/documentation/unreal-engine/event-dispatchers-in-unreal-engine?lang=en-US), [gestión de niveles](https://dev.epicgames.com/documentation/en-us/unreal-engine/managing-multiple-levels-in-unreal-engine). Esta guía no ha sido ejecutada por el agente en el editor.
