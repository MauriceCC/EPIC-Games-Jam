# Whitechapel 240 × 180 m — Etapa 1: auditoría y planificación

> División D · 2026-11-15 · **No se ha modificado Unreal.** Solo consultas de lectura por MCP y archivos de texto propios de D.
> Referencias: imagen «Plan de nivel» (composición) y `SourceData/D/WHITECHAPEL_MASTERPLAN_CON_REQUISITOS_ASSETS_CLAUDE.md` (medidas). Las variantes de 60 × 54 y 100 × 90 m no se han usado como base.
> Todo lo que no figura en los documentos de diseño es **[PROPUESTA]**.

## Entregables de esta etapa

| Archivo | Contenido |
|---|---|
| `whitechapel_layout.json` | Envolventes, nodos (con coordenadas UE), espacios transitables, 156 volúmenes (139 ambientales, 10 hitos, 1 conector, 6 siluetas), muros, 12 portones, fases, props de comprobación, áreas libres, rutas y familias |
| `whitechapel_masterplan.svg` | Plano técnico cenital con cuadrícula de 10 m, cotas de ancho libre medidas, rutas y leyenda |
| `whitechapel_buildings.csv` | Una fila por colocación: grupo, familia, rectángulo, frente, altura, yaw de plano y de UE, coordenadas UE, oclusión |
| `whitechapel_routes.csv` | Tramos con ancho exigido y medido, rutas con longitud por tramo, portones con comportamiento |
| `validation_report.md` | Salida del validador (solapes, anchos, alcance por fase, rutas, nodos, recuentos) |
| `../whitechapel_assets.csv` | Inventario de recursos únicos (formato del anexo §12.9) |
| `Scripts/D/masterplan240_layout.py` | Fuente de todo lo anterior: `python -I Scripts/D/masterplan240_layout.py`. No usa Unreal |

---

## 1. Herramientas comprobadas

| Comprobación | Resultado |
|---|---|
| Servidor MCP | Plugin oficial `ModelContextProtocol` del editor, conectado en esta sesión (`unreal-mcp`) |
| Nivel abierto | `/Game/Unscripted/Maps/L_Whitechapel` con `_Geo`, `_Light`, `_AI`, `_Story` cargados |
| Toolsets usados | `SceneTools` (carpetas, actores), `ActorTools` (bounds, transform, label), `StaticMeshTools.get_bounds/get_triangle_count`, `ObjectTools.get_properties`, `ProgrammaticToolset.execute_tool_script` (Python aislado sin `import unreal`) |
| Disponibles para el blockout | `SceneTools.add_to_scene_from_asset/class`, `set_actor_folder`, `create_level_instance`, `trace_world`; `PrimitiveTools`; `PCGToolset`/`PCGSpatialToolset`; `EditorAppToolset` (capturas, PIE) |
| No comprobado en esta etapa | Capturas (`CaptureViewport`) y PIE: no se han lanzado para no alterar la sesión del editor |
| Límites conocidos | Editor en español (ids de nodos BP localizados); `execute_tool_script` no permite `.get(k, default)`; los scripts `Scripts/D/*.py` con `import unreal` requieren *Execute Python Script* |
| Scripts antiguos | **No se ha ejecutado ninguno** (`build_blockout.py`, `place_houses_v3.py`, etc.) |

## 2. Auditoría del mapa real (comprobado)

915 actores. Ejes del mapa actual: **UE X = norte, UE Y = este** (PlayerStart en X=300 al sur; taller en Y≈5450 al este).

