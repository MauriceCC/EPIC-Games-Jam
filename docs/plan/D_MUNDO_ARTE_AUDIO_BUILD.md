# División D — Mundo: nivel, arte, VFX, audio y build (+ integración)

> **Base confirmada:** Unscripted ? UE 5.8.4 ? Blueprint. Todo contenido para el jugador debe estar en ingl?s, incluidos placeholders visibles. Ver [arranque F0](02_ARRANQUE_F0.md). Las rutas de contenido son relativas a `Unscripted/`; `Scripts/` y `SourceData/` parten del repositorio.

**Persona:** _(nombre)_ · **Rama:** `d/<tarea>` · **Commits:** `[D] …` (y `[INT] …` como integrador)

## 1. Misión

Construir **Whitechapel 1888** como espacio jugable y legible desde la cámara isométrica, darle atmósfera (niebla, faroles, lluvia), dar identidad visual y sonora a la tecnología temporal, y garantizar que el juego **se empaqueta y se entrega**. Si D es también integrador, es quien mantiene `main` sano.

**Fuentes de diseño:** `docs/05` (mapa, zonas, encuentros), `docs/07` (dirección visual, audio, alcance), `docs/02` (cámara, cobertura), `docs/06` (riesgos técnicos).

## 2. Propiedad

- `Content/CorteFinal/World/`, `Art/`, `Materials/`, `VFX/`, `Audio/`
- Mapas `L_Whitechapel` (persistente, con `git lfs lock`), `L_Whitechapel_Geo`, `L_Whitechapel_Light`, `Maps/Test/L_Test_D`
- `SourceData/D/`, `Scripts/D/`, `CREDITS.md`
- Como integrador: `Core/`, `Config/`, `.uproject`, `Plugins/`, `docs/plan/00_*`, `docs/plan/01_*`, `AGENTS.md`, `README.md`
- Este archivo.

**No tocas:** lógica de jugador, enemigos o narrativa; subniveles `_AI` y `_Story`.

## 3. Lo que provees y lo que consumes

| Provees | A quién | Cuándo |
|---|---|---|
| Esqueleto del proyecto (si eres integrador) | Todos | F0 |
| Placeholders de VFX/SFX/materiales con nombre definitivo (`01_CONTRATOS §8`) | A, B, C | F0–F1 |
| **Blockout** de `L_Whitechapel_Geo` con NavMesh funcional | B, C | **Lo antes posible en F1** (es el único bloqueo real del equipo) |
| Oclusión de cámara (edificios que se vuelven translúcidos o se recortan) | A | F2 |
| Arte final, iluminación, ambiente sonoro, música | — | F3 |
| Builds empaquetadas | Todos | Prueba al final de F2, final en F4 |

| Consumes | De quién |
|---|---|
| `OnStoryPhaseChanged`, `OnEndingTriggered` (cambiar música/ambiente por acto) | C |
| `OnRetakePerformed` (post-proceso), `OnTelegraphStarted` (audio) | A, B |

## 4. Backlog

### F0 — Integración (si eres integrador)

Ver `00_PLAN_GENERAL.md §5.1`. Pedir a tu agente un script de Python del editor (`Scripts/INT/`) que cree carpetas, enums, structs, Input Actions y cascarones en lote.

### F1

| ID | Tarea | Prioridad | Criterio de aceptación |
|---|---|---|---|
| D-01 | Placeholders de `01_CONTRATOS §8` | P0 | Existen en su ruta definitiva; A/B/C pueden referenciarlos |
| D-02 | **Blockout** con cubos/BSP/modelado de UE: inicio, plaza, callejón, taller, paso central, refugio, archivo (`docs/05`, ~60×40 m) | P0 | Recorrido completo caminable; áreas de combate con espacio para esquivar |
| D-03 | `NavMeshBoundsVolume` + NavMesh dinámico | P0 | `P` en el editor muestra navegación en todo el recorrido |
| D-04 | Cobertura de sigilo: cajas, barriles, muros bajos con colisión de visibilidad | P0 | Bloquean line trace de visión |
| D-05 | Prueba de cámara en el blockout (con el pawn de la plantilla) y lista de zonas donde el edificio tapa al jugador | P0 | |
| D-06 | Buscar/importar packs de entorno victoriano y sonido; anotar licencias en `CREDITS.md` | P1 | |

