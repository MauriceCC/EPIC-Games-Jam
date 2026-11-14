# División A — Agente: jugador, combate y poderes temporales

**Persona:** _(nombre)_ · **Rama:** `a/<tarea>` · **Commits:** `[A] …`

## 1. Misión

Que controlar al agente **se sienta bien**: moverse en isométrico, apuntar con el mouse, encadenar golpes, esquivar, hacer parry, interrumpir con Corte de Fotograma y corregir errores con Retoma. Es la división de la que depende el *game feel*.

**Fuentes de diseño:** `docs/02` (cámara, controles), `docs/03` (combate y balance), `docs/04` (Corte y Retoma), `docs/06` (implementación sugerida).

## 2. Propiedad

- `Content/CorteFinal/Player/` (incluye `Input/`, `Animation/`, `Test/`)
- `Maps/Test/L_Test_A`
- `SourceData/A/`, `Scripts/A/`, `Source/CorteFinal/Player/` (si hay C++)
- Este archivo.

**No tocas:** `Core/`, enemigos, interactuables, HUD, mapas de `L_Whitechapel`.

## 3. Lo que provees y lo que consumes

| Provees (contrato) | A quién |
|---|---|
| `BP_PlayerCharacter` implementando `BPI_Damageable`, `BPI_PlayerControl`, `BPI_CheckpointListener` | B, C |
| Dispatchers de `BP_HealthComponent`, `BP_CombatComponent`, `BP_TemporalComponent` | C (HUD), D (post-proceso) |
| `BP_HealthComponent` reutilizable (lo usan los enemigos) | B |
| Llamadas a `ReceiveHit` y `ApplyTemporalFreeze` sobre objetivos | B |

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
| A-08 | Detección de impacto: trazas en arco frontal en la ventana, set de actores ya golpeados | P0 | Cada actor recibe **un** `ReceiveHit` por golpe |
| A-09 | Ataque fuerte (daño 28, rompe bloqueo) | P0 | Contra un dummy que bloquea, el fuerte entra |
| A-10 | Esquiva con i-frames parciales (`Dodged`) | P0 | Golpe que llega en i-frames devuelve `Dodged` |
| A-11 | Parry: ventana ~0,2 s por notify; `ReceiveHit` devuelve `Parried` | P0 | Un dummy que ataca cada 2 s puede ser parryado consistentemente |
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
Trabajo en la División A (Agente: jugador, combate y poderes temporales) del proyecto CORTE FINAL (UE5).
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/A_AGENTE_COMBATE_TEMPORAL.md y después docs/02, docs/03, docs/04 y docs/06.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: solo puedo modificar Content/CorteFinal/Player/, Maps/Test/L_Test_A, SourceData/A/, Scripts/A/
y mi archivo de división. Respeta exactamente las firmas del contrato v<versión>.
Entrégame: (1) los pasos para construirlo en Blueprint, nodo a nodo, indicando en qué asset va cada cosa;
(2) los datos de DataTable en CSV si aplica; (3) cómo probarlo en L_Test_A;
(4) si necesitas algo fuera de mis carpetas, redáctalo como solicitud de contrato y no lo implementes.
```

## 8. Solicitudes de contrato

| # | Fecha | Petición | A quién | Estado |
|---|---|---|---|---|
| | | | | |

## 9. Estado

- [ ] Mínimo F1 alcanzado
- [ ] Vertical slice F2 (parte A) en `main`
- [ ] F3 completo
- [ ] F4 cerrado

Notas del día:
