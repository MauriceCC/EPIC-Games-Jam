# Whitechapel v4 — auditoría, plano de masas y flujo de trabajo

> División D · 2026-11-15 · Fases 1–3 del encargo de diseño de niveles. **No se ha modificado el nivel** salvo una copia de seguridad.
> Todo lo que no está en `docs/` es **[PROPUESTA]**. Las zonas jugables, conexiones y huecos de B/C de `LEVEL_DESIGN.md §6–§9` se conservan: el rediseño cambia la ciudad que rodea a los espacios, no el recorrido.

Copia de seguridad: `/Game/Unscripted/Maps/Backup_20261115/L_Whitechapel_Geo_Bak` y `L_Whitechapel_Light_Bak`. AI y Story son de B y C y no se tocan.

Capturas del estado actual: `antes_cenital.png`, `antes_isometrica.png`, `antes_camara_plaza.png` (en esta carpeta).

---

## Fase 1 — Capacidades

| Pregunta | Respuesta verificada |
|---|---|
| Versión de Unreal | **5.8.4** (CL 58902052, `++UE5+Release-5.8`, build del Launcher) |
| Servidor MCP | **Plugin oficial `ModelContextProtocol` de Epic** dentro del editor, `http://127.0.0.1:8000/mcp`, con `AllToolsets` (activado hoy, solo en el `.uproject` local) |
| Inspeccionar actores | `SceneTools.find_actors / get_actors_in_folder / trace_world`, `ActorTools.get_actor_bounds / get_components / get_actor_transform`, `ObjectTools.get_properties` |
| Transformar | `ActorTools.set_actor_transform / look_at`, `SceneTools.add_to_scene_from_asset (snap_to_ground) / set_actor_folder / remove_from_scene / merge_actors`, `create_level_instance` |
| Materiales | `MaterialTools` (grafo), `MaterialInstanceTools` (parámetros), `TextureTools` |
| Capturas | `EditorAppToolset.CaptureViewport` con **pose libre** (cenital, isométrica, cámara del jugador) y **cuadrícula de coordenadas superpuesta**; `CaptureEditorImage` (pantalla completa del editor, sirve durante PIE) |
| Scripts | `ProgrammaticToolset.execute_tool_script`: Python **aislado** que solo encadena herramientas (sin `import unreal`). Los scripts de `Scripts/D/*.py` con `import unreal` siguen necesitando *Tools → Execute Python Script* |
| PIE | `StartPIE / StopPIE / IsPIERunning` + transformaciones de actores en el mundo PIE + `LogsToolset.GetLogEntries` |
| PCG | **Sí.** `PCGToolset` y `PCGSpatialToolset` (crear grafos, nodos, volúmenes, ejecutar, inspeccionar datos por nodo, dibujar splines). Skills en el editor: `Skill_PCGGraphGeneration` (obligatoria), `Skill_PCGShapeGrammarDefinition` (secuencias de módulos a lo largo de un camino → **fachadas en hilera**), `Skill_PCGInstancingOnMeshActor` (detalle sobre superficies), `Skill_PCGAssetZoo`, `Skill_InstantLevelOperations` |
| Búsqueda de assets | `SemanticSearchToolset` (vectores + BM25) |
| Skills de Claude Code | `unreal-engine-skills-for-claude-code` ya instalado (skills `unreal-mcp`, `create-toolset`, `unreal-skill`); usa el mismo MCP, no lo sustituye |
| Descartado | `uemcp` (ATDev): declara UE 5.0–5.7, ejecución remota de Python sin autenticación, duplica el MCP oficial |

Límites detectados:
- El editor está en español: los `type_id` de nodos de Blueprint están localizados y el DSL `write_graph_dsl` no cablea la ejecución (ver memoria del agente). No afecta a la colocación de actores ni a PCG.
- `CaptureViewport` usa el FOV del visor (~90°), no el de la cámara del jugador (40°). Para la vista real del jugador: capturar durante PIE con `CaptureEditorImage`.
- `get_properties` no lee `bHiddenEd` ni `extendedBounds`; los tamaños nativos se derivan de bounds ÷ escala.

---

