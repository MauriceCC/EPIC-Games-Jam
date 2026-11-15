# A-03 — Orientación continua hacia el cursor

Fecha: 2026-11-15. Responsable: Mauricio / División A.
Base revisada después del pull: `b2ceb53`.

**Estado: implementado, guardado y comprobado tras recargar con UE 5.8.4.
Pendiente la aceptación visual en Play, especialmente sobre pendientes.**

## Comportamiento

WASD conserva el desplazamiento existente. El personaje actualiza su orientación
hacia el cursor sin necesitar un ataque. Solo gira en yaw; no se inclina hacia
arriba o hacia abajo para apuntar.

Se reutiliza la función `FaceCursor`, que obtiene un impacto bajo el cursor y
solo rota si la traza acierta. Cuando no hay impacto, conserva la orientación.
La traza existente usa `TraceTypeQuery1`; no se cambiaron canales ni colisiones.
La orientación depende de las superficies que respondan a esa traza, por lo
que todavía se debe comprobar suelo, pendientes y obstáculos en el nivel.

## Cambio exacto

Único asset modificado:

`/Game/Unscripted/Player/BP_PlayerCharacter`

1. Se añadió la función privada `A_UpdateCursorFacing`.
2. Su condición es `IsLocallyControlled AND NOT bDead`.
3. Si se cumple, llama a la función existente `FaceCursor`.
4. `Event Tick` llama a `A_UpdateCursorFacing` y después continúa por la misma
   rama que antes registraba el historial de Retoma.
5. En CharacterMovement, `Orient Rotation to Movement` pasó de true a false.
   Así el movimiento no sobrescribe la orientación solicitada por el cursor.
6. `Use Controller Rotation Yaw` ya estaba en false y se conserva.

**[PROPUESTA]** El nombre de la función privada y la guarda de control local
son decisiones de implementación de A. No añaden firmas ni contratos compartidos.
La orientación continua también se actualiza durante ataques y esquivas;
cualquier bloqueo de dirección por animación será una decisión posterior de combate.

Los grafos originales conservaron sus nodos, valores y conexiones, salvo el
único enlace de ejecución de Tick en el que se insertó la nueva llamada.
`DoMove`, `FaceCursor`, los ataques y los poderes no se reconstruyeron.
`BP_PlayerController`, IMC_Default, mapas, Core y assets de B/C/D no se guardaron.

## Compatibilidad con el pull

Los commits recibidos entre `6053c45` y `b2ceb53` añaden trabajo de C/D y no
cambian los Blueprints de A. Se revisó el handoff
`SourceData/C/CLOSURE_BLOCK1_STATUS.md`:

- C ya gestiona E y Tab mediante su adaptador del HUD. No se duplicó esa entrada.
- C reporta salud inicial cero en el componente instalado en el personaje,
  aunque la clase Health tenga máximos de 100. Esa corrección corresponde al
  siguiente trabajo de A-04; no se alteró como efecto secundario de A-03.
- Los bloqueos narrativos y restauración por checkpoint siguen pendientes en A.
  Esta tarea no declara resueltos A-16/A-18/A-22 ni el Bloque 1 integrado.

## Comprobaciones realizadas

- 12 comprobaciones durante implementación: prerrequisitos, compilación,
  conservación de grafos, propiedad de rotación y guardado exclusivo del personaje.
- 16 comprobaciones en otro proceso de Unreal, cargando el asset ya guardado:
  compilación, persistencia de la configuración, ruta de Tick, guardas,
  continuación hacia Retoma y conservación íntegra del archivo del controlador.
- Se invocó el helper en la clase real sin controlador: no cambió orientación
  ni posición. Esto comprueba la guarda; no sustituye la prueba con mouse.
- Las ejecuciones finales de implementación y validación terminaron con
  0 errores y 0 warnings en el resumen del commandlet.
- Git confirmó que el único `.uasset` modificado es BP_PlayerCharacter.

Evidencia: `a03_implementation_result.json` y `a03_validation.json`.
No se ejecutó una sesión visual de Play ni se probó el mouse real con NullRHI.
No se marca A-03 ni el mínimo F1 como aceptado hasta completar la prueba siguiente.

## Prueba paso a paso para Mauricio

1. Abrir `Unscripted/Unscripted.uproject` y `Maps/Test/L_Test_A`.
2. Ejecutar Play y comprobar que el pawn es `BP_PlayerCharacter` y el controlador
   `BP_PlayerController`. Si el mapa usa un override de pruebas diferente,
   registrar ese hecho antes de atribuir un fallo al cambio.
3. Sin pulsar teclas ni atacar, mover el cursor alrededor del personaje sobre
   suelo con colisión. Debe girar sin desplazarse.
4. Mantener A o D y dejar el cursor al lado contrario: el personaje debe
   desplazarse con WASD mientras mira al cursor. No debe oscilar entre ambos giros.
5. Repetir con W/S y diagonales. La cámara debe mantener su orientación isométrica.
6. Apuntar sobre una pendiente suave disponible en el mapa de pruebas de A:
   debe girar en horizontal, sin inclinarse ni teletransportarse.
7. Apuntar fuera del suelo: al fallar la traza, debe conservar la última orientación.
8. Probar un ataque y una Retoma para detectar regresiones de conexión. Los
   defectos previos de esos sistemas siguen siendo los de la auditoría anterior.
9. Detener Play, revisar Output Log y anotar resultado. No usar Save All sobre
   paquetes de otras divisiones.

Si no gira: comprobar que la traza acierta y que el pawn está poseído localmente,
con `bDead=false`. Si hay giro de cámara u oscilación, registrar las propiedades
de la instancia de cámara/CharacterMovement antes de modificar assets compartidos.

## Scripts y respaldo

- `implement_a03.py`: migración de una sola ejecución, ya aplicada. Se detiene si
  encuentra el helper existente; no volver a ejecutarla sobre el asset editado.
- `a03_graph_tools.py`: comprobación de conexiones y preservación de grafos.
- `validate_a03.py`: validación sin guardar assets; puede repetirse con Unreal
  Python. Para validar disco, ejecutarlo en un commandlet nuevo.
- La ruta de la copia previa del `.uasset` y sus hashes están en el informe de
  implementación. El respaldo está en el directorio temporal local, fuera del repo.

El primer intento falló por el nombre de un acceso Python al componente, antes
de guardar. Se corrigió el acceso, se repitió y se validó el resultado persistido.
No se realizaron commits, pushes ni cambios de rama.

## Siguiente secuencia de A [PROPUESTA]

1. Completar esta aceptación de A-03 junto con la prueba de A-01/A-02.
2. A-04: corregir/verificar el Health instalado en el personaje, su valor inicial
   y los valores emitidos por sus dispatchers; contrastar con el HUD real de C.
3. A-05/A-06/A-12: resistencia, estados permitidos y balance ajustable.
4. A-07–11: resultados de daño correctos, fuerte separado y combo con ventanas.
5. A-13–16/A-22: Corte elegible, Retoma segura y bloqueos/checkpoints con C.
