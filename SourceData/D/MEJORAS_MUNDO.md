# Mejoras del mundo — Whitechapel (diagnóstico y plan)

> Dueño: División D. Fecha: 2026-11-15. Base: capturas del editor de Yizens tras la tanda 1 (fachadas, ventanas, faroles, vapor, NPCs, fondo) y revisión con la cámara del juego (Pitch −55°, Yaw 45°).
> Todo lo marcado **[PROPUESTA]** es una decisión de arte de D que no cambia rutas jugables ni contratos.

## 1. Qué funciona ya

- Las fachadas victorianas con escaparates, canalones y ventanas iluminadas dan escala de calle.
- Los faroles cálidos contra la luna fría crean contraste y guían el recorrido.
- El Archivo se lee como "otro mundo" (cian, columnas de la agencia) frente al Whitechapel cálido.
- Props de cobertura con lectura clara: fuente, barriles, cajas, carros.

## 2. Errores detectados

| # | Problema | Dónde se ve | Causa | Gravedad |
|---|---|---|---|---|
| E1 | **Muros planos "sin fondo"**: desde arriba se ven cajas finas de ladrillo con el canto superior plano; no hay edificios detrás, ni tejados | Todo el borde del recorrido | El blockout es un anillo de muros de 1 m; las fachadas solo cubren la cara interior | Alta |
| E2 | **Suelo exterior azul y repetido**: el empedrado exterior se ve como una alfombra azulada enorme | Fuera de las zonas (este, sur y huecos entre zonas) | Plano de 160 × 160 m con el material de calle a escala de calle | Alta |
| E3 | **Bloques de "ciudad" como cajas negras sin detalle** | Bordes norte y este | Cubos lisos sin tejado ni chimeneas | Media |
| E4 | **El vapor parece algodón**: bolas blancas opacas y bien definidas | Plaza, Callejón, Paso central | `NS_Steam` con partículas pequeñas, demasiado opacas y concentradas | Alta |
| E5 | **La niebla no se nota en las calles**: la atmósfera está en el cielo, no en el suelo | Todo el mapa | Niebla de altura con poca densidad cerca del suelo; sin volúmenes locales | Media |
| E6 | **Suelo provisional en la Plaza** (plano liso oscuro) | Centro de la Plaza | BSP de Mauricio pendiente de *Build Geometry* | Alta (1 clic) |
| E7 | Los iconos de bombilla y altavoz | Por todo el mapa | Son iconos del editor; **no salen en el juego** | Ninguna |
| E8 | Muros bajos del lado de la cámara también planos | Bordes sur y oeste | Mismo origen que E1 | Media |

## 3. Soluciones

### S1 — Manzanas con tejados alrededor de todo el recorrido (E1, E2, E3, E8)

Rellenar **todo el espacio fuera de las zonas** con bloques de edificio, de modo que desde la cámara se vean tejados y no suelo ni muros sueltos:

- Rejilla de 1 m sobre el plano del nivel (mismo `blockout_layout.json`), ampliada 12 m por cada lado. Las celdas que no son calle ni muro se agrupan en manzanas de hasta 8 × 8 m.
- **Altura según la cámara**, para no tapar al jugador (con Pitch −55° un obstáculo de altura *h* a distancia *d* al suroeste tapa si *h* > 1,43·*d*):
  - manzanas a menos de 7 m al **suroeste** de una calle: **3 m** (una planta, como los muros bajos);
  - el resto: **9–13 m** alternando, para dar silueta.
- Cada manzana: cuerpo de ladrillo oscuro + **tapa de tejado** de pizarra (algo más ancha, sobresale como un alero) + **chimeneas** en una de cada tres manzanas altas, algunas con humo.
- Se elimina el plano exterior azul y los cubos negros del fondo.

### S2 — Vapor sutil y disperso (E4)

`NS_Steam`: partículas **grandes (1,5–3,5 m), muy transparentes (alfa 0,05)**, gris azulado, subida lenta, vida de 6–9 s y menos emisión. Debe leerse como bruma que sale de las alcantarillas, no como nubes.

### S3 — Niebla de calle (E5)

- Niebla de altura más densa a ras de suelo (más caída con la altura) para que las calles tengan neblina y los tejados queden limpios.
- **[PROPUESTA]** Volúmenes de niebla local (*Local Fog Volume*) grandes y suaves en la Plaza, el Callejón, el Paso central y el Tramo, que la reparten por todo el recorrido.

### S4 — Suelo provisional (E6)

**Build → Build Geometry** en `L_Whitechapel` y guardar. Lo hace Yizens en el editor.

### S5 — Calles como en el Londres de 1888 (petición del 15-nov)

**Referencia: cómo era la calle en Whitechapel**

