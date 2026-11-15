# Paso 5 — Assets del distrito: reutilizar, adaptar, generar

> División D · 2026-11-15 · Medidas tomadas en el editor (bounds a escala 1) y en el layout aprobado. Detalle completo en `../whitechapel_assets.csv`.
> El blockout de `L_Test_D` **no es arte final**: son cubos a medida sobre los que se sustituirá cada familia.
> Generación: imagen de referencia con GPT Image vía Meshy (9 créditos) → aprobación del usuario → 3D con Meshy (textura `meshy-7` PBR), importación, escala, pivote y colisión, y registro en `CREDITS.md`.

## A. Reutilizar tal cual

| Asset | Medida real (m) | Uso | Instancias en el layout |
|---|---|---|---|
| `BP_GasLamp` / `SM_GasLamp_A` | 0,8 × 0,8 × 3,2 | Farolas | 17 (25–40 previstas) |
| `SM_Barrel_A` | 0,72 × 0,72 × 0,9 | Cobertura | 20–35 |
| `SM_CrateStack_A` | 1,22 × 1,22 × 1,2 | Cobertura | 30–50 |
| `SM_ArchivePillar_A` | 1,63 × 1,58 × 4,0 | Pilares del antepatio y del archivo | 4 + 4–6 |
| `SM_Cart_Overturned` | 2,82 × 1,96 × 1,2 | Nichos del escape | 1–2 |
| `SM_Cot_A`, `SM_Wardrobe_A`, `SM_Chair_A`, `SM_Shelf_A`, `SM_ArchiveCabinet_A` | conformes | Interiores | según sala |
| `SM_Ledger_Nursing`, `SM_Folder_Report` | conformes | Evidencias (lógica de C) | 1 + 1 |
| `SM_LowWall_Stone_A`, `SM_DebrisPile_A` | 3,1 × 0,7 × 1,0 / 2,9 × 2,9 × 0,8 | Cobertura baja | por metros |
| `SM_House_Filler` (girada 90°) | 7,5 × 13,5 × 12,5 | **AR02** vivienda mediana 7 × 13 (escala 0,93 / 0,96) | 11 |
| Materiales de blockout (adoquín, losa, bordillo, ladrillo, madera, pizarra) | — | Suelos y paramentos | — |

## B. Adaptar (sin generar malla nueva)

| Asset | Problema medido | Cambio | Prioridad |
|---|---|---|---|
| `SM_Handcart_A` | 2,7 × 1,7 × 1,3 m (demasiado grande) | Escala uniforme 0,65 | P1 |
| `SM_Fountain_Square` | 0,64 × 0,74 × 1,3 m (es una pila) | Sobre base/vaso de 5 m (blockout ya puesto; malla de vaso en C) | P1 |
| `SM_RecordStation_*` | 1,6 × 1,0–1,1 m | Peana de 2,0 × 1,4 m (blockout ya puesto) | P1 |
| `SM_IronGate_A` | 3,4 × 0,5 × 2,5 m de total | Medir hueco útil y separar hojas; variante de 4,5 m | P0 |
| `SM_Door_Wood_Frame` | Marco de 1,4 m de alto frente a una hoja de 2,0 m | Reimportar o corregir el marco | P0 |
| `SM_WorkshopTable_A` | 1,46 × 0,96 (pide 2 × 0,9) | Aceptar | P2 |
| `SM_Facade_Brick_A` / `Shopfront_A` | Módulo de 4,8–5,1 m | Válido para frentes de 5 m; no para 6 m sin pilastra | P1 |
| `M_BO_WorldTiling_Occl` (nuevo) | — | Recorte de oclusión: llevarlo al material final de fachadas | P0 |

## C. Generar con Meshy (10 familias, no 139 casas)

Cada familia es **una malla** (o dos variantes) instanciada muchas veces. Las medidas son las de la huella del layout; la escala se corrige al importar sin deformar (tolerancia ±10 %).

