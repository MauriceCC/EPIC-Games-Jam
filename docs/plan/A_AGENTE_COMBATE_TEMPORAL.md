# División A — Agente: jugador, combate y poderes temporales

> **Base confirmada:** Unscripted · UE 5.8.4 · Blueprint. Todo contenido para el jugador debe estar en inglés, incluidos placeholders visibles. Ver [arranque F0](02_ARRANQUE_F0.md). Las rutas de contenido son relativas a `Unscripted/`; `Scripts/` y `SourceData/` parten del repositorio.

**Persona:** Mauricio (confirmado 2026-11-15) · **Rama:** `a/<tarea>` · **Commits:** `[A] …`

## 1. Misión

Que controlar al agente **se sienta bien**: moverse en isométrico, apuntar con el mouse, encadenar golpes, esquivar, hacer parry, interrumpir con Corte de Fotograma y corregir errores con Retoma. Es la división de la que depende el *game feel*.

**Fuentes de diseño:** `docs/02` (cámara, controles), `docs/03` (combate y balance), `docs/04` (Corte y Retoma), `docs/06` (implementación sugerida).

## 2. Propiedad

- `Content/Unscripted/Player/` (incluye `Input/`, `Animation/`, `Test/`)
- `Maps/Test/L_Test_A`
- `SourceData/A/`, `Scripts/A/`, `Source/Unscripted/Player/` (si hay C++)
- Este archivo.

**No tocas:** `Core/`, enemigos, interactuables, HUD, mapas de `L_Whitechapel`.

## 3. Lo que provees y lo que consumes

| Provees (contrato) | A quién |
|---|---|
| `BP_PlayerCharacter` implementando `BPI_Damageable`, `BPI_PlayerControl`, `BPI_CheckpointListener` | B, C |
| Dispatchers de `BP_HealthComponent`, `BP_CombatComponent`, `BP_TemporalComponent` | C (HUD), D (post-proceso) |
| `BP_HealthComponent` reutilizable (lo usan los enemigos) | B |
| Llamadas a `ReceiveCombatHit` y `ApplyTemporalFreeze` sobre objetivos | B |

| Consumes | De quién | Mientras no exista… |
|---|---|---|
| Enemigos con `BPI_Damageable` / `BPI_TimeAffectable` | B | Tu propio `BP_TestDummy_A` en `Player/Test/` |
| `BP_StealthComponent.SetCrouched` | B | El cascarón de F0 no hace nada: no pasa nada |
| `ReportStoryEvent(PlayerDefeated)` → respawn | C | En `L_Test_A`, recarga el nivel |
| VFX/SFX placeholders (`NS_*`, `SC_*`, `PP_Retake`) | D | Ya existen como placeholders desde F0 |

## 4. Backlog

Prioridad: **P0** = versión mínima (`docs/07`), **P1** = mejora importante, **P2** = extensión (solo tras hito F3).

### F1 — Sistemas aislados en `L_Test_A`

