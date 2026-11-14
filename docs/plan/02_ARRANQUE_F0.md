# Arranque del equipo — Unscripted

## Decisiones confirmadas el 2026-11-14

- Nombre definitivo: **Unscripted**.
- Motor: **UE 5.8.4**, según confirmación del usuario; verificar la instalación en cada equipo.
- Proyecto creado como **Blueprint**. No se requiere C++ para arrancar.
- **Todo contenido visible o audible para el jugador debe estar en inglés**, desde el prototipo. Documentación y comentarios internos pueden estar en español. Esto incluye UI, objetivos, diálogos, prompts, documentos, finales, créditos, carteles, imágenes con texto y voces.
- El usuario autorizó asumir excepcionalmente el rol de integrador para esta preparación. No equivale a una asignación permanente ni habilita modificaciones indiscriminadas a trabajo ajeno.

## Estado observado, sin confundir documentación con implementación

La revisión de archivos encontró `Unscripted/Unscripted.uproject`, configuración Enhanced Input, mapa y Blueprints Top Down, maniquíes, animaciones y geometría provisional. No encontró `Unscripted/Content/Unscripted/` ni los assets de F0. No se abrió el editor ni se probaron Blueprints durante esta revisión.

El `.uproject` usa un identificador de instalación para `EngineAssociation`; no prueba por sí solo la versión exacta. El integrador debe comprobar que los cuatro equipos lo abren con 5.8.4 sin convertir assets a otra versión.

No crear un proyecto nuevo ni mover la plantilla. Las rutas `Content/`, `Config/` y `Source/` del plan parten de `Unscripted/`; `Scripts/` y `SourceData/` parten del repositorio. La raíz interna acordada es `/Game/Unscripted/`, unificada con el título por autorización del usuario. Crear las nuevas carpetas y assets con este nombre.

## Qué puede preparar cada división ahora

| División | Antes de tener F0 | Primer trabajo ejecutable después de F0 |
|---|---|---|
| A | Desglosar A-01–03, preparar balance de `docs/03` y casos de prueba de movimiento/Retoma | Input, cámara, WASD y orientación al cursor en `L_Test_A`; después salud, resistencia y dummy propio |
| B | Preparar balance enemigo, transiciones y casos de percepción/congelación | Patrulla y detección en `L_Test_B`, con suelo y NavMesh propios; jugador de prueba sin esperar a A |
| C | Adaptar al inglés diálogos, checklist, documentos y finales; preparar CSV y transiciones narrativas | Fases, interacción y HUD en `L_Test_C`, con eventos simulados sin esperar combate real |
| D | Preparar distribución del nivel, inventario de assets provisionales y licencias | Blockout en `_Geo`, navegación, iluminación provisional y placeholders; sin esperar arte final |

Los CSV pueden prepararse como texto antes de F0; su importación y validación requieren los structs de fila correspondientes. Cada división conserva sus carpetas y su backlog; los dobles de prueba no deben convertirse en dependencias del contenido final.

## Lista del integrador para desbloquear F1

Guía de ejecución para principiantes: [F0 paso a paso en el editor](../../Scripts/INT/F0_GUIA_EDITOR.md). El usuario confirmó apertura del proyecto y Play; la creación de contratos, cascarones, conexiones y mapas sigue pendiente. Crear los componentes vacíos antes de las interfaces que los devuelven evita que falten tipos en sus selectores.

Seguir `00_PLAN_GENERAL.md §5` y las firmas exactas de `01_CONTRATOS_Y_PROPIEDAD.md`. Las casillas siguientes permanecen pendientes hasta comprobarlas en el editor.

1. **Verificar la base.**
   - [x] Abrir `Unscripted/Unscripted.uproject` con UE 5.8.4 y ejecutar Play de la plantilla (confirmado por el usuario; no implica verificación de los cuatro equipos).
   - [ ] Comprobar Git LFS en los cuatro equipos y que los assets descargados abren.
   - [ ] Revisar `.gitignore`: las reglas actuales `Content/Developers/` y `Content/Collections/` no cubren esas carpetas dentro de `Unscripted/`. Ajustarlas antes de guardar borradores personales en Git.
   - [ ] Revisar plugins/configuración requeridos por el contrato; no asumir que un plugin está desactivado solo por no aparecer explícitamente en el `.uproject`.
