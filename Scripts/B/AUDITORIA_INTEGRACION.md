# Auditoría de B — 2026-11-14

**Resultado: no apto todavía para declarar entrega completa.** Revisión estática del checkout, scripts, contratos, inventario de assets y registros existentes. Unreal no estaba ejecutándose; no se recompilaron ni ejecutaron los Blueprints en esta revisión. Los scripts describen cómo se construyeron grafos, pero no garantizan que los binarios actuales coincidan exactamente.

## Base existente

### Verificación adicional de mapas mediante Unreal

Se ejecutó `b_audit_placements.py` con UnrealEditor-Cmd 5.8.4, sin guardar paquetes. Resultado en `SourceData/B/placement_audit.json`: tanto L_Whitechapel_AI como el persistente cargado contienen únicamente dos BP_Pursuer y un BP_PatrolRoute de B. No contienen Jack, Interventor ni Supervisor. L_Test_B sí contiene tres Perseguidores, una ruta y Jack con tres puntos de prueba.

Los Perseguidores del nivel real están en X=-150/150, Y=0 cm, con ruta alrededor del origen. No corresponden a la Plaza del layout D (X=800–2200, Y=600–2600 cm). Falta reubicarlos y ajustar su patrulla, además de añadir las patrullas del Callejón y Patio, tres Perseguidores del Paso central, Jack y su ruta Taller→Refugio, Interventor del Tramo y Supervisor del Archivo. Las coordenadas de D son sugerencias; verificar colisiones y navegación antes de cerrar colocación.

El commandlet terminó con 0 errores y 1 warning de RecastNavMesh. Esto verifica inventario/carga, no combate, navegación en Play ni compilación exhaustiva de todos los Blueprints.

Existen BP_GuardBase, Pursuer, Interventor, Supervisor, StealthComponent, PatrolRoute, Jack y dos dobles de prueba. Hay scripts de patrulla, percepción, sospecha/investigación, daño/postura, congelación, neutralización, turnos de ataque, ruta de Jack y restauración local. El plan B registra pruebas previas en Play; no son una nueva certificación de esta auditoría.

## Pendientes para integración, en orden

| Prioridad | Pendiente y evidencia | Criterio de cierre |
|---|---|---|
| P0 | B-CON-01 sigue pendiente: el plan registra Source de ReportStoryEvent como Actor Action Utility, incompatible con Actor. | Integrador/C verifican y corrigen la interfaz y GameState; B puede enviar Self y C recibe el actor correcto. |
| P0 | El estado de B declara sin asignar/cablear BPI_Damageable, TimeAffectable, Interactable y CheckpointListener en GuardBase. Tener funciones locales homónimas no implementa una interfaz. | Mensajes de interfaz ejercitan daño, IsDefeated, Corte, elegibilidad, remate y checkpoint en las tres subclases. Migración sin perder grafos existentes. |
| P0 | b_deal_combat_hit.py busca BP_PlayerCharacter por clase y llama directamente a su función. Fuerza AttackType=EnemyBasic, incluso para el Interventor. | Usar el objetivo real mediante BPI_Damageable; payload correspondiente a cada ataque; comprobar Hit, Blocked, Parried, Dodged e Ignored con dobles y jugador A. |
| P0 | Remate y eventos de neutralización figuran en la guía, no en los scripts ejecutables revisados. | CanInteract solo en estado/rango válido; prioridad 100; RequestFinisher al jugador; neutralización civil no letal y EnemyNeutralized emitido una sola vez. |
| P0 | Jack tiene avance local pero el plan declara pendientes interacción, fase y eventos narrativos. | Interact emite JackFound; ProtectJack habilita avance; JackReachedRefuge una sola vez; sin saltarse puerta/fase; checkpoint no repite eventos. |
| P0 | Interventor: hay bloqueo de ligeros y windup más lento; falta el disparo Correction_Order según el plan. | Permanece aliado hasta OnDialogueFinished(Correction_Order), pasa a hostil y emite InterventorTurnedHostile una sola vez. |
| P0 | Supervisor: existen asset, salud, windup y resistencia parcial al Corte; el encuentro completo sigue pendiente. | Ataque básico, circular y desplazamiento temporal con destino válido; avisos legibles; eventos de inicio/derrota; derrotarlo habilita progreso sin elegir el final. La segunda fase al 50% es P2 opcional. |
| P0 | B-32/B-33: encuentros de todas las zonas y ruta real taller-refugio no cerrados. | Instancias y rutas en L_Whitechapel_AI; recorridos válidos sobre geometría/NavMesh de D; Jack llega 10/10 veces, incluyendo espera por obstáculos y reanudación. |
| P0 | Checkpoint es un evento local B_ResetAtCheckpoint. La política de conservar neutralizados sigue marcada como propuesta. | Conectar OnCheckpointRestore y verificar sección, salud, postura, posición, percepción, ataques latentes, tokens, congelación y estado narrativo de Jack. Acordar política con C. |
| P1 | No existe DT_EnemyBalance en el inventario de Enemies. b_editor_setup.py lee el CSV a balance pero luego asigna constantes sin consumirlo. Salud y stun también tienen constantes en otros scripts. | Una fuente de balance aplicada de forma verificable a todos los arquetipos; editar una fila modifica el comportamiento; documentar conversión metros→centímetros. |
| P1 | Ataques implementados con Delay; no se encontraron assets de animación propios ni creación de notifies en Scripts/B. | Animaciones/ventanas de impacto sincronizadas; un daño por objetivo/ataque; telegráficas y recuperación legibles en cámara final. |
| P1 | No hay evidencia suficiente de emisión de todos los dispatchers contractuales. b_attack_telegraph.py invoca directamente Niagara. | Suscriptor de prueba recibe OnEnemyStateChanged y OnTelegraphStarted con tipo/duración correctos, sin duplicados. |

