# 05 — Sprint de mejora del MVP (2 horas)

> Fecha: 2026-11-15. Base: `main` @ `83ee5bf` (`[INT] Integrar propsP0-hudHideout…`).
> Complementa a `04_PLAN_DE_CIERRE.md` (Bloques 0–3). Este sprint **no cambia** el diseño (`docs/01`–`07`) ni los contratos (`01_CONTRATOS_Y_PROPIEDAD.md`). Lo que no está en el diseño va marcado **[PROPUESTA]**.
> Si la entrega de la jam sigue en pie (15-nov 20:59 Lima, code freeze 17:59), este sprint **es** el Bloque 3: solo bugs, legibilidad y build; nada de mecánicas nuevas.

## 1. Dónde estamos (análisis de la documentación y del historial)

Este diagnóstico es **estático**: documentación, scripts, informes JSON e historial Git. No se abrió Unreal ni se jugó. Todo lo marcado "verificar" se confirma en la partida de triaje del minuto 0.

| Área | Lo que ya existe (según commits e informes) | Huecos que afectan al MVP |
|---|---|---|
| **A — Jugador** (Mauricio) | Movimiento WASD isométrico, orientación al cursor (A-03), salud 100/100 (A-04), resistencia con costes y regeneración (A-05), combo de 2 golpes, esquiva, parry, Corte (F), Retoma (R, 2 cargas), muerte → checkpoint (`B_ResumePlayerAtCheckpoint`) | **A-16** sin implementar: `SetRetakeBlocked` / `ClearRetakeHistory` no tienen manejador (C los llama al registrar el final). `ReceiveCombatHit` devuelve **el mismo literal** en las 4 salidas (parry/esquiva no se distinguen para B). Corte sin línea de visión. Prints de depuración en el controlador (E, Ctrl, Tab, **ratón cada frame**, Esc) — verificar si siguen. Esc no pausa |
| **B — Enemigos** (Jesus) | Perseguidores en la Plaza, patrullas del Acto I, combate por turnos (máx. 2), aturdimiento, congelación, neutralización no letal, escolta de Jack hasta el Refugio (`d05b0eb`), Interventor y Supervisor colocados, puerta del Archivo ligada a la derrota del Interventor | `BP_GuardBase` sin interfaces reales (deuda, no bloquea). Golpes enemigos sin traza de oclusión (pegan a través de esquinas). Checkpoint no cancela ataques en *windup*. Problema de NavMesh junto a la tubería del Taller. Falta un recorrido **manual** completo con Jack real (las pruebas de C usaron fixture) |
| **C — Historia/UI** (Daniel) | Transmisión del Director, checklist inicial y reescrito, HUD pulido, diálogo, documentos, escondite, 3 puertas con fase, mensaje del yo futuro, 2 evidencias, *CONTINUITY ALTERED*, 2 estaciones de expediente con confirmación, `WBP_Ending` A y B | **La pantalla final pausa el juego y no tiene salida** (sin menú, reinicio ni créditos: C-33 recortado). No hay pantalla de título ni pausa/salir. Créditos en pantalla pendientes. Revisión de idioma final |
| **D — Mundo/build** (Yizens) | Whitechapel v3 (casas, tejados, aceras, charcos), luz nocturna, niebla, vapor, 9 personajes, 28+ props, VFX, 11 SFX, 4 temas musicales | **No hay ninguna build empaquetada** (no existe `.exe` ni carpeta de staging). Oclusión de cámara sin cerrar (D-20). Música por fase/combate (D-33) por confirmar. Rendimiento sin medir (D-40). `CREDITS.md` con nombres vacíos y licencia de música sin confirmar. Página de la jam |

**Conclusión:** la historia completa ya existe de principio a fin en `main`. El MVP no necesita más contenido; necesita **(1) que una persona pueda jugarlo de Start a cada final sin editor, (2) que pueda salir del juego y (3) un `.exe` que arranque en otro PC.** Todo lo demás es pulido.

## 2. Objetivo del sprint (definición de "hecho")

Al terminar las 2 horas, en `main`:

1. **Build Development (o Shipping) que arranca en un PC distinto** al de desarrollo, sin pantalla de error ni texto de depuración.
2. **Dos partidas manuales completas** (teclado + ratón, sin consola ni scripts de Python), una hasta el Final A y otra hasta el Final B.
3. Desde la pantalla final se puede **salir del juego** (y, si da tiempo, volver a empezar).
4. Morir en cualquier zona reaparece en el último checkpoint sin atascar la historia.
5. Ningún texto en español ni nombre interno (`NewEnumerator0`, `C_SideDoor`, etc.) en pantalla.

