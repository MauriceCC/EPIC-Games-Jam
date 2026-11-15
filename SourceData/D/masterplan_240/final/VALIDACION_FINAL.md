# Validación final del distrito vestido en `L_Test_D`

> División D · 2026-11-15 · Mapa: `/Game/Unscripted/Maps/Test/L_Test_D` (guardado).
> **Alcance:** escenario de D vestido y validado en el mapa de pruebas. **No está integrado** en `L_Whitechapel` (propuesta en `../INTEGRACION_PROPUESTA.md`). El juego **no está completo**: faltan la integración y la lógica de B y C sobre este escenario.

## 1. Qué hay en el mapa

| Concepto | Valor |
|---|---|
| Actores del arte final (`MP240_FINAL`) | 1 439 (1 430 colocaciones del generador + niebla, postproceso, audio y vapor) |
| Actores totales del mapa | 1 473 (incluye 7 luces interiores, NavMesh, cielo y el prototipo heredado `PR_*`; ver §8) |
| Generador | `Scripts/D/district_art_build.py` → `../district_art_placements.json` (regenerado con KIT4) |
| Kit vigente | `SM_KIT4_*` (1 217 piezas). Ninguna referencia a KIT, KIT2 ni KIT3 |
| Dependencias de otras divisiones | Solo `Narrative/BP_GameMode` (modo de juego del mapa). Ningún actor de A, B ni C colocado por D |
| PlayerStart | Movido a N01 (UE 900, 22 400, yaw 0): Play arranca en el inicio del recorrido |

## 2. Anchos libres con el arte colocado (trazas a 0,5 m)

`widths_art.json`: **20 de 20 tramos cumplen**. Los más ajustados:

| Tramo | Exigido (m) | Medido (m) |
|---|---:|---:|
| Estrechamientos NK1 / NK2 | 4,2 | 4,5 / 4,5 |
| Calle a evidencias (STEV) | 4,0 | 4,5 |
| Ruta azul B, tramo 2 (ALB2) | 2,7 | 3,5 |
| Escape 1 / Escape 2 | 5,0 | 5,84 / 6,4 |

Áreas que deben quedar libres (arenas A 18 × 16 y B 16 × 14, ensanche 17 × 15, arena del Supervisor 26 × 24, sala final 15 × 10, espera de Jack 5 × 5, interacción del taller, spawn y patio intermedio): **ningún sólido**. Los bajantes son decorativos y no tienen colisión. Los pilares del antepatio G-07 y los muros de linde del patio del taller son intencionados.

## 3. Puertas y huecos

- Los huecos de los edificios especiales salen de los rectángulos `doors` del layout. Se añadieron dos al archivo: el pórtico (90–94,5; 145,4–146,6) y la entrada lateral del cuerpo central (93,4–94,6; 148,4–151,6).
- Los 12 portones solo tienen los **pilares de piedra** de D y una marca en el suelo. La hoja, el estado y la lógica son de C (`BP_Door`).
- **Las pruebas se hicieron con todos los pasos abiertos. Que se pueda pasar no demuestra que la progresión narrativa funcione** (pendiente P2 de C).

## 4. NavMesh y recorrido completo

- NavMeshBoundsVolume que cubre X −200…18 200 y Y 11 800…36 200 cm, creado con `BRUSH ADDVOLUME` y reconstruido.
- Recorrido con `BP_Jack` siguiendo al jugador, que se teletransporta por los nodos:
  - Primera pasada: 32 de 36 tramos (`route_log_final.json`). Fallaron N03, N12, N18b y la calle norte.
  - Esos cuatro, repetidos con pasos intermedios: 25 de 25 (`route_log_retry.json`).
- Atribuyo los fallos al seguimiento de Jack cuando el PIE corre a unos 3 fps (editor en segundo plano), no a cortes del NavMesh: con pasos intermedios pasan todos y la malla es continua.

## 5. Oclusión desde la cámara real (A, sin cambios: brazo 1 700, pitch −55, yaw 45, FOV 40)

- El recorte por pantalla está en todos los materiales de muros y cubiertas y en `M_ART_MeshyPBR`: círculo central, profundidad menor de 1 620 cm y altura mayor de 40 cm; las sombras se conservan.
- `CutRadius` vale 0,30 en muros y 0,9 en cubiertas.
- Capturas en juego con el kit definitivo (`v_kit4/pie/`, hoja de contacto `v_kit4/pie_contact_sheet.png`). El jugador se ve en los 10 puntos: N01, N02, plaza A, N06, J0 (con Jack), N09, N12 refugio, N17 arena, N18 reja y N20 sala final.
- Las 16 capturas anteriores (`pie/`) son anteriores al cambio de kit; se conservan para comparar.
- **Corregido en esta pasada (N06):** el recorte funcionaba, pero el jugador quedaba en la sombra profunda de la casa MD-S03 y no se distinguía. Se resolvió con contraste local de sombras 0,55 en el postproceso, sin tocar la cámara.

## 6. Iluminación nocturna (final)

| Elemento | Valor |
|---|---|
| Luna (`DirectionalLight_1`) | 2,0 lux, temperatura 9 500 K, pitch −38 |
| Cielo (`SkyLight_1`) | 1,8, tinte azul (0,62, 0,70, 0,92) |
| Postproceso | exposición automática −1…0,5 EV, sesgo +1,0, contraste local de sombras 0,55 y de luces 0,8, viñeta 0,45 |
| Farolas | 17 `BP_GasLamp` (25 cd, radio 9 m) |
| Interiores | 7 luces puntuales de 40 cd con sombras |

