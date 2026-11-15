# Blockout completo del distrito 240 × 180 — informe

> División D · 2026-11-15 · Mapa: `/Game/Unscripted/Maps/Test/L_Test_D` (de D). Guardado.
> Fuente única: layout aprobado (`Scripts/D/masterplan240_layout.py`) → `Scripts/D/district240_build.py` → `../district_placements.json`.
> No se ha tocado `L_Whitechapel*` (mapa integrado), la cámara de A ni ningún actor o asset de B/C. Sin arte final ni assets nuevos.

## 1. Qué se construyó

| | |
|---|---|
| Ámbito | Distrito completo: piloto (Inicio, Plaza, Taller), escape, rutas azul y verde, paso central, refugio, evidencias, antepatio del Supervisor, acceso lateral y archivo |
| Actores | 407 con etiqueta `MP240` (carpeta `MP240/`) + 1 NavMeshBoundsVolume. Sustituyen a los 111 del piloto, regenerados desde la misma fuente |
| Desglose | 44 suelos, 148 volúmenes de edificio, 43 cajas de cascarón para los 7 edificios con interior, 95 muros (21 del layout + 74 cierres automáticos de bordes abiertos), 61 props, 12 marcas de portón, 3 dinteles |
| Interiores accesibles | Taller, casa-refugio, enfermería (sala + pasillo), informe (sala + acceso), archivo (pórtico, vestíbulo, sala de elección, galería y ala este) |
| Assets existentes | `BP_GasLamp` (17), `SM_CrateStack_A`, `SM_Barrel_A`, `SM_Handcart_A` (escala uniforme 0,65), `SM_ArchivePillar_A` (4), `SM_RecordStation_Official/Authentic` sobre peana, `SM_Cot_A`, `SM_WorkshopTable_A`, `SM_Shelf_A`, `SM_Fountain_Square` |
| Portones | **Solo marcas en el suelo**: el recorrido se prueba con todo abierto. Las 12 posiciones y anchos están en `whitechapel_routes.csv`; la lógica por fases es de C (`BP_Door`) |

**Corrección previa al montaje:** el validador 2D dejaba que la puerta de un edificio abriera el muro de un edificio contiguo. Se hizo estricto y destapó dos huecos que faltaban en el archivo (pórtico → puertas del cuerpo central, y galería → vestíbulo). Las dos puertas se añadieron al layout. Con el validador estricto: **0 problemas**.

## 2. Medidas reales (editor)

- **331/331 piezas geométricas** (suelos, edificios, cascarones, muros) coinciden con el plano: **desviación máxima 0,0 m** (bounds del editor frente al layout).
- Estaciones finales: centros a 5 m, peanas de 2,0 × 1,4 m; franja frontal de 2,5 m libre tras girarlas 90°.

## 3. Espacios libres (trazas a 0,5 m, con props colocados)

| Tramo | Exigido | Mínimo medido |
|---|---:|---:|
| Avenida sur / Llegada | 7 / 7 | 10,0 / 8,3 |
| Calle este / Calle norte | 6 / 5,5 | 8,0 / 8,0 |
| Ruta azul (oeste, arco, este) | 2,7 | 4,5 / 3,5 / 4,5 |
| Paso central | 5 | 6,0 |
| Calle taller–escape / Escape 1 / Escape 2 | 5 | 7,0 / 5,84 / 6,4 |
| Cuellos 1 y 2 | 4,2 | 4,5 / 4,5 |
| Pasadizo de servicio | 2,2 | 3,5 |
| Tránsito al refugio | 5 | 6,0 |
| Corredor de evidencias / Ruta verde / Retorno | 4 / 3 / 2,7 | 4,5 / 4,0 / 3,5 |
| Pasillo del taller / Paso de servicio | 2,7 | 4,0 / 4,0 |

**20/20 tramos cumplen.** Comprobación de solapes en las áreas que deben quedar libres (arenas A 18 × 16 y B 16 × 14, ensanche 17 × 15, arena del Supervisor 26 × 24, sala final 15 × 10, espera de Jack 5 × 5, interacción del taller, spawn, patio intermedio): **ningún sólido**. Los únicos contactos son los muros de linde del patio del taller con el portón G-07, que son intencionados.

## 4. Navegación y recorrido completo

NavMesh reconstruido sobre todo el distrito (`01_cenital_navmesh.png`). Prueba en Play con `BP_Jack` de B en modo seguir al jugador. Lo referencié solo en este mapa y lo retiré al terminar. El jugador se teletransporta de nodo a nodo y Jack tiene que alcanzarlo andando por el NavMesh con su colisión real.

