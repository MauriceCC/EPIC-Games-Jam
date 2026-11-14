# Guía de Implementación Blueprint — División B (Enemigos, IA, Sigilo y Jack)

> **Proyecto:** Unscripted · **Motor:** Unreal Engine 5.8.4 · **Modo:** Blueprint
> **Área:** División B (`Content/Unscripted/Enemies/`, `Maps/L_Whitechapel_AI`, `Maps/Test/L_Test_B`, `SourceData/B/`, `Scripts/B/`)
> **Norma de idioma:** Todo texto visible o audible para el jugador en pantalla/HUD/prompts debe estar en **inglés**. Comentarios internos en español.

---

## 1. Resumen de la División B

La División B es responsable del sistema de sigilo, comportamiento de enemigos (percepción, estados de alerta, persecución, combate por turnos/tokens, aturdimiento y remate no letal), poderes temporales aplicados a enemigos (`ApplyTemporalFreeze`), el NPC Jack con su avance por tramos, y los encuentros en `L_Test_B` y `L_Whitechapel_AI`.

---

## 2. Estructura de Balance de Enemigos

### 2.1. Crear la Estructura `ST_EnemyBalance`
1. En `Content/Unscripted/Enemies/`, clic derecho → **Blueprints** → **Structure**.
2. Nombrar: `ST_EnemyBalance`.
3. Añadir los siguientes campos:

| Campo | Tipo | Valor por defecto |
|---|---|---|
| `Health` | Float | 45.0 |
| `AttackDamage` | Float | 12.0 |
| `PostureDamage` | Float | 8.0 |
| `VisionRange` | Float | 1800.0 |
| `DetectionRange` | Float | 800.0 |
| `WalkSpeed` | Float | 130.0 |
| `RunSpeed` | Float | 240.0 |
| `AlertDelaySeconds` | Float | 1.2 |
| `StunDurationSeconds` | Float | 1.8 |
| `TemporalFreezeDurationSeconds` | Float | 0.8 |
| `NeutralizeWindowSeconds` | Float | 1.6 |
| `Priority` | Integer | 100 |

4. Guardar y compilar.

### 2.2. Importar DataTable `DT_EnemyBalance`
1. En el Content Browser, dentro de `Content/Unscripted/Enemies/`, hacer clic en **Import**.
2. Seleccionar `SourceData/B/DT_EnemyBalance.csv`.
3. En el cuadro de diálogo de importación:
   - **DataTable Row Type**: Seleccionar `ST_EnemyBalance`.
4. Nombrar la DataTable resultante: `DT_EnemyBalance`. Guardar.

---

## 3. `BP_StealthComponent` (Componente de Sigilo del Jugador)

Ubicación: `Content/Unscripted/Enemies/BP_StealthComponent`  
Padre: `ActorComponent`

### 3.1. Variables
- `DetectionLevel` (Float): Nivel agregado de detección (0.0 a 1.0). Default = `0.0`.
- `bIsCrouched` (Boolean): Si el jugador está agachado. Default = `false`.
- `bIsHidden` (Boolean): Si el jugador está dentro de un escondite. Default = `false`.
- `DetectionDecayRate` (Float): Velocidad de reducción de alerta por segundo cuando nadie ve al jugador. Default = `0.3`.
- `AlertedEnemies` (Map de Actor a Float): Registra el nivel de detección de cada enemigo.

### 3.2. Event Dispatchers
- `OnDetectionChanged(Level: Float)`: Disparado cuando el valor agregado de alerta cambia.

### 3.3. Funciones del Contrato

#### Función `SetCrouched(bCrouched: Boolean)`
- **Input:** `bCrouched` (Boolean)
- **Nodos:**
  - `Set bIsCrouched = bCrouched`

#### Función `SetHidden(bHidden: Boolean)`
- **Input:** `bHidden` (Boolean)
- **Nodos:**
  - `Set bIsHidden = bHidden`
  - Si `bHidden == true`:
    - Limpiar `AlertedEnemies` (Clear).
    - `Set DetectionLevel = 0.0`.
    - Llamar `OnDetectionChanged(0.0)`.