Antes de esta pasada, la luna estaba a 6 lux en blanco y la exposición a +1,8: se leía como de día (ver `v_kit4/pie` frente a las capturas sobreexpuestas descartadas). Los valores nuevos se comprobaron en juego.

## 7. Rendimiento (medido)

`v_kit4/perf_plaza_fpschart.log` (`StartFPSChart` / `StopFPSChart`, 16,7 s en la plaza A en juego, ventana del editor en primer plano):

| Medida | Valor |
|---|---|
| Hardware | Intel Core i7-13650HX · NVIDIA GeForce RTX 4060 Laptop GPU · 15,7 GB RAM · Windows 11 23H2 |
| Motor y escalabilidad | UE 5.8 (Development, PIE), calidad Épica (3), 1 707 × 1 067 |
| Media | **59,16 fps** (limitado a 60; el 1,4 % de los fotogramas no llega a 60) |
| GPU / hilo de juego / hilo de render | 7,25 / 7,45 / 5,95 ms |
| Percentil 75 | GPU 7,55 ms, hilo de juego 7,54 ms |
| Tirones | 1 de 0,07 s en 16,7 s |

Hay margen de unos 9 ms por fotograma. No hizo falta fusionar actores ni pasar a ISM, aunque sigue siendo la medida recomendada si la integración añade carga (ver la propuesta de integración).

## 8. Comprobaciones de limpieza

| Comprobación | Resultado |
|---|---|
| Paredes invisibles | Ninguna. Todo sólido con colisión es visible. Las piezas sin colisión son decorativas (`SM_KIT4_DecoBox`/`DecoCyl`: bajantes, sumideros, charcos) |
| Solapes y suelos duplicados | Los 1 430 colocados tienen etiqueta única. Hay un solo suelo general (`F_Suelo`, cara superior a 0 cm). Las 95 capas de pavimento, aceras, patios e interiores están escalonadas: los pavimentos llegan a 2–2,5 cm y las capas superiores, que nacen a 2 cm, a 3–12 cm. En las capturas no se ve parpadeo. No se comprobó pieza a pieza que dos capas superiores no se crucen |
| Cubos provisionales en sectores terminados | Ninguno. Los únicos `Engine/BasicShapes/Cube` son el prototipo heredado `PR_Road/Pave/Kerb` y las casas `PR_N*`/`PR_Lamp` en el origen (0, 0), a 118 m del distrito y fuera del juego. Se conservan porque son anteriores a esta tarea |
| Referencias a `/Game/Developers` | Ninguna (`get_dependencies` de `L_Test_D`) |
| Blockout `SM_BO_*` | Sin uso en el arte final |
| Texto visible | El arte de D no lleva rótulos: las fascias están en blanco a propósito. Solo hay texto en el HUD de C, en inglés |
| Texturas | Las de los modelos Meshy (color, rugosidad, metal y normal) y las repetibles nuevas `T_Slate_D` y `T_StoneAshlar_D`. Sin texturas faltantes (`WorldGridMaterial` solo aparece por el prototipo `PR_*`) |

## 9. Errores observados y a quién corresponden

| # | Observación | Dueño |
|---|---|---|
| B1 | `BP_Pursuer` con `BP_PatrolRoute` no se movió en `L_Test_D` (estado Patrol, índice 0, velocidad 0) aunque el NavMesh es válido | B |
| B2 | En el modo de seguimiento, `BP_Jack` se detiene o se pasa en tramos largos cuando el PIE va lento; con pasos intermedios llega siempre | B |
| A1 | El encuadre de unos 12 × 9 m no abarca las arenas de 16–26 m: harían falta brazos de unos 2 200–3 600 o un modo de cámara de combate | A |
| C1 | `BP_Door` en los 12 portones con sus estados por fase. Las pruebas con todo abierto no acreditan la progresión | C |
| C2 | En Simular, los BP de HUD dan errores de referencia nula sin jugador. En Play, el aviso "errores y advertencias durante la reproducción" aparece en cada sesión | C |
| D1 | La lluvia (`NS_Rain`, global) cae dentro de los interiores: taller, refugio y sala final. **[PROPUESTA]** Volúmenes que la anulen en los interiores, o lluvia ligada a la cámara con prueba de techo | D |
| D2 | Las sombras nocturnas tienen bastante saturación azul. Es aceptable para la jam; se puede ajustar el tinte del cielo al integrar | D |

## 10. Modelos corregidos y descartados

Ver `../PASO5_ASSETS.md` §F.

- **Descartados:** `SM_House_AR01` (fachada demasiado estrecha) y `SM_MarketStall_A` (sustituido por `SM_MarketStall_01`).
- **Kits obsoletos:** `SM_KIT_*`, `SM_KIT2_*` y `SM_KIT3_*` nunca se guardaron en disco y ya no los referencia nada.
- `SM_House_AR01/` y `SM_MarketStall_A/` siguen en disco sin uso. Se pueden borrar cuando el equipo lo confirme.

## 11. Capturas comparables

| Carpeta | Contenido |
|---|---|
| `v_kit4/` (definitivas) | `01_cenital`, `02_isometrica`, `03_isometrica_angulo_camara`, `sector_A_inicio_plaza`, `B_taller`, `C_escape`, `D_refugio`, `E_evidencias`, `F_reja_rutas`, `G_antepatio`, `H_archivo`, más `pie/` (10 puntos) y `pie_contact_sheet.png` |
| raíz de `final/` y `final/pie/` | Pasada anterior (kit 3, iluminación sin ajustar). Las letras de los sectores no coinciden: allí F = antepatio, G = archivo y H = fondo oeste |

Las vistas del editor (`CaptureViewport`) usan la iluminación del editor y no la exposición de juego. El aspecto nocturno real es el de `v_kit4/pie/`.