## Fase 2 — Inventario del nivel

### Composición (915 actores)

| Subnivel | Dueño | Contenido |
|---|---|---|
| `L_Whitechapel` (persistente) | D | Sol, cielo, SkyLight, PostProcess, NavMeshBoundsVolume (v −3…57 m, u −1…61 m, z −3…7 m), RecastNavMesh |
| `L_Whitechapel_Geo` | D | 830 StaticMeshActor + 3 NPC esqueléticos |
| `L_Whitechapel_Light` | D | 18 `BP_GasLamp`, 14 PointLight, 6 LocalFog, 4 Niagara (vapor/lluvia), 3 AmbientSound, niebla de altura |
| `L_Whitechapel_AI` | B | 4 `BP_Pursuer` + 4 `BP_GuardFinisher`, 4 `BP_PatrolRoute`, `BP_Jack` (30,5 ; 54,5 m), `BP_JackInteraction` |
| `L_Whitechapel_Story` | C | PlayerStart (3 ; 18 m), 2 `BP_Checkpoint`, 1 `BP_Hideout` |

### `L_Whitechapel_Geo` por carpeta

| Carpeta | Actores | Estado en juego | Colisión |
|---|---|---|---|
| `Houses_v3` (casas enteras de Meshy) | 47 | visible | sí |
| `Streets_v3` (aceras, bordillos, props de tienda) | 71 | visible | sí |
| `Ground` (gran suelo exterior, 170 × 170 m) | 1 | visible | sí |
| `Blockout/Floors` (suelos por zona) | 11 | visible | sí |
| `Blockout/Partitions` | 12 | visible | sí |
| `Blockout/Cover` | 1 | visible | sí |
| `Street/*` (bolardos, sumideros, charcos, tramos) | 75 | visible | sí |
| `Dressing/*` (props por zona, NPC, clusters) | 51 | visible | sí |
| **`Blockout/Walls`** | 31 | **oculto** | **sí** |
| **`CityBlocks/High`, `Low`, `Roofs`, `Chimneys`** | 508 | **oculto** | **sí** |
| **`Dressing/Facades`** | 26 | **oculto** | **sí** |

### Edificios (`Houses_v3`)

7 mallas para 47 casas: Brick (~8,1 × 8,3 × 12 m), Shop (~6,7 × 6,7 × 10 m), ShopLow (~6,7 × 5,8 × 4,5 m), Corner (~7,4 × 8,4 × 6 m), Filler (~13,5 × 7,6 × 12,5 m), Workshop (~10,8 × 17,2 × 11 m), Agency (~13,2 × 17,5 × 16 m). Los tamaños nativos están derivados de bounds ÷ escala.

Escalas aplicadas: **no uniformes en 46 de 47 casas** (solo H08 se acerca a uniforme). Rango por eje 0,49–2,07; relación máxima entre ejes ≈ 4:1 (H01 1,19 × 2,07 × 1,02; H30 1,37 × 0,50 × 0,92; H13 0,99 × 0,71 × 0,49). 18 casas con escala **negativa** (espejo).

Huella construida: x −6…60,6 m, y −6…66 m. Zonas jugables según `LEVEL_DESIGN.md §6` (60 × 54 m).

Modulares disponibles: `SM_Facade_Brick_A` (4,8 × 1,1 × 7 m), `SM_Facade_Shopfront_A` (5,1 × 1,2 × 7 m), `SM_Facade_Corner_A`, `SM_LowWall_Stone_A`, `SM_Drainpipe_A`, puertas e `SM_IronGate_A`. Más 21 props, `SM_GasLamp_A` y 9 personajes.

Materiales de suelo: `MI_Ground_Cobble_Dark` (exterior), `MI_Cobble_Wet` (Plaza), `MI_Flagstone_York` (aceras), `MI_Kerb_Granite`, `MI_Puddle_Wet`, `MI_WoodPlanks_Old`, `MI_Brick_*`, `MI_Roof_Slate`.

### Qué está bien

