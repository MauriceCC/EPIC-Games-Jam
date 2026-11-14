# A-01 — Controles de Unscripted en Blueprint

**Estado:** guía preparada; assets y prueba en Unreal pendientes. UE 5.8.4, Blueprint.

**Criterio de aceptación del backlog:** todas las acciones de la tabla de controles disparan un Print en test. A-01 no implementa todavía movimiento, ataques, poderes ni menús.

## Alcance y preparación

F0 no está creado en los archivos revisados. **[PROPUESTA]** Probar A-01 con un controlador y GameMode exclusivos de A en `Player/Test/`. Esto permite validar input sin inventar contratos ni crear los cascarones compartidos por cuenta propia. Estos assets de prueba no se referencian desde el juego final. Al integrar F0, trasladar las conexiones al `BP_PlayerController` de A y usar el GameMode compartido configurado por el integrador.

No editar `TopDown/`, `Core/`, `Config/` ni `Narrative/`. Si el editor solicita cambiar plugins o configuración compartida, registrar la necesidad con el integrador. Enhanced Input ya aparece configurado en los `.ini`, pero debe verificarse en el editor.

Las rutas siguientes son del Content Browser (`/Game/` = `Unscripted/Content/`). Crear solo los assets que falten; no reemplazar los existentes.

## 1. Crear las acciones

En `/Game/Unscripted/Player/Input/`, clic derecho → Input → Input Action. Crear las acciones de la tabla y abrir cada una para configurar Value Type. Dejar Triggers vacíos para esta prueba.

| Asset | Value Type | Tecla | Print en inglés |
|---|---|---|---|
| IA_Move | Axis2D | WASD | Move: seguido del valor |
| IA_LookMouse | Axis2D | Mouse XY 2D-Axis | Mouse input: seguido del valor |
| IA_LightAttack | Digital (bool) | Left Mouse Button | Light attack |
| IA_HeavyAttack | Digital (bool) | Right Mouse Button | Heavy attack |
| IA_Dodge | Digital (bool) | Space Bar | Dodge |
| IA_Parry | Digital (bool) | Q | Parry |
| IA_TemporalCut | Digital (bool) | F | Temporal cut input |
| IA_Retake | Digital (bool) | R | Retake input |
| IA_Interact | Digital (bool) | E | Interact |
| IA_Crouch | Digital (bool) | Left Ctrl | Crouch |
| IA_Checklist | Digital (bool) | Tab | Checklist |
| IA_Pause | Digital (bool) | Escape | Pause requested |

**[PROPUESTA]** `IA_Pause` completa el control Esc de `docs/02`, sin implementar el menú de C. Los mensajes de poderes son etiquetas de diagnóstico, no nombres de producto aprobados.

## 2. Crear el contexto

En la misma carpeta, clic derecho → Input → Input Mapping Context → `IMC_Default`. Es distinto del contexto de la plantilla bajo `/Game/TopDown/`.

Añadir las acciones y teclas de la tabla. Para `IA_Move`, crear cuatro mappings:

| Tecla | Modifiers, en orden | Valor esperado aislado |
|---|---|---|
| D | Ninguno | X=1, Y=0 |
| A | Negate (X) | X=-1, Y=0 |
| W | Swizzle Input Axis Values, orden YXZ | X=0, Y=1 |
| S | Negate (X), después Swizzle YXZ | X=0, Y=-1 |

**[PROPUESTA]** En `IA_Move`, usar Accumulation Behavior = Cumulative para que direcciones opuestas se cancelen. Verificar W+S y A+D; en A-02 se limitará la magnitud de movimiento para no correr más rápido en diagonal.

## 3. Crear el controlador de prueba

En `/Game/Unscripted/Player/Test/`, crear Blueprint Class con padre **PlayerController**, llamado `BP_InputTestController_A`.

En Event Graph conectar:

1. `Event BeginPlay` → `Is Local Controller` → `Branch`.
2. Salida True → obtener `Enhanced Input Local Player Subsystem` del controlador local (`Self`).
3. Comprobar `Is Valid` del subsystem; si es válido → `Add Mapping Context`, contexto `/Game/Unscripted/Player/Input/IMC_Default`, Priority `0`.
4. Después → `Set Show Mouse Cursor` en Self = true.
5. Después → `Set Input Mode Game Only`, Player Controller = Self.

No llamar `Clear All Mappings`. Este controlador nuevo no hereda el click-to-move de la plantilla. Registrar el contexto una vez en BeginPlay, no en Tick.

Para cada acción digital: clic derecho en el grafo, buscar su evento Enhanced Input Action → conectar **Started** a `Print String` con el texto de la tabla. No usar Triggered para estas impresiones: mantener una tecla no debe generar ataques repetidos en el diagnóstico.

Para `IA_Move` y `IA_LookMouse`: conectar **Triggered** → leer Action Value como Vector2D → convertir a String → anteponer la etiqueta → `Print String`. Usar duración corta para poder leerlo. Para `IA_Move`, conectar también **Completed** y **Canceled** a `Print String("Move stopped")`.

Para `IA_Crouch`, conectar además Completed y Canceled a `Print String("Crouch released")`. No conectar todavía al componente de sigilo.

`IA_LookMouse` solo verifica que llega input del mouse. A-03 calculará la posición del cursor en el mundo; no usar estos deltas como si fueran una posición absoluta.

Compilar y guardar este Blueprint.

## 4. Preparar el mapa sin cambiar Project Settings

1. En `/Game/Unscripted/Player/Test/`, crear `BP_InputTestGameMode_A` con padre **GameModeBase**.
2. En Class Defaults, asignar Player Controller Class = `BP_InputTestController_A`. Default Pawn Class = **SpectatorPawn** para esta prueba de eventos; no valida movimiento del protagonista.
3. Crear un nivel vacío y guardarlo como `/Game/Unscripted/Maps/Test/L_Test_A`. Si ya existe, abrirlo sin reemplazarlo.
4. Añadir un PlayerStart. Opcionalmente añadir un suelo con un cubo del motor para tener una referencia visual.
5. En World Settings del mapa, GameMode Override = `BP_InputTestGameMode_A`.
6. Compilar, guardar y ejecutar Play. Hacer clic en el viewport para darle foco.

La entrada Escape puede estar reservada para detener PIE. Probarla mediante **Standalone Game** para verificar `Pause requested`, sin modificar atajos globales del equipo. Esta acción solo imprime; no pausa todavía.

## 5. Prueba y registro

- [ ] W, A, S y D imprimen los valores esperados; al soltar, aparece Move stopped.
- [ ] W+D entrega ambos ejes; W+S y A+D se cancelan.
- [ ] Mover el mouse produce Mouse input.
- [ ] Cada botón digital imprime una vez al pulsar; mantenerlo no repite el Started.
- [ ] Ctrl imprime Crouch al pulsar y Crouch released al soltar.
- [ ] Esc imprime Pause requested en Standalone.
- [ ] No aparece movimiento click-to-move procedente del controlador Top Down.
- [ ] No hay errores de compilación ni Accessed None durante Play.
- [ ] Todo mensaje mostrado está en inglés.
- [ ] Al salir y volver a Play, los eventos siguen funcionando sin duplicarse.

Si no llega input, revisar en este orden: foco del viewport, GameMode Override del mapa, Player Controller Class, contexto correcto y validez del subsystem. No modificar la plantilla para corregir esta prueba.

Registrar versión del editor, resultado y fallos en el apartado Estado del plan A. Solo marcar A-01 completado después de ejecutar estas pruebas. Después sigue A-02 (movimiento/cámara), con los contratos y cascarones de F0 listos para integrarse.

Referencias: `docs/02`, `docs/06`, plan A y [Enhanced Input de Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine). La documentación de Epic respalda el uso de acciones, contextos y modificadores; esta guía no ha sido ejecutada en UE 5.8.4.