## 3. Calendario (T = minutos desde el inicio)

| T | Todos | Puerta |
|---|---|---|
| **0–20** | **Triaje.** Unreal cerrado → `git pull` de `main` → abrir `L_Whitechapel` → **cada uno juega la partida entera** (o hasta atascarse) y anota fallos en la tabla del §6 con la plantilla. Yizens lanza ya el empaquetado (D1) en segundo plano | Lista de bugs priorizada por Mauricio en el grupo (≤ 10 min) |
| **20–75** | Trabajo en la rama propia (§4). Cada uno arregla **primero** los P0 de su división que salieron en el triaje y después sus tareas del §4 | — |
| **75** | **Puerta 1:** cada uno sube su rama; Mauricio fusiona en `main` y juega hasta el Final A | Commit bueno anunciado en el grupo |
| **75–105** | Correcciones de lo que falló en la Puerta 1 + tareas P1. Yizens empaqueta desde el commit de la Puerta 1 | — |
| **105** | **Code freeze.** Solo entra un arreglo si bloquea la partida y lo aprueba Mauricio | — |
| **105–120** | **Puerta 2:** build final desde `main`; partida completa al Final B **en el `.exe`**, en otro PC. Capturas y entrega | Build probada + entrega |

Si algo se retrasa se recorta de los P1, **nunca** de las Puertas.

## 4. Tareas por persona

Prioridad: **P0** = sin esto el MVP no cumple el §2 · **P1** = mejora clara si sobra tiempo · **P2** = solo si todo lo demás está hecho.
Cada tarea indica el asset; nadie toca assets de otra división (`01_CONTRATOS §2`).

### 4.1 Mauricio — División A (jugador) + integrador

Rama: `a/sprint-mvp` · Assets: `Player/`, `Maps/Test/L_Test_A` · Además: fusión en `main`.

| # | Prio | Tarea | Asset | Hecho cuando… |
|---|---|---|---|---|
| A1 | P0 | **A-16 mínimo:** implementar en `BP_PlayerCharacter` los eventos de `BPI_PlayerControl` `SetRetakeBlocked(bBlocked)` (variable `bRetakeBlocked`; `DoRetake` sale si es true) y `ClearRetakeHistory` (vaciar el array de muestras). `SetGameplayInputEnabled` si aún no existe | `Player/BP_PlayerCharacter` | Tras registrar un expediente, R no hace nada y la cuenta de cargas no cambia |
| A2 | P0 | **Limpiar depuración del input:** quitar los `PrintString` de E, Ctrl, Tab, Esc y sobre todo el de `LookMouse` (imprime un Vector2D cada frame). Verificar que E sigue llegando al `BP_InteractionComponent` de C | `Player/BP_PlayerController` | En Play no aparece texto azul/cian de debug |
| A3 | P0 | **Resultados de `ReceiveCombatHit`:** que cada rama devuelva su valor real (`Ignored`, `Dodged`, `Parried`, `Hit`) en vez del mismo `NewEnumerator0` | `Player/BP_PlayerCharacter` | Con Jesus: un parry a un Perseguidor le provoca *stagger*; una esquiva a tiempo no quita salud |
| A4 | P0 | **Esc → salir** [PROPUESTA, mínimo]: Esc abre el `WBP_Pause` que haga Daniel (C3); si no está a tiempo, Esc → `Quit Game` con confirmación de 2 pulsaciones | `Player/BP_PlayerController` | Desde el juego se puede cerrar sin Alt+F4 |
| A5 | P0 | **Integración:** Puerta 1 y Puerta 2 (§3). Fusionar ramas en orden B → C → D → A, compilar todo, jugar | `main` | Commit bueno anunciado |
| A6 | P1 | Retoma: guardar/restaurar resistencia con `SetStamina` (A-15 parcial) y no consumir carga si el historial está vacío | `Player/BP_PlayerCharacter` | R sin muestras no gasta carga |
| A7 | P1 | Corte: ignorar enemigos derrotados y sin línea de visión (line trace al candidato) | `Player/BP_PlayerCharacter` | F no congela a alguien detrás de una pared |
| A8 | P2 | A-31 *hit-stop* leve (0,05 s de `CustomTimeDilation` en el golpeado, **no** global) y *camera shake* pequeño al recibir golpe | `Player/` | El golpe "pesa" |
| — | — | **Decidir en el triaje** (`04_PLAN §5`): morir con cargas = derrota directa → checkpoint | Grupo | Escrito en el grupo |

