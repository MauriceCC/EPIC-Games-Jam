# Art bible (mini) — Unscripted

> **Dueño:** División D. **Estado:** borrador para el equipo. **Fecha:** 2026-11-14.
> **Fuentes:** `docs/07` (dirección visual, efectos, audio), `docs/04` (aspecto de la tecnología temporal), `docs/02` (cámara), `docs/03` (telegráficas, parry), `docs/01` (escenas clave).
> Lo que no aparece en `docs/` está marcado como **[PROPUESTA]**. Los valores hex son orientativos: se ajustan en la prueba de iluminación.

## 1. Pilares visuales

1. **Legibilidad antes que belleza.** Desde la cámara isométrica, el jugador debe leer siempre: dónde está, dónde están los enemigos, qué ataque viene y qué se puede usar (`docs/02`, `docs/07`).
2. **Dos mundos que chocan.** Whitechapel 1888 es cálido, húmedo, sucio y analógico. La tecnología de la agencia es fría, precisa y **anacrónica**: metal negro, latón y pulsos cian (`docs/04`, `docs/07`).
3. **El relato se edita.** El tema *Director's Cut* se ve en los efectos de "corte" y "toma": fotogramas que se fragmentan, imágenes residuales y glitches de continuidad. **No** es estética de cine genérica (claqueta, grano por todas partes).
4. **Contención.** Pocos efectos y claros. Ninguno debe tapar al personaje ni las telegráficas enemigas (`docs/07`).

## 2. Paleta [PROPUESTA]

### Mundo victoriano (base del entorno)

| Uso | Color | Hex |
|---|---|---|
| Noche, sombras profundas | Azul negro | `#0E1218` |
| Niebla, cielo | Gris azulado | `#4A5560` |
| Ladrillo | Marrón rojizo apagado | `#5A3A2E` |
| Adoquín mojado | Gris carbón | `#2B2F33` |
| Madera vieja | Marrón oscuro | `#3B2C22` |
| Luz de farol de gas | Ámbar | `#F2B25C` |
| Interior (vela, lámpara) | Naranja cálido | `#D98E4A` |

### Agencia (tecnología temporal)

| Uso | Color | Hex |
|---|---|---|
| Pulso temporal, energía | **Cian** | `#2EC8E8` |
| Herrajes, mecanismos | Latón | `#B08D57` |
| Carcasas | Metal negro | `#1A1A1D` |

**Regla del cian:** el cian es **exclusivo** de la tecnología de la agencia y de sus efectos (Corte, Retoma, parry, dispositivos, Archivo). No se usa en faroles, ventanas, carteles ni en el entorno victoriano. Así, cuando el jugador ve cian, sabe que es la agencia.

### Colores de jugabilidad (semánticos)

Se acuerdan con A, B y C. Los HUD y widgets son de C; aquí solo se fijan los significados.

| Significado | Color | Hex | Dónde |
|---|---|---|---|
| Telegráfica de ataque enemigo | Rojo anaranjado | `#E5482F` | Destello o decal antes del golpe (B) |
| Ataque que no se puede parar (si existe) | Rojo intenso | `#FF2E2E` | Diferenciar del parable (B, según `docs/03`) |
| Parry con éxito | Blanco dorado | `#FFF1C1` + chispa cian | `NS_ParrySpark` (A/D) |
| Enemigo congelado (Corte) | Cian translúcido | `#2EC8E8` al 35 % | `M_TemporalFrozen_Overlay` (B) |
| Interactuable o evidencia | Blanco cálido suave | `#FFE9C7` | Brillo o contorno discreto (C) |
| Continuidad alterada | Cian + magenta en "aberración" | `#2EC8E8` / `#D23CC8` | `NS_ContinuityGlitch`, post-proceso (C/D) |

El **rojo de telegráfica** no se usa en el entorno, igual que el cian. **Pendiente:** confirmar con C si el HUD de detección usa ámbar en vez de rojo para no confundirse con un ataque.

## 3. Valores y lectura isométrica

- **Suelo medio-oscuro, personajes más claros.** Los personajes llevan una luz de recorte (*rim*) o un borde más claro para destacar sobre el adoquín mojado.
- **Lectura desde arriba:** hombros, sombrero y arma tienen que distinguirse vistos a 55°. Las siluetas se diseñan pensando en la vista **cenital**, no en la frontal.
- **[PROPUESTA] Marcador del jugador:** un decal circular tenue bajo el agente (ámbar o blanco, nunca cian ni rojo) para no perderlo en las peleas de grupo. A decide si lo usa.
- **Tejados y muros del lado de cámara:** bajos o recortados (regla de `LEVEL_DESIGN.md §4`). Más tarde, oclusión con dither (D-20).
- **Contraste por zona:** las arenas de combate son las zonas **más iluminadas**; las de sigilo, las más oscuras, con islas de luz (`LEVEL_DESIGN.md §11`).