#### Función `GetVisibilityMultiplier() -> Float`
- **Output:** `Result` (Float)
- **Nodos:**
  - Si `bIsHidden`: Return `0.0` (completamente invisible).
  - Si `bIsCrouched`: Return `0.5` (cono y rango de visión se reducen al 50 %).
  - Else: Return `1.0` (visibilidad normal).

#### Función `ReportDetection(Enemy: Actor, Level: Float)`
- **Inputs:** `Enemy` (Actor Object Reference), `Level` (Float)
- **Nodos:**
  - Si `bIsHidden`: Return (ignorar reportes).
  - En `AlertedEnemies`, hacer `Add/Set` con clave `Enemy` y valor `Level`.
  - Calcular el valor máximo de detección entre todos los elementos de `AlertedEnemies` (usar `Values` -> bucle `Max`).
  - `Set DetectionLevel = Clamp(MaxLevel, 0.0, 1.0)`.
  - Llamar `OnDetectionChanged(DetectionLevel)`.

#### En `Event Tick`:
- Si `AlertedEnemies` está vacío y `DetectionLevel > 0.0`:
  - `DetectionLevel = Max(0.0, DetectionLevel - (DetectionDecayRate * DeltaSeconds))`.
  - Llamar `OnDetectionChanged(DetectionLevel)`.

---

## 4. `BP_PatrolRoute` (Ruta de Patrulla Editable)

Ubicación: `Content/Unscripted/Enemies/BP_PatrolRoute`  
Padre: `Actor`

1. Añadir componente: `DefaultSceneRoot` o `Billboard`.
2. Variable:
   - `Waypoints` (Array de `Vector` o `Transform`), marcar **Instance Editable** y **Show 3D Widget**. Esto permite arrastrar los puntos de la ruta directamente en el viewport de Unreal sin abrir el Blueprint.
3. Funciones:
   - `GetWaypointLocation(Index: Integer) -> Vector`:
     - Retorna `GetActorLocation() + Waypoints[Index]` (o el Transform transformado a World Space).
   - `GetNumWaypoints() -> Integer`:
     - Retorna `Length(Waypoints)`.

---

## 5. `BP_GuardBase` (Base de Enemigos e IA)

Ubicación: `Content/Unscripted/Enemies/BP_GuardBase`  
Padre: `Character`  
Interfaces implementadas (Class Settings → Implemented Interfaces):
- `BPI_Damageable`
- `BPI_TimeAffectable`
- `BPI_Interactable`
- `BPI_CheckpointListener`

Componentes agregados (Components Panel):
- `Health` (`BP_HealthComponent`)

### 5.1. Variables
- `CurrentAIState` (`EEnemyAIState`): Default = `Patrol`.
- `TargetActor` (Actor): Referencia al jugador cuando es detectado.
- `LastKnownPlayerLocation` (Vector).
- `AlertTimer` (Float): Acumulador de tiempo de sospecha. Default = `0.0`.
- `AlertDelaySeconds` (Float): Tiempo para pasar de Suspicious a Chase. Default = `1.2`.
- `VisionRange` (Float): Rango máximo de visión en cm. Default = `1800.0`.
- `DetectionRange` (Float): Rango de detección cercana/inmediata en cm. Default = `800.0`.
- `SightHalfAngle` (Float): Semisuma angular del cono de visión en grados. Default = `50.0`.
- `AttackRange` (Float): Distancia para iniciar golpe en cm. Default = `160.0`.
- `AttackDamage` (Float): Daño base. Default = `12.0`.
- `PostureDamage` (Float): Daño de postura. Default = `8.0`.
- `CurrentPosture` (Float): Postura actual. Default = `30.0`.
- `MaxPosture` (Float): Postura máxima. Default = `30.0`.
- `bCanAttack` (Boolean): Default = `true`.
- `bIsTemporalFrozen` (Boolean): Default = `false`.
- `FrozenPreState` (`EEnemyAIState`): Almacena el estado previo al congelamiento.
- `PatrolRoute` (`BP_PatrolRoute` Object Reference): Marcar **Instance Editable**.
- `CurrentWaypointIndex` (Integer): Default = `0`.
- `bNonLethalCivilian` (Boolean): Default = `true` para Perseguidores.