| Elemento | En 1888 | Medidas aproximadas | Dónde lo aplicamos |
|---|---|---|---|
| **Calzada** (*carriageway*) | Adoquín de granito (*setts*) para carros y caballos, ligeramente abombado hacia el centro | Calles principales de 6–10 m; calles secundarias de 3–5 m | Suelo empedrado actual de todas las zonas |
| **Acera** (*footway*) | Losas grandes de piedra de York, más claras y lisas que la calzada, a ambos lados en calles principales | 1,5–3 m de ancho, **10–15 cm** más alta que la calzada | Junto a las fachadas de Start, Plaza, Tramo y Paso central |
| **Bordillo** (*kerb*) | Piezas de granito gris que separan acera y calzada; cuneta al pie | 25–30 cm de ancho | Borde exterior de cada acera |
| **Patios y pasajes** (*courts*, *alleys*) | Sin acera; losas o adoquín de borde a borde, cuneta central; se entra por un pasaje estrecho | 1–4 m | Callejón y Patio del Taller (sin acera, a propósito) |
| **Bolardos** | Postes de hierro fundido en esquinas y entradas de pasaje, para que los carros no entren | 90–100 cm de alto | Entradas del Callejón y del Patio, borde del Paso central |
| **Farolas de gas** | En el borde de la acera, separadas ~30 m; luz escasa y amarillenta | 3–3,5 m | `BP_GasLamp` (ya colocadas) |
| **Fachadas** | Ladrillo ennegrecido por el hollín, 2–3 plantas, tiendas en planta baja, sótanos con verja | 7–10 m | Fachadas victorianas sobre los muros del fondo |
| **Tejados** | Pizarra gris, muchas chimeneas humeando (carbón) | — | Manzanas con tejado y chimeneas alrededor del mapa |
| **Ambiente** | Niebla amarillenta (*pea-souper*), barro, estiércol, carteles pegados | — | Niebla de calle; carteles y suciedad en la tanda siguiente |

**Aplicado:** 11 tramos de acera de losa (`MI_Flagstone_York`, 2,6 m × 15 cm) con bordillo de granito (`MI_Kerb_Granite`) delante de las fachadas de calle, y 6 bolardos de hierro. El Callejón y el Patio quedan sin acera, como los *courts* de la época. La acera de 15 cm es transitable (el personaje sube escalones de hasta 45 cm), así que no cambia el NavMesh ni las rutas.

## 4. Más vida — siguiente tanda (por orden de impacto)

| # | Idea | Cómo | Coste |
|---|---|---|---|
| V1 | **Charcos con reflejo** en el empedrado | Variación de rugosidad por textura de ruido en el material de suelo | Gratis |
| V2 | **Gente que camina** (la Enfermera o el Vagabundo yendo y viniendo) | Blueprint "ir y volver" con `BP_LocomotionAnim` | Gratis |
| V3 | **Humo de chimeneas** en los tejados | `NS_Steam` más oscuro y alto | Gratis |
| V4 | **Ventanas que se encienden y apagan** de vez en cuando | Temporizador aleatorio en las luces de ventana | Gratis |
| V5 | **Sonidos de ciudad**: murmullo lejano, campana, perro, carruaje, goteo, cuervos | fal / ElevenLabs (prompts en la conversación del 15-nov) | Bajo |
| V6 | **Carteles "WANTED" y anuncios** en las paredes | GPT Image → texturas como decals | 9 créditos c/u |
| V7 | **Ropa tendida, carteles colgantes de tienda, farolas de pared** | GPT Image → Meshy | ~24 créditos c/u |
| V8 | **Papeles y hojas arrastradas por el viento** | Niagara | Gratis |

## 5. Estado

| Solución | Estado |
|---|---|
| S1 Manzanas y tejados | ✅ 187 manzanas (110 altas de 9–13 m con tejado de pizarra con alero y chimeneas, 77 bajas de 3 m en el lado de la cámara) + suelo exterior de pizarra; 337 actores con etiqueta `D_CityBlock` en `_Geo`. Sustituyen al plano azul y a los cubos negros |
| S2 Vapor | ✅ `NS_Steam` rehecho: partículas de 1,5–3,5 m, alfa 0,05, 4 por segundo, vida 6–9 s |
| S3 Niebla de calle | ✅ Niebla de altura 0,045 con caída 0,9 + 6 *Local Fog Volume* suaves. Dispersión volumétrica de faroles (0,2) y luces (0,15) reducida para evitar halos |
| S4 Build Geometry | Pendiente (editor, Yizens) |
| S5 Calles de 1888 | ✅ Aceras, bordillos y bolardos |
| V1–V8 | Pendiente de decidir |
