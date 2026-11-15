# Auditoría de A — 2026-11-15

Responsable de A confirmado por el usuario: Mauricio.

## Método y límites

Inspección de assets guardados mediante Unreal Engine 5.8.4, usando un proceso
UnrealEditor-Cmd con Python y NullRHI. No se modificaron grafos ni se guardaron
paquetes. No se ejecutó Play ni se certificó el comportamiento en partida.
Los cambios sin guardar del editor abierto no forman parte de esta inspección.

Extractor: `audit_a_readonly.py`. Evidencia: `audit_a_readonly.json`.
El proceso final terminó con código 0. Su warning corresponde a una API de
inspección obsoleta (`get_object`), no a una compilación fallida del juego.
Los campos `_error` de propiedades nativas cualificadas en el JSON son límites
de la reflexión del extractor, no errores acreditados de los Blueprints.
No se ejecutó una recompilación explícita de los Blueprints.

## Bloque confirmado en BP_PlayerController

Se inspeccionaron las conexiones de los pines, no solo los nombres de nodos:

1. BeginPlay → Branch, condición IsLocalController.
2. True → macro Is Valid.
3. Self → EnhancedInputLocalPlayerSubsystem; su resultado alimenta InputObject
   de Is Valid y el Target de AddMappingContext.
4. Is Valid → AddMappingContext, con
   `/Game/Unscripted/Player/Input/IMC_Default.IMC_Default`, Priority 0.
5. AddMappingContext → Set bShowMouseCursor = true.
6. Set bShowMouseCursor → SetInputMode_GameOnly, PlayerController = Self.

Existe una llamada a AddMappingContext en los grafos inspeccionados del
controlador. El valor inicial de ShowMouseCursor es false, pero la cadena lo
establece a true durante BeginPlay: no confundir ambos momentos.

## Input guardado

Las 12 Input Actions existen: Move y LookMouse son Axis2D; las demás Boolean.
IMC_Default contiene 15 mappings: 4 de WASD y los otros 11 controles.
Move usa Cumulative; D sin modificadores, A Negate X, W Swizzle YXZ,
S Negate X seguido de Swizzle YXZ. LookMouse usa Mouse2D.

| Entrada | Conexión real en el controlador |
|---|---|
| WASD | Triggered → Cast del pawn a PlayerCharacter → DoMove(X,Y) |
| Clic izquierdo | Started → DoLightAttack |
| Clic derecho | Started → DoLightAttack también; no hay ataque fuerte distinto |
| Espacio | Started → DoDodge |
| Q | Started → DoParry |
| F | Started → DoTemporalCut |
| R | Started → DoRetake |
| E | PrintString: Interact |
| Ctrl | PrintString: Crouch; Completed/Canceled sin conectar |
| Tab | PrintString: Checklist |
| Esc | PrintString: Pause requested |
| Mouse | Triggered imprime Vector2D; Completed imprime Mouse stopped |

No hay llamada continua a FaceCursor en el controlador. En los grafos de A,
FaceCursor se llama desde DoLightAttack. El movimiento no tiene los prints de
Completed/Canceled de la guía original. Los casts fallidos no tienen diagnóstico.

## Estado de sistemas de A

