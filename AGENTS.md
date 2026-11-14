# AGENTS.md — Contexto persistente del proyecto Unscripted

Este archivo está pensado para agentes de IA que colaboren con la implementación. Leer primero [`README.md`](README.md), después el plan de equipo (`docs/plan/00_PLAN_GENERAL.md` y `docs/plan/01_CONTRATOS_Y_PROPIEDAD.md`), el archivo de la división con la que trabajas y, por último, los documentos de diseño que ese archivo cite.

## Trabajo en equipo: reglas obligatorias para agentes

El proyecto lo desarrollan **4 personas en paralelo**, cada una con su agente, divididas en A (Agente/combate/poderes), B (Enemigos/IA/sigilo/Jack), C (Narrativa/interacción/UI) y D (Mundo/arte/audio/build + integración).

1. **Pregunta o deduce a qué división perteneces** antes de proponer cambios (la persona lo indicará en el prompt). Si no lo sabes, pregunta.
2. **Solo propones o haces cambios en las rutas de tu división** (tabla en `docs/plan/01_CONTRATOS_Y_PROPIEDAD.md §2`). Los `.uasset`/`.umap` son binarios y **no se pueden fusionar**: tocar un asset ajeno destruye trabajo de otra persona.
3. **Los contratos (`Core/`, interfaces, dispatchers, enums, structs) son de solo lectura.** Si necesitas cambiarlos, redacta una solicitud en la sección "Solicitudes de contrato" del archivo de tu división y detente.
4. **No puedes editar Blueprints como texto.** Entrega guías nodo a nodo indicando el asset exacto, CSV/JSON para DataTables, scripts de Python del editor o, si el equipo lo aprobó, C++ en el módulo de tu división.
5. Marca como **[PROPUESTA]** cualquier cosa que no esté en la documentación de diseño.
6. Nunca recomiendes `git add .`, `git push --force` sobre `main` ni resolver conflictos de binarios "fusionando".

## Decisiones confirmadas y norma de idioma (2026-11-14)

- El nombre definitivo es **Unscripted**. CORTE FINAL fue el título provisional; no debe aparecer como título ante el jugador.
- Motor acordado: **Unreal Engine 5.8.4**. Proyecto creado como **Blueprint**; C++ no está autorizado por defecto.
- **TODO contenido visible o audible para el jugador debe estar en inglés**, desde el prototipo: menús, HUD, objetivos, prompts, tutoriales, diálogos, subtítulos, documentos, finales, créditos, carteles y texto integrado en imágenes, además de voces si las hay.
- La documentación, conversaciones de desarrollo y comentarios internos pueden estar en español. Los ejemplos narrativos españoles de `docs/` son material de diseño: deben adaptarse al inglés antes de incorporarse al juego.
- Cada división responde por el idioma de su contenido; C coordina la consistencia de términos y D revisa también arte, audio y build. No mostrar nombres internos de enums/assets como sustituto del texto al jugador.
- El proyecto existente está en `Unscripted/Unscripted.uproject`. Las rutas de contenido/configuración del plan son relativas a `Unscripted/`; `docs/`, `Scripts/` y `SourceData/` son relativas al repositorio. La raíz de contenido propia es `Content/Unscripted/` (en el editor: `/Game/Unscripted/`), unificada con el nombre definitivo por autorización del usuario el 2026-11-14.
- La autorización excepcional para actuar como integrador en esta preparación no transfiere de forma permanente la propiedad de las otras divisiones.

## Producto

- **Título definitivo:** Unscripted.
- **Game Jam:** *Director's Cut*.
- **Plataforma:** PC, Unreal Engine **5.8.4**, proyecto **Blueprint**, 3D isométrico.
- **Género:** acción isométrica táctica con sigilo, combate cuerpo a cuerpo y manipulación temporal.
- **Contenido narrativo:** Whitechapel 1888; Departamento de Continuidad; Director; Supervisor; Jack; protagonista agente; mensajes de una versión futura del agente.
- **Experiencia deseada:** una partida corta, inicialmente estimada en 10–15 minutos; validar duración tras introducir combates.

## Principios de diseño que deben conservarse