- La **estructura jugable** (secuencia de zonas, anchos de §3, arenas ≥ 12 × 12 m, conexiones de §7) funciona: en Play los Perseguidores patrullan y combaten, Jack está en el Taller, los checkpoints de C responden.
- **Calle a escala de jugador** en la Plaza: empedrado, aceras con bordillo, farolas, toldos y escaparates se leen bien desde la cámara (ver `antes_camara_plaza.png`).
- Props y personajes coherentes con 1888; HUD en inglés.

### Qué hay que rediseñar (por prioridad)

| # | Problema | Evidencia | Consecuencia |
|---|---|---|---|
| R1 | **565 actores ocultos con colisión completa** (antiguos muros, manzanas, tejados, fachadas) | `bHidden = true`, `collisionEnabled = QueryAndPhysics` | Paredes invisibles, NavMesh recortada por geometría que no se ve, trazas de visión de los guardias bloqueadas por nada visible |
| R2 | **Casas deformadas** por escala no uniforme y espejadas | 45/47 con escala no uniforme, ratios hasta 4:1 | Puertas de 1 m o de 3 m, ventanas estiradas, cornisas aplastadas; la principal causa de "proporciones raras" |
| R3 | **Manzanas sin continuidad**: casas sueltas con huecos y muros de blockout | Cenital e isométrica | Aspecto de laberinto, no de calle adosada victoriana |
| R4 | **Gran tapiz exterior**: el suelo de 170 × 170 m con `MI_Ground_Cobble_Dark` brilla azul y parece tejado | Isométrica | No hay ciudad fuera del recorrido; la escena se lee como maqueta sobre una alfombra |
| R5 | **Interiores sin techo sobreexpuestos** (Refugio, Taller, Archivo cian) | Cenital | Manchas de luz que dominan el encuadre; cajas abiertas |
| R6 | **Charcos** como discos oscuros de borde duro | Cámara de la Plaza | Se leen como agujeros |
| R7 | **Repetición**: 7 mallas para 47 casas, mismos tejados azulados | Isométrica | Monotonía a distancia |
| R8 | Huella construida (66 × 72 m) mayor que la del diseño (60 × 54 m) | Bounds | Manzanas de borde que nadie ve de cerca; coste de actores sin función. El NavMeshBounds (v −3…57, u −1…61 m) sí cubre todas las zonas |

---

## Fase 3 — Diseño profesional

### Principios aplicados

1. **El recorrido manda.** Las 11 zonas y 10 conexiones de `LEVEL_DESIGN.md` quedan igual: B y C ya colocaron patrullas, Jack, checkpoints y escondite sobre ellas.
2. **Calle adosada (terrace), no casas sueltas.** Whitechapel 1888 = hileras continuas de 2–3 plantas, medianeras compartidas, esquinas achaflanadas, patios traseros. Cada manzana es un bloque cerrado con fachada continua hacia la calle.
3. **Escala correcta por construcción.** Planta baja 3,5 m, plantas superiores 3 m, cornisa + tejado 2–3 m. Frente por parcela **5 m** (= un módulo de fachada). Puertas 1 × 2,2 m. **Escala uniforme 1,0**; tolerancia máxima ±10 % en un eje. Prohibidas las escalas negativas: el espejo se hace con rotación de 180°.
4. **Regla de cámara** (Pitch −55°, Yaw 45°, cámara al suroeste): las fachadas que quedan **al sur o al oeste** de un espacio jugable tienen 1 planta (4,5 m) o corte de maqueta; las del **norte y este**, 2–3 plantas (7–11 m). El fondo norte y este remata con siluetas altas.
5. **Jerarquía de calles legible.** Principal: Plaza y Paso central (calzada ≥ 8 m + aceras de 2 m). Secundaria: Callejón (4 m, sin acera). Patios: Patio del taller y Tramo al refugio (adoquín irregular, sin bordillo). El material del suelo cambia con la jerarquía.
6. **Composición por encuadre.** Un foco de luz dominante por encuadre, siluetas recortadas contra fondo oscuro, cian solo en la Agencia. Los props se agrupan por oficio (no repartidos al azar) y nunca en el centro de una arena.
7. **Ciudad más allá del recorrido.** Anillo exterior de 1–2 manzanas de tejados y chimeneas sin colisión, que se funde en la niebla. Sustituye al gran suelo exterior.