### 5.2. Event Dispatchers
- `OnEnemyStateChanged(NewState: EEnemyAIState)`
- `OnTelegraphStarted(AttackType: EAttackType, Duration: Float)`

---

### 5.3. Grafo de Percepción y Detección (`CheckPerception`)

Crear función local `CheckPerception` que se evalúa en `Event Tick` (si no está congelado ni derrotado):
1. Obtener `PlayerCharacter` (`Get Player Character(0)`).
2. Calcular vector `DirectionToPlayer = Player.GetActorLocation() - GetActorLocation()`.
3. Distancia = `VectorLength(DirectionToPlayer)`.
4. Normalizar vector. Calcular producto escalar (`Dot Product`) con `GetActorForwardVector()`.
5. Convertir a ángulo en grados: `Acos(Dot) * (180 / PI)`.
6. Obtener componente de sigilo del jugador:
   - Llamar `BPI_PlayerControl.GetStealthComponent` sobre el jugador.
   - Si es válido: llamar `GetVisibilityMultiplier()`. Si no, usar `1.0`.
7. `EffectiveVisionRange = VisionRange * VisibilityMultiplier`.
8. Si `Angle <= SightHalfAngle` y `Distancia <= EffectiveVisionRange`:
   - Realizar `LineTraceSingleByChannel`:
     - Start: `GetActorLocation() + Vector(0,0,50)` (ojos).
     - End: `Player.GetActorLocation() + Vector(0,0,50)`.
     - Channel: `Visibility`.
   - Si el impacto golpea al jugador (o no hay obstáculos):
     - **¡Jugador Visto!**
     - Si `CurrentAIState == Patrol`:
       - `Set CurrentAIState = Suspicious`.
       - `Set TargetActor = Player`.
       - Disparar `OnEnemyStateChanged(Suspicious)`.
     - Si `CurrentAIState == Suspicious`:
       - `AlertTimer += DeltaSeconds`.
       - Notificar al componente de sigilo: `StealthComponent.ReportDetection(Self, AlertTimer / AlertDelaySeconds)`.
       - Si `AlertTimer >= AlertDelaySeconds`:
         - `Set CurrentAIState = Chase`.
         - Disparar `OnEnemyStateChanged(Chase)`.
     - Si `CurrentAIState == Chase` o `Combat`:
       - `Set LastKnownPlayerLocation = Player.GetActorLocation()`.
9. Si el jugador NO es visto:
   - Si `CurrentAIState == Suspicious`:
     - `AlertTimer -= DeltaSeconds`.
     - Si `AlertTimer <= 0.0`:
       - `Set CurrentAIState = Patrol`.
       - Disparar `OnEnemyStateChanged(Patrol)`.

---

### 5.4. Máquina de Estados de IA (`EvaluateAIStateMachine`)

En `Event Tick`, si `bIsTemporalFrozen == false` y `CurrentAIState != Defeated`:
- `Switch on EEnemyAIState(CurrentAIState)`:

#### Rama `Patrol`:
- Si `PatrolRoute` es válido:
  - Obtener localización del waypoint actual: `PatrolRoute.GetWaypointLocation(CurrentWaypointIndex)`.
  - `AI Move To` (Destination: WaypointLocation, Acceptance Radius: 60.0).
  - En `OnSuccess`:
    - `CurrentWaypointIndex = (CurrentWaypointIndex + 1) % PatrolRoute.GetNumWaypoints()`.

#### Rama `Suspicious`:
- Detener movimiento (`StopMovementImmediately`).
- `Find Look At Rotation` hacia `TargetActor.GetActorLocation()`.
- Rotar suavemente hacia el jugador.