| Área | Evidencia y diferencia respecto al backlog |
|---|---|
| Cámara | CameraComponent perspectiva FOV 40; SpringArm pitch -55, yaw 45, longitud 1700, prueba de colisión desactivada. Encuadre y oclusión pendientes de Play |
| Movimiento | DoMove conectado; direcciones fijas (0.7071,0.7071,0) y (-0.7071,0.7071,0), acordes con yaw 45. Bloquea movimiento si muerto o atacando. No consulta dinámicamente la cámara |
| Orientación | FaceCursor tiene traza bajo cursor, LookAt y SetActorRotation. Solo llamada al iniciar ataque en los grafos inspeccionados; A-03 no está completo |
| Salud | MaxHealth/CurrentHealth = 100; BeginPlay inicializa; ApplyHealthDamage resta, acota y emite avisos; SetHealth acota y emite OnHealthChanged. Pruebas de límites y reutilización pendientes |
| Resistencia/estados | CombatComponent tiene declaraciones OnStaminaChanged/OnCombatStateChanged; BeginPlay/Tick sin lógica conectada. No hay sistema de costes/regeneración ni máquina ECombatState implementada en A |
| Ataque ligero | Alterna dos AnimSequence con PlayOneShot y temporizadores; no es combo x3 con ventanas de montage/notifies |
| Impacto | AttackHit busca BP_GuardBase por clase y proximidad; usa ApplyDamage nativo con daño 25. No usa ReceiveCombatHit/ST_HitInfo hacia B ni trazas de ventana de impacto |
| Ataque fuerte | No hay DoHeavyAttack; clic derecho ejecuta el ligero |
| Esquiva/parry | Hay LaunchCharacter, animaciones y booleanos temporizados bInvulnerable/bParryWindow; no gastan resistencia |
| Resultado de golpe | Las cuatro salidas de ReceiveCombatHit tienen el mismo literal NewEnumerator0. No distinguen Ignored, Dodged, Parried y Hit, aunque el grafo ramifica por esos casos. No se resolvió el display name del literal en esta auditoría |
| Corte | Selecciona el GuardBase más cercano dentro de 1500 cm; llama su función concreta ApplyTemporalFreeze(1.2,10), emite VFX/audio y cooldown 10 s. No consulta CanBeTemporalCutTarget ni línea de visión; no consume el resultado efectivo por interfaz |
| Retoma | Empieza con 2 cargas. Tick acumula tiempo y registra posición/salud cada ~0.1 s; conserva 30 muestras (~3 s), no las 50 del plan. R toma índice 0, resta una carga, vacía historial y emite avisos/efectos |
| Seguridad de Retoma | SetActorLocation con Sweep=false y Teleport=true; sin validación de destino ni fallback. No guarda orientación ni resistencia, ni consulta bloqueo narrativo |
| Componentes temporales | TemporalComponent declara los tres dispatchers; la lógica de poderes está en PlayerCharacter |
| Control externo/checkpoints | PlayerCharacter sí declara BPI_Damageable, BPI_PlayerControl y BPI_CheckpointListener. GetStealthComponent devuelve el componente. No hay implementaciones de SetGameplayInputEnabled, SetRetakeBlocked, ClearRetakeHistory, RequestFinisher u OnCheckpointRestore en sus grafos inspeccionados |
| Derrota | Die deshabilita movimiento, reporta un evento y programa RestartLevel a los 3 s. El pin Event contiene NewEnumerator0: verificar su significado antes de afirmar que envía PlayerDefeated. No está implementado el restore por checkpoint de A |
| Balance | No se encontró DT_PlayerBalance ni ST_RewindSnapshot en el inventario Player; hay constantes en nodos |

El GameMode compartido guardado referencia BP_PlayerCharacter y
BP_PlayerController, además de GameState/HUD de C. No se inspeccionaron aquí
los overrides de mapas ni la posesión efectiva durante Play.

## Siguiente trabajo [PROPUESTA]

1. Probar en L_Test_A el controlador y pawn realmente activos, WASD y cámara.
2. Completar orientación continua (A-03) conservando el bloque de input existente.
3. Implementar resistencia/estados y balance; después separar ataque fuerte y
   completar el combo con los criterios de A-07–11.
4. Corregir los resultados de ReceiveCombatHit y migrar el ataque al contrato
   con B, sin editar sus assets.
5. Completar seguridad, historial y bloqueos de Retoma y selección del Corte.
6. Implementar las funciones de control/checkpoint de A y conectar E/Ctrl/Tab
   con las operaciones acordadas de B/C. No modificar contratos unilateralmente.

La existencia de estos grafos no marca ningún hito F1/F2 como terminado.
