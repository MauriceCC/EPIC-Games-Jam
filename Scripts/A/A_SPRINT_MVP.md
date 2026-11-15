# Sprint MVP — División A (A1–A4)

Implementado el 2026-11-15 sobre `0b81db2` (= `main` @ `83ee5bf` + plan `05_SPRINT_MVP_2H.md`). Rama `a/sprint-mvp`.
Solo se guardaron `Player/BP_PlayerCharacter` y `Player/BP_PlayerController`. Sin cambios en `Core/`, assets de B/C/D ni mapas.

## Cambios

| Tarea | Asset | Cambio |
|---|---|---|
| **A1** | `BP_PlayerCharacter` | Implementa `BPI_PlayerControl`: `SetRetakeBlocked(bBlocked)` → `bRetakeBlocked`; `ClearRetakeHistory` → vacía `PosHistory`, `HPHistory` y `SnapAccum = 0`; `SetGameplayInputEnabled(bEnabled)` → `bGameplayInputBlocked = NOT bEnabled`. `DoRetake` sale al inicio si `bRetakeBlocked`. `DoMove`, `DoLightAttack`, `DoDodge`, `DoParry`, `DoTemporalCut` y `DoRetake` salen al inicio si `bGameplayInputBlocked` |
| **A2** | `BP_PlayerController` | Eliminados los 6 `PrintString` de depuración (`Interact`, `Crouch`, `Checklist`, `Pause requested`, `Mouse stopped` y el Vector2D de `LookMouse` cada frame) y su `ToString`. Los nodos de acción se conservan; E/Tab de C no pasaban por ellos |
| **A3** | `BP_PlayerCharacter.ReceiveCombatHit` | Muerto → `Ignored` · invulnerable (esquiva) → `Dodged` · ventana de parry y golpe parryable → `Parried` · daño → `Hit`. Antes las 4 ramas devolvían `Hit` (`NewEnumerator0`). B ya compara con `Parried` y aplica stagger, así que el parry ahora desequilibra al Perseguidor |
| **A4** **[PROPUESTA]** | `BP_PlayerController.A_HandlePause` | Esc (`IA_Pause`): la 1.ª pulsación muestra *Press Esc again to quit* durante 3 s; la 2.ª dentro de esa ventana llama a `Quit Game`. Tiempo real (no le afecta la pausa) |

Consecuencias para otras divisiones:

- **C:** sus llamadas existentes ya tienen efecto. Durante diálogos (`SetGameplayInputEnabled(false)`) el agente no se mueve, ni ataca, ni usa F/R; el ratón sigue orientando y E/Tab no se tocan. Al registrar el expediente, `SetRetakeBlocked(true)` deja R sin efecto y sin gastar carga. Si un flujo llama `false` y nunca `true`, el jugador queda inmóvil: avisar a Mauricio.
- **B:** la esquiva devuelve `Dodged` y el parry `Parried`; no cambian firmas.
- **C3 (`WBP_Pause`):** cuando exista, sustituir en `A_HandlePause` la lógica de doble pulsación por `Create Widget (WBP_Pause)` → `Add to Viewport` (lo hace A; C solo entrega el widget, que pausa y restaura `Game Only` al cerrar).
- El aviso de Esc usa `PrintString`: se ve en Development y **no** en Shipping (en Shipping la doble pulsación sigue saliendo del juego).

A6 ya se cumplía en parte: `DoRetake` exige muestras (`PosHistory > 0`), así que sin historial no gasta carga. Queda pendiente guardar/restaurar la resistencia (P1).

## P1: A6 y A7 (segunda migración, solo `BP_PlayerCharacter`)