| # | Modelo | Huella × altura (m) | Instancias | Prioridad | Estado |
|---|---|---|---|---|---|
| G1 | **Casa adosada AR01** (fachada + medianeras ciegas + tejado de pizarra) | 6 × 10 × 7 al alero (+2,5 de tejado) | 108 (variantes por material) | **P0** | **Imagen de prueba en curso** |
| G2 | **Puesto de mercado** | 5 × 3,5 × 2,8 | 7 | **P0** | **Imagen de prueba en curso** |
| G3 | Comercio AR03 (tienda con vivienda) | 8 × 13 × 9–11 | 7 | P1 | Tras validar G1 |
| G4 | Almacén / depósito AR05 con portón | 12 × 15 × 8–10 (variante 10 × 13) | 8 | P1 | |
| G5 | Esquina AR04 | 6–12 × 7–12 × 7–9 | 2 | P2 | |
| G6 | Taller de Jack AR06 (cubierta separable) | 16 × 18 × 6,5 | 1 | P1 | Interior por piezas |
| G7 | Casa-refugio AR07 | 13 × 12 × 8 | 1 | P1 | |
| G8 | Enfermería AR08 (fachada institucional) | 18 × 20 × 10 | 1 | P1 | |
| G9 | Archivo AR09: cuerpo central, ala, pórtico (por cuerpos) | 38 × 24 × 14; 18–19 × 20–22 × 11; 16 × 9 × 10 | 4 | P1 | Por piezas, no una sola malla |
| G10 | Cobertizo AR10 | 5 × 7 × 3,5 (variante 6 × 6) | 6 | P2 | |
| G11 | Carro victoriano entero | 2,2 × 4,5 × 2,2 | 2–3 | P1 | |
| G12 | Muro de cierre 2,3–3,2 m + pilar | tramo 3 × 0,4 × 2,8 | ~150 m lineales | P0 | Puede ser cubo con material hasta el final |
| G13 | Escritorio de enfermería | 1,8 × 0,85 × 0,8 | 1 | P2 | |
| G14 | Árbol sin hojas | copa 3–4, alto 5–7 | 3–6 | P2 | |
| G15 | Sacos, cubos, mercancía | 0,5–1 | 10–18 grupos | P2 | |
| G16 | Canalón y sumidero | modulares | 20–35 | P2 | |

**Coste estimado** (imagen 9 + 3D `meshy-7.1` con textura 30): ≈ 39 créditos por modelo. G1–G11 son unos 430 créditos; el saldo actual es de 1 031.

## D. Aceptación de cada modelo (antes de pasar al siguiente)

1. Escala real tras importar: huella dentro de ±10 % de la tabla, con **escala uniforme**.
2. Pivote en la esquina de ensamblaje (casas) o en la base (props). Sin escalas negativas.
3. Medianeras planas en AR01–AR03 para formar hileras sin huecos.
4. Colisión simple (caja por cuerpo); los portones con hueco real.
5. Lectura desde la cámara real (−55°, 17 m) y compatibilidad con el recorte de oclusión.
6. Triángulos: casa ≤ 15 k, puesto ≤ 8 k.

## E. Resultado de la prueba de calidad y escala (G1 casa AR01, G2 puesto)

Generado con imagen GPT Image vía Meshy (9 créditos cada una) y 3D `meshy-t2.5` smart topology + textura `meshy-7` PBR 2K (15 créditos cada uno). Total: 48 créditos; quedan ≈ 983.
Importado en `Art/Buildings/SM_House_AR01/` y `Art/Props/SM_MarketStall_A/` con material propio (`M_House_AR01`, `M_MarketStall_A`): base color, normal, roughness, metallic y el mismo recorte de oclusión que el blockout.
Colocado en `L_Test_D` (carpeta `MP240/ArtePrueba`, etiqueta `MP240_ART`) en lugar de `MD-N02` y `MC-S04` (casas) y `PR-STALL-S2` (puesto). El cubo de blockout queda invisible y **conserva su colisión**.

| Criterio | Casa AR01 | Puesto |
|---|---|---|
| Triángulos | 10 381 ✅ (≤ 15 k) | 7 383 ✅ (≤ 8 k) |
| Proporciones del modelo (frente : fondo : alto) | 4,6 : 6,0 : 9,6 | 9,6 : 5,3 : 7,2 |
| Escala uniforme aplicada | ×13 (frente = 6 m) | ×5,2 (largo = 5 m) |
| Medida en el mapa | 6,08 × 7,69 × 12,4 m (alero ≈ 7,7 m) | 4,96 × 2,75 × 3,79 m |
| Frente exigido | 6 m ✅ | 5 m ✅ |
| Fondo exigido | 10 m ❌ (−23 %; el resto lo cubre la caja del blockout) | 3,5 m ❌ (−21 %) |
| Altura | Alero 7,7 m: aceptable (+3 % sobre 7,5) | 3,8 m frente a ~2,8 m ❌ (+35 %; toldo alto) |
| Medianeras planas para hileras | ✅ sin ventanas en los laterales | — |
| Pivote | Centro del modelo ❌: hay que compensar Z al colocar | Ídem |
| Colisión propia | No importada: se usa la caja del blockout | Ídem |
| Lectura en la cámara real | Puerta, ventanas y farol a escala humana (`en_juego/pie_casa_calle_este.png`) | Se lee el toldo a rayas (`en_juego/pie_casa_y_puesto_plaza_sur.png`) |
| Texturas | Fachada fiel a la referencia; pizarra del tejado algo estirada; rugosidad y metal casi constantes (mapas de 32 px) | Correctas |

