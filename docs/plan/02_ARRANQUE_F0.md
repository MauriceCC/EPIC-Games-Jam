# Arranque del equipo — Unscripted

## Decisiones confirmadas el 2026-11-14

- Nombre definitivo: **Unscripted**.
- Motor: **UE 5.8.4**, según confirmación del usuario; verificar la instalación en cada equipo.
- Proyecto creado como **Blueprint**. No se requiere C++ para arrancar.
- **Todo contenido visible o audible para el jugador debe estar en inglés**, desde el prototipo. Documentación y comentarios internos pueden estar en español. Esto incluye UI, objetivos, diálogos, prompts, documentos, finales, créditos, carteles, imágenes con texto y voces.
- El usuario autorizó asumir excepcionalmente el rol de integrador para esta preparación. No equivale a una asignación permanente ni habilita modificaciones indiscriminadas a trabajo ajeno.

## Estado observado, sin confundir documentación con implementación

La revisión inicial encontró la plantilla Top Down y no encontró los assets de F0. **Actualización 2026-11-14:** el proyecto se abrió en UE 5.8.4 y se generó la mayoría de los assets F0. El inventario del editor confirma todos los assets listados en este plan, las seis interfaces con sus nombres de funciones, los cinco componentes requeridos en el jugador y las clases del GameMode. Esto no implica que F0 esté cerrado: faltan asignaciones de interfaces, getters/retornos seguros, validación de colisiones y una prueba de arranque/Play con la configuración nueva.

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

Guía de ejecución para principiantes: [F0 paso a paso en el editor](../../Scripts/INT/F0_GUIA_EDITOR.md). La guía se ejecutó parcialmente con el worker Python del editor. No volver a crear assets ya presentes; completar y validar solo los puntos pendientes.

Seguir `00_PLAN_GENERAL.md §5` y las firmas exactas de `01_CONTRATOS_Y_PROPIEDAD.md`. Las casillas siguientes permanecen pendientes hasta comprobarlas en el editor.

1. **Verificar la base.**
   - [x] Abrir `Unscripted/Unscripted.uproject` con UE 5.8.4 y ejecutar Play de la plantilla (confirmado por el usuario; no implica verificación de los cuatro equipos).
   - [ ] Comprobar Git LFS en los cuatro equipos y que los assets descargados abren.
   - [ ] Revisar `.gitignore`: las reglas actuales `Content/Developers/` y `Content/Collections/` no cubren esas carpetas dentro de `Unscripted/`. Ajustarlas antes de guardar borradores personales en Git.
   - [ ] Revisar plugins/configuración requeridos por el contrato; no asumir que un plugin está desactivado solo por no aparecer explícitamente en el `.uproject`.
2. **Crear el vocabulario compartido.**
   - [x] Los nueve enums, tres structs y seis assets de interfaz existen.
   - [ ] Auditar todos los campos y pines contra §3–§4, incluidos tipos y valores; la presencia de los assets no acredita firmas exactas.
   - [ ] Compilar y guardar todos los contratos sin errores.
3. **Crear las piezas vacías.**
   - [x] Los cascarones de §5 y las clases derivadas de enemigos existen.
   - [x] Health, Combat, Temporal, Interaction y Stealth están añadidos al jugador; Health al GuardBase; ObjectiveManager al GameState.
   - [x] El GameMode referencia PlayerCharacter, PlayerController, GameState y HUD.
   - [ ] Asignar las interfaces a PlayerCharacter, GuardBase, Jack, InteractableBase y GameState. La auditoría actual confirma que aún faltan.
   - [ ] Completar retornos seguros y getters de componentes; después compilar y guardar todos los cascarones.
