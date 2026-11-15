# Sector piloto Inicio → Plaza → Taller de Jack — informe

> División D · 2026-11-15 · Mapa: `/Game/Unscripted/Maps/Test/L_Test_D` (de D). Guardado.
> Fuente única: layout aprobado (`Scripts/D/masterplan240_layout.py`) → `Scripts/D/pilot240_build.py` → `pilot_placements.json`.
> No se ha tocado `L_Whitechapel*`, la cámara de A ni ningún asset de B/C. Sin generación de assets.

## Qué se construyó

| | |
|---|---|
| Ubicación | Offset A aprobado: plano (x, y) → UE (X = 100·y, Y = 12000 + 100·x). La calle de prueba antigua del origen de `L_Test_D` queda intacta y lejos |
| Ámbito | Plano x 26–174, y −2–90 m: avenida sur, calle de llegada (Z01), plaza 68 × 48 (Z02/Z03), calle este 8 m, taller 16 × 18 con interior, anexo, pasillo de 4 m, patio 14 × 13 y portón G-07 |
| Actores | 111 con etiqueta `MP240_PILOT` en la carpeta `MP240_Pilot/` + 1 NavMeshBoundsVolume: 46 volúmenes de edificio, 9 suelos, 23 muros (10 cierres automáticos de bordes abiertos), 28 props, portón |
| Volúmenes | Cubos a medida exacta del layout (blockout); alturas del CSV aprobado (lado cámara = mínimo de la familia) |
| Assets existentes usados | `BP_GasLamp` (7), `SM_CrateStack_A`, `SM_Barrel_A`, `SM_Fountain_Square` (sobre base de 5 m), `SM_WorkshopTable_A`, `SM_Shelf_A` ×2, `SM_IronGate_A` |
| Assets nuevos (mínimos) | 7 copias del cubo básico con material de D en `/Game/Unscripted/Art/Blockout/SM_BO_*` (las sobrescrituras de material por instancia no se aplican vía MCP). Los materiales ya existían (`M_WorldTiling`, mapeado mundial: no se estiran) |
| Pendiente de generar (no hecho) | Puestos de mercado y carro: siguen como cajas de madera de su huella exacta (5 × 3,5 y 2,2 × 4,5) |

**Dimensiones:** comprobadas con los bounds reales de cada actor en el editor: coinciden al centímetro con el layout (p. ej. plaza 41–109 × 24–72, calle este 109–140 × 44–52, taller 140–156 × 40–58, muros de 0,4 m con huecos de 2,5 / 3,0 / 2,5 m). No se ha reducido ningún espacio.

## Colisiones (trazas reales a 0,5 m de altura)

| Tramo | Exigido | Medido en el motor |
|---|---:|---:|
| Calle este | ≥ 6 m | **8,0 m** en las 7 secciones |
| Calle norte (hasta la verja G-PN-S) | ≥ 5,5 m | **8,0 m** |
| Pasillo junto al taller | ≥ 2,7 m | **4,0 m** |
| Calle de llegada (tramo entre fachadas) | ≥ 7 m | **14 m** hasta las fachadas (incluye el paso de servicio contiguo) |
| Avenida sur | ≥ 7 m | **12 m** |
| Plaza N–S / E–O | — | 68 m / 37,5 m entre filas de puestos |
| Recorrido N01 → N02 → plaza → N04 → N05 → puerta oeste → interior → puerta trasera → patio N07 (15 tramos) | sin impacto | **0 impactos** |

## Navegación

- `RecastNavMesh` generado sobre todo el sector (`03_cenital_navmesh.png`, verde): plaza, calles, interior del taller, pasillo y patio. También aparecen islas en patios traseros cerrados y encima de los puestos: no son alcanzables (cierres automáticos), pero conviene marcar esos volúmenes con `CanEverAffectNavigation` o un `NavModifier` en el blockout definitivo.
- **Prueba de recorrido con IA:** `BP_Jack` (de B, solo referenciado en este mapa de pruebas y retirado al terminar) con `bB_FollowPlayerWithoutRoute`:
  1. Desde N04 (106, 48) → calle este → **puerta oeste de 2,5 m** → junto al jugador dentro del taller (147,4; 50,6) en ≈ 10 s.
  2. Jugador movido al patio → Jack pasa la **puerta trasera de 3 m** y llega a (154,6; 63,4) junto a N07.
  3. Jugador movido al Inicio → Jack vuelve por taller → calle este → plaza → calle de llegada y se detiene en (104,9; 14) junto al jugador (`pie_12_jack_llega_al_inicio.png`).
  
  Resultado: **el recorrido Inicio ↔ Plaza ↔ Taller ↔ Patio es navegable de punta a punta**, con la colisión real del personaje, incluidas las dos puertas de paso de Jack.