## Defectos y riesgos concretos que deben probarse/corregirse

- **Jack y zona despejada:** b_jack_clearance.py busca cualquier GuardBase en un radio de 240 alrededor del destino. No filtra hostilidad y no inspecciona todo el tramo. Un aliado puede bloquear el avance y un enemigo intermedio puede pasar inadvertido.
- **Impacto a través de obstáculos:** b_melee_blueprint.py valida distancia, objetivo válido y congelación, pero no realiza traza de oclusión ni valida arco frontal en el impacto. Revisar el grafo final y probar ataque junto a pared y esquiva hacia detrás.
- **Salud/checkpoint:** b_guard_health.py crea B_Health flotante; b_checkpoint_reset.py guarda B_CheckpointHealth como entero. Puede truncar salud fraccionaria. B_ApplyHealthDamage resta sin acotar: revisar daño negativo y exceso de daño.
- **Ataques latentes:** checkpoint no cancela explícitamente los Delay de ataque/cooldown. Probar reset durante windup para impedir un golpe de la vida anterior. El coordinador libera el tag de turno al terminar el windup: revisar interrupciones y limpieza.
- **Congelación:** revisar aplicación directa a derrotados, ya congelados y duración efectiva cero. La elegibilidad debe cumplirse también dentro de ApplyTemporalFreeze, no depender solo del llamador. Probar Corte durante stun y recuperación.
- **Reproducibilidad:** varios scripts seleccionan nodos por nombres como K2Node_CallFunction_9 y omiten trabajo por presencia de una variable. No ejecutar todos en lote sobre assets actuales: pueden fallar o dejar una migración parcial. Inspeccionar grafos y guardar solo assets B.
- **JSON de IA:** el validador acepta Investigate aunque no existe como valor del enum compartido. Mantener investigación como comportamiento interno de Suspicious, o solicitar contrato; no añadir un enum unilateralmente.

## Pruebas realizadas en esta revisión

- `python Scripts/B/b_enemy_balance.py`: pasa, cuatro filas. Solo valida columnas y nombres, no coherencia numérica ni aplicación en runtime.
- `python Scripts/B/b_ai_machine.py`: pasa, cuatro arquetipos. Valida estructura; no ejecuta la IA ni comprueba equivalencia con Blueprints.
- Inventario: nueve .uasset bajo Enemies; no DataTable ni carpeta Animation con assets.
- Sin nueva compilación, Play, diez recorridos de Jack ni build empaquetada. Los warnings históricos de NavMesh requieren comprobarse en el mapa integrado; por sí solos no demuestran un defecto de B.

## Puerta de salida del módulo

1. Contratos correctos y mensajes de interfaz probados con A/C.
2. Tres perseguidores patrullan, detectan con oclusión/sigilo, combaten con máximo dos atacantes, reciben parry/Corte/remate y se neutralizan sin duplicar eventos.
3. Interventor cambia de bando en el diálogo correcto; Supervisor completa todos sus ataques P0 y comunica derrota.
4. Jack completa diez recorridos del nivel real y respeta fases, obstáculos, amenazas y checkpoint.
5. Retoma de A no restaura heridas enemigas ni eventos narrativos.
6. Blueprints B compilan sin errores ni warnings; prueba integrada y build con D; sin referencias a Test/Developers desde contenido de producción ni controles de debug en entrega.

No se modificaron assets compartidos. AGENTS.md obliga a registrar solicitudes y detener cambios que requieran alterar contratos. B-CON-01 necesita resolución del integrador/C antes de cerrar la integración narrativa.