1. El tema *Director's Cut* **no es solo una estética cinematográfica**. El Director impone su interpretación de la historia; el jugador participa en la creación o preservación de un relato histórico.
2. Cada pelea debe tener función jugable y/o narrativa. El sigilo ofrece alternativas, no es obligatorio en todos los encuentros.
3. La tecnología temporal es **tecnología de la agencia**, no magia abstracta.
4. **Corte de Fotograma** interrumpe brevemente a **un enemigo**; **Retoma** rebobina **solo al protagonista**. No implementar un rewind global por defecto.
5. No se retroceden elecciones narrativas, pruebas registradas, puertas persistentes ni daño ya infligido a enemigos mediante Retoma.
6. El protagonista debe poder neutralizar civiles sin matarlos; los perseguidores son personas manipuladas por rumores.
7. El final narrativo se decide **registrando un expediente**, no simplemente ganando o perdiendo una pelea.
8. Los números y nombres de Blueprints documentados son propuestas: se pueden ajustar preservando el comportamiento y explicando los cambios.
9. **No presumir** que existen assets, animaciones, plugins, niveles o clases por estar descritos en estos Markdown.
10. La organización del equipo, las fases y la propiedad de archivos están en `docs/plan/`. Los documentos de diseño (`docs/01`–`docs/07`) describen el *qué*; el plan describe el *quién* y el *cómo*.

## Fuente de verdad por asunto

| Asunto | Archivo |
|---|---|
| Historia, motivaciones, finales y diálogos | `docs/01_VISION_Y_NARRATIVA.md` |
| Bucle jugable, exploración y sigilo | `docs/02_JUGABILIDAD_GENERAL.md` |
| Daño, combos, resistencia, guardias, jefe | `docs/03_COMBATE_Y_ENEMIGOS.md` |
| Corte de Fotograma, Retoma, snapshots, limitaciones | `docs/04_TECNOLOGIA_TEMPORAL.md` |
| Localizaciones, misiones, checklist, HUD | `docs/05_NIVEL_MISIONES_Y_HUD.md` |
| Componentes, eventos, estados, Unreal Engine | `docs/06_UNREAL_ENGINE_5.md` |
| Arte, efectos, audio, alcance del prototipo | `docs/07_ARTE_AUDIO_ALCANCE.md` |
| Forma de trabajo, fases, Git, agentes | `docs/plan/00_PLAN_GENERAL.md` |
| **Nombres y firmas compartidas, propiedad de carpetas** (prevalece sobre `docs/06`) | `docs/plan/01_CONTRATOS_Y_PROPIEDAD.md` |
| Backlog de cada división | `docs/plan/A_*.md` … `docs/plan/D_*.md` |

## Contradicciones de las propuestas anteriores ya resueltas

| Propuesta preliminar | Decisión consolidada |
|---|---|
| Rewind de 5 s de todos los actores | Retoma revierte solo posición/salud/resistencia del agente |
| 3 cargas de rewind | 2 cargas de Retoma por sección |
| Sigilo + rewind como único núcleo | Combate + poderes temporales + sigilo alternativo |
| R para rewind global | R para Retoma personal |
| Personaje solo teclado | WASD + orientación de ataque hacia el mouse |
| Guardias solo como amenazas de detección | Perseguidores, Interventores y Supervisor con combate |

## Decisiones abiertas (no inventar como requisitos cerrados)

- Assets finales y animaciones definitivas (la plantilla ya aporta contenido provisional).
- Perspectiva ortográfica o perspectiva con lente larga; altura/encuadre exactos.
- Balance final de daño, resistencia, salud y cooldowns.
- Si habrá golpe fuerte cargable, cancelaciones, lock-on o esquivas avanzadas.
- Si Salto de Fotograma, Eco de una Toma, bomba de humo y otras extensiones llegan a implementarse.
- La identidad real del asesino en esta ficción: **no es necesario revelarla** para contar la historia.
- Alcance exacto del borrado de memoria y mecánica temporal de la copia de pruebas: son recursos narrativos, no sistemas jugables obligatorios.
- Si la pelea con el Interventor es opcional (`docs/01`) u obligatoria en el tramo al refugio (`docs/05`).
- Qué ocurre al llegar a 0 de salud con cargas de Retoma (Retoma automática, ventana para pulsar R o derrota directa).
- Si ser detectado en sigilo inicia combate (propuesta vigente) o es un fallo inmediato.
- Qué se reinicia de los enemigos al reaparecer en un checkpoint.

## Interfaces narrativas innegociables

- Checklist inicial: localizar a Jack, protegerlo, mantener secreta su identidad.
- Revelación: la agencia necesita un culpable conveniente, aunque Jack sea inocente.
- Checklist posterior: incriminar a Jack y hacerlo desaparecer.
- Decisión final entre **expediente oficial falso** y **expediente auténtico**.
- Final A: se impone el corte del Director.
- Final B: borran la memoria del protagonista, pero una copia de la verdad llega a su próximo yo.

## Estilo de implementación previsto

Preferir componentes reutilizables, Blueprints de enemigos derivados de una base compartida, `BPI_Interactable`, `ECombatState`, `EStoryPhase`, Animation Montages + Notifies, navegación NavMesh y datos ajustables en DataTables. La arquitectura está en `docs/06_UNREAL_ENGINE_5.md`; los nombres y firmas definitivos que cruzan divisiones, en `docs/plan/01_CONTRATOS_Y_PROPIEDAD.md`.