#### Rama `Investigate`:
- `AI Move To` hacia `LastKnownPlayerLocation`.
- En `OnSuccess` o `OnFail` (tras esperar 2 segundos con `Delay`):
  - `Set CurrentAIState = Return`.
  - Disparar `OnEnemyStateChanged(Return)`.

#### Rama `Chase`:
- `CharacterMovement.MaxWalkSpeed = RunSpeed`.
- `AI Move To` hacia `TargetActor` (Acceptance Radius: `AttackRange - 20.0`).
- Si Distancia <= `AttackRange`:
  - `Set CurrentAIState = Combat`.
  - Disparar `OnEnemyStateChanged(Combat)`.

#### Rama `Combat`:
- Si Distancia > `AttackRange * 1.5`:
  - `Set CurrentAIState = Chase`.
  - Disparar `OnEnemyStateChanged(Chase)`.
- Si `bCanAttack == true` y Distancia <= `AttackRange`:
  - Ejecutar secuencia de ataque:
    1. `bCanAttack = false`.
    2. Disparar `OnTelegraphStarted(EAttackType::EnemyBasic, 0.8)`. (Muestra aviso o animación de carga).
    3. `Delay(0.8)`.
    4. Comprobar si sigue en rango y no congelado/aturdido:
       - Armar estructura `ST_HitInfo`:
         - `Damage = AttackDamage`
         - `PostureDamage = PostureDamage`
         - `AttackType = EAttackType::EnemyBasic`
         - `Instigator = Self`
         - `HitLocation = TargetActor.GetActorLocation()`
         - `HitDirection = Normal(TargetActor.GetActorLocation() - GetActorLocation())`
         - `bParryable = true`
         - `bNonLethal = false`
       - Llamar interfaz `BPI_Damageable.ReceiveHit(HitInfo)` sobre `TargetActor`.
       - `Switch on EHitResult`:
         - `Parried`:
           - **El jugador hizo parry perfecto.**
           - `CurrentPosture -= 20.0`.
           - Si `CurrentPosture <= 0.0`:
             - `Set CurrentAIState = Stunned`.
             - Disparar `OnEnemyStateChanged(Stunned)`.
             - Activar timer de aturdimiento (`1.8` s).
         - `Blocked`: Reproducir feedback de impacto bloqueado.
         - `Hit`: Daño aplicado con éxito al jugador.
         - `Dodged`: El jugador esquivó.
    5. `Delay(1.2)` (tiempo de cooldown).
    6. `bCanAttack = true`.

#### Rama `Return`:
- `CharacterMovement.MaxWalkSpeed = WalkSpeed`.
- Moverse hacia el waypoint de inicio de patrulla.
- Al llegar: `Set CurrentAIState = Patrol`.

---

### 5.5. Implementación de Interfaces en `BP_GuardBase`

#### 1. `BPI_Damageable`
- **`ReceiveHit(HitInfo: ST_HitInfo) -> EHitResult`**:
  - Si `CurrentAIState == Defeated`: Return `Ignored`.
  - Restar `HitInfo.Damage` del `HealthComponent`.
  - Restar `HitInfo.PostureDamage` de `CurrentPosture`.
  - Si `CurrentPosture <= 0.0` y `CurrentAIState != Defeated`:
    - `Set CurrentAIState = Stunned`.
    - Disparar `OnEnemyStateChanged(Stunned)`.
    - `SetTimerByEvent` para restaurar postura y volver a `Combat` tras `1.8` segundos.
  - Return `Hit`.

- **`IsDefeated() -> Boolean`**:
  - Return `CurrentAIState == Defeated`.

#### 2. `BPI_TimeAffectable`
- **`CanBeTemporalCutTarget() -> Boolean`**:
  - Return `(CurrentAIState != Defeated) AND (bIsTemporalFrozen == false)`.