2. **Crear el vocabulario compartido.**
   - [ ] Crear carpetas de propiedad y todos los enums de contratos §3.
   - [ ] Crear `ST_HitInfo`, `ST_DialogueLine` y `ST_ChecklistRow` con sus campos exactos.
   - [ ] Crear las seis interfaces de §4 y sus entradas/salidas exactas.
   - [ ] Compilar y guardar. No añadir firmas inventadas para resolver dudas: documentarlas y acordarlas.
3. **Crear las piezas vacías.**
   - [ ] Crear los cascarones de §5, incluidos componentes y dispatchers con parámetros exactos.
   - [ ] Conectar Health, Combat, Temporal, Interaction y Stealth al personaje.
   - [ ] Configurar las clases de jugador, controlador, GameState y HUD en el GameMode.
   - [ ] Mantener la lógica de cada división para F1; esta etapa verifica que las referencias existen y compilan.
4. **Preparar los espacios de trabajo.**
   - [ ] Crear `L_Test_A`, `L_Test_B`, `L_Test_C` y `L_Test_D` bajo `Content/Unscripted/Maps/Test/`.
   - [ ] Crear `L_Whitechapel` y subniveles según contratos §6, verificando compatibilidad de la configuración del mapa con ese esquema. No asumir que el mapa Top Down existente ya lo usa.
   - [ ] Configurar colisiones, mapas y Enhanced Input según §7. A implementará el comportamiento de las acciones.
   - [ ] Preparar placeholders de D según §8, sin textos españoles visibles.
5. **Entregar una base comprobada.**
   - [ ] Abrir mapas, compilar cascarones y comprobar que no hay referencias rotas.
   - [ ] Cada integrante abre la misma revisión en su equipo y encuentra sus assets.
   - [ ] Publicar el esqueleto siguiendo el flujo de integración del equipo; registrar revisión y responsable.
   - [ ] Solo entonces marcar F0 terminado y congelar el contrato v1.0.

## Guía práctica para entender los assets

- **Enum:** lista de estados, por ejemplo `Idle` y `Attacking`.
- **Struct:** paquete de datos, por ejemplo daño, dirección y atacante en `ST_HitInfo`.
- **Interface:** operaciones comunes. A llama `ReceiveHit`; B decide cómo recibe el golpe.
- **Cascarón:** Blueprint con clase, funciones y eventos declarados, todavía sin lógica.
- **Dispatcher:** aviso que otros escuchan, por ejemplo `OnHealthChanged` para actualizar el HUD.
- **Mapa de prueba:** sala aislada para probar una división con dobles de prueba, sin tocar el nivel compartido.

## Control de idioma y criterio de entrega

Cada división revisa sus salidas al jugador. C coordina vocabulario y traducción narrativa; D comprueba también texturas, carteles, audio y presentación de la build. Los textos españoles de diseño conservan su significado narrativo, pero no deben copiarse directamente a widgets o DataTables del juego. Los identificadores internos y nombres de assets no son textos de presentación.

**[PROPUESTA]** C puede mantener un glosario inglés en `SourceData/C/` para acordar nombres visibles de poderes, facciones y acciones antes de producir UI y audio. No se fijan traducciones nuevas como requisito en este documento.

**[PROPUESTA] Primera comprobación conjunta tras F0:** A demuestra movimiento y orientación, B una patrulla con detección, C un objetivo en inglés disparado por un evento de prueba y D un recorrido de blockout. Luego se integran gradualmente según F2; no es necesario esperar arte definitivo.

## Estado de esta preparación

- [x] Nombre, versión, modalidad Blueprint e idioma registrados en Markdown.
- [x] Rutas reales y contenido provisional contrastados con el repositorio.
- [ ] Assets compartidos creados y validados en Unreal.
- [ ] Esqueleto publicado y abierto por los cuatro integrantes.

La actualización documental no acredita implementación ni pruebas del juego.