### 4.2 Jesus — División B (enemigos, Jack, encuentros)

Rama: `b/sprint-mvp` · Assets: `Enemies/`, `L_Whitechapel_AI`, `SourceData/B/`, `Scripts/B/`.

| # | Prio | Tarea | Asset | Hecho cuando… |
|---|---|---|---|---|
| B1 | P0 | **Recorrido manual con Jack real** desde el Taller al Refugio, 3 veces seguidas, incluyendo pelear durante la escolta y morir a mitad. Arreglar lo que lo atasque | `Enemies/Jack/BP_Jack`, `L_Whitechapel_AI` | 3/3 llega al Refugio y se emite `JackReachedRefuge` una vez |
| B2 | P0 | **Checkpoint durante un ataque:** al restaurar, cancelar timers/`Delay` de *windup* (usar `Clear and Invalidate Timer` o una variable de "generación" que invalide el golpe pendiente) y liberar el token de ataque | `Enemies/BP_GuardBase` | Morir justo cuando un enemigo telegrafía no provoca un golpe al reaparecer |
| B3 | P0 | **Interventor y Supervisor jugables sin ayuda:** el Interventor se vuelve hostil tras `Correction_Order`; al vencer al Supervisor se emite `SupervisorDefeated` y la puerta de Registros se abre | `BP_Interventor`, `BP_Supervisor` | Llegar a Registros en una partida manual |
| B4 | P0 | **Quitar depuración:** texto de estado sobre la cabeza (B-01), prints, y comprobar que ningún actor de producción referencia `Enemies/Test/` | `Enemies/` | En Play no hay texto de debug sobre los enemigos |
| B5 | P0 | **Ajuste de balance tras el triaje:** si alguna pelea es injusta o trivial, ajustar salud/daño/windup en `DT_EnemyBalance.csv` y aplicarlo | `SourceData/B/DT_EnemyBalance.csv`, CDOs de B | Un jugador nuevo gana la Plaza en 1–2 intentos y el Supervisor en 2–3 |
| B6 | P1 | **Golpe a través de paredes:** en el impacto del enemigo, añadir line trace (canal Visibility) del enemigo al jugador; si choca, no hay daño | `Enemies/BP_GuardBase` | Junto a una esquina el enemigo no pega a través del muro |
| B7 | P1 | **Legibilidad del telegrafiado** desde la cámara isométrica: windup del Supervisor ≥ 0,6 s con VFX de aviso visible; el Interventor con un aviso distinto para el ataque cargado | `BP_Supervisor`, `BP_Interventor` | Se puede reaccionar con Q/Espacio mirando solo la pantalla |
| B8 | P1 | Con Yizens: tubería del Taller / NavMesh. B confirma con `P` en el editor dónde se corta la navegación; D mueve la tubería o el volumen | Coordinación (el cambio lo hace D en `_Geo`) | Jack y los enemigos no se atascan ahí |
| B9 | P2 | Supervisor: un segundo patrón al 50 % (B-34) | `BP_Supervisor` | Solo si todo P0/P1 está cerrado |

### 4.3 Daniel — División C (historia, interacción, UI)

Rama: `c/sprint-mvp` · Assets: `Narrative/`, `UI/`, `L_Whitechapel_Story`, `SourceData/C/`, `Scripts/C/`.