**Conclusión:** la calidad visual y el estilo son válidos. Meshy **no respeta el fondo pedido**: las dos piezas salen ~22 % más cortas de fondo. No se pueden escalar en un solo eje sin deformar puertas y ventanas.

**Propuesta para el resto (pendiente de aprobación):**
1. Casas AR01: aceptar el módulo de 6 × 7,7 m y completar el fondo hasta 10 m con un **cuerpo trasero** (anexo bajo de ladrillo, el *outrigger* típico de las terrace houses). Es una pieza sencilla, reutilizable y casi nunca a la vista. Alternativa: regenerar con una vista lateral explícita (`meshy_multi_image_to_3d`, 9 + 9 + 15 créditos), sin garantía de proporción.
2. Puesto: regenerar más bajo (2,8 m) o aceptar 3,8 m. Su huella cabe en la reserva de 5 × 3,5 m.
3. Siguientes generaciones con `origin_at: bottom` y la altura real indicada, para que el pivote quede en la base.
4. Orden siguiente: G3 comercio y G4 almacén (P1). Muros de cierre (G12) como cubos con material hasta el final.

## F. Inventario final del distrito vestido (L_Test_D, 2026-11-15)

Fuente: `Scripts/D/district_art_build.py` → `district_art_placements.json` (1 430 colocaciones con suelos interiores; 1 439 actores `MP240_FINAL` con niebla, postproceso y ambiente; 1 473 en total con las luces interiores, el NavMesh y el prototipo heredado `PR_*`).

### Familias arquitectónicas, mallas únicas e instancias

| Familia | Solución | Mallas únicas | Variantes de material | Instancias |
|---|---|---:|---:|---:|
| AR01 vivienda / AR02 / AR04 pequeña | Fachada Meshy `SM_HouseFront_AR01` (6 × 2,81 m, alero 7,2) + cuerpo y cubierta de kit hasta el fondo de la parcela | 1 | 3 (`MI_HouseFront_AR01`, `_B`, `_C`) | 120 |
| AR03 comercio / AR04 ancha / AR05 estrecha | Fachada Meshy `SM_ShopFront_AR03` (8 × 5,1 m, alero 9,5) + cuerpo + cubierta | 1 | 2 | 9 |
| AR05 almacén | Fachada Meshy `SM_WarehouseFront_AR05` (12 × 8,56 m, alero 8,5) + cuerpo + cubierta | 1 | 1 | 6 |
| AR10 cobertizo / anexo | Kit: madera + cubierta a un agua | 0 (kit) | — | 4 (+2 especiales) |
| Especiales (taller, refugio, enfermería, informe, archivo: cuerpo central, dos alas, pórtico y galería) | Cascarón de muros de kit con los huecos de puerta del layout, dinteles, cubierta, cornisa y ventanas de kit | 0 (kit) | piedra / ladrillo / madera | 11 |
| Fondo (Z17/Z18 y bordes) | Franjas de 6 m de casas simplificadas, alturas 7–11 m | 0 (kit) | 3 ladrillos | 6 masas (≈ 60 franjas) |
| **Kit** | `SM_KIT4_Box`, `_Gable`, `_Mono`, `_Cornice`, `_Window`, `_DecoBox`, `_DecoCyl` | 7 | — | ≈ 1 070 |

**Conteo justificado:** 139 parcelas ambientales del layout aprobado con 909,5 m de frente construible. Resultan 135 casas o comercios (las parcelas AR10 son cobertizos) dibujados con **3 mallas Meshy + 7 piezas de kit**. Ninguna parcela invade un recorrido (validado con trazas tras vestir) y ningún edificio es una fachada sin volumen: cada uno tiene cuerpo hasta el fondo de su parcela y cubierta.

### Props y mobiliario finales