| ID | Tarea | Prioridad | Criterio de aceptación |
|---|---|---|---|
| A-01 | Input: `IA_*` y `IMC_Default` según `docs/06` | P0 | Todas las acciones de la tabla de controles disparan un Print en test |
| A-02 | Cámara isométrica (Pitch -55°, Yaw 45°) y movimiento WASD relativo a cámara | P0 | El personaje se mueve en diagonal correcto respecto a pantalla |
| A-03 | Orientación hacia el cursor (proyección del cursor en el plano del suelo) | P0 | El personaje mira al cursor en todo el mapa, también en pendientes suaves |
| A-04 | `BP_HealthComponent` (salud, acotado [0,máx], `OnHealthChanged`, `OnDepleted`) | P0 | Reutilizable en cualquier actor; probado en el dummy |
| A-05 | Resistencia en `BP_CombatComponent` (costes, regeneración 30/s tras pausa) | P0 | Sin resistencia no se puede atacar/esquivar; HUD de prueba la muestra |
| A-06 | `ECombatState` del jugador y tabla de transiciones permitidas | P0 | Ninguna acción se inicia desde un estado no permitido; siempre vuelve a `Idle` |
| A-07 | Combo ligero x3 con montages + notifies (ventana de combo, ventana de impacto) | P0 | Golpe 3 empuja; clicks fuera de ventana no encadenan |
| A-08 | Detección de impacto: trazas en arco frontal en la ventana, set de actores ya golpeados | P0 | Cada actor recibe **un** `ReceiveCombatHit` por golpe |
| A-09 | Ataque fuerte (daño 28, rompe bloqueo) | P0 | Contra un dummy que bloquea, el fuerte entra |
| A-10 | Esquiva con i-frames parciales (`Dodged`) | P0 | Golpe que llega en i-frames devuelve `Dodged` |
| A-11 | Parry: ventana ~0,2 s por notify; `ReceiveCombatHit` devuelve `Parried` | P0 | Un dummy que ataca cada 2 s puede ser parryado consistentemente |
| A-12 | `DT_PlayerBalance` + CSV en `SourceData/A/` con todos los valores de `docs/03` | P0 | Cambiar el CSV y reimportar cambia el juego sin tocar nodos |
| A-13 | Corte de Fotograma: selección de objetivo, `ApplyTemporalFreeze`, cooldown 10 s, dispatcher | P0 | El dummy se congela 0,8 s; cooldown visible en HUD de prueba |
| A-14 | Retoma: buffer circular de 50 snapshots cada 0,1 s (`ST_RewindSnapshot`) | P0 | Debug draw de la estela de posiciones |
| A-15 | Retoma: activación, validación de destino seguro, restauración, consumo de carga | P0 | No restaura dentro de geometría; las cargas **no** vuelven; el dummy conserva el daño |
| A-16 | `BPI_PlayerControl` completo (input on/off, bloquear Retoma, limpiar historial, `RequestFinisher`) | P0 | Llamable desde un Blueprint de prueba |
| A-17 | Agacharse (Ctrl): velocidad reducida + `SetCrouched` al Stealth | P0 | |
| A-18 | Muerte: `OnDepleted` → oferta de Retoma o `ReportStoryEvent(PlayerDefeated)` | P0 | Decidir con C el UX (ver §6) |

**Mínimo F1 (hito):** en `L_Test_A`, contra 2 dummies, se puede combear, hacer parry, esquivar, cortar y retomar, con valores desde DataTable.

### F2 — Vertical slice en `L_Whitechapel`

| ID | Tarea | Prioridad | Criterio |
|---|---|---|---|
| A-20 | Probar contra `BP_Pursuer` real de B; ajustar trazas/alcances | P0 | Pelea con 2 Perseguidores jugable |
| A-21 | Remate contextual vía `RequestFinisher` | P0 | Enemigo aturdido + E = remate no letal |
| A-22 | `OnCheckpointRestore`: reaparecer, restaurar 2 cargas, salud según balance | P0 | Probado con el checkpoint de C |
| A-23 | Enganchar VFX/SFX placeholders de D (golpe, parry, corte, retoma) | P1 | |
| A-24 | Ataque sigiloso desde no-detectado (consultar `GetVisibilityMultiplier`/estado del enemigo) | P1 | Acordar con B cómo saber si el enemigo no te ha detectado |

### F3 — Contenido

| ID | Tarea | Prioridad |
|---|---|---|
| A-30 | Ajuste de feel contra Interventor (bloqueo) y Supervisor (resistencia a Corte) | P0 |
| A-31 | Hit-stop/screen shake leve en impactos | P1 |
| A-32 | Ataque fuerte cargable | P2 |
| A-33 | Salto de Fotograma / Eco de una Toma (`docs/04`) | P2 |

### F4 — Pulido

Balance por DataTable con los resultados de playtesting, bugs, nada de mecánicas nuevas.

## 5. Notas técnicas

- **Animaciones:** la fuente (Mannequin UE5, Mixamo, Fab) se decide en el kickoff. Si se usa el esqueleto del Mannequin, B puede reutilizar el retarget. Los montages son tuyos; la malla final del agente puede venir de D (se cambia en tu BP, lo haces tú).
- **Retoma y mundo que no rebobina:** usar `Sweep`/`Capsule Overlap` en el destino; si no es seguro, probar snapshots más recientes; si ninguno, cancelar sin consumir carga.
- **No usar `Global Time Dilation`** para el Corte (`docs/04`).
- Las cargas de Retoma viven **fuera** del snapshot.

## 6. Decisiones abiertas de la división

- UX al llegar a 0 de salud con cargas: ¿Retoma automática, ventana de "cámara lenta + pulsa R", o muerte directa? *(propuesta: cámara lenta 1 s para pulsar R)* — acordar con C.
- ¿Mantener o no la carga del golpe fuerte? (P2 por defecto).

