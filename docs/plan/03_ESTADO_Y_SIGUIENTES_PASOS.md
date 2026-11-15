# Estado revisado y siguientes pasos — Unscripted

> Revisión documental: 2026-11-14 (America/Lima). Base: `main`, commit `4afcd57` (`Enemys after merge`). Alcance autorizado: plan de trabajo. No se ejecutaron scripts del editor, no se guardaron assets ni se modificaron contratos o configuración.

## 1. Diagnóstico

**F1 en desarrollo, con cierre de F0 pendiente de acreditación y avances parciales de integración.** Ya existe contenido propio; no corresponde reconstruir el esqueleto ni tratar todo como una plantilla inicial. Tampoco hay evidencia suficiente para declarar completado el encuentro F2, los tres actos o la build final.

La prioridad es conectar y validar jugador, enemigos y narrativa sobre la misma revisión. Los assets de arte, audio y VFX ya entregados deben aprovecharse antes de solicitar nuevas tandas.

Este informe actualiza el estado, no el diseño ni las firmas de [01_CONTRATOS_Y_PROPIEDAD.md](01_CONTRATOS_Y_PROPIEDAD.md). Los IDs y criterios de los backlogs A–D se conservan. No se asigna un porcentaje global: contar assets no mide jugabilidad.

## 2. Cómo interpretar la evidencia

| Estado | Significado |
|---|---|
| Presente | Archivo o configuración comprobado en este checkout; no acredita funcionamiento |
| Reportado | El historial o la documentación de una división registra implementación o prueba anterior |
| Por validar | Falta una prueba reproducible sobre la revisión integrada actual |
| Sin evidencia localizada | No se encontró el entregable esperado; no descarta trabajo local de otro integrante |

Se revisaron README, planes A–D, diseño `docs/01`–`docs/07`, inventario local, historial Git, configuración, fuentes de datos, entrega de D y el log local existente. No se inspeccionaron los grafos binarios ni se hizo una nueva sesión de Play. Los logs locales no sustituyen un reporte versionado: pueden corresponder a trabajo sin guardar o a revisiones anteriores.

## 3. Avance por división y pendientes