| # | Prio | Tarea | Asset | Hecho cuando… |
|---|---|---|---|---|
| C1 | P0 | **Salida desde el final:** en `WBP_Ending`, añadir dos botones (con foco de teclado): **"Quit"** → `Quit Game`, y **"Play again"** → `Open Level (L_Whitechapel)` + quitar pausa + `Input Mode Game Only` [PROPUESTA] | `UI/WBP_Ending`, `DT_EndingText` | En los dos finales se puede salir o reiniciar sin editor |
| C2 | P0 | **Partida completa sin fixture** (sin `prepare_*_play.py`): Start → Jack → Refugio → evidencias → revelación → Supervisor → Registros → final. Anotar y arreglar lo que sea de C; pasar a Jesus lo que sea de B | `L_Whitechapel_Story` | Ambos finales alcanzados a mano (uno lo juega Daniel, otro Mauricio en la Puerta 2) |
| C3 | P0 | **Pausa mínima** [PROPUESTA]: `WBP_Pause` con *Resume* y *Quit* (en inglés), que Mauricio abre con Esc (A4). Pausar con `Set Game Paused` y `Input Mode UI Only`; al cerrar restaurar `Game Only` | `UI/WBP_Pause` (nuevo) | Esc → pausa → Resume vuelve al juego con control |
| C4 | P0 | **Revisión de idioma:** recorrer todos los CSV (`DT_Dialogue`, `DT_Checklist`, `DT_HUDText`, `DT_NarrativeText`, `DT_UIStrings`, `DT_EndingText`) y los textos fijos de los WBP. Ni español, ni nombres internos de enums/actores | `SourceData/C/*.csv`, `UI/WBP_*` | Búsqueda de tildes/ñ en los CSV sin resultados; partida sin texto interno |
| C5 | P1 | **Créditos en pantalla:** una página más en `WBP_Ending` (o botón "Credits") con el equipo y las herramientas de IA de `CREDITS.md`. Pedir a Yizens los nombres y la licencia de la música antes de escribirla | `UI/WBP_Ending`, `DT_EndingText` | Se ven los créditos tras cualquier final |
| C6 | P1 | **Onboarding de controles:** en los primeros 30 s, prompts breves en el HUD (WASD move · LMB attack · Space dodge · Q parry · F Frame Cut · R Retake · E interact · Tab dossier), que desaparecen solos | `UI/WBP_HUD`, `DT_HUDText` | Un jugador nuevo sabe qué hace F y R sin leer la página |
| C7 | P1 | **Pantalla de título mínima** [PROPUESTA]: título *Unscripted* + "Press any key" sobre el primer plano del nivel, antes de la transmisión del Director | `UI/WBP_Title` (nuevo), `BP_HUD` | El juego no empieza "en frío" |
| C8 | P2 | Ajuste de ritmo: velocidad del texto, duración del aviso *CONTINUITY ALTERED* tras jugar la partida completa | `UI/` | — |

### 4.4 Yizens — División D (mundo, arte, audio, build)

Rama: `d/sprint-mvp` · Assets: `Art/`, `Audio/`, `VFX/`, `World/`, `L_Whitechapel_Geo`, `L_Whitechapel_Light`, `CREDITS.md`, `Config/` de empaquetado (coordinado con Mauricio).

| # | Prio | Tarea | Asset | Hecho cuando… |
|---|---|---|---|---|
| D1 | P0 | **Primera build YA** (minuto 0, en segundo plano): *Platforms → Windows → Package Project* (Development). Comprobar en *Project Settings → Packaging* que `L_Whitechapel` y sus 4 subniveles están en *List of maps to include*, y *Game Default Map* = `L_Whitechapel`. Anotar cada error de cook y repartirlo a su dueño | `Config/DefaultGame.ini`, `DefaultEngine.ini` (con Mauricio) | El `.exe` arranca y se ve Whitechapel con HUD |
| D2 | P0 | **Probar el `.exe` en otro PC** (el de Jesus o Daniel): partida de 5 min, anotar fps, fallos de sonido, materiales rosas, texto de debug | — | Lista de fallos de la build en el grupo |
| D3 | P0 | **Oclusión de cámara (D-20)** en los puntos anotados en el triaje: bajar o esconder (`Hidden in Game` / quitar colisión de cámara) los bloques que tapan al jugador en peleas | `L_Whitechapel_Geo` | En la Plaza, Paso central, Tramo y Archivo nunca se pierde de vista al jugador ni las telegráficas |
| D4 | P0 | **Tubería del Taller / NavMesh** (con Jesus, B8): mover la pieza o ajustar el volumen y reconstruir navegación | `L_Whitechapel_Geo` | Jack pasa sin atascarse |
| D5 | P0 | **`CREDITS.md` completo:** nombres del equipo por división, herramienta y licencia de la música (preguntar a Mauricio), cuenta/plan de la segunda cuenta de Meshy. Pasar el texto a Daniel (C5) | `CREDITS.md` | Sin filas vacías |
| D6 | P0 | **Build final (Puerta 2)** desde `main` congelado: Shipping si compila a la primera, si no Development sin consola. Probar en otro PC hasta el Final B | — | `.exe` final probado, zip listo |
| D7 | P1 | **Música por fase (D-33):** exploración por defecto, combate cuando hay enemigos en `Combat`, decisión al entrar en `FinalChoice` (escuchar `OnStoryPhaseChanged`). Fundido de 1–2 s | `Audio/`, actor de música en `_Light` o `_Geo` | La música cambia al empezar una pelea y en Registros |
| D8 | P1 | **Rendimiento (D-40):** `stat fps` en la Plaza y el Paso central; si < 60, reducir sombras de faroles (solo las cercanas proyectan), `Local Fog Volume` y dispersión volumétrica | `L_Whitechapel_Light` | ≥ 60 fps en el PC más débil, o anotado el valor |
| D9 | P1 | **Página de la jam (D-42):** 4–6 capturas (Plaza de noche, pelea con Corte, Retoma, revelación, cada final), GIF de 10 s, descripción en inglés, controles, herramientas de IA (*ChatGPT/OpenAI, Meshy, Hyper3D Rodin, fal/ElevenLabs* + la de música) | — | Borrador listo antes del minuto 105 |
| D10 | P2 | Vida del mundo (`MEJORAS_MUNDO §4`): V2 NPC que camina, V3 humo de chimeneas, V4 ventanas que parpadean, V5 sonidos de ciudad en `MS_Ambience_Whitechapel` | `World/`, `Audio/` | Solo con P0/P1 cerrados |