## 7. Prompt de arranque para tu agente

```text
Trabajo en la División A (Agente: jugador, combate y poderes temporales) del proyecto Unscripted (UE 5.8.4, Blueprint).
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/A_AGENTE_COMBATE_TEMPORAL.md y después docs/02, docs/03, docs/04 y docs/06.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: solo puedo modificar Content/Unscripted/Player/, Maps/Test/L_Test_A, SourceData/A/, Scripts/A/
y mi archivo de división. Respeta exactamente las firmas del contrato v<versión>.
Entrégame: (1) los pasos para construirlo en Blueprint, nodo a nodo, indicando en qué asset va cada cosa;
(2) los datos de DataTable en CSV si aplica; (3) cómo probarlo en L_Test_A;
(4) si necesitas algo fuera de mis carpetas, redáctalo como solicitud de contrato y no lo implementes.
```

## 8. Solicitudes de contrato

| # | Fecha | Petición | A quién | Estado |
|---|---|---|---|---|
| A-CON-01 | 2026-11-14 | Renombrar `BPI_Damageable.ReceiveHit` a `ReceiveCombatHit`, conservando entrada `HitInfo: ST_HitInfo` y salida `Result: EHitResult`. El nombre anterior colisiona con `AActor.ReceiveHit` (DisplayName Hit, parámetro MyComp), impidiendo compilar PlayerCharacter. Actualizar contrato, guías y consumidores A/B; reconstruir la implementación afectada en el editor si conserva la firma nativa. | Integrador y B | Aprobado por el usuario; documentación actualizada. Migración y compilación en Unreal pendientes |

Evidencia A-CON-01: capturas del usuario muestran `ReceiveHit` en la interfaz y `Hit` en PlayerCharacter, con error de firma diferente y parámetro `MyComp`. La [API oficial de AActor::ReceiveHit](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/AActor/ReceiveHit) confirma ese nombre nativo y sus parámetros. La causa no es un parámetro MyComp añadido por el usuario. No editar binarios como texto ni renombrar únicamente la implementación local.

## 9. Estado

### Revisión documental 2026-11-14 (`main` @ `4afcd57`)

- A-01–03: Input Actions e `IMC_Default` ya presentes; el historial registra movimiento base (`8b0c65f`), mensajes (`8e6dd52`) e integración. El log local muestra Play en `L_Test_A`. Falta verificar cada criterio de input, cámara y orientación; la nota antigua «pendiente de crear assets» ya no describe el inventario actual.
- Health, Combat y Temporal existen. No se localizaron DataTable de jugador, snapshot ni montages propios bajo `Content/Unscripted/`; revisar grafos antes de completar A-04–18. No está acreditado el mínimo F1.
- Próximo trabajo **[PROPUESTA]**: validar movimiento y A-CON-01, después cerrar salud/resistencia/combate y Corte/Retoma con dummies; integrar con B/C para remate, muerte y checkpoint. Ver [secuencia y criterios](03_ESTADO_Y_SIGUIENTES_PASOS.md).

Las notas del día que siguen son historial de preparación.

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte A) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

Notas del día:

- 2026-11-15: **Sprint MVP (`05_SPRINT_MVP_2H §4.1`) A1–A4 implementados y validados técnicamente** en `a/sprint-mvp`. A1 (A-16 mínimo): `SetRetakeBlocked`, `ClearRetakeHistory` y `SetGameplayInputEnabled` con efecto real en el jugador. A2: sin `PrintString` de depuración en el controlador. A3: `ReceiveCombatHit` devuelve `Ignored`/`Dodged`/`Parried`/`Hit`. A4 **[PROPUESTA]**: Esc dos veces → salir, hasta que exista `WBP_Pause`. Compilan las 58 Blueprints; 27 comprobaciones tras recarga. Pendiente la prueba en Play. [Detalle y prueba](../../Scripts/A/A_SPRINT_MVP.md).
- 2026-11-15: **Sprint MVP A6 y A7 (P1) implementados y validados técnicamente.** A6: la Retoma rebobina también la resistencia. Corregido además que, tras reaparecer en un checkpoint, R rebobinaba a antes de la muerte: ahora el respawn vacía el historial. A7: el Corte exige línea de visión (Visibility; los Pawns no bloquean). 15 comprobaciones funcionales con el editor completo; A1–A4 siguen en 27/27 y las 58 Blueprints compilan. A8 (P2) sin empezar.
- 2026-11-15: **Sprint MVP A8 (P2) [PROPUESTA] implementado y validado técnicamente:** hit-stop de 0,06 s solo en el enemigo golpeado y sacudida de cámara `CS_PlayerHit_A` al recibir daño. 15 comprobaciones; sin regresiones en A1–A7. **Parte A del sprint completa** salvo A4 con `WBP_Pause` (depende de C3) y A5 (integración manual). Pendiente la prueba en Play.

- 2026-11-15: **A-05 implementado y validado técnicamente** sobre `be77859`, por petición de Mauricio, aunque `04_PLAN_DE_CIERRE §4` proponía recortarlo. `BP_CombatComponent` tiene resistencia 100, regeneración de 30/s tras una pausa de 0,6 s **[PROPUESTA]** y costes de docs/03. Usa `SetStamina`, `HasStamina` y `TryConsumeStamina`, y emite `OnStaminaChanged`. Ligero, esquiva y parry del jugador requieren el coste completo; sin él no se ejecutan. HUD de prueba `Player/Test/BP_StaminaHUDTest_A` colocado en `L_Test_A`. 140 comprobaciones tras recarga; firmas compartidas y resto de grafos del jugador preservados. [Guía, evidencia y prueba visual](../../Scripts/A/A05_RESISTENCIA.md). Pendiente aceptación visual en Play. El coste del fuerte espera a A-09 y la resistencia en Retoma, a A-14/15. Para C-21: `OnStaminaChanged` del Combat del jugador ya emite valores reales.

- 2026-11-15: **A-03 confirmado funcional por Mauricio**, commit `e95d5b9`. **A-04 implementado y validado técnicamente**: Health instalado 100/100; actualización acotada y notificación con valores capturados; OnDepleted solo en transición positiva→cero. Probado en dos actores dummy transitorios con dos observadores reales, tras recargar los assets. Firmas compartidas y grafos del jugador preservados. [Guía, propuestas locales, evidencia y prueba visual](../../Scripts/A/A04_SALUD.md). Pendiente aceptación visual del HUD en Play; no implica cierre de A-18/A-22 ni F1. Siguiente: A-05, resistencia.

- 2026-11-15: A-03 implementado sobre `b2ceb53`, tras revisar los cambios del pull de C/D. Tick llama a `A_UpdateCursorFacing` (local y vivo), reutilizando `FaceCursor`; CharacterMovement deja de girar hacia WASD. Solo se guardó `BP_PlayerCharacter`. Compilación y 16 comprobaciones tras recarga correctas; pendiente aceptación visual con mouse y pendientes en `L_Test_A`. [Cambio, evidencia y prueba paso a paso](../../Scripts/A/A03_ORIENTACION_CONTINUA.md). No se marca F1 completo. El handoff nuevo de C sitúa la salud del componente instalado y checkpoints entre los siguientes pendientes de A.

- 2026-11-15: auditoría de los assets guardados con Unreal 5.8.4, sin editar ni guardar paquetes. Confirmados BeginPlay/IMC y mappings; hay movimiento, salud y combate/poderes provisionales en PlayerCharacter. Detectadas diferencias de contrato, fuerte enlazado al ligero, ausencia de resistencia y Retoma sin destino seguro. [Informe y límites](../../Scripts/A/AUDITORIA_A_2026_11_15.md). No se ejecutó Play ni se marca A-01/F1 completo. Las notas anteriores son históricas.

- 2026-11-14: A-01 iniciada como guía de implementación: [Input en Blueprint](../../Scripts/A/A01_INPUT_BLUEPRINT.md). Pendiente de crear assets y verificar en Unreal; no se marca terminada.
- **[PROPUESTA]** Mientras F0 no exista, probar input con `BP_InputTestController_A` y `BP_InputTestGameMode_A` en `Player/Test/`, usando solo `L_Test_A`. No sustituye F0 ni modifica contratos. Tras F0, llevar las conexiones al controlador de A.
- **[PROPUESTA]** Añadir `IA_Pause` para comprobar Esc; acumulación Cumulative para WASD. Son decisiones locales de A-01; la implementación del menú pertenece a C.