## 4. Personajes: lectura por silueta y color

Los modelos los aporta quien los busque (A/B). D vela por que encajen en esta guía.

| Personaje | Silueta | Color dominante | Toque de identidad |
|---|---|---|---|
| Agente (jugador) | Abrigo largo, bastón | Negro y gris oscuro | Dispositivo de muñeca **cian**; bastón con herrajes de latón (`docs/07`) |
| Perseguidor (vecino) | Ropa de trabajo, gorra o pañuelo | Marrones y grises **apagados** | Arma improvisada; nada de cian (son civiles manipulados) |
| Interventor | Abrigo de agencia, más rígido | Negro y latón | Acentos cian **visibles** que lo distinguen del Perseguidor (`docs/07`) |
| Supervisor | Uniforme o abrigo distintivo, mayor presencia | Negro, latón más abundante | Equipo temporal más grande y luminoso (`docs/07`) |
| Jack | Ropa corriente y gastada | Tonos neutros | Cansado y asustado. **Evitar estereotipo de monstruo** (`docs/07`) |

Regla rápida: **marrón = civil · negro + latón + cian = agencia**.

## 5. Entorno

- **Materiales clave:** adoquín mojado (con charcos que reflejan faroles), ladrillo, madera, hierro forjado, carteles de papel.
- **Kit modular mínimo para cubrir el blockout:** fachada (planta baja + piso), esquina, muro bajo, puerta, ventana, farol, cajas, barriles, carretilla, carro, verja, columnas del Archivo, mesas o estaciones de registro.
- **Archivo:** es el único espacio con arquitectura de la agencia (metal negro, latón, luz cian fría). Debe sentirse **fuera de lugar** en 1888.
- **Texto en el escenario:** todo cartel, letrero o documento visible debe estar **en inglés** (`AGENTS.md`). Nada de texto español en texturas.
- **Escala:** 1 unidad = 1 cm. Puertas de 2 × 3 m, alturas de muro según `LEVEL_DESIGN.md §3`.

## 6. Iluminación

- Noche lluviosa. **Lumen dinámico, sin Build Lighting** (`01_CONTRATOS §6`).
- **Luz principal:** una direccional muy tenue y fría (luna entre niebla) y un Sky Light bajo.
- **Faroles de gas** (ámbar) como fuentes principales: definen islas de luz y guían el recorrido.
- **Niebla de altura y volumétrica** moderada: atmósfera sin ocultar telegráficas. Se valida en la arena del Paso central.
- **Interiores** (Taller, Refugio) cálidos; **Archivo** frío y cian.
- **Rendimiento:** pocas luces con sombra. Los faroles lejanos, sin sombras (D-40: 60 fps en el PC más débil).

## 7. Efectos (VFX) y post-proceso

Basado en `docs/07` y `docs/04`. D rellena los placeholders de `01_CONTRATOS §8`.

| Efecto | Asset | Lenguaje visual | Duración y límite |
|---|---|---|---|
| Corte de Fotograma | `NS_TemporalCut` + `M_TemporalFrozen_Overlay` | Silueta fragmentada, cortes horizontales tipo fotograma, ruido cian **en el enemigo objetivo** | Lo que dure la congelación (~0,8 s, `docs/03`); solo sobre el objetivo |
| Retoma | `NS_RetakeTrail` + `PP_Retake` | Estela e imágenes residuales del agente; flash moderado; tinte cian breve | < 0,5 s de post-proceso; nunca a pantalla completa en blanco |
| Parry (Contraorden) | `NS_ParrySpark` | Impacto del bastón + pulso circular breve | Muy corto y muy claro: es una recompensa |
| Golpe | `NS_HitImpact` | Polvo y chispa seca, sin sangre exagerada (los civiles quedan incapacitados, no mueren) | Corto |
| Continuidad alterada | `NS_ContinuityGlitch` | Aberración cromática cian/magenta, desplazamiento de líneas | Puntual, ligado al aviso de C |
| Registro final | `NS_FinalRegister` | "Sello" o impresión del expediente con pulso cian | Momento único; puede ser el más vistoso |