**Mínimo F1 (hito):** blockout navegable en `main` y anunciado al equipo (B y C empiezan a colocar actores).

### F2

| ID | Tarea | Prioridad | Criterio |
|---|---|---|---|
| D-20 | Oclusión de cámara (material con dither/opacidad por distancia al jugador, o `Hidden in Game` por volumen) | P0 | El jugador y las telegráficas nunca quedan ocultos |
| D-21 | **Congelar layout** jugable al terminar F2 | P0 | Avisado al equipo; desde aquí solo cambios de arte |
| D-22 | Primera **build empaquetada** de prueba (Development, Win64) | P0 | Arranca en otro PC |
| D-23 | VFX reales de Corte, Retoma y parry (rellenando los placeholders) | P1 | |

### F3

| ID | Tarea | Prioridad |
|---|---|---|
| D-30 | Arte final de zonas sobre el blockout (sin mover rutas jugables) | P0 |
| D-31 | Iluminación nocturna: faroles, niebla volumétrica, Lumen; lectura clara de enemigos | P0 |
| D-32 | Ambiente sonoro (lluvia, viento, pasos, multitud distante) y SFX de combate/UI | P0 |
| D-33 | Música o capas de ambiente por fase (`OnStoryPhaseChanged`) | P1 |
| D-34 | Post-proceso «CONTINUIDAD ALTERADA» y Retoma | P1 |

### F4

| ID | Tarea | Prioridad |
|---|---|---|
| D-40 | Optimización básica (draw calls, niebla, sombras) a 60 fps en el PC más débil del equipo | P0 |
| D-41 | Build **Shipping** final, prueba en PC limpio, subida a la plataforma de la jam | P0 |
| D-42 | Capturas, GIF/video, página de la jam, `CREDITS.md` completo | P0 |

## 5. Notas técnicas

- El persistente **solo** se modifica con `git lfs lock`. Todo lo visual va a `_Geo` o `_Light`.
- Nada de *Build Lighting*: Lumen + luces dinámicas.
- No mover/renombrar assets ya referenciados por otros: cambia su contenido.
- Probar la build empaquetada pronto: los errores de empaquetado (assets de `Developers/`, referencias rotas, mapas no incluidos) aparecen ahí y no en el editor.
- Incluir `L_Whitechapel` y sus subniveles en *Project Settings → Packaging → List of maps to include*.

## 6. Decisiones abiertas de la división

- Proyección de cámara (D0.7) y su efecto en sombras/oclusión.
- Estilo: realista oscuro vs. estilizado (afecta a qué packs sirven).

## 7. Prompt de arranque para tu agente

```text
Trabajo en la División D (Mundo: nivel, arte, VFX, audio y build) del proyecto Unscripted (UE 5.8.4, Blueprint),
y soy además el integrador del repositorio.
Lee AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md,
docs/plan/D_MUNDO_ARTE_AUDIO_BUILD.md y después docs/02, docs/05, docs/06 y docs/07.
Tarea de hoy: <ID y título del backlog>. Criterio de aceptación: <copiar>.
Restricciones: como División D solo puedo modificar World/, Art/, Materials/, VFX/, Audio/,
los mapas L_Whitechapel (persistente), _Geo, _Light y L_Test_D, SourceData/D/, Scripts/D/ y CREDITS.md.
Como integrador puedo tocar Core/, Config/, .uproject y Plugins/ solo para aplicar contratos aprobados.
Entrégame: (1) los pasos en el editor o un script de Python del editor cuando sirva para trabajo en lote;
(2) cómo verificarlo; (3) cualquier efecto sobre otras divisiones, para avisarles.
```

## 8. Solicitudes de contrato (incluye peticiones de placeholders)

| # | Fecha | Petición | De quién | Estado |
|---|---|---|---|---|
| | | | | |

## 9. Estado

- [ ] F0 esqueleto publicado (si integrador)
- [ ] Blockout navegable en `main`
- [ ] Layout congelado + build de prueba
- [ ] F3 completo
- [ ] Build final entregada

Notas del día:
