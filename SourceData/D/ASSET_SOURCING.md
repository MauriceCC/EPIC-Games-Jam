# Búsqueda de assets y licencias (D-06 / T5)

> **Dueño:** División D. **Fecha de la investigación:** 2026-11-14.
> Precios y licencias consultados en la web ese día. **Volver a comprobarlos en la página del vendedor antes de descargar.** Esto no es asesoramiento legal.

## 0. ⚠️ Plazo de la jam

Según la página de la jam en itch.io, **las entregas cierran el 15 de noviembre a las 17:59 PST** (02:00 UTC del día 16) y **las entregas tardías se descalifican**. La jam empezó el 12 de noviembre. **Hay que confirmar la hora exacta en las reglas oficiales**, porque las fuentes secundarias difieren.

Consecuencia para D: **no hay tiempo para un pipeline de arte "bonito"**. Prioridad absoluta: blockout jugable, luz y atmósfera con lo que ya tiene el motor y la plantilla, y una build que arranque. Todo lo que se importe debe ser **rápido de integrar**.

## 1. Reglas de la jam sobre assets (resumen)

Fuente: página de la jam en itch.io. Leer también las reglas oficiales (enlace al final).

| Regla | Qué implica para nosotros |
|---|---|
| Se pueden usar assets ajenos (p. ej. de Fab) **con la licencia adecuada** | Gratis o de pago, siempre con licencia válida |
| Hay que **listarlos en la entrega** | `CREDITS.md` al día desde la primera importación |
| Atribución tal como la pida el dueño | Respetar las licencias CC-BY y similares |
| **No empezar a construir antes del 12 de noviembre**; declarar lo hecho antes | Nada que declarar por parte de D |
| Herramientas de IA permitidas (opcional listarlas; algunos premios lo piden) | Podemos mencionar el uso de agentes en la entrega |
| Audio del partner (WeLoveIndies): licencia gratuita **no comercial** | Sirve para la jam; para un lanzamiento comercial haría falta otra licencia |
| Motor: Unreal Engine o UEFN, sin versión obligatoria | 5.8.4 está bien |

**Aviso:** una fuente secundaria menciona una cláusula 7(h) según la cual "el resto del arte debe hacerse durante el concurso". Parece contradecir el permiso de usar assets de Fab. **Comprobarlo en las reglas oficiales antes de importar packs.**

## 2. Lo que ya tenemos gratis (usar primero)

| Fuente | Qué aporta | Licencia |
|---|---|---|
| Plantilla Top Down + `LevelPrototyping` (ya en el repo) | Materiales de rejilla, cubos, rampas, cilindros: el blockout | Contenido de Epic incluido en la plantilla. Listarlo como "Epic starter content" |
| Maniquíes de UE5 (ya en el repo) | Personajes y animaciones provisionales para A y B | Ídem |
| Motor (Niagara, MetaSound, Lumen, Volumetric Fog, Exponential Height Fog) | Lluvia, niebla y luz sin assets externos | Del motor |

**Con solo esto se consigue la atmósfera de `ART_BIBLE.md`:** cubos con materiales oscuros, niebla, faroles con luces puntuales ámbar y lluvia con Niagara. Es la opción **más segura para el plazo**.

## 3. Candidatos de entorno

| # | Asset | Vendedor | Precio (14-nov) | Licencia | Estilo | Valoración |
|---|---|---|---|---|---|---|
| E1 | **Medieval Village MegaKit** (versión gratuita) | Quaternius | Gratis la parte Standard (60–70 % del pack) | **CC0**: sin atribución obligatoria, uso comercial permitido | Low-poly estilizado, modular sobre rejilla, +300 piezas (OBJ/FBX/glTF) | ✅ **Mejor opción gratuita.** Es medieval, no victoriano, pero muros, ventanas, tejados y escaleras modulares sirven con materiales oscuros. Importar FBX → crear MI propios |
| E2 | Victorian Street | Vitruvian Triad (Fab) | De pago (~136 PEN) | Fab Standard License | Realista, modular, Nanite/Lumen | 💰 Muy acorde al tema, pero de pago y sin número de piezas visible. Puede ser pesado |
| E3 | Abandoned European Street Environment | Barrel Bark Interactive (Fab) | De pago (~170 PEN) | Fab Standard License | Realista, 278 mallas, modular | 💰 Completo, pero no es victoriano (tiene aparatos de aire acondicionado y escaleras de incendios modernas) |
| E4 | Steampunk Modular Street – Victorian City | Entroverse Lab (Fab) | De pago (~204 PEN) | Fab Standard License | Detallado, steampunk | 💰 Encaja con la tecnología anacrónica, pero **exige Runtime Virtual Texture**, que implica cambiar la configuración del proyecto (integrador) |
| E5 | Modular Victorian Asset Pack | Jacob Smith (Sketchfab) | Gratis | **CC-BY** (atribución obligatoria) | Callejón sucio, modular | ⚠️ Posible complemento. Revisar calidad, escala y atribución |
| E6 | Victorian Gas Street Light | BlendKit | Gratis | CC0 | Farol (Blender) | ⚠️ Solo un farol; habría que exportarlo desde Blender |

**Descartados:** sitios como *gameassetsfree* o *gfx-hub* ofrecen packs de pago gratis. **Son copias piratas**: no se pueden usar ni enlazar, y descalificarían la entrega.