| Subnivel | Dueño | Contenido relevante | Extensión (UE, cm) |
|---|---|---|---|
| `L_Whitechapel` | D | Sol, SkyAtmosphere, SkyLight, PostProcess, NavMeshBoundsVolume (centro 2700, 3000), RecastNavMesh | — |
| `L_Whitechapel_Geo` | D | 47 casas `Houses_v3`, 70 `Streets_v3`, `Ground` 170 × 170 m, 11 suelos, 12 particiones, 31 muros ocultos, **508 `CityBlocks` ocultos con colisión**, 26 fachadas ocultas, 75 elementos de calle, 51 de dressing, 3 NPC | X −1320…6720, Y −1120…7116 (Ground hasta 11 500) |
| `L_Whitechapel_Light` | D | 18 `BP_GasLamp`, 14 PointLight, 6 LocalFog, 4 Niagara, 3 AmbientSound, niebla | dentro de 0…6000 |
| `L_Whitechapel_AI` | **B** | 4 `BP_PatrolRoute`, 4 `BP_Pursuer`, 4 `BP_GuardFinisher`, `BP_Jack` + `BP_JackInteraction` en (3050, 5450) | X ≤ 3178, Y ≤ 5578 |
| `L_Whitechapel_Story` | **C** | `PlayerStart` (300, 1800), `BP_Checkpoint` ×2, `BP_Hideout` | X ≤ 1728, Y ≤ 3728 |

**No colocados todavía** (existen como clases en `Narrative/`, sin instancia en el nivel): `BP_Evidence`, `BP_FinalChoice`, `BP_Door`, `BP_StoryTrigger`. Tampoco hay Supervisor ni Interventor en `_AI`.

### Cámara real del jugador (comprobado en `BP_PlayerCharacter`, dueño A)

`IsoCameraArm`: TargetArmLength **1700**, rotación relativa **pitch −55°, yaw 45°**, `bInheritYaw = false`, sin test de colisión, con lag. `IsoCamera`: **perspectiva, FOV 40°** (horizontal).

Consecuencias calculadas (16:9):
- Altura de cámara ≈ 13,9 m; el encuadre a nivel del jugador cubre **≈ 12,4 m de ancho × 8,7 m de fondo**.
- La cámara mira al **noreste** desde el suroeste: las fachadas **al sur y al oeste** de un espacio jugable tapan al jugador. Una fachada de altura H oculta el suelo hasta 0,70·H detrás de ella en la dirección de la vista (7 m → 4,9 m; 10 m → 7 m).
- Una arena de 26 × 24 m **no cabe** en el encuadre: haría falta un brazo de ≈ 36 m para su anchura.

### Mallas medidas (bounds locales, escala 1)

| Malla | Medida (m) | Lectura para este plano |
|---|---|---|
| SM_House_Brick | 8,2 × 8,3 × 12 | No sirve para 6 × 10 sin deformar |
| SM_House_Shop | 6,8 × 6,8 × 10 | Frente de tienda; fondo insuficiente |
| SM_House_ShopLow | 6,7 × 5,8 × 4,5 | Cuerpo bajo / anexo |
| SM_House_Corner | 7,4 × 8,4 × 6 | Esquina con ajuste |
| SM_House_Filler | 13,5 × 7,5 × 12,5 | **Encaja con AR02 7 × 13 girado (escala 0,93/0,96)** |
| SM_House_Workshop | 17,3 × 10,8 × 11 | Falta fondo y sobra altura para el taller 16 × 18 × 6–7 |
| SM_House_Agency | 17,5 × 13,1 × 16 | Referencia; no cubre 38 × 24 |
| SM_Fountain_Square | **0,64 × 0,74 × 1,3** | Es una pila, no una fuente de 4–6 m |
| SM_Door_Wood_Frame / Leaf | **marco 1,3 × 1,4 de alto** / hoja 1,17 × 2,0 | Marco incoherente con la hoja |
| SM_Facade_Corner_A | **1,2 × 1,2 × 1,2** | Es un remate, no una esquina de fachada |
| SM_IronGate_A | 3,4 × 0,5 × 2,5 | Hueco útil por medir |
| SM_Handcart_A | 2,7 × 1,7 × 1,3 | Grande: escala uniforme 0,65 |
| SM_RecordStation_* | ≈1,6 × 1,0–1,1 × 1,4 | Necesitan base para 2,0 × 1,4 |
| SM_GasLamp_A, Barrel, CrateStack, Pillar, Cot, Wardrobe, Chair, Shelf, Cabinet | conformes | Reutilizar |