Reglas:

- Ningún efecto tapa al jugador ni las telegráficas durante más de 0,2 s.
- Nada de grano de película, viñeta fuerte o letterbox permanentes: perjudican la lectura.
- Los efectos de la agencia **siempre** en cian. Los impactos físicos en blancos o ámbar.

## 8. Audio (tono)

Detalle en T6 (`AUDIO_VFX_LIST.md`). Tono general según `docs/07`:

- **Mundo:** lluvia, viento, siseo de gas, pasos sobre adoquín, multitud lejana. Orgánico y húmedo.
- **Agencia:** pulsos cortos, sintéticos y limpios. La Retoma suena a "inversión" o eco. Debe sonar **anacrónica**, como el cian.
- **Combate:** golpes secos de bastón. **Bloqueo y parry claramente distintos.**
- **Voz:** sin doblaje obligatorio. Si hay voces, en inglés.

## 9. Decisión de estilo (D-A)

> **✅ Decidido por el usuario (2026-11-14): estilizado oscuro**, con desgaste "usado y húmedo". Prompts de referencia en `IMAGE_PROMPTS.md`. La tabla siguiente queda como registro de la decisión.

| Opción | A favor | En contra |
|---|---|---|
| **Realista oscuro** | Encaja con el tono serio; hay packs gratuitos (Quixel/Fab) de calidad | Mezclar packs se nota; más difícil mantener la lectura isométrica; más pesado |
| **Estilizado** (formas simples, texturas pintadas o colores planos, iluminación dramática) | Lectura isométrica más fácil; packs dispares se unifican con materiales propios; más ligero | Menos packs victorianos estilizados; requiere más trabajo de materiales |

**Criterio para decidir:** el estilo que permita **cubrir el kit modular de §5 con los packs encontrados en T5**, con licencia compatible con la jam y manteniendo la lectura de §3.

**Recomendación provisional [PROPUESTA]:** realista oscuro con **paleta y luz controladas**, si T5 encuentra un pack victoriano coherente que cubra la mayor parte del kit. Si no, estilizado. Decidir **antes de importar** nada.

## 10. Checklist de aceptación de un asset

Antes de importar un modelo, textura o sonido:

- [ ] Licencia compatible con la jam y con uso en el juego; anotada en `CREDITS.md`.
- [ ] Encaja con la paleta (§2) y el estilo decidido (§9).
- [ ] Escala real (1 uu = 1 cm), pivote en la base y orientación +X hacia delante.
- [ ] Sin texto en español; cualquier texto visible, en inglés.
- [ ] Tamaño razonable: texturas de 2K como máximo salvo excepción justificada; nada de assets fuente pesados en Git (`.psd`, `.blend`, `.wav` enormes).
- [ ] Importado a la carpeta de D que corresponda (`Art/`, `Materials/`, `VFX/`, `Audio/`) y con su prefijo.

### Nomenclatura

| Tipo | Prefijo | Ejemplo |
|---|---|---|
| Static Mesh | `SM_` | `SM_Facade_Brick_A` |
| Skeletal Mesh | `SK_` | `SK_Pursuer_A` |
| Material / instancia | `M_` / `MI_` | `MI_Cobble_Wet` |
| Textura | `T_` + sufijo `_D` `_N` `_ORM` | `T_Brick_A_D` |
| Niagara | `NS_` | `NS_TemporalCut` |
| Sound Cue / MetaSound / Wave | `SC_` / `MS_` / `SW_` | `SW_Rain_Loop` |
| Material de post-proceso | `PP_` | `PP_Retake` |
| Decal | `M_Decal_` | `M_Decal_PlayerRing` |

## 11. Referencias (descriptivas)

En lugar de copiar imágenes protegidas, se describe qué buscar. Cada uno puede reunir capturas en una carpeta personal **fuera del repositorio**. Ojo: hoy `.gitignore` no cubre `Unscripted/Content/Developers/` (`02_ARRANQUE_F0.md`).

- Calles londinenses victorianas nocturnas: gas, niebla y adoquín mojado.
- Juegos de acción isométrica con buena lectura de combate en entornos oscuros, para estudiar cómo destacan personajes y telegráficas.
- Diseño "brass and black" con luz cian: instrumentos de precisión, relojería y mecanismos expuestos.
- Efectos de fotograma partido, *datamoshing* sutil y aberración cromática, como inspiración para Corte y continuidad.