| Tarea | Cambio |
|---|---|
| **A6** | La Retoma también rebobina la **resistencia**. El Tick guarda `CurrentStamina` en `StaminaHistory`, junto a posición y salud (cada 0,1 s, máximo 30 muestras). `DoRetake` aplica `SetStamina(StaminaHistory[0])` si el historial está alineado con `PosHistory` y luego lo vacía. `ClearRetakeHistory` también lo vacía. R sin muestras ya no gastaba carga |
| **A6, corrección** | `B_ResumePlayerAtCheckpoint` no vaciaba el historial, así que **R justo después de reaparecer devolvía al jugador a un punto anterior a su muerte**, con la salud de entonces. Ahora, al reaparecer, se vacían los historiales y la resistencia vuelve al máximo. Las cargas no se tocan |
| **A7** | El Corte (F) exige **línea de visión**: en el bucle de candidatos, después de `CanBeTemporalCutTarget` de B (que ya descarta derrotados y congelados), se traza una línea en el canal Visibility del agente al enemigo. Si choca con algo que no es un Pawn (muro, prop), ese enemigo no es elegible. Otros personajes en medio no bloquean. Si no queda ningún candidato, no se gasta el cooldown |

- [Migración](implement_a_sprint_mvp_p1.py) → [resultado](a_sprint_mvp_p1_implementation_result.json): 37 comprobaciones de conservación del grafo.
- [Parche](patch_a6_retake_condition.py) → [resultado](a6_patch_result.json): se retiró una condición `> 0` redundante. Ya está aplicado; no repetir.
- [Validación](validate_a_sprint_mvp_p1.py) → [resultado](a_sprint_mvp_p1_validation_result.json): **15 comprobaciones**, ejecutadas con el editor completo ([runner](run_validate_a_sprint_mvp_p1_editor.py)). El commandlet no tiene colisión para actores transitorios, así que la prueba con pared necesita el editor completo. Casos: Retoma 40 → 70 de resistencia; historial desalineado sin restauración; respawn que vacía el historial, rellena la resistencia y deja R sin gastar carga; Corte que congela a un guardia visible; Corte con un muro en medio que no congela ni gasta el cooldown.

## Evidencia

- [Migración](implement_a_sprint_mvp.py) (una sola ejecución; rechaza un proyecto ya migrado) → [resultado](a_sprint_mvp_implementation_result.json). Comprueba que cada nodo, valor y enlace previo se conserva salvo las aristas de entrada desviadas, los 4 literales de `Result` y los prints borrados. Copia de seguridad: ruta `backup` del resultado.
- [Validación tras recarga](validate_a_sprint_mvp.py) → [resultado](a_sprint_mvp_validation_result.json): **27 comprobaciones correctas**. Compilan las **58 Blueprints** de `/Game/Unscripted`. En un jugador transitorio del mundo del editor: Retoma bloqueada no gasta carga ni mueve; con la entrada desactivada no hay Retoma ni esquiva; `ClearRetakeHistory` vacía el historial y R ya no gasta carga; sin bloqueo la Retoma rebobina y gasta 1.

Límites: no es una sesión de Play. Falta la prueba manual de abajo.

```powershell
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' "$PWD/Unscripted/Unscripted.uproject" -run=pythonscript "-script=$PWD/Scripts/A/validate_a_sprint_mvp.py" -unattended -nullrhi -nosound -NoSplash
```

## Prueba en Play (Mauricio, ~5 min en `L_Whitechapel`)

1. Play. Mover el ratón y pulsar E, Ctrl y Tab: **no** aparece texto cian de depuración.
2. Plaza: Q justo antes de que un Perseguidor golpee → chispa de parry y el enemigo queda en *stagger*. Esquivar a tiempo (Espacio) no quita salud.
3. Hablar con Jack: durante el diálogo WASD, clic, F y R no hacen nada; al terminar vuelven a funcionar.
4. Esc → aparece *Press Esc again to quit*; esperar 3 s y pulsar Esc otra vez → vuelve a pedir confirmación; dos Esc seguidos → se cierra la sesión de Play.
5. Registros: registrar un expediente y pulsar R → nada, y el contador de cargas del HUD no cambia.
6. A6: gastar resistencia con esquivas, esperar ~1 s y pulsar R → la resistencia vuelve al valor de hace unos 3 s.
7. A6: morir, reaparecer y pulsar R enseguida → no pasa nada (no se rebobina a antes de morir) y no se gasta carga.
8. A7: con un enemigo detrás de una esquina o un muro, pulsar F → no se congela y el Corte sigue disponible. Con el enemigo a la vista, se congela.