Tabla completa con estados en `whitechapel_assets.csv`.

## 3. Transformación plano → editor

El masterplan propone `UE_X = OffX + 100·X`. **Con los ejes reales del mapa eso espejaría el distrito** (en Unreal, +Y está 90° en sentido horario de +X visto desde arriba; con X = este, el norte quedaría al sur). La transformación correcta, coherente con el mapa actual y con la cámara a yaw 45° mirando al noreste, es:

```
UE_X   = OffX + 100 · y      (norte)
UE_Y   = OffY + 100 · x      (este)
UE_Z   = OffZ + 100 · z
yaw_UE = 90° − heading_plano   (heading 0 = este, 90 = norte)
```

| Opción | Offset (cm) | Distrito en UE | Ventaja | Inconveniente |
|---|---|---|---|---|
| **A (recomendada)** | (0, 12 000, 0) | X 0…18 000, Y 12 000…36 000 | No se solapa con nada del mapa actual (Ground llega a Y 11 500): se construye mientras el nivel actual sigue jugable y se cambia de golpe | NavMeshBounds y actores de B/C se mueven todos |
| B | (−600, −8 600, 0) | X −600…17 400, Y −8 600…15 400 | N01 cae sobre el PlayerStart actual | Solapa la geometría actual: obliga a descargar el Geo viejo antes de empezar |

Con cualquiera de las dos, **todos** los actores de B y C cambian de sitio: el recorrido nuevo no coincide con el de 60 × 54 m. Tabla de nodos con offset A:

| Nodo | Plano (m) | UE X, Y (cm) |
|---|---|---|
| N01 | 104, 9 | 900, 22400 |
| N02 | 104, 32 | 3200, 22400 |
| N03 | 78, 48 | 4800, 19800 |
| N04 | 106, 48 | 4800, 22600 |
| N05 | 117, 48 | 4800, 23700 |
| N06 | 140, 45 | 4500, 26000 |
| N07 | 158, 64 | 6400, 27800 |
| N08 | 176, 75 | 7500, 29600 |
| N09 | 176, 103 | 10300, 29600 |
| N10 | 181, 127 | 12700, 30100 |
| N11 | 205.5, 143 | 14300, 32550 |
| N12 | 214, 158 | 15800, 33400 |
| N13 | 211, 122 | 12200, 33100 |
| N14 | 212, 87 | 8700, 33200 |
| N15 | 161, 115 | 11500, 28100 |
| N16 | 120, 115 | 11500, 24000 |
| N17 | 94, 122 | 12200, 21400 |
| N18 | 122, 137 | 13700, 24200 |
| N19 | 92, 149 | 14900, 21200 |
| N20 | 77, 160 | 16000, 19700 |

## 4. Layout propuesto (resumen)

Ver el SVG. Red de espacios (anchos entre caras sólidas):