- Incidencias encontradas:
  - Un `NavMeshBoundsVolume` creado por MCP nace **sin geometría de brocha** y el NavMesh sale vacío. Solución aplicada: `BRUSH MOVETO` + `BRUSH ADDVOLUME CLASS=NavMeshBoundsVolume` desde la consola del editor, escalar y `RebuildNavigation`. Documentado en `pilot240_build.py`.
  - Un `BP_Pursuer` con una `BP_PatrolRoute` de 13 puntos **no se movió** en este mapa (estado `Patrol`, índice 0, velocidad 0), mientras Jack sí navegaba por el mismo NavMesh. No es un problema de navegación. Queda anotado para B; no lo he investigado dentro de sus Blueprints.
- El PIE corre a ~3 fps cuando el editor está en segundo plano (`max tick rate 3`): las pruebas de IA son más lentas pero válidas.

## Visibilidad desde la cámara real del jugador

Capturas `pie_01` … `pie_12`, en Play, con `BP_PlayerCharacter` y su cámara sin modificar (brazo 1700, pitch −55°, yaw 45°, FOV 40°).

| Punto | Observación |
|---|---|
| N01 inicio, N02, N03, arena A, N04 | Encuadre ≈ 12 × 9 m: se ve el adoquín, el farol y el jugador; **no se ve ni la plaza entera ni sus fachadas a la vez** |
| Plaza sur junto a los puestos (60, 31) | Jugador visible; los puestos de 2,6 m se leen bien |
| Calle este a 0,8 m de la fachada sur (125, 44,8) | **Jugador totalmente oculto** por la fachada sur de 6,5 m |
| N06 entrada del taller (138, 45,25) | **Oculto**: la puerta del taller cae en la franja tapada por la fachada sur de la calle |
| J0 interior del taller | Visible (sin cubierta) |
| Pasillo junto al taller | **Oculto** por el muro este del taller (6,5 m) |
| N07 patio | Visible |

Franja oculta medida: ≈ 0,7 × altura de la fachada en la dirección de la cámara (≈ 3,2 m perpendiculares a una fachada sur de 6,5 m).

## Ajustes necesarios (documentados, no aplicados)

**Para A (cámara, no modificada):**
- El encuadre fijo de ≈ 12 × 9 m no permite leer las arenas: A 18 × 16 necesita brazo ≈ 2 500; B 16 × 14 ≈ 2 200; Supervisor 26 × 24 ≈ 3 600 (con FOV 40°). Propuesta: volúmenes de cámara por zona con brazo variable y transición suave, o subir el FOV en combate.

**Para D (propio, siguiente paso recomendado):**
1. **Sistema de oclusión (P0):** fundido/recorte de fachadas y muros en el lado de la cámara (sur/oeste) cuando tapan al jugador. Sin él, la entrada del taller y el pasillo no son jugables.
2. Alternativa o complemento: bajar a una planta (≈ 3–4,5 m) o recortar en maqueta las fachadas del lado de la cámara que dan a calles de ≤ 8 m (MD-S, muros del taller).
3. Excluir del NavMesh los patios traseros y techos de los puestos.
4. Sustituir los cubos de puesto y carro cuando se aprueben los assets (sin cambiar la huella).

## Archivos

- Capturas: `01_cenital.png`, `02_isometrica.png`, `03_cenital_navmesh.png`, `04_isometrica_angulo_camara.png`, `pie_01`…`pie_12`.
- Plan de colocación: `../pilot_placements.json`. Script: `Scripts/D/pilot240_build.py`. Para rehacer: generar el script y ejecutarlo con `ProgrammaticToolset.execute_tool_script`, que borra y recrea solo los actores `MP240_PILOT`, salvo el volumen de navegación.
- Nada subido a Git.
