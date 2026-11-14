# A-CON-01 — Corrección del nombre de la operación de daño

Aprobado por el usuario el 2026-11-14 durante la integración F0. Documentación actualizada; assets pendientes de migración y comprobación en Unreal. No se editan binarios desde scripts de texto.

## Causa

`AActor.ReceiveHit` ya existe en el motor, se muestra como `Hit` e incluye `MyComp`. Nuestro contrato anterior reutilizaba ese nombre con otros parámetros. Las capturas del usuario y el error de compilación identifican esa colisión; no es un parámetro añadido por el usuario. [API oficial](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/AActor/ReceiveHit).

## Cambio

En `BPI_Damageable`, la operación pasa a llamarse `ReceiveCombatHit`. Entrada: `HitInfo` de tipo `ST_HitInfo`; salida: `Result` de tipo `EHitResult`; ambos valores individuales. `IsDefeated` no cambia. No renombrar el evento nativo Hit del motor.

## Primer intento: actualizar desde la interfaz

1. Salir de Play. Abrir `/Game/Unscripted/Core/Interfaces/BPI_Damageable`.
2. En Mi Blueprint, seleccionar la función `ReceiveHit`, pulsar F2 y renombrar a `ReceiveCombatHit`.
3. Comprobar entrada HitInfo y salida Result, con sus tipos. Compilar y guardar la interfaz.
4. Abrir `BP_PlayerCharacter`; usar Archivo → Refresh All Nodes si es necesario. Abrir la implementación de `ReceiveCombatHit` desde Interfaces.
5. Comprobar que la entrada se conecta al Return Node mediante el cable blanco; salida Result = Ignored para el cascarón actual. Compilar.
6. Si compila, guardar y revisar también IsDefeated = false y GetStealthComponent conectado. No hace falta retirar interfaces.

## Si persiste el grafo Hit o el error MyComp

Antes de retirar nada, guardar una captura o copia del contenido de las funciones de BPI_Damageable si contienen más lógica que los retornos provisionales. El procedimiento siguiente reconstruye solamente esas implementaciones; no el personaje ni sus componentes.

1. En PlayerCharacter → Ajustes de clase → Interfaces implementadas, retirar únicamente `BPI_Damageable`.
2. Si pregunta si debe transferir/conservar sus funciones como funciones locales, elegir **no conservarlas**: queremos quitar las implementaciones incompatibles. Leer el texto del diálogo, no basarse solo en la posición de los botones.
3. Comprobar que no quedaron funciones locales del intento anterior. Si Unreal sigue mostrando una función Hit/ReceiveHit y no está claro su origen, detenerse y revisar la captura antes de borrar; no quitar eventos nativos de colisión.
4. Compilar PlayerCharacter sin BPI_Damageable. Si falla todavía, revisar el error antes de seguir.
5. Añadir otra vez `BPI_Damageable` desde Ajustes de clase y compilar.
6. Abrir ReceiveCombatHit desde Interfaces, conectar entrada a retorno y fijar Result = Ignored.
7. Abrir IsDefeated, conectar entrada a retorno y dejar Result = false.
8. Compilar y guardar. BPI_PlayerControl, BPI_CheckpointListener, GetStealthComponent y componentes no se retiran.

## Consumidores y verificación

- Buscar implementaciones y llamadas de la interfaz en los Blueprints de A/B que ya existan, incluidos dobles de prueba; usar ReceiveCombatHit en todos ellos. No reemplazar eventos nativos Hit de colisión.
- Confirmar que BPI_Damageable y PlayerCharacter compilan sin errores de firma ni MyComp.
- Confirmar que los pines coinciden con el contrato y se conservaron las otras interfaces.
- Reabrir los assets guardados y compilar nuevamente si se reconstruyeron grafos.
- Registrar el resultado en el plan A. La edición de Markdown por sí sola no acredita reparación del proyecto.