### Plano de masas v4

Celda = 2 × 2 m; `u` = este (eje Y de Unreal), `v` = norte (eje X). Letras = zonas jugables de `LEVEL_DESIGN.md §6`. Cifras = plantas del edificio que ocupa esa celda (**1** = lado cámara, **3** = fondo de un espacio, **2** = interior de manzana / relleno). Generado por `Scripts/D/plano_v4_masas.py`.

```text
v= 60 |222222222222222333333222222222222222|
v= 54 |222222222222111EEEEEE333222222222222|   E = Registros (Agencia)
v= 48 |222222222111SSSSSSSSSSSS333222222222|   S = Archivo
v= 42 |222233333111SSSSSSSSSSSS333222222222|
v= 38 |222233333111SSSSSSSSSSSS333333332222|
v= 36 |2111RRRRRR331111XXXXXXXXXX3333332222|   R = Refugio   X = Paso central
v= 32 |2111RRRRRRttttttXXXXXXXXXXTTTTTT3332|   t = Tramo     T = Taller
v= 24 |2111RRRRRR111111XXXXXXXXXXTTTTTT3332|
v= 22 |222111PPPPPPPPPP1111111111AAAAAA3332|   P = Plaza     A = Patio del taller
v= 18 |222111PPPPPPPPPPCCCCCCCCCCAAAAAA3332|   C = Callejón
v= 14 |222111PPPPPPPPPP1111hh1111AAAAAA3332|   h = Rincón
v= 10 |222111PPPPPPPPPP1111111111AAAAAA3332|
v=  8 |222222111IIIIII133221122221111112222|   I = Inicio
v=  2 |222222111IIIIII333222222222222222222|
v= -4 |222222222111111222222222222222222222|
       u=-6                              u=66
```
(Filas representativas; la cuadrícula completa la imprime el script.)

### Manzanas

| Manzana | Rect. u × v (m) | Frente a | Plantas | Composición |
|---|---|---|---|---|
| M1 Sur | −6…66 × −6…0 | Inicio (norte) | 1 frente al Inicio, 2 resto | Hilera de tiendas bajas con escaparate y toldo hacia el Inicio |
| M2 Oeste de la Plaza | −6…6 × 0…22 | Plaza (este) | 1 | Fachada baja continua con puestos de mercado; corte de maqueta hacia la cámara |
| M3 Rincón | 26…46 × 0…14 | Plaza (oeste), Callejón (norte) | 1 al Callejón, 2 a la Plaza | Pub en esquina a la Plaza (foco de luz cálido); el Rincón (h) es un hueco entre dos casas |
| M4 Este del Patio | 58…66 × 0…34 | Patio, Taller (oeste) | 3 | Almacenes y talleres altos; remate de fondo |
| M5 Entre Callejón y Paso | 26…46 × 18…22 | Callejón (sur), Paso (norte) | 1 | Fila estrecha de casas de una crujía; tejados bajos para ver el Paso central |
| M6 Refugio | −6…2 × 22…36 + Refugio | — | 1 lado oeste; interior con techo recortado | Casa de vecindad; techo solo sobre la mitad norte |
| M7 Norte del Tramo | 14…26 × 32…36 | Tramo (sur) | 1 | Tiendas bajas |
| M8 Archivo | 18…42 × 36…48 + bordes | Paso (sur) | Muro de la Agencia, 3 al norte y este | Edificio institucional: pilastras, verja, sin toldos |
| M9 Agencia / Registros | 18…42 × 48…60 | Archivo | 3 + remates cian | `SM_House_Agency` sin deformar, centrado en el eje del Archivo |
| M10 Taller | 46…66 × 22…48 | Patio, Paso | 2–3 | Nave de taller con chimeneas; puerta lateral de C hacia el Paso |
| Anillo exterior | fuera de −6…66 × −6…60 | — | Siluetas 2–4 | Tejados y chimeneas sin colisión, sin suelo visible: se funden en la niebla |

### Interiores

