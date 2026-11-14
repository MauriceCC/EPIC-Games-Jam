# Unscripted — Proyecto y documentación de diseño

> **Estado:** plantilla Top Down existente; esqueleto compartido F0 pendiente de creación y validación.
> **Motor:** Unreal Engine **5.8.4**, proyecto **Blueprint**, perspectiva isométrica 3D.
> **Ambientación:** Whitechapel, Londres, 1888, **ficción histórica alternativa**.  
> **Tema de la Game Jam:** *Director's Cut*.

**Nombre definitivo:** Unscripted (antes CORTE FINAL). **Idioma obligatorio del juego: inglés** para todo contenido visible o audible al jugador. La documentación puede seguir en español; sus textos narrativos son referencias de diseño, no textos listos para publicar. Ver las normas de [AGENTS.md](AGENTS.md).

Abrir el proyecto existente [`Unscripted/Unscripted.uproject`](Unscripted/Unscripted.uproject). No crear otro proyecto. Para preparar el trabajo paralelo, seguir la [lista de arranque F0](docs/plan/02_ARRANQUE_F0.md).

## Premisa

El jugador encarna a un agente del **Departamento de Continuidad**, organización capaz de intervenir en el pasado y controlar la narración oficial de los hechos. Su misión inicial es hallar y proteger a **Jack** de una multitud. Conforme avanza, descubre que el Director quiere fabricar un culpable, ocultar la identidad de Jack y hacerlo desaparecer. El jugador decide qué versión será archivada: la oficial manipulada o un registro de la verdad.

**Lema:** «La historia no pertenece a quien la vivió, sino a quien decide cómo contarla».

## Diseño jugable

Acción isométrica con sigilo, combate cuerpo a cuerpo deliberado, parry, esquiva, control de grupos y tecnología temporal. La identidad jugable es **Combatir → Interrumpir → Repetir**. El sigilo permite preparar encuentros o evitarlos; no es la única forma de jugar.

## Plan de trabajo del equipo (empezar aquí)

- [`docs/plan/00_PLAN_GENERAL.md`](docs/plan/00_PLAN_GENERAL.md): cómo trabajan 4 personas + agentes en paralelo sin conflictos: divisiones, fases, Git/LFS, reglas.
- [`docs/plan/01_CONTRATOS_Y_PROPIEDAD.md`](docs/plan/01_CONTRATOS_Y_PROPIEDAD.md): quién es dueño de cada carpeta y las interfaces entre divisiones. **Fuente de verdad de nombres compartidos.**
- División A — [`A_AGENTE_COMBATE_TEMPORAL.md`](docs/plan/A_AGENTE_COMBATE_TEMPORAL.md): jugador, combate, Corte y Retoma.
- División B — [`B_ENEMIGOS_IA_SIGILO.md`](docs/plan/B_ENEMIGOS_IA_SIGILO.md): enemigos, IA, sigilo y Jack.
- División C — [`C_NARRATIVA_INTERACCION_UI.md`](docs/plan/C_NARRATIVA_INTERACCION_UI.md): fases, interacción, diálogos, HUD y finales.
- División D — [`D_MUNDO_ARTE_AUDIO_BUILD.md`](docs/plan/D_MUNDO_ARTE_AUDIO_BUILD.md): nivel, arte, VFX, audio, build e integración.

> El repositorio **no** debe clonarse dentro de OneDrive u otra carpeta sincronizada. Usar una ruta corta, p. ej. `C:\Dev\CorteFinal`, e instalar Git LFS antes de clonar.

## Documentos de diseño

1. [`AGENTS.md`](AGENTS.md): contexto inmediato y convenciones para agentes de IA.
2. [`docs/01_VISION_Y_NARRATIVA.md`](docs/01_VISION_Y_NARRATIVA.md): mundo, personajes, tres actos, diálogos y finales.
3. [`docs/02_JUGABILIDAD_GENERAL.md`](docs/02_JUGABILIDAD_GENERAL.md): bucle jugable, movimiento, sigilo, interacción y controles.
4. [`docs/03_COMBATE_Y_ENEMIGOS.md`](docs/03_COMBATE_Y_ENEMIGOS.md): combate, recursos, IA, arquetipos y jefe.
5. [`docs/04_TECNOLOGIA_TEMPORAL.md`](docs/04_TECNOLOGIA_TEMPORAL.md): equipo, poderes, Retoma y reglas técnicas.
6. [`docs/05_NIVEL_MISIONES_Y_HUD.md`](docs/05_NIVEL_MISIONES_Y_HUD.md): mapa, misiones, progreso y UI.
7. [`docs/06_UNREAL_ENGINE_5.md`](docs/06_UNREAL_ENGINE_5.md): arquitectura sugerida de Blueprints, estados y sistemas.
8. [`docs/07_ARTE_AUDIO_ALCANCE.md`](docs/07_ARTE_AUDIO_ALCANCE.md): dirección visual, sonido, mínimo jugable y extensiones.

## Cómo leer las decisiones

Esta documentación recopila y consolida dos iteraciones: una versión original con sigilo + rewind y una **versión posterior con combate expandido**. **La versión posterior prevalece en mecánicas contradictorias**:

- **Retoma (versión vigente):** rebobina **solo el estado personal del protagonista** hasta cinco segundos. Enemigos, mundo y decisiones narrativas no retroceden.
- **Cargas de Retoma (versión vigente):** dos por sección, recuperadas en checkpoints, en lugar de las tres de la idea preliminar.
- **Controles vigentes:** mouse para orientación, clic izquierdo/derecho para ataques, espacio esquiva, Q parry, F Corte, R Retoma.
- **Combate:** parte central del juego; el sigilo es una vía complementaria.
- **Narrativa:** tres actos, un nivel y dos finales; el jugador elige qué expediente registrar.

Los valores de daño, duración y dimensiones son **propuestas iniciales de ajuste**, no resultados de playtesting. Las mecánicas marcadas como ampliación no están comprometidas para la versión mínima.

## Estado observado del repositorio

La revisión de archivos del 2026-11-14 encontró el proyecto `Unscripted/`, Blueprints y mapa Top Down, maniquíes, animaciones y geometría de prototipado. No encontró `Unscripted/Content/CorteFinal/` ni los sistemas propios descritos por el plan. No se ha validado su funcionamiento en el editor en esta revisión.

Las rutas `Content/`, `Config/` y `Source/` del plan son relativas a `Unscripted/`; `docs/`, `Scripts/` y `SourceData/` son relativas al repositorio. `CorteFinal` en rutas internas es un namespace histórico, no el título del juego. Los esquemas y pseudocódigo siguen describiendo intención de diseño, no implementación verificada.