- **`ApplyTemporalFreeze(Duration: Float, PostureDamage: Float) -> Float`**:
  - `bIsTemporalFrozen = true`.
  - `FrozenPreState = CurrentAIState`.
  - `CurrentAIState = TemporalFrozen`.
  - Disparar `OnEnemyStateChanged(TemporalFrozen)`.
  - `StopMovementImmediately()`.
  - `CustomTimeDilation = 0.0` (congela animaciones y lógica local).
  - Restar `PostureDamage` de `CurrentPosture`.
  - Crear `SetTimerByEvent` con tiempo `Duration`:
    - Al disparar:
      - `CustomTimeDilation = 1.0`.
      - `bIsTemporalFrozen = false`.
      - Si `CurrentPosture <= 0.0`: `CurrentAIState = Stunned`.
      - Else: `CurrentAIState = Combat` (o restaurar `FrozenPreState`).
      - Disparar `OnEnemyStateChanged(CurrentAIState)`.
  - Return `Duration`.

#### 3. `BPI_Interactable` (Remate No Letal cuando está aturdido)
- **`CanInteract(Interactor: Actor) -> Boolean`**:
  - Return `(CurrentAIState == Stunned)`.

- **`GetInteractionText(Interactor: Actor) -> Text`**:
  - Return `"Take Down"` (en inglés).

- **`GetInteractionPriority() -> Integer`**:
  - Return `100` (prioridad de remate según contrato).

- **`Interact(Interactor: Actor) -> Void`**:
  - Llamar `BPI_PlayerControl.RequestFinisher(Self)` sobre `Interactor`.
  - `Set CurrentAIState = Defeated`.
  - Disparar `OnEnemyStateChanged(Defeated)`.
  - Desactivar colisiones de cápsula: `SetActorEnableCollision(false)`.
  - Reportar evento narrativo:
    - `GetGameState() -> BPI_StoryEvents.ReportStoryEvent(EnemyNeutralized, Self, "PursuerNeutralized")`.

#### 4. `BPI_CheckpointListener`
- **`OnCheckpointRestore(CheckpointId: Name, RespawnTransform: Transform)`**:
  - Si el enemigo estaba derrotado pero pertenece a una sección posterior al checkpoint, reactivar con salud y postura restauradas.
  - Resetear `CurrentAIState = Patrol`.
  - `bIsTemporalFrozen = false`.
  - `CustomTimeDilation = 1.0`.

---

## 6. Subclases de Enemigos

### 6.1. `BP_Pursuer` (Perseguidor Común)
- Padre: `BP_GuardBase`
- Class Defaults:
  - `VisionRange = 1800.0`
  - `WalkSpeed = 130.0`
  - `RunSpeed = 240.0`
  - `AttackDamage = 12.0`
  - `PostureDamage = 8.0`
  - `bNonLethalCivilian = true`

### 6.2. `BP_Interventor` (Agente Interventor)
- Padre: `BP_GuardBase`
- Class Defaults:
  - `VisionRange = 2000.0`
  - `WalkSpeed = 120.0`
  - `RunSpeed = 220.0`
  - `AttackDamage = 18.0`
  - `PostureDamage = 12.0`
  - `MaxPosture = 50.0`
- Lógica adicional (Conversión Aliado → Hostil):
  - En `BeginPlay`, enlazarse al `ObjectiveManager` de `BP_GameState`:
    - `Bind Event to OnDialogueFinished`.
  - En el evento enlazado:
    - Si `RowName == "Correction_Order"`:
      - `Set CurrentAIState = Chase`.
      - Disparar `OnEnemyStateChanged(Chase)`.
      - `GetGameState() -> BPI_StoryEvents.ReportStoryEvent(InterventorTurnedHostile, Self, "RefugeApproach")`.

### 6.3. `BP_Supervisor` (Jefe de Continuidad)
- Padre: `BP_GuardBase`
- Class Defaults:
  - `VisionRange = 2400.0`
  - `WalkSpeed = 110.0`
  - `RunSpeed = 200.0`
  - `AttackDamage = 26.0`
  - `PostureDamage = 18.0`
  - `MaxPosture = 90.0`
- Sobrescritura de `ApplyTemporalFreeze`:
  - El Supervisor **resiste parcialmente el Corte Temporal**:
  - Multiplica `Duration` por `0.5` antes de aplicar el timer.
  - Retorna `Duration * 0.5`.
