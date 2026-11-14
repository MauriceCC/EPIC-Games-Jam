# Prompts de imágenes de referencia (concept → 3D)

> **Dueño:** División D. **Fecha:** 2026-11-14.
> **Decisiones de estilo del usuario (2026-11-14):** estilizado oscuro · desgaste "usado y húmedo" · estaciones del expediente: la oficial fría y la auténtica cálida.
> Se basa en `ART_BIBLE.md` (paleta, regla del cian) y en `AI_ASSET_BRIEF.md` (lista de props).
> Uso: generar **una imagen por prop** con cualquier generador de imágenes y convertirla en 3D con Meshy (props sueltos) o con Rodin (props "héroe").

## 1. Por qué las imágenes son así

- **Fondo liso gris claro, luz neutra y sin sombras proyectadas.** La imagen se convierte en un modelo 3D y su textura. Si la imagen ya tiene "noche", la oscuridad queda **pintada en la textura** y luego no se puede iluminar en Unreal. La atmósfera nocturna (faroles, niebla, lluvia) la pone el motor.
- **Un solo objeto, entero, centrado, en vista 3/4 desde algo arriba.** Es lo que mejor reconstruyen Meshy y Rodin, y coincide con cómo se verá desde la cámara isométrica.
- **Mismo bloque de estilo en todos los prompts.** Así parecen del mismo artista. No hay que cambiar el bloque; solo cambia el "SUBJECT".

## 2. Bloque de estilo común (copiar SIEMPRE)

**Objetos victorianos (1888):**

```text
STYLE: stylized dark Victorian game art, hand-painted textures, clean readable silhouette, slightly chunky and sturdy proportions, simplified shapes with confident bevels, muted desaturated palette of soot-stained brick red, dark brown aged wood, black wrought iron and dull brass, used and damp surfaces with light wear, subtle grime in crevices, no heavy damage, cohesive art direction as if made by the same artist for an isometric action game set in Whitechapel, London, 1888.
PRESENTATION: single isolated object, fully visible, centered, three-quarter view from slightly above, plain flat light-grey background, soft even neutral studio lighting, no cast shadows, no environment, no ground plane, no people, no text, no letters, no logos, no watermark.
```

**Tecnología de la agencia (anacrónica, solo las estaciones y piezas del Archivo):**

```text
STYLE: stylized dark game art, hand-painted textures, clean readable silhouette, slightly chunky proportions, anachronistic precision technology from a secret time agency hidden in 1888 London, black lacquered metal and polished brass, exposed clockwork details, thin glowing cyan light lines as the only bright accent, cohesive art direction with the Victorian props of an isometric action game.
PRESENTATION: single isolated object, fully visible, centered, three-quarter view from slightly above, plain flat light-grey background, soft even neutral studio lighting, no cast shadows, no environment, no ground plane, no people, no text, no letters, no logos, no watermark.
```

**Negative prompt** (si el generador lo admite):

```text
photorealistic, photo, realistic scan, night scene, dark background, dramatic lighting, cast shadows, multiple objects, cropped, cut off, text, letters, numbers, logo, watermark, signature, people, hands, blurry, low detail, cartoonish bright colors, neon, cyan on Victorian objects, futuristic plastic
```

## 3. Prompts por prop

Para cada uno: **SUBJECT + bloque de estilo correspondiente**. Nombra el archivo como indica la columna "Archivo".

### P0: hacen falta ya

| # | Archivo | Herramienta 3D | Bloque |
|---|---|---|---|
| 1 | `barrel.png` | Meshy | Victoriano |
| 2 | `crate_stack.png` | Meshy | Victoriano |
| 3 | `handcart.png` | Meshy | Victoriano |
| 4 | `gas_lamp.png` | Rodin | Victoriano |
| 5 | `station_official.png` | Rodin | Agencia |
| 6 | `station_authentic.png` | Rodin | Agencia |

**1 · Barril** (`SM_Barrel_A`, ~0,6 m de diámetro × 0,9 m de alto)
```text
SUBJECT: an old Victorian wooden storage barrel standing upright, dark brown oak staves, three black iron hoops slightly rusted at the edges, closed lid, small dent and water stains near the base.
```

**2 · Pila de cajas** (`SM_CrateStack_A`, ~1,5 × 1 × 2 m)
```text
SUBJECT: a stack of three rough wooden shipping crates, two at the bottom and one on top slightly rotated, dark weathered planks with iron corner brackets and rope tied around the top crate, blank surfaces with no markings.
```

**3 · Carretilla de mano** (`SM_Handcart_A`, ~2 × 1 × 1,2 m)
```text
SUBJECT: an empty Victorian street vendor's wooden handcart, flat cargo bed with low side rails, two large wooden spoked wheels with iron rims, two long pull handles resting on the ground, worn dark wood.
```

**4 · Farol de gas** (`SM_GasLamp_A`, ~3,2 m de alto)
```text
SUBJECT: a tall Victorian cast-iron gas street lamp, slender fluted black post with a simple heavy base, four-sided glass lantern on top with a small pointed cap, warm amber glass panes glowing softly, short horizontal ladder bar below the lantern.
```

**5 · Estación del expediente OFICIAL** (`SM_RecordStation_Official`, ~1,2 × 0,8 × 1,4 m), fría e imponente
```text
SUBJECT: an imposing official records registration desk of the time agency, cold black metal body with sharp rectangular forms, a thick sealed government dossier tied with red ribbon on top, a heavy brass stamping mechanism with a lever, a blood-red wax seal, rigid cyan light lines along the edges, authoritarian and bureaucratic mood.
```

**6 · Estación del expediente AUTÉNTICO** (`SM_RecordStation_Authentic`, ~1,2 × 0,8 × 1,4 m), cálida y humilde
```text
SUBJECT: a humble worn wooden records desk adapted by the time agency, scuffed warm brown wood with brass fittings, an open handwritten case file with loose papers and a small photograph pinned to it, a compact brass archival recorder with a soft cyan glowing lens, a small oil lamp, honest and personal mood.
```

### P1: si sobra tiempo

**7 · Fuente de la plaza** (`SM_Fountain_Square`, Rodin)
```text
SUBJECT: a small Victorian public drinking fountain, weathered grey granite basin on a short pedestal with a black cast-iron top and spout, simple and sturdy.
```

**8 · Carro volcado** (`SM_Cart_Overturned`, Meshy)
```text
SUBJECT: an overturned Victorian wooden goods cart lying on its side, one broken spoked wheel, a few burlap sacks spilled next to it.
```

**9 · Banco de trabajo del taller** (`SM_WorkshopTable_A`, Meshy)
```text
SUBJECT: a cluttered Victorian leather-worker's workbench, thick dark wooden top, hand tools, leather scraps, a small unlit oil lamp, a low shelf underneath.
```

**10 · Archivador de la agencia** (`SM_ArchiveCabinet_A`, Meshy, bloque de agencia)
```text
SUBJECT: a tall narrow filing cabinet with many small drawers, black lacquered metal and brass handles, a thin vertical cyan light strip on one side.
```

**11 · Columna del Archivo** (`SM_ArchivePillar_A`, Rodin, bloque de agencia)
```text
SUBJECT: a tall square machine pillar with exposed brass gears and pipes behind black metal panels, one vertical cyan light strip running from base to top.
```

## 4. Cómo comprobar la coherencia antes de pasármelas

- [ ] Todas tienen el **mismo fondo gris claro** y la misma luz suave.
- [ ] Los colores son apagados; ninguna imagen "brilla" más que las otras.
- [ ] **Ningún objeto victoriano tiene cian**; solo las estaciones y las piezas de la agencia.
- [ ] No hay texto ni letras, ni siquiera inventadas, en carteles o papeles.
- [ ] El objeto se ve entero, sin recortes.

Si una imagen desentona, regenérala con el **mismo prompt** antes de pasármela: cambiar el prompt rompe la coherencia.

## 5. Después

Guardar las imágenes en `C:\TRABAJOS\JUEGOS\AI_Staging\Refs\` (fuera del repo) con el nombre de la columna "Archivo". Después:

1. Confirmar el coste: Meshy unos 15 créditos por prop (`meshy-t2` + `meshy-n1`, topología limpia ~4.000–6.000 triángulos); Rodin según el saldo de la cartera.
2. Generar el 3D y revisarlo frente a la referencia.
3. Si se aprueba, importarlo a `Art/Props/<nombre>/` en Unreal (Rodin: corregir escala y pivote con `Scripts/D/fix_rodin_props.py`) y anotarlo en `CREDITS.md`.
