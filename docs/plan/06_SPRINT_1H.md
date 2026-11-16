# 06 — Sprint MVP de 1 hora

> Fecha: 2026-11-15. Base: `main` @ `867e7d8` (`[A/B] Pulir animaciones del protagonista y ataques enemigos`).
> Complementa a `04_PLAN_DE_CIERRE.md` y `05_SPRINT_MVP_2H.md`. No cambia el diseño (`docs/01`–`07`) ni los contratos (`01_CONTRATOS_Y_PROPIEDAD.md`). Lo que no está en el diseño va marcado **[PROPUESTA]**.
> Diagnóstico **estático**: documentación, historial Git, configuración y referencias dentro de los mapas. No se abrió Unreal ni se jugó.
> Si la entrega de la jam sigue a las 20:59 (Lima), este sprint es solo de cierre: nada de mecánicas nuevas.

## 1. Lo que encontré

| # | Hallazgo | Por qué importa |
|---|---|---|
| **1** | **El mapa por defecto es `L_Test_D`**, en el editor y en el juego (`EditorStartupMap` y `GameDefaultMap`, cambiados en el merge `1ef9335`). Ese mapa solo tiene casas, faroles y props: no tiene subniveles, enemigos, Jack, puertas, evidencias, checkpoints ni estaciones de expediente | Si el `.exe` arranca ahí, la historia no se puede jugar. Toda la historia está en `L_Whitechapel` y sus subniveles `_AI` y `_Story` |
| 2 | No hay mapas configurados para empaquetar en `DefaultGame.ini` y todavía no existe ninguna build | El objetivo principal del sprint anterior sigue sin cumplirse |
| 3 | De C no hay commits desde el sprint anterior. No existen `WBP_Pause` ni `WBP_Title`, y el final sigue sin salida (C1, C3, C5–C7) | No se puede salir del juego desde el final |
| 4 | De B tampoco hay commits propios desde el sprint anterior. B1–B6 siguen pendientes y `BP_GuardBase` sigue sin interfaces | La partida manual con Jack real no está acreditada |
| 5 | `CREDITS.md` tiene la tabla del equipo vacía y la herramienta de la música sin confirmar | Hace falta para la entrega y los créditos |
| 6 | ✅ Los 6 CSV de `SourceData/C/` no tienen ni una tilde ni una ñ | Falta revisar solo los textos fijos de los WBP |
| 7 | La parte A del sprint está hecha (A1–A8). Falta la prueba en Play y A4 con `WBP_Pause` | — |
| 8 | ⚠️ El trabajo de animaciones de muerte (rama `animations`) modifica `BP_GuardBase`, que es de B | Si Jesús lo edita a la vez, uno de los dos pierde su trabajo |

**Decisión sobre el mapa [PROPUESTA]:** volver a **`L_Whitechapel` como mapa por defecto** para el MVP. Pasar el distrito nuevo de `L_Test_D` a `_Geo` y recolocar todo lo de B y C lleva mucho más de 1 hora y cambia rutas que ya se probaron. Queda para después de la entrega.

## 2. Tareas (cada una cabe en 1 hora, solo en las carpetas de cada uno)

Prioridad: **P0** = sin esto el MVP no se puede jugar ni entregar · **P1** = si sobra tiempo.

### 2.1 Mauricio — A, integración y animaciones

Las animaciones nuevas las hace Mauricio.

| # | Prio | Tarea | Hecho cuando… |
|---|---|---|---|
| M1 | P0 · 10 min | En `Config/DefaultEngine.ini`, volver `GameDefaultMap` y `EditorStartupMap` a `L_Whitechapel`. En `DefaultGame.ini`, añadir `L_Whitechapel` y sus 4 subniveles a la lista de mapas a empaquetar. Subir y avisar | El juego arranca en Whitechapel con la historia |
| M2 | P0 · 10 min | Subir la rama `animations` (muerte) y fusionarla en `main`. **Avisar a Jesús de que ya puede modificar `BP_GuardBase`** | Jesús hace pull antes de tocarlo |
| M3 | P0 | Esc abre el `WBP_Pause` de Daniel en cuanto esté (A4). Si no llega, se queda el doble Esc para salir | Desde el juego se puede salir sin Alt+F4 |
| M4 | P1 | **Animaciones nuevas [PROPUESTA]**, por orden: ① reacción del enemigo al ser golpeado o al recibir un parry, ② pose de carga más visible para Supervisor e Interventor (ayuda a B7), ③ animación del agente al interactuar o registrar el expediente. Pasarle a Jesús el nombre del clip y el punto donde llamarlo | Se ve en Play desde la cámara isométrica |
| M5 | P0 · últimos 15 min | Puerta de integración: fusionar en orden B → C → D → A, compilar y jugar hasta un final | Commit bueno anunciado en el grupo |

