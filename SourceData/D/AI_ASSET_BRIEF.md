# Brief de assets generados con IA (D)

> **Dueño:** División D. **Fecha:** 2026-11-14. Estilo y reglas: [`ART_BIBLE.md`](ART_BIBLE.md). Licencias y créditos: [`ASSET_SOURCING.md`](ASSET_SOURCING.md) y `CREDITS.md`.
> Herramientas disponibles (perks de la jam): **Hyper3D Rodin** (Business hasta el 20-nov), **Meshy** (Pro), **fal** (30 $; también ofrece Rodin), **PBRgen** (Pro), **Tripo** (opcional).
> **Prioridad por el plazo (entrega el 15-nov, 17:59 PST):** primero P0; P1 solo si sobra tiempo.

## 1. Reglas comunes

- **Prompts siempre en inglés.** Pedir explícitamente *no text* (nada de letreros con letras inventadas).
- **Sufijo de estilo** que se añade a cada prompt de props victorianos:
  > `, stylized dark Victorian 1888 London, game-ready prop, clean readable silhouette from a top-down isometric camera, muted desaturated colors, worn and wet surfaces, no text, no logos, PBR textures`
- **Sufijo de estilo** para la tecnología de la agencia (anacrónica):
  > `, anachronistic precision technology, black metal and polished brass, thin glowing cyan light accents, clean industrial design, game-ready prop, no text, no logos, PBR textures`
- **Prohibido el cian en props victorianos** (`ART_BIBLE §2`).
- **Exportar FBX o GLB.** Topología limpia o de bajo poligonaje si la herramienta lo ofrece (Tripo: "Topología limpia"; Meshy: low poly / remesh).
- **Presupuesto:** props pequeños ≤ 5k triángulos, medianos ≤ 15k, "héroe" ≤ 30k. Texturas de 2K como máximo.
- **Descargar a una carpeta FUERA del repo**, p. ej. `C:\TRABAJOS\JUEGOS\AI_Staging\`. Al repo solo entran los `.uasset` importados.
- **Al importar:** escala real (comprobar con el maniquí de ~1,8 m), pivote en la base, carpeta `Art/Props/` (o `Materials/` para texturas) y prefijos de `ART_BIBLE §10`.
- **Créditos:** cada asset generado se anota en `CREDITS.md` (herramienta, fecha y prompt abreviado). Al entregar, listar las herramientas en *"Tools you used"*: Rodin, Meshy, fal, PBRgen. Rodin cuenta para el premio de Hyper3D.

## 2. Props 3D

| P | Asset | Herramienta | Tamaño real | Dónde va (`LEVEL_DESIGN`) | Prompt (+ sufijo victoriano o de agencia) |
|---|---|---|---|---|---|
| **P0** | `SM_GasLamp_A` | Rodin | 3,2 m de alto | Faroles de todas las zonas | `Victorian cast-iron gas street lamp on a tall slender post, four-sided glass lantern with warm amber glass, ornate but simple base` |
| **P0** | `SM_Barrel_A` | Meshy | Ø 0,6 × 0,9 m | Coberturas bajas | `old wooden barrel with dark iron hoops, slightly dented` |
| **P0** | `SM_CrateStack_A` | Meshy | 1,5 × 1 × 2 m | Coberturas altas del Callejón y el Patio | `stack of three rough wooden shipping crates, rope and iron corner brackets` |
| **P0** | `SM_Handcart_A` | Meshy | 2 × 1 × 1,2 m | Carretilla del Callejón | `Victorian wooden handcart with two large spoked wheels and long handles, empty` |
| **P0** | `SM_RecordStation_Official` | **Rodin** | 1,2 × 0,8 × 1,4 m | Estación 1 de la Sala de registros | `official records registration desk, sealed government dossier on top, rubber stamp mechanism, red wax seal, imposing and bureaucratic` + **sufijo agencia** |
| **P0** | `SM_RecordStation_Authentic` | **Rodin** | 1,2 × 0,8 × 1,4 m | Estación 2 de la Sala de registros | `worn records desk with an open handwritten case file and loose evidence papers, small brass archival recorder, humble and honest` + **sufijo agencia** |
| P1 | `SM_Fountain_Square` | Rodin | 2 × 2 × 2,5 m | Centro de la Plaza | `small Victorian stone drinking fountain with a cast-iron top, weathered granite` |
| P1 | `SM_Cart_Overturned` | Meshy | 3 × 1,5 × 1,5 m | Paso central | `overturned Victorian wooden goods cart lying on its side, broken wheel, scattered sacks` |
| P1 | `SM_WorkshopTable_A` | Meshy | 2 × 1 × 0,9 m | Taller de Jack | `cluttered Victorian workbench with tools, leather scraps and an oil lamp` |
| P1 | `SM_ArchiveCabinet_A` | Meshy | 1,2 × 0,5 × 2,2 m | Bordes del Archivo | `tall filing cabinet with many small drawers` + **sufijo agencia** |
| P1 | `SM_ArchivePillar_A` | Rodin | 1 × 1 × 4 m | Columnas del Archivo | `tall machine pillar with exposed gears, pipes and a vertical cyan light strip` + **sufijo agencia** |
| P2 | `SM_IronGate_A` | Meshy | 4 × 0,2 × 3 m | Verja cerrada Plaza–Refugio | `Victorian wrought-iron double gate, closed, chained and padlocked` |
| P2 | `SM_Bench_A`, `SM_Sacks_A`, `SM_Crate_Single` | Meshy | — | Decoración | Variantes simples |

**Assets de otras divisiones (solo si los piden):** el bastón del agente y el dispositivo de muñeca son de **A**; Jack y los enemigos, de **B**. D puede generarlos y entregárselos, pero el dueño decide. **No generar personajes riggeados ahora:** no hay tiempo para retargeting.

## 3. Texturas PBR (PBRgen, en la web)

Materiales repetibles (*tileable*) para vestir el blockout. Exportar 2K: Base Color, Normal y ORM (o Roughness + AO por separado).

| P | Material destino | Uso en el blockout | Prompt |
|---|---|---|---|
| **P0** | `MI_Cobble_Wet` | Suelos de todas las zonas exteriores | `wet dark cobblestone street, rounded granite setts, rain puddles in the gaps, Victorian London at night, tileable` |
| **P0** | `MI_Brick_Dirty` | Muros exteriores y fachadas | `dark soot-stained red brick wall, uneven mortar, damp and grimy, Victorian London, tileable` |
| **P0** | `MI_WoodPlanks_Old` | Suelos de Taller y Refugio | `old dark wooden floor planks, worn and scratched, tileable` |
| P1 | `MI_Plaster_Stained` | Muros interiores y tabiques | `stained cracked plaster wall with damp patches, muted grey-beige, tileable` |
| P1 | `MI_AgencyMetal` | Suelo y muros del Archivo | `black brushed metal floor panels with thin brass trim lines, clean futuristic, tileable` |
| P2 | `MI_WroughtIron` | Verjas y faroles | `dark wrought iron with light rust, tileable` |

## 4. Orden de trabajo

1. **PBRgen:** generar las 3 texturas P0 → descargarlas a `AI_Staging\Textures\`.
2. **Rodin:** el farol y las 2 estaciones de expediente (lo más visible y lo que cuenta para el premio).
3. **Meshy:** barril, cajas y carretilla, en lote.
4. **Con Unreal MCP activo:** se importan, se crean los `MI_` y se aplican al blockout cambiando los materiales en `blockout_layout.json` (sin mover rutas jugables).
5. P1 y P2 solo si sobra tiempo.