## 5. Dependencias entre personas (hablar a tiempo)

| Quién necesita | De quién | Qué | Antes de |
|---|---|---|---|
| Daniel (C1, C3) | Mauricio (A1, A4) | `SetRetakeBlocked` real; Esc que abra `WBP_Pause` | Puerta 1 |
| Jesus (B5, B7) | Mauricio (A3) | Resultados reales de `ReceiveCombatHit` para que parry/esquiva funcionen contra B | T = 45 |
| Jesus (B1) y Yizens (D4) | entre ellos | Tubería del Taller / NavMesh | T = 50 |
| Daniel (C5) | Yizens (D5) | Nombres y licencias para los créditos | T = 60 |
| Yizens (D1, D6) | todos | Errores de cook atribuidos a sus assets | Lo antes posible |
| Mauricio (A5) | todos | Ramas subidas | T = 75 y T = 105 |

**Contratos:** nada de este sprint requiere cambiar `Core/`. Si alguien lo necesita, lo escribe en "Solicitudes de contrato" de su archivo de división y **se detiene**.

## 6. Plantilla de bug (copiar al grupo)

```text
[DUEÑO A/B/C/D] [P0/P1] Zona: Plaza | Callejón | Taller | Paso central | Tramo | Refugio | Archivo | Registros | UI
Pasos: 1) … 2) … 3) …
Esperado: …        Observado: …
Commit: 83ee5bf (o el de la última puerta)    ¿Bloquea la partida? sí/no
```

Criterio de prioridad: **P0** = atasca la partida, crash, no se puede salir, texto de debug o en español visible. **P1** = feo o injusto pero se puede terminar. Todo lo demás espera.

## 7. Reglas del sprint

- **Unreal cerrado** antes de cada `git pull` / `git checkout`. Nada de `git add .`: añadir solo las rutas propias. Nunca `push --force` sobre `main`.
- Cada uno coloca actores **solo en su subnivel** (`_AI` Jesus, `_Story` Daniel, `_Geo`/`_Light` Yizens). El persistente `L_Whitechapel` solo lo toca Mauricio al fusionar, con `git lfs lock`.
- No usar *Save All* si hay paquetes ajenos modificados: guardar asset por asset.
- Los scripts de migración de una sola ejecución (`implement_a0*.py`, `combine_props_hud_assets.py`, `build_*` de C, `b_*` que buscan `K2Node_*` por nombre) **no se vuelven a ejecutar** sobre los assets actuales.
- Conflicto en un `.uasset`/`.umap`: no fusionar; el dueño decide qué versión gana y rehace el cambio pequeño encima.
- Nada de mecánicas nuevas tras la Puerta 1. Las pantallas de título/pausa/créditos son UI de salida, no mecánicas.

## 8. Registro del sprint

| T | Commit | Quién | Prueba | Resultado |
|---|---|---|---|---|
| 0 | `83ee5bf` | Todos | Triaje: partida completa | |
| 75 | | Mauricio | Puerta 1: Start → Final A en editor | |
| 105 | | Yizens | Build desde Puerta 1 en otro PC | |
| 120 | | Mauricio + Yizens | Puerta 2: `.exe` → Final B en otro PC | |