### 2.2 Jesús — B, enemigos y Jack

| # | Prio | Tarea | Asset |
|---|---|---|---|
| B1 | P0 | **Empezar ya**, sin tocar `BP_GuardBase`: recorrido manual con Jack real del Taller al Refugio, 2 o 3 veces, muriendo una vez a mitad | `BP_Jack`, `L_Whitechapel_AI` |
| B3 | P0 | El Interventor se vuelve hostil con `Correction_Order`. Vencer al Supervisor emite `SupervisorDefeated` y abre Registros | `BP_Interventor`, `BP_Supervisor` |
| B2+B4 | P0 | **Solo después del pull de M2:** al reaparecer en un checkpoint, cancelar el golpe que estaba cargando y liberar el turno de ataque. Quitar el texto de depuración sobre los enemigos | `BP_GuardBase` |
| B6 | P1 | El golpe enemigo comprueba primero que no hay un muro entre el enemigo y el jugador (traza Visibility) | `BP_GuardBase` |
| B-anim | P1 | Llamar a las animaciones de M4 en el aturdimiento y en la carga del golpe | Derivados de B |

### 2.3 Daniel — C, historia y UI

| # | Prio | Tarea | Asset |
|---|---|---|---|
| C1 | P0 | Dos botones en `WBP_Ending`: **Quit** y **Play again** (abre `L_Whitechapel`, quita la pausa y devuelve el input al juego) **[PROPUESTA]** | `UI/WBP_Ending` |
| C3 | P0 | `WBP_Pause` con *Resume* y *Quit* **[PROPUESTA]**. Pasarle el nombre a Mauricio para M3 | `UI/WBP_Pause` (nuevo) |
| C4 | P0 · 10 min | Revisar los textos fijos de los WBP. Los CSV ya están limpios | `UI/WBP_*` |
| C6 | P1 | Prompts de controles en los primeros 30 s, en inglés | `WBP_HUD`, `DT_HUDText` |
| C5 | P1 | Página de créditos, con los datos que pase Yizens (D5) | `WBP_Ending` |

### 2.4 Yizens — D, mundo, build y entrega

| # | Prio | Tarea |
|---|---|---|
| D1 | P0 | **En cuanto Mauricio suba M1:** empaquetar una build Development y repartir cada error de cook a su dueño |
| D5 | P0 · 10 min | Rellenar los nombres del equipo en `CREDITS.md` y confirmar con Mauricio la herramienta de la música. Pasárselo a Daniel |
| D2 | P0 | Probar el `.exe` en otro PC durante 5 min y anotar fps, materiales rosas y texto de depuración |
| D4 | P1 | Con Jesús: tubería del Taller y NavMesh en `_Geo` |
| D3 | P1 | Quitar las oclusiones de cámara en la Plaza y en el Archivo |
| D9 | P1 | Página de la jam: capturas, descripción en inglés, controles y herramientas de IA |
| — | Después de la entrega | Pasar el distrito de `L_Test_D` a `_Geo` |

## 3. Cronograma

| Minuto | Qué pasa |
|---|---|
| 0–10 | Mauricio sube M1 y M2. Los demás cierran Unreal y hacen `git pull` |
| 10 | Yizens lanza la build. Jesús ya puede tocar `BP_GuardBase` |
| 10–45 | Cada uno trabaja en su rama |
| 45 | Todos suben su rama |
| 45–60 | Mauricio integra y juega hasta un final. Yizens empaqueta desde ese commit |

## 4. Dependencias

| Quién necesita | De quién | Qué |
|---|---|---|
| Mauricio (M3) | Daniel (C3) | El nombre de `WBP_Pause` |
| Jesús (B2, B4, B6) | Mauricio (M2) | Aviso de que `BP_GuardBase` ya está libre |
| Jesús (B-anim) | Mauricio (M4) | Nombres de los clips nuevos |
| Daniel (C5) | Yizens (D5) | Datos de los créditos |
| Yizens (D1) | Mauricio (M1) | Mapa por defecto y lista de mapas a empaquetar |

## 5. Reglas

- Unreal cerrado antes de cada `git pull` o `git checkout`. Añadir solo las rutas propias, nunca `git add .`. Nunca `push --force` sobre `main`.
- Cada uno coloca actores solo en su subnivel (`_AI` Jesús, `_Story` Daniel, `_Geo`/`_Light` Yizens).
- Conflicto en un `.uasset` o `.umap`: no se fusiona. El dueño decide qué versión gana.
- Ningún cambio en `Core/`. Si hace falta, se escribe en "Solicitudes de contrato" y se detiene el trabajo.