| Área / IDs | Avance acreditado | Qué falta para cerrar |
|---|---|---|
| INT / F0 | Presentes 9 enums, 3 structs y 6 interfaces; componentes, cascarones, mapas A–D, persistente y cuatro subniveles. Configuración apunta a Whitechapel y `BP_GameMode`. `.gitignore` ya cubre las carpetas personales bajo `Unscripted/` | Auditar firmas, implementaciones, retornos y dispatchers; compilar consumidores; comprobar colisiones y navegación; apertura de la misma revisión por los cuatro integrantes |
| A-01–03, A-17 | Input Actions e `IMC_Default` presentes. `8b0c65f` registra movimiento base y `8e6dd52` mensajes de movimiento; integración en `47df584` y `4ea25d1`. Existe script de agacharse | Demostrar todas las entradas, WASD relativo a cámara, orientación al cursor y sigilo con el jugador real. Un script disponible no acredita su ejecución |
| A-04–16, A-18, A-20–24 | Health, Combat y Temporal existen como assets; no se localizó `DT_PlayerBalance`, `ST_RewindSnapshot` ni montages propios en `Content/Unscripted/` | Auditar lógica existente antes de completar salud/resistencia, estados, combo, fuerte, parry, esquiva, Corte, Retoma segura, remate y muerte/checkpoint. No hay evidencia del mínimo F1 de A completo |
| B-01–12, B-14 | [Estado de B](B_ENEMIGOS_IA_SIGILO.md#9-estado) reporta Play con daño, neutralización, turnos, aturdimiento, congelación, Jack y restauración local. Hay scripts de patrulla, percepción, investigación y combate; `57818bb` registra nuevas mejoras | Repetir tras merges. Enlazar las interfaces de GuardBase y Jack; probar tres perseguidores, recuperación tras Corte y ruta de Jack 10/10. La prueba local no acredita integración con A/C |
| B-13 | CSV `SourceData/B/DT_EnemyBalance.csv`, máquina de estados JSON y scripts presentes; B reporta balance aplicado a valores por defecto | No se localizó `DT_EnemyBalance.uasset`; demostrar importación y que reimportar cambia el comportamiento, según el criterio del backlog |
| B-20–22, B-30–33 | B reporta dos perseguidores en `_AI`, lógica local de checkpoint y clases Interventor/Supervisor presentes | Combate con A, eventos con C, política compartida de respawn, hostilidad por `Correction_Order`, jefe completo y ruta real taller–refugio |
| C-01–05, C-09 | Presentes GameMode, GameState, ObjectiveManager, Interaction e interactuables. Historial: `463d325`, `8323e63`, `5d54d01`; tabla de fases documentada | Verificar lógica y firmas. Demostrar fases, prioridad de interacción, puerta persistente, escondite, dos evidencias y checkpoint. Existencia del BP no cierra la tarea |
| C-06–08, C-20–34 | `BP_HUD` presente; D ya entrega mallas de evidencias, puertas y estaciones finales | No se localizaron `WBP_*`, `DT_Dialogue`, `DT_Checklist` ni fuentes narrativas en `SourceData/C/`. Completar textos en inglés, diálogos, checklist reescrito, HUD, ambos finales y recorrido completo |
| D-01, D-06 | Placeholders presentes (`ab23129`); props, materiales, audio y VFX entregados en varios commits. [Handoff de D](../../SourceData/D/HANDOFF_ASSETS.md) y créditos disponibles | Verificar referencias desde consumidores, escala/colisiones y licencias finales. `MS_Ambience_Whitechapel` sigue vacío según handoff; hay loops de lluvia/viento disponibles |
| D-02–05, D-20–23 | Layout JSON, script, mapas, materiales de blockout y `BP_GasLamp` presentes; `6621298` registra blockout y `43ece9c` navegación | Recorrido completo, navegación efectiva, cobertura y oclusión con la cámara de A. Congelar layout solo tras F2. Falta evidencia de build probada en otro PC |
| D-30–42 | Props de entorno, efectos y sonidos ya producidos; parte del contenido de F3 se adelantó | Colocación e integración final, legibilidad, rendimiento, empaquetado, créditos revisados y entrega |

**Evidencia local adicional:** `Unscripted/Saved/Logs/Unscripted.log` identifica UE `5.8.4-58902052` y sesiones PIE de `L_Test_A` y `L_Test_B` a las 01:34–01:35 UTC del 15-nov (20:34–20:35 del 14-nov en Lima). Esto acredita arranques locales, no los criterios completos de esos mapas ni una partida de Whitechapel. También contiene avisos de RecastNavMesh y `LogAutomationTest: Error: Condition failed`; falta atribuirlos antes de declarar una validación limpia. No se interpretan automáticamente como errores de compilación Blueprint.

## 4. Bloqueos y discrepancias que deben resolverse

| Asunto | Evidencia / impacto | Responsable y cierre |
|---|---|---|
| A-CON-01 | Renombrado a `ReceiveCombatHit` aprobado en contrato; el estado de A todavía deja migración/compilación pendiente | INT + A/B: comprobar llamada y recepción con la firma aprobada, sin colisión con el evento nativo |
| B-CON-01 | B reporta `Source` como `Actor Action Utility` en vez de `Actor`; impide reportar eventos desde sus pawns | INT + C: tramitar la solicitud ya existente y verificar interfaz/implementación. No se cambió el contrato en esta revisión |
| Adaptadores de B | B declara pendientes interfaces en GuardBase y conexiones narrativas de Jack | B implementa los adaptadores hacia su lógica local; A/C prueban consumidores. No duplicar la IA ya hecha |
| Navegación | `DefaultEngine.ini` contiene `RuntimeGeneration=DynamicModifiersOnly`; el contrato pide `Dynamic` | D/INT: comprobar resultado en mapa y resolver discrepancia por el flujo acordado. No asumir que navegar en test valida Whitechapel |
| Colisiones | Existen canales Interaction y Combat con respuesta predeterminada Ignore; el perfil Pawn no declara respuesta Combat explícita en el INI | INT + A/B/C: comprobar respuestas efectivas de componentes y trazas; no dar por verificado Overlap Pawn |
| Controles de prueba | B documenta clic para moverse, Espacio para golpear y congelación de 2 s | B conserva su banco de pruebas; F2 debe validarse con controles de A y comportamiento acordado, sin confundir ambos resultados |
| Muerte/checkpoints | B tiene una política local que conserva neutralizados; decisión global sigue abierta | A/B/C: acordar salud cero con cargas, restauración de enemigos/Jack y progreso persistente antes de cerrar A-18/B-22/C-22 |
| Calendario | El plan inmediato de D cita un plazo de itch.io sin enlace verificable en esta revisión | Integrador confirma plazo oficial y horario; no convertir esa nota histórica en un calendario validado |

## 5. [PROPUESTA] Orden de trabajo desde esta revisión

La secuencia siguiente prioriza el backlog existente; no autoriza cambios de contrato ni nuevas mecánicas. Cada persona trabaja únicamente en sus rutas.

| Orden | Trabajo y responsables | Entrega verificable / dependencia |
|---|---|---|
| 1 | INT con A/B/C: cerrar auditoría F0, A-CON-01 y B-CON-01; D revisa navegación | Mismo commit abre en los cuatro equipos; contratos/consumidores compilan; llamadas de prueba llegan con parámetros correctos. Registrar revisión y resultado |
| 2A | A: validar movimiento existente y completar A-04–18 | Mínimo F1 de A con dos dummies, balance ajustable y Retoma personal segura; usar arte provisional si faltan animaciones finales |
| 2B | B: preservar lo probado y conectar interfaces/eventos; cerrar B-01–14 | Mínimo F1 de B con tres perseguidores y Jack 10/10, sin depender del jugador de prueba para acreditar integración |
| 2C | C: C-01–09, preparando textos/UI mientras se resuelven firmas | Secuencia de fases, interacción, diálogos, checklist y HUD en `L_Test_C` con eventos simulados; todo texto visible en inglés |
| 2D | D: validar D-02–05 y preparar D-22 con assets existentes | Recorrido caminable y navegación comprobada; lista de problemas de cámara/cobertura para A/B/C |
| 3 | A/B/C/D: encuentro F2 en Whitechapel | Aparición, órdenes, dos perseguidores, combo/parry/esquiva/Corte/Retoma, puerta, HUD/checklist y muerte/checkpoint funcionando juntos |
| 4 | D + equipo: empaquetado Development, a más tardar al cerrar F2 | Arranque y recorrido del encuentro en otro PC; registrar errores de cook/referencias y resolverlos antes de ampliar contenido |
| 5 | B/C/D con A: completar los tres actos y dos expedientes | Dos recorridos separados hasta Final A y Final B, sin intervención del editor; activar feature freeze |
| 6 | Todos, D coordina: F4 | Balance y duración medidos, idioma/créditos revisados, build Shipping comprobada y entrega registrada |

Las filas 2A–2D describen trabajo paralelo de las cuatro personas del equipo. No requieren esperar a que termine otra división para probar con dobles propios. P2 continúa fuera del trabajo inmediato.

## 6. Lista de aceptación pendiente

- [ ] F0: firmas y componentes auditados; compilación y apertura comprobadas en los cuatro equipos.
- [ ] A: todas las acciones responden, sin daño duplicado por ataque; parry/esquiva devuelven resultados correctos.
- [ ] Corte: un objetivo válido, cooldown y recuperación de IA; resistencia del Supervisor comprobada.
- [ ] Retoma: solo restaura al jugador, consume una de dos cargas, valida geometría y respeta bloqueos narrativos; no recupera cargas del snapshot ni deshace daño enemigo/evidencias/puertas.
- [ ] B: tres enemigos respetan turnos; civiles neutralizados sin morir; Jack alcanza refugio 10/10.
- [ ] C: interacción priorizada, eventos sin duplicar progreso, checklist inicial y reescritura en inglés, HUD enlazado y respawn coherente.
- [ ] D: navegación, cobertura y lectura de combate comprobadas en Whitechapel con el jugador real.
- [ ] F2: encuentro completo con el mismo commit y build Development probada fuera del PC de desarrollo.
- [ ] F3: ambos finales solo se activan al registrar el expediente correspondiente; historia completa y sin bloqueos.
- [ ] F4: Shipping, rendimiento, idioma, créditos y entrega comprobados.

## 7. Registro de próximas validaciones

Cada dueño actualiza el estado de su división con evidencia; el integrador consolida los hitos. Mantener las notas anteriores como historial, no como diagnóstico actual.

| Fecha | Commit | Dueño / ID | Mapa o build | Pasos y resultado esperado | Resultado observado | Evidencia / incidencia |
|---|---|---|---|---|---|---|
| Pendiente | — | — | — | — | — | — |

Un commit o un script acredita una entrega, pero una tarea funcional solo se cierra cuando cumple su criterio de aceptación. Si falla, registrar el bloqueo y su dueño; no marcar toda la división como terminada.