- Eventos de jefe:
  - Al entrar en `Combat`: `ReportStoryEvent(SupervisorEncounterStarted, Self, "FinalBoss")`.
  - Al ser derrotado: `ReportStoryEvent(SupervisorDefeated, Self, "FinalBoss")`.

---

## 7. `BP_Jack` (NPC Jack)

Ubicación: `Content/Unscripted/Enemies/Jack/BP_Jack`  
Padre: `Character`  
Interfaces: `BPI_Interactable`, `BPI_CheckpointListener`

### 7.1. Variables
- `Waypoints` (Array de `Actor` o `Transform`): Puntos de la ruta de escape hacia el refugio.
- `CurrentWaypointIndex` (Integer): Default = `0`.
- `bJackFound` (Boolean): Default = `false`.
- `bEscaping` (Boolean): Default = `false`.
- `bReachedRefuge` (Boolean): Default = `false`.

### 7.2. Interfaz `BPI_Interactable`
- **`CanInteract(Interactor: Actor) -> Boolean`**:
  - Return `(bJackFound == false)`.
- **`GetInteractionText(Interactor: Actor) -> Text`**:
  - Return `"Speak with Jack"` (en inglés).
- **`GetInteractionPriority() -> Integer`**:
  - Return `60` (prioridad de diálogo según contrato).
- **`Interact(Interactor: Actor) -> Void`**:
  - `bJackFound = true`.
  - `GetGameState() -> BPI_StoryEvents.ReportStoryEvent(JackFound, Self, "Workshop")`.

### 7.3. Lógica de Escape
- En `BeginPlay`:
  - Obtener `ObjectiveManager` de `BP_GameState`.
  - `Bind Event to OnStoryPhaseChanged`.
- En el evento enlazado:
  - Si `NewPhase == ProtectJack`:
    - `bEscaping = true`.
- En `Event Tick`:
  - Si `bEscaping == true` y `bReachedRefuge == false`:
    - Moverse hacia `Waypoints[CurrentWaypointIndex]` con `AI Move To`.
    - Al llegar (`OnSuccess`):
      - Si `CurrentWaypointIndex < Waypoints.Num() - 1`:
        - `CurrentWaypointIndex++`.
      - Else:
        - `bReachedRefuge = true`.
        - `bEscaping = false`.
        - `GetGameState() -> BPI_StoryEvents.ReportStoryEvent(JackReachedRefuge, Self, "Refuge")`.

---

## 8. Validación en `L_Test_B`

1. Abrir `Content/Unscripted/Maps/Test/L_Test_B`.
2. Verificar que existe:
   - Suelo con colisión.
   - `NavMeshBoundsVolume` cubriendo todo el suelo (pulsar `P` para ver la malla verde).
   - `PlayerStart`.
   - 1 actor `BP_PatrolRoute` con 3 waypoints configurados en el viewport.
   - 2 instancias de `BP_Pursuer` asignadas a la ruta.
   - 1 instancia de `BP_Jack` colocado cerca de cajas de cobertura.
3. Ejecutar Play (PIE):
   - [ ] Comprobar que los enemigos recorren sus waypoints en estado `Patrol`.
   - [ ] Acercarse de pie dentro del cono: pasan a `Suspicious` y la barra de alerta sube.
   - [ ] Agacharse (Ctrl) o esconderse detrás de cajas: la alerta deja de subir o se reduce.
   - [ ] Si la alerta se llena: pasan a `Chase` y corren hacia el jugador.
   - [ ] En rango cercano: telegrafían el ataque antes de golpear.
   - [ ] Probar el Corte Temporal (F): el enemigo se congela, detiene su animación y retoma su estado al terminar.
   - [ ] Al agotar su postura: el enemigo queda en `Stunned` y muestra el prompt `"Take Down"`.
   - [ ] Pulsar E en el enemigo aturdido: se ejecuta el remate no letal y pasa a `Defeated`.
   - [ ] Interactuar con Jack: reporta `JackFound`.