- **Sur:** avenida visual de 12 m (tramo navegable 84–124, cerrado con barricadas) y calle de llegada de 10 m hasta la plaza.
- **Plaza (SO):** 68 × 48 m transitables (contiene Z03). Fuente de 5 m en (75, 48) con anillo libre de 5 m; arenas A 18 × 16 al oeste y B 16 × 14 al este, como las dos cruces de la imagen; 7 puestos en los bordes norte y sur; carro en el borde oeste; 5 farolas; 8 coberturas.
- **Calle este (8 m)** hasta la entrada del taller N06. **Taller (SE):** cuerpo 16 × 18 con interior accesible, anexo 8 × 10, pasillo de 4 m, patio trasero 14 × 13 y portón lateral de 3 m (N07).
- **Escape (centro-este):** calle de 7 m → cuello 4,5 × 7 → ensanche de combate 17 × 15 (N09) → cuello 4,5 × 7 → calle de 7 m; dos nichos 4 × 6 y pasadizo de servicio de 3,5 m. Eje ≈ 68 m + 19 m de calle desde el taller.
- **Ruta azul A:** callejón de 4,5 m desde la calle norte, patio intermedio 12 × 10, arco de 3,5 m al paso central y tramo este hasta el ensanche (171, 104).
- **Paso central:** calle de 6 m desde el escape (N15) hasta el antepatio (N16).
- **Refugio (NE):** tránsito de 6 m, recinto amurallado con portón principal SO (N11) y de servicio SE, patio 20 × 17, casa 13 × 12 con estancia, cobertizo 5 × 7.
- **Evidencias (NE):** corredor sur–norte de 4,5 m (ruta verde) que une la ruta verde B, el patio de carga del informe (N14) y la enfermería (N13) con el portón de servicio del refugio; retorno al escape por un callejón de 3,5 m.
- **Supervisor:** antepatio 36 × 31 con arena libre 26 × 24 (N17), 4 pilares en las esquinas, rejas al sur (calle norte) y al este (paso central).
- **Archivo (NO):** cuerpo central 38 × 24 con vestíbulo (N19) y sala de elección 24 × 17 (N20), ala oeste 19 × 22, ala este 18 × 20, pórtico 16 × 9 y galería interior de 3,2 m; patio de acceso lateral con reja N18.

### Resultado del validador (`validation_report.md`)

| Comprobación | Resultado |
|---|---|
| Solapes edificio–edificio | **0** |
| Solapes sólido–espacio transitable | **0** (los 4 muros de linde con reja son intencionados y se listan aparte) |
| Props en áreas que deben quedar libres (arenas, anillo de la fuente, espera de Jack, frentes de estaciones, spawn r 3 m) | **0** |
| Anchos libres tras colocar props | **20/20 tramos cumplen** (p. ej. escape 5,5–6,0 m, cuellos 4,5 m, ruta azul 3,25–4,5 m, corredor de evidencias 4,5 m) |
| Rutas principal, A, B y de Jack (holgura 2,4 m desde su puesto) | **Conectadas** sin atravesar sólidos |
| Alcance por fase (portones cerrados según fase) | Sin fugas: en Acto I solo N01–N07; el escape solo tras abrir G-07; evidencias solo tras Jack a salvo; antepatio solo en Acto III |
| Envolventes de las piezas especiales | Todas dentro; Z16 dentro del cuerpo central |
| Huecos de 0–3 m entre volúmenes | 23, no transitables: se cierran con medianera o muro al construir |

Rejilla de 0,25 m: las anchuras medidas tienen ±0,25 m de resolución. Es una prueba en planta; **no sustituye** al NavMesh ni al recorrido en PIE.

## 5. Recuento: modelos únicos frente a instancias

| | Cantidad |
|---|---|
| Familias arquitectónicas | **10** (AR01–AR10) + siluetas |
| Mallas arquitectónicas únicas estimadas | ≈ 20–25 (variantes de AR01–AR05, 4 conjuntos especiales, kit de fachada) |
| Colocaciones ambientales del layout v1 | **139** (AR01 108, AR02 11, AR03 7, AR04 2, AR05 7, AR10 4) |
| Piezas especiales (hitos) | **10** + galería conectora |
| Siluetas lejanas sin colisión | 6 masas |

**Desviación respecto a §6 (61 colocaciones):** con casas de 6 m de frente, enmarcar con fachada continua todas las calles exigidas hace falta más del doble. Las cifras por grupo están en `validation_report.md` (M-E 21 frente a 8, M-I 22 frente a 5, etc.). Son **instancias** de unas pocas mallas, no modelos distintos. Si se quiere acercar el número de colocaciones a 61, la alternativa es una malla de **hilera de 3 casas (18 m)** por familia, que reduce a ≈ 60 colocaciones sin cambiar la planta. → decisión D3.