**Sobre la Fab Standard License** (según Epic y su foro): las mismas condiciones para assets gratis y de pago, uso comercial en juegos permitido, sin redistribuir los archivos fuente, y con limitaciones en proyectos totalmente open source. **Atención:** el repositorio no debe ser público con assets de Fab dentro, o eso podría contar como redistribución. Comprobar la visibilidad del repo con el equipo.

## 4. Candidatos de audio

| # | Fuente | Licencia | Para qué |
|---|---|---|---|
| A1 | **Sonniss GameAudioGDC Bundle** (ediciones anuales) | Royalty-free, uso comercial, sin atribución obligatoria. La edición 2024 prohíbe entrenar IA con ella | Lluvia, viento, multitud, golpes, pasos. **Son decenas de GB**: descargar solo las librerías necesarias |
| A2 | Freesound.org | **Por sonido**: usar solo **CC0** (o CC-BY con crédito). **Evitar CC-BY-NC** | Sonidos concretos (farol de gas, adoquín) |
| A3 | WeLoveIndies (partner de la jam) | Gratis para uso **no comercial** | Música o ambiente si hace falta; listarlo |
| A4 | Generación propia (MetaSound) | Propia | Pulsos de la agencia (Corte, Retoma): sintéticos, encajan con `ART_BIBLE §8` |

## 5. Recomendación [PROPUESTA]

Teniendo en cuenta el plazo:

1. **Estilo (D-A): "estilizado oscuro" usando la geometría propia del blockout**, más E1 (Quaternius CC0) para fachadas y props donde dé tiempo. Es gratis, sin atribución obligatoria y ligero.
2. **No comprar packs** salvo que el equipo lo decida y alguien tenga tiempo de integrarlo. Un pack realista de 2–5 GB cuesta horas de descarga, importación y ajuste de escala y materiales que **no tenemos**.
3. **Atmósfera con el motor:** niebla, faroles ámbar, lluvia con Niagara y post-proceso. Es lo que más luce por hora invertida.
4. **Audio:** 5–8 sonidos clave de Sonniss o de Freesound CC0 (lluvia en bucle, pasos, golpe, parry), más pulsos sintéticos con MetaSound.
5. **Personajes:** que A y B sigan con los maniquíes de UE5. Si hay tiempo, diferenciar perseguidor, Interventor y Supervisor **por color de material** (`ART_BIBLE §4`) en lugar de buscar modelos.

## 6. Proceso al importar cualquier asset

1. Comprobar la licencia en la **página oficial** del autor y guardar la URL.
2. Importar a la carpeta de D que corresponda (`Art/`, `Materials/`, `Audio/`) con los prefijos de `ART_BIBLE §10`.
3. Añadir una fila en `CREDITS.md` en el mismo commit: nombre, autor, URL, licencia y si exige atribución.
4. No subir los archivos fuente originales (ZIP, FBX sueltos, WAV enormes) al repo: solo los `.uasset` importados.

## 7. Fuentes consultadas

- [Página de la jam en itch.io](https://itch.io/jam/2026-epic-ai-megajam) · [Reglas oficiales (Box de Epic)](https://epicgames.box.com/s/a7xcgl07fqoieeb99sjtd3juhj4agc4z) · [Anuncio del tema (X de Unreal Engine)](https://x.com/UnrealEngine/status/2120601842489168038) · [Resumen de reglas (vibestackweekly)](https://vibestackweekly.com/epic-ai-megajam-2026/) · [Resumen de reglas (threejsassets)](https://threejsassets.com/blog/epic-ai-megajam-2026) · [Devlog con mención de la cláusula 7(h)](https://nastycracked.itch.io/uefn-megajam-2026/devlog/1771270/before-the-first-build-rules-tools-and-an-honest-development-record)
- Fab: [Victorian Street](https://www.fab.com/listings/9e1179af-5a01-47cf-9195-e08228d83dbf) · [Abandoned European Street](https://www.fab.com/listings/046ae5fd-066c-42c8-a2de-470f6515657a) · [Steampunk Modular Street](https://www.fab.com/listings/abb6c4c6-ec3b-4c1c-b0dd-3fb27d3a197e) · [Victorian Era Street Lamps](https://www.fab.com/listings/39487439-5308-4386-b511-157d4059d6f1?lang=en)
- Licencia Fab: [Lanzamiento de Fab (Epic)](https://www.unrealengine.com/en-US/blog/fab-epics-new-unified-content-marketplace-launches-today) · [Hilo del foro sobre la Standard License](https://forums.unrealengine.com/t/all-free-assets-including-ue-ones-are-now-standard-license-on-fab-meaning-no-commercial-use/2080626) · [CG Channel](https://www.cgchannel.com/2024/11/epic-games-to-share-new-free-assets-on-fab-every-two-weeks)
- Gratis: [Quaternius Medieval Village MegaKit](https://quaternius.com/packs/medievalvillagemegakit.html) · [itch.io de Quaternius](https://quaternius.itch.io/medieval-village-megakit) · [Modular Victorian Asset Pack (Sketchfab)](https://sketchfab.com/3d-models/modular-victorian-asset-pack-464974e287bc42858e974fe314c247df) · [Farol victoriano (BlendKit)](https://www.blendkit.com/asset-gallery-detail/316cc7bd-5fcc-46fb-8b1f-fb0a8fd770e4/)
- Audio: [Sonniss GDC 2026 (rekkerd)](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/) · [Sonniss GDC 2024 (gamefromscratch)](https://gamefromscratch.com/sonniss-27-5gb-sound-effect-giveaway-at-gdc-2024/)