Refugio, Taller, Archivo y Registros siguen siendo **salas sin techo** (la cámara isométrica tiene que ver dentro), con dos cambios:
- Muros del lado cámara a 3 m y muros de fondo a altura completa, con cornisa.
- Luz interior al **40–50 %** de la actual y un solo foco principal por sala; el cian del Archivo, limitado a las estaciones y la columna de la Agencia.

### Sector de prueba (Fase 4, pendiente de aprobación)

**Inicio + Plaza + boca del Callejón** (u −6…34, v −6…22). Es lo primero que ve el jugador, contiene la primera pelea y los checkpoints CP0/CP1, y sus manzanas (M1, M2, M3) cubren los tres tipos de frente (bajo hacia la cámara, esquina y fondo).

Pasos:
1. Crear el subnivel `L_Whitechapel_Geo_v4` (nuevo, de D). El actual queda intacto.
2. **Quitar la colisión** a los 565 actores ocultos (o moverlos a `L_Whitechapel_Geo_Legacy` descargado) y comprobar con B que patrullas y NavMesh siguen bien. Va primero porque afecta a todo lo demás.
3. Construir M1–M3 con fachadas modulares de 5 m a escala 1,0 (`SM_Facade_*` + `SM_House_*` sin deformar como volúmenes traseros), mediante un script de colocación alimentado por una tabla de parcelas.
4. Detalle de acera con PCG (`Skill_PCGInstancingOnMeshActor`): bajantes cada 2 parcelas, bolardos, sumideros; densidad baja y exclusión del centro de las arenas.
5. Sustituir el gran suelo exterior por el anillo de siluetas en el sector.
6. Capturas cenital, isométrica y en PIE desde la cámara real; recorrido del Inicio al Callejón en Play con dos Perseguidores.

### Herramientas recomendadas

| Necesidad | Herramienta |
|---|---|
| Plano y parcelas | Tabla CSV/JSON en `SourceData/D/plano_v4/` + `plano_v4_masas.py` |
| Colocación modular exacta | `ProgrammaticToolset` → `add_to_scene_from_asset` + `set_actor_folder`, a escala 1,0 |
| Fachadas en hilera | PCG con `Skill_PCGShapeGrammarDefinition` sobre un spline por frente de manzana (solo si el script de parcelas se queda corto) |
| Detalle disperso | PCG con `Skill_PCGInstancingOnMeshActor` |
| Verificación | `CaptureViewport` con cuadrícula (cenital/isométrica) + PIE con `CaptureEditorImage` + `trace_world` para huecos y solapes |
| Assets nuevos | Megascans (Fab) para suelos y muros, si se aprueba; Meshy solo para piezas que falten |

---

## Flujo permanente (cada cambio importante)

1. **Analizar**: inventario por carpeta, bounds, escalas, colisión, actores de B/C en la zona.
2. **Diseñar**: actualizar la tabla de manzanas y el plano de masas antes de colocar nada.
3. **Construir por sectores** en un subnivel nuevo o en una copia, nunca en el original sin copia.
4. **Capturar** siempre los mismos tres encuadres por sector:
   - cenital, pitch −90°, con cuadrícula de 6 m;
   - isométrica general, desde (−22, −18, 52 m) con pitch −45° y yaw 45°;
   - cámara real del jugador en PIE.
5. **Evaluar y corregir**:
   - Escala: puertas de ~2,2 m junto a un personaje.
   - Continuidad: sin huecos entre fachadas.
   - Legibilidad: el jugador visible y un solo foco de luz.
   - Recorrido: el NavMesh cubre la zona y la patrulla de B la completa.
   - Rendimiento: número de actores y de luces.

No dar un sector por terminado sin las tres capturas y el recorrido en Play.

## Decisiones pendientes

| # | Decisión | Quién |
|---|---|---|
| D1 | ¿Aprobar el sector de prueba Inicio + Plaza + boca del Callejón en un subnivel nuevo? | Usuario (D) |
| D2 | ¿Quitar la colisión a los 565 actores ocultos? Puede cambiar el NavMesh por el que patrulla B | D + B (Jesús) |
| D3 | ¿Usar Megascans de Fab para suelos y muros? | Usuario |