## 6. Contradicciones y ajustes que necesitan revisión antes de construir

| # | Asunto | Detalle | Propuesta |
|---|---|---|---|
| C1 | **Fórmula de conversión del masterplan** | `UE_X = 100·X` espejaría el mapa con los ejes reales | Usar `UE_X = 100·y`, `UE_Y = 100·x` (§3) |
| C2 | **Cámara vs arenas** | El encuadre real es ≈ 12 × 9 m; la arena del Supervisor es 26 × 24 y las de la plaza 18 × 16 | Solicitud a A: brazo variable por zona (≈ 2 400–3 600) o aceptar lectura parcial. D no toca la cámara |
| C3 | **Oclusión** | Fachadas S/O de 6,5–10 m tapan al jugador hasta ≈ 4,5–7 m detrás | Alturas mínimas en el lado cámara (ya aplicadas en el CSV) + sistema de fade/recorte de D (`World/`), P0 |
| C4 | Cuellos del escape 4,2–4,8 m vs «banda ≥ 5 m libre para Jack» | Incompatibles en el mismo tramo | Cuellos de 4,5 m sin props; holgura de Jack 2,4 m (regla de puertas). Validado |
| C5 | Puerta de taller 1,6–2,2 m vs paso de Jack ≥ 2,4 m | Incompatibles | Puerta trasera de 3 m (paso de Jack); entrada y lateral 2,5 m |
| C6 | Taller: «fachadas al sur/este, patio al norte» vs N06 (140, 45) | Con el patio al norte y la salida N07 al NE, N06 cae en la fachada **oeste** | Entrada al oeste desde la calle este; patio al norte como pide el texto |
| C7 | Orden N17 → N18 → N19 vs «verja de entrada al archivo de 4–5 m» en el antepatio | Dos lecturas posibles | Propuesta: tras el jefe se abre la reja lateral N18 → ala este → galería → vestíbulo N19. Las puertas frontales (G-ARCH) quedan selladas como bloqueo narrativo. Alternativa: entrar por el pórtico y usar N18 solo como checkpoint |
| C8 | La ruta amarilla plaza → norte → Supervisor de la imagen permite saltarse el taller y el escape | La ruta azul se cruza con esa calle | Rejas G-PN-S (cerrada en Actos I–II) y G-PN-N / G-CP (abren en Acto III). Requiere `BP_Door` de C |
| C9 | Ruta verde B abierta durante el escape permitiría coger evidencias antes de poner a Jack a salvo | §3.3 lo prohíbe | Portones G-B1/G-B2 cerrados hasta Jack a salvo (o comprobación de fase en `BP_Evidence`, de C) |
| C10 | Nodos N11 y N15 | N15 (161, 111) cae dentro de la hilera de casas; N11 (203, 146) dentro del recinto | N15 → (161, 115); N11 → (205,5, 143). Resto de nodos sin cambio |
| C11 | Envolventes de plaza | La hilera sur empieza en y = 14 (Z02 en 16) y la norte llega a y = 87 (Z02 en 83) | Ajuste de 2–4 m permitido por §0; documentado |
| C12 | 61 colocaciones de §6 | Insuficientes para fachada continua (ver §5) | Decisión D3 |
| C13 | Geometría heredada | 565 actores ocultos con colisión completa en `_Geo` (R1 del plano v4) | El blockout nuevo va en un subnivel nuevo; el `_Geo` viejo se descarga al cambiar (opción A) |
| C14 | Assets defectuosos | Fuente de 0,7 m; marco de puerta de 1,4 m de alto; `SM_Facade_Corner_A` de 1,2 m | Corregir antes de usarlos (CSV) |
| C15 | Plazo | La entrega cierra hoy 15-nov a las 17:59 PST. El plano completo son ≈ 150 volúmenes, 5 interiores y la reubicación de todo B/C | Recomendación: blockout de cajas por sectores (Z01→Z03→Z04 primero) y arte final solo donde se vea |