| Elemento | Asset | Estado | Instancias |
|---|---|---|---:|
| Puesto de mercado | `SM_MarketStall_01` (corregido: 4,32 × 2,40 × 3,0 m, mostrador a ~0,9 m, pivote en la base) | GENERADO + CORREGIDO | 7 |
| Carro victoriano entero | `SM_Cart_Victorian` (4,5 × 2,38 × 1,99 m) | GENERADO | 1 |
| Fuente | `SM_Fountain_Square` sobre base Ø 5 m y vaso Ø 3,6 m de piedra | ADAPTADO | 1 |
| Farolas | `BP_GasLamp` (25 cd, radio 9 m, sin sombra) | REUTILIZADO | 17 |
| Cobertura | `SM_CrateStack_A`, `SM_Barrel_A`, `SM_Handcart_A` (×0,65) | REUTILIZADO | 12 / 8 / 1 |
| Pilares del antepatio | `SM_ArchivePillar_A` | REUTILIZADO | 4 |
| Mobiliario | Mesa, estantes, catre, armario, silla, archivadores (13), escritorios de kit (2) | REUTILIZADO / KIT | 22 |
| Evidencias (mallas; lógica de C) | `SM_Ledger_Nursing`, `SM_Folder_Report` sobre escritorio | REUTILIZADO | 2 |
| Estaciones finales | `SM_RecordStation_Official` (fría) / `_Authentic` (cálida) sobre peana de 2,0 × 1,4 m, a 5 m entre centros | REUTILIZADO + peana | 2 |
| Canalones y bajantes | Kit (hierro); bajantes sin colisión | KIT | 135 + 135 |
| Sumideros, charcos (manchas húmedas mates) | Kit sin colisión | KIT | 15 / 18 |
| Aceras con bordillo | Kit (losa York), calle de llegada, calle este y avenida | KIT | 6 tramos |
| Muros, cierres y albardillas | Kit (ladrillo + piedra) | KIT | 95 + 95 |
| Pilares de portón (hoja y lógica: C) | Kit (piedra) | KIT | 24 |
| Ventanas de edificios especiales | `SM_KIT4_Window` (30 % iluminadas) | KIT | 84 |

### Materiales finales (compartidos)

`MI_ART_BrickA/B/C` (ladrillo, 3 tonos), `MI_ART_Slate` (pizarra nueva repetible, tesela de 2 m ≈ hiladas de 25 cm), `MI_ART_Stone` (sillería nueva, 3 m), `MI_ART_Wood`, `MI_ART_Iron`, `MI_ART_Glass`, `MI_ART_GlassLit`, `MI_ART_Plaster`, `MI_ART_WetPatch` (charco mate, sin efecto espejo), `MI_ART_YardGround` (suelo de patio oscuro), más adoquín, losa y bordillo existentes. Todos los de muros y cubiertas derivan de `M_BO_WorldTiling_Occl` (mapeado mundial + recorte de oclusión; `CutRadius` 0,30 en muros y 0,9 en cubiertas). Los modelos Meshy usan `M_ART_MeshyPBR` (color, rugosidad, metal y normal de Meshy, sin canales inventados).

### Registro de modelos corregidos y descartados

| Modelo | Decisión | Motivo |
|---|---|---|
| `SM_House_AR01` (imagen única) | **Descartado** | Fachada estrecha: con alero de 7,2 m salía de 4,8 m de frente (haría falta deformarla +30 %) |
| `SM_MarketStall_A` | **Sustituido** por `SM_MarketStall_01` | Escala y pivote horneados; altura corregida de 3,8 a 3,0 m |
| Multivista AR01b / AR03 / AR05 | **Usados como bloque de fachada** | Proporción de fachada correcta (ancho/alero 0,84); fondo corto (2,8 / 5,1 / 8,6 m): se descarta su cubierta y el cuerpo y el tejado los pone el kit |
| `SM_KIT_*`, `SM_KIT2_*`, `SM_KIT3_*` | **Descartados** (sin uso en el mapa) | Orden de caras invertido (v1), normales suavizadas que estiraban la pizarra (v2) y normales invertidas por el cambio de ejes (v3). Vigente: `SM_KIT4_*` |
| `SM_BO_*` (blockout) | Sin uso en el arte final | Se conservan para pruebas |

### Créditos Meshy de esta fase

Imágenes: 4 multivista + 2 texturas (54) · 3D multivista: 4 × 30 (120) · total 174; saldo al iniciar 983 → **809**. Sin compras ni recargas.
