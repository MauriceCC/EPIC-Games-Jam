# División D — Plan inmediato (mientras se cierra F0)

> Borrador para revisar y decidir. Dueño: División D. Fecha: 2026-11-14.
> Fuentes: `docs/05`, `docs/07`, `docs/plan/00`, `01`, `02` y `D_MUNDO_ARTE_AUDIO_BUILD.md`.
> Todo lo que no figura en los documentos de diseño está marcado como **[PROPUESTA]**.

## 0. Situación de partida

**Registro histórico de preparación, sustituido para seguimiento por la revisión de `main` @ `4afcd57` (2026-11-14):** ya existen cascarones, mapas, configuración, placeholders, props, audio y VFX; hay commits de blockout/navegación. Las cruces de la tabla inferior y la espera por creación de mapas describen el punto de partida, no el estado actual. No recrear esos assets ni volver a ejecutar scripts en lote sin revisar su contenido actual.

El trabajo inmediato pasa a validar recorrido, NavMesh, cobertura y cámara, integrar assets disponibles y preparar la build de prueba. Consultar [estado de D](D_MUNDO_ARTE_AUDIO_BUILD.md#9-estado) y [plan actualizado conjunto](03_ESTADO_Y_SIGUIENTES_PASOS.md). El plazo citado más abajo queda como referencia histórica pendiente de confirmación oficial; esta revisión no lo verificó.

| Elemento | Estado en `main` |
|---|---|
| Enums, structs e interfaces (`Core/`) | ✅ Hechos por Mauricio |
| 6 componentes (Health, Combat, Temporal, Stealth, Interaction, ObjectiveManager) | ⚠️ Creados, pero **sin dispatchers** |
| Cascarones (PlayerCharacter, GameMode, GuardBase, Jack, interactuables…) | ❌ |
| Mapas `L_Whitechapel` + subniveles, `L_Test_A`–`L_Test_D` | ❌ |
| Config (mapa por defecto, canales de colisión) | ❌ |
| Placeholders de D (`01_CONTRATOS §8`) | ❌ |
| Blockout, NavMesh, arte, audio | ❌ |

**Bloqueo:** quién termina F0 (¿Mauricio o D?). Pendiente de su respuesta. Mientras tanto, D trabaja **solo en archivos de texto propios**, sin tocar ningún `.uasset`.

## 1. Objetivo de esta etapa

Que, cuando F0 esté en `main`, D pueda tener el **blockout navegable en ~1 hora** (hito F1), porque ya estará todo diseñado y automatizado.

## 2. Tareas

**Estado (2026-11-14):** T1 ✅ redactado (`SourceData/D/LEVEL_DESIGN.md`, pendiente de revisión por B y C) · T2 ✅ escrito y validado fuera de Unreal (`SourceData/D/blockout_layout.json`, `Scripts/D/build_blockout.py`, vista previa `SourceData/D/blockout_preview.svg`); falta la primera ejecución en el editor tras F0 · T3 ✅ escrito (`Scripts/D/create_placeholders.py` + `README_PLACEHOLDERS.md` con alternativa manual); **no depende de F0**, falta crearlos en el editor · T4 ✅ borrador (`SourceData/D/ART_BIBLE.md`); la decisión de estilo D-A sigue abierta hasta T5 · T5 ✅ (`SourceData/D/ASSET_SOURCING.md`) · T6 ✅ (`SourceData/D/AUDIO_VFX_LIST.md`). Todo T1–T6 es documentación y scripts: falta ejecutarlo en el editor.

**Actualización (2026-11-14, noche):** Unreal MCP + Meshy + Hyper3D conectados. **D-01 hecho:** 16 placeholders creados y verificados en el editor. **Props P0 importados** a `/Game/Unscripted/Art/Props/` (barril, cajas, carretilla con Meshy; farol y 2 estaciones con Rodin), con colisión y anotados en `CREDITS.md`. Props de Rodin corregidos: escala real (farol 3,2 m; estaciones ~1,6 × 1,0 × 1,4 m), pivote en la base (`Scripts/D/fix_rodin_props.py`), canales PBR bien conectados y emisivo con parámetro `EmissiveStrength`. Pendiente: blockout (espera los mapas de Mauricio) y luz real del farol (`BP_GasLamp`) al colocarlo en `_Light`.

> ⚠️ **Plazo:** según itch.io, la entrega cierra el **15-nov a las 17:59 PST**. Con ese margen, F2–F4 del plan general se comprimen a horas: priorizar blockout jugable + atmósfera con el motor + build que arranque.

### T1 — Documento de diseño del nivel · P0 · ~1–1,5 h

- **Entregable:** `SourceData/D/LEVEL_DESIGN.md`
- **Contenido:**
  - Métricas **[PROPUESTA]**: rejilla de 1 m; callejón ≥ 3 m de ancho; arena de combate ≥ 12×12 m; muro bajo de cobertura ~1,1 m; puertas de 2 m; altura máxima de fachada junto al recorrido, condicionada por la cámara.
  - Plano de ~60×40 m con las 7 zonas de `docs/05`: coordenadas, función y encuentro de cada una.
  - Huecos reservados para B y C, como propuesta: patrullas, ruta de Jack, puerta lateral, 2 evidencias, checkpoints y las 2 estaciones del archivo.
  - Líneas de visión y cobertura en el acceso al taller (zona de sigilo).
- **Criterio de hecho:** B y C pueden leerlo y decir "mi contenido cabe aquí".
- **Depende de:** nada.

### T2 — Layout del blockout en JSON + script de Python · P0 · ~1–1,5 h

- **Entregables:** `SourceData/D/blockout_layout.json` y `Scripts/D/build_blockout.py`
- **Qué hace:** el JSON lista cada bloque (tipo, posición, tamaño). El script lo lee y coloca cubos en el subnivel actual (`L_Whitechapel_Geo`). Antes de reconstruir, borra solo los actores que él mismo creó, identificados con una etiqueta.
- **Criterio de hecho:** se ejecuta sin errores y reproduce el plano de T1. Esto solo puede verificarse **después de F0**.
- **Depende de:** T1. Para ejecutarlo, de que existan los mapas.

### T3 — Script de placeholders (D-01) · P0 · ~30 min

- **Entregable:** `Scripts/D/create_placeholders.py`
- **Qué hace:** crea los 16 assets de `01_CONTRATOS §8` (`NS_*`, `SC_*`, `M_TemporalFrozen_Overlay`, `PP_Retake`) en su ruta definitiva, vacíos, y omite los que ya existen.
- **Criterio de hecho:** A, B y C pueden referenciarlos por su nombre.
- **Depende de:** nada para escribirlo; de F0 para ejecutarlo.

### T4 — Mini art bible · P1 · ~45 min

- **Entregable:** `SourceData/D/ART_BIBLE.md`
- **Contenido:** paleta (ladrillo, ocre de farol, niebla azul-gris; **cian reservado para la tecnología de la agencia**), reglas de legibilidad (enemigos y avisos de ataque siempre visibles; perseguidor e Interventor distinguibles), iluminación nocturna con Lumen y referencias visuales.
- **Para qué:** fijar el estilo **antes** de descargar modelos y responder con criterio a la presión del equipo.
- **Depende de:** la decisión D-A (ver §3).

### T5 — Búsqueda de assets y licencias (D-06) · P1 · ~1 h

- **Entregable:** tabla de candidatos en `SourceData/D/ASSET_SOURCING.md`, más `CREDITS.md` actualizado al importar.
- **Contenido:** packs de entorno victoriano (Fab/Quixel), personajes o animaciones si A/B los piden, y sonido (lluvia, pasos, multitud). Licencia y tamaño de cada uno.
- **Antes de empezar:** leer las reglas de la jam sobre assets de terceros.
- **Depende de:** D-A y las reglas de la jam.

### T6 — Inventario de audio y VFX · P2 · ~30 min

- **Entregable:** `SourceData/D/AUDIO_VFX_LIST.md`
- **Contenido:** cada sonido o efecto con su nombre de asset, el evento que lo dispara (p. ej. `OnRetakePerformed`, `OnTelegraphStarted`), su prioridad y su origen (pack, generado o pendiente).
- **Depende de:** nada.

## 3. Decisiones que debes tomar

| # | Decisión | Opciones | Recomendación |
|---|---|---|---|
| D-A | Estilo visual | Realista oscuro / estilizado (low-poly, cel) | Depende de los packs gratuitos que encontremos; un estilo estilizado tolera mejor mezclar packs |
| D-B | Proyección de cámara (D0.7) | Ortográfica / perspectiva con FOV bajo | Perspectiva con FOV bajo (el plan la recomienda: menos problemas con sombras y Lumen) |
| D-C | ¿Blockout con script o a mano? | JSON + Python / a mano en el editor | Script: el resultado se puede repetir y revisar en Git |
| D-D | ¿Probar ya en `L_Test_D`? | Sí, después de confirmar con Mauricio / esperar a F0 | Sí, si Mauricio no va a crear ese mapa él |
| D-E | Orden de las tareas | T1→T2→T3→T4/T5/T6, o adelantar T5 por la presión del equipo | Mantener T1–T3 primero (son el bloqueo real del equipo) y hacer T5 en huecos |

## 4. Después de F0 (siguiente etapa, para referencia)

1. `git pull` con Unreal cerrado.
2. Ejecutar T3 (placeholders) y T2 (blockout) en `L_Whitechapel_Geo`.
3. Colocar el `NavMeshBoundsVolume` en el persistente (con `git lfs lock`) y comprobar con `P` (D-03).
4. Revisar la cobertura de sigilo (D-04) y probar la cámara con el pawn de la plantilla (D-05).
5. PR `[D] Blockout v1` y aviso a B y C → **hito F1 de D**.

## 5. Lo que no se hace ahora

- No tocar `Core/`, cascarones ni `Config/` mientras no esté claro quién cierra F0.
- No importar packs pesados antes de decidir el estilo (D-A) ni de revisar las reglas de la jam.
- No hacer arte final ni iluminación definitiva: eso es F3.