## 7. Actores de otras divisiones que tendrán que moverse (solo propuesta; los mueve su dueño)

| Actor actual | Dueño | Posición actual (UE) | Destino propuesto (plano → UE, offset A) |
|---|---|---|---|
| PlayerStart | C | 300, 1800 | N01 (104, 9) → 900, 22400 |
| C_Closure_CP0 / CP1 | C | 500, 1800 / 1600, 2700 | CP0 en N02; CP1 en N06; añadir en N12, N16 y N18 (reja) |
| C_Closure_AlleyHideout | C | 1100, 3600 | Nicho NI2 (185, 121) → 12100, 30500 |
| B_Jack_Workshop + B_Jack_Workshop_Interaction | B | 3050, 5450 | Puesto J0 (150, 52) → 5200, 27000 |
| Pursuers / Finishers de la plaza (2 + 2) y sus rutas | B | ≈1200–1900, 1200–2200 | Arenas A (55, 48) y B (96, 48) |
| B_Alley_Pursuer (+ finisher, ruta) | B | 1653, 3750 | Ensanche del escape N09 |
| B_Yard_Pursuer (+ finisher, ruta) | B | 1075, 5250 | [PROPUESTA] calle taller–escape o segundo cuello |
| Supervisor (no existe en el nivel) | B | — | N17 |
| Evidencias, estaciones finales, puertas (clases sin instancia) | C | — | N13, N14, Z16 (estaciones en (74,5, 163,5) y (79,5, 163,5)), portones de la tabla de `whitechapel_routes.csv` |
| Faroles, luces, niebla, audio | D | `_Light` | Rehacer en el sector nuevo |
| NavMeshBoundsVolume | D | persistente | Ampliar/duplicar para X 0…18 000, Y 12 000…36 000 |

## 8. Qué está comprobado y qué es propuesta

**Comprobado en el editor:** herramientas MCP disponibles; subniveles y número de actores; clases y posiciones de los actores de B/C; extensión de cada carpeta de `_Geo`/`_Light`; parámetros de cámara del jugador; bounds y triángulos de 7 casas y 28 props; materiales presentes en disco.

**Comprobado fuera del editor:** que el layout no tiene solapes de sólidos, que los anchos libres se mantienen tras colocar los props de prueba y que las rutas y fases se conectan (validador en planta).

**Propuesta, no comprobada:** todo el layout (posiciones, alturas, familias), el offset A, los portones y su lógica de fases, el reparto de grupos, el desglose de mallas, los destinos de los actores de B/C. Sin capturas ni PIE en esta etapa. Contenido de `BP_House_Brick`/`BP_House_Shop` (carpeta nueva sin seguimiento en Git), colisiones reales de las casas y mallas usadas por los actores de `Street/*`: sin auditar.

## 9. Decisiones que necesito antes del blockout

| # | Decisión |
|---|---|
| D1 | Aprobar el layout v1 (o indicar cambios sobre el SVG) |
| D2 | Offset A (zona libre, recomendado) o B (alineado al spawn actual) |
| D3 | Mantener ≈ 139 instancias de casas sueltas o crear hileras de 3 casas (≈ 60 colocaciones) |
| D4 | Lectura del acceso al archivo (C7): reja lateral N18 + ala este, o pórtico frontal |
| D5 | Portones de fase G-PN-S, G-PN-N, G-CP, G-B1, G-B2: ¿los acepta C (`BP_Door`)? |
| D6 | Enviar a A la solicitud de cámara (C2) |
| D7 | Sector piloto: Z01 → Z03 → Z04 en un subnivel nuevo `L_Whitechapel_Geo_v5` con cajas a escala 1,0 |