| Tramo | Resultado |
|---|---|
| N01 → N02 → N03 → N04 → N05 → N06 → J0 (interior) → N07 (patio) | ✅ todos |
| N07 → N08 → N09 → N10 → N11 → N12 (refugio) | ✅ todos |
| N12 → N13 (enfermería, puerta de servicio) → N14 (informe) → N15 → N16 | ✅ todos |
| N16 → N17 (arena) → N18 (reja) → N19 (vestíbulo) → N20 (sala de elección) | ✅ en la repetición dirigida (ver nota) |
| Ruta azul: N09 → AL-A3 → patio → arco → N15, en los dos sentidos | ✅ |
| Ruta verde: N08 → AL-B1 → corredor → N14 → N13 → N12 | ✅ todos |
| Calle norte: N03 ↔ calle norte ↔ ruta azul | ✅ |

**Nota:** en la primera pasada larga, Jack se detuvo o se pasó de largo en 4 casos (N17, arco desde N20, N15 desde el arco y calle norte desde el refugio). Repetí esos tramos con pasos intermedios y **todos se completaron**, también el antepatio y el arco en los dos sentidos. Lo atribuyo al seguimiento de Jack a ~3 fps (el editor está en segundo plano), no a cortes del NavMesh. Registros: `route_log_main1.json`, `route_log_main2.json`, `route_log_fc.json` y `route_log_pn.json` en esta carpeta; anchos en `widths_result.json`.

## 5. Oclusión desde la cámara real

Muestreo cada 2 m sobre todo el suelo transitable e interior (2 480 puntos). Para cada punto se lanzan trazas desde la posición real de la cámara (brazo 1700, −55°, yaw 45°) hasta el pecho y la cabeza del jugador. Mapa: `../occlusion_map.svg`; datos: `../occlusion_points.json` y `../occlusion_nodes.json`.

- **19,4 % del suelo jugable deja al jugador totalmente oculto.**
- Nodos ocultos: **N05, N06** (calle este junto a la fachada sur), **N11** (portón del refugio), **N13** y **N14** (salas de evidencia), **N15** (paso central) y **N19** (vestíbulo del archivo). Visibles: N01–N04, N07–N10, N12, N16–N18, N20 y J0.
- Peores zonas: interiores con muro alto del lado de la cámara (pasillo de la enfermería 100 %, vestíbulo del archivo 90 %, ala este 89 %, salas de enfermería e informe ≈ 72 %, sala de elección 55 %, refugio 50 %) y callejones de 3,5–4,5 m entre fachadas de 6,5–10 m (pasillo del taller 56 %, ruta verde 48 %, ruta azul este 46 %, corredor de evidencias 41 %).
- Bien resueltos: plaza 6 %, antepatio 10 %, escape (cuellos, nichos, tramo 2) 0–14 %, avenida y llegada 0 %.

Las capturas `pie_N01` … `pie_N20` y `pie_J0` lo confirman (por ejemplo, en `pie_N13` el jugador no aparece). En las arenas el encuadre real sigue siendo de ≈ 12 × 9 m (`pie_N17`).

## 6. Qué falta antes del arte final (por orden)

1. **Oclusión (D, P0):** recorte o fundido de muros y fachadas del lado de la cámara. En los interiores, quitar o bajar a 1–1,5 m el muro sur y el oeste de cada sala (vista de maqueta). Sin esto, 3 de las 4 salas narrativas y 7 nodos no se ven.
2. **Cámara (A, solo documentado):** encuadre variable en las arenas (brazo ≈ 2 200–3 600). Sin cambios por mi parte.
3. **Portones (C):** convertir las 12 marcas en `BP_Door` con los estados por fase de `whitechapel_routes.csv`, y volver a pasar la prueba de fases en el motor.
4. **Recolocar actores de B/C** en el mapa integrado cuando se decida pasar el distrito a `L_Whitechapel` (tabla del informe de auditoría, §7). No hecho: no se trasladó nada.
5. Excluir del NavMesh los patios cerrados y los techos de los puestos y cobertizos (islas inalcanzables, visibles en verde).

## 7. Capturas comparables con el piloto

`01_cenital_navmesh.png` (NavMesh visible), `02_isometrica.png`, `04_isometrica_angulo_camara.png`, `pie_N01` … `pie_N20` y `pie_J0` (cámara real en Play). Mismo método y mismos encuadres que `../pilot/`.

Para rehacer: `python -I Scripts/D/district240_build.py <dir>` y ejecutar `district_mcp_script.py` con `ProgrammaticToolset.execute_tool_script`. El script borra y recrea solo los actores `MP240`/`MP240_PILOT`, salvo el NavMeshBoundsVolume. Nada subido a Git.