4. **Preparar los espacios de trabajo.**
   - [x] Los mapas de prueba A–D, `L_Whitechapel` y sus cuatro subniveles existen; el editor informa los cuatro subniveles cargados en el persistente.
   - [x] El persistente contiene iluminación y NavMeshBoundsVolume; Geo contiene suelo; Story contiene PlayerStart.
   - [x] Placeholders tipados de VFX, audio y materiales están creados.
   - [x] `DefaultEngine.ini` apunta al mapa y GameMode nuevos; se añadieron los canales de traza Interaction y Combat con respuesta global Ignore.
   - [ ] Recargar el proyecto y comprobar Mapas & Modes y los canales en Project Settings. Combat aún no tiene verificada la respuesta Overlap de Pawn; no inventar un perfil hasta resolverlo.
   - [ ] Verificar Enhanced Input, generación dinámica de NavMesh y la navegación efectiva en los mapas de prueba.
5. **Entregar una base comprobada.**
   - [ ] Reabrir el proyecto con la configuración nueva; compilar Blueprints, cargar mapas y ejecutar Play. Aún no se ha hecho esta prueba tras cambiar el mapa por defecto.
   - [ ] Revisar Output/Message Log y eliminar errores de compilación atribuibles a los Blueprints; no confundir errores de diagnóstico Python del worker con compilaciones de BP.
   - [ ] Cada integrante abre la misma revisión en su equipo; Git LFS y validación de los cuatro equipos no se han comprobado.
   - [ ] Publicar el esqueleto siguiendo el flujo de integración del equipo; registrar revisión y responsable.
   - [ ] Solo entonces marcar F0 terminado y congelar el contrato v1.0.

## Guía práctica para entender los assets

- **Enum:** lista de estados, por ejemplo `Idle` y `Attacking`.
- **Struct:** paquete de datos, por ejemplo daño, dirección y atacante en `ST_HitInfo`.
- **Interface:** operaciones comunes. A llama `ReceiveCombatHit`; B decide cómo recibe el golpe.
- **Cascarón:** Blueprint con clase, funciones y eventos declarados, todavía sin lógica.
- **Dispatcher:** aviso que otros escuchan, por ejemplo `OnHealthChanged` para actualizar el HUD.
- **Mapa de prueba:** sala aislada para probar una división con dobles de prueba, sin tocar el nivel compartido.

## Control de idioma y criterio de entrega

Cada división revisa sus salidas al jugador. C coordina vocabulario y traducción narrativa; D comprueba también texturas, carteles, audio y presentación de la build. Los textos españoles de diseño conservan su significado narrativo, pero no deben copiarse directamente a widgets o DataTables del juego. Los identificadores internos y nombres de assets no son textos de presentación.

**[PROPUESTA]** C puede mantener un glosario inglés en `SourceData/C/` para acordar nombres visibles de poderes, facciones y acciones antes de producir UI y audio. No se fijan traducciones nuevas como requisito en este documento.

**[PROPUESTA] Primera comprobación conjunta tras F0:** A demuestra movimiento y orientación, B una patrulla con detección, C un objetivo en inglés disparado por un evento de prueba y D un recorrido de blockout. Luego se integran gradualmente según F2; no es necesario esperar arte definitivo.

## Estado de esta preparación

- [x] UE 5.8.4 detectado en el editor; proyecto y assets compartidos presentes.
- [x] El grafo de `BP_PlayerController` registra IMC_Default en BeginPlay, con guarda `IsLocalController`, comprobación `IsValid` del subsistema, compilación exitosa y guardado.
- [ ] F0 no está cerrado: faltan interfaces en cinco clases, retornos/getters, verificación de Combat/Pawn, recarga de configuración y prueba de Play.
- [ ] Git LFS y apertura por los cuatro integrantes sin validar; no se ha publicado una base compartida.
- **Limitaciones de la máquina observadas en `Unscripted/Saved/Logs/Unscripted.log`:** el adaptador solo declara SM5 aunque se pidió SM6; Unreal intentó fallback a D3D11/SM5. La compilación de assets avisó de un requisito estimado de 4608 MiB frente a un límite de ~483 MiB y continuó. También hubo un aviso de límite de tiles del RecastNavMesh. Volver a comprobarlo tras el reinicio y revisar navegación; no cambiar el renderer como solución sin una decisión explícita.
