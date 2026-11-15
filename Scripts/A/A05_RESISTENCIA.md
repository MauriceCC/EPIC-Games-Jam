# A-05 — Resistencia en BP_CombatComponent

Implementado el 2026-11-15 sobre `be77859` (A-04). Responsable: Mauricio / División A.
Solo se guardaron assets de A. No se modificaron Core, enemigos, HUD/UI de C ni mapas compartidos.

**Criterio de aceptación (backlog):** sin resistencia no se puede atacar/esquivar; un HUD de prueba la muestra.
**Estado:** implementado, guardado y validado técnicamente (140 comprobaciones tras recarga).
Pendiente la aceptación visual de Mauricio en Play (`L_Test_A`).

> Nota de plan: `docs/plan/04_PLAN_DE_CIERRE.md §4` proponía recortar A-05. Se implementó por petición
> expresa de Mauricio. No cambia contratos ni consumidores: si se prefiere desactivarla, basta con poner
> los costes a 0 en la plantilla Combat del jugador.

## Assets modificados

| Asset | Cambio |
|---|---|
| `Player/BP_CombatComponent` | Variables de resistencia, 4 funciones, BeginPlay y Tick conectados. Dispatchers `OnStaminaChanged` y `OnCombatStateChanged` sin cambios |
| `Player/BP_PlayerCharacter` | `DoLightAttack`, `DoDodge` y `DoParry` consumen resistencia tras su guarda existente. Plantilla Combat instalada con los valores iniciales |
| `Player/Test/BP_StaminaHUDTest_A` (nuevo) | HUD de prueba: muestra `Stamina: X / Y` en pantalla mediante el dispatcher real |
| `Maps/Test/L_Test_A` | Una instancia `A_StaminaHUDTest` en (0, 0, 200). El mapa usa `BP_GameMode` → `BP_PlayerCharacter` |

## Valores (categoría *Stamina*, editables por instancia)

| Variable | Valor | Fuente |
|---|---:|---|
| `MaxStamina` | 100 | docs/03 |
| `StaminaRegenRate` | 30 /s | docs/03 |
| `StaminaRegenDelay` | 0,6 s | **[PROPUESTA]** «pausa breve» de docs/03 |
| `LightAttackStaminaCost` | 10 | docs/03 |
| `HeavyAttackStaminaCost` | 25 | docs/03 — declarado, sin uso hasta A-09 |
| `DodgeStaminaCost` | 20 | docs/03 |
| `ParryStaminaCost` | 10 | docs/03 |
| `CurrentStamina` | 100 | Solo lectura para consumidores; no escribir directamente |

Privadas: `A_RegenPauseRemaining` (pausa restante) y `bA_UpdatingStamina` (guarda de reentrada).
Cuando exista `DT_PlayerBalance` (A-12), estos valores se cargarán desde la tabla, sin tocar los nodos.

## Lógica nodo a nodo

En `/Game/Unscripted/Player/BP_CombatComponent`:

1. **A_CommitStamina(NewStamina, Maximum)**, privada: Branch NOT bA_UpdatingStamina → Set guarda=true → Set MaxStamina=Maximum → Set CurrentStamina=NewStamina → Call **OnStaminaChanged**(NewStamina, Maximum) → Set guarda=false.
2. **SetStamina(Value)**: Maximum = Max(MaxStamina, 0) → A_CommitStamina(Clamp(Value, 0, Maximum), Maximum). Uso previsto: BeginPlay, Retoma (A-15) y checkpoint (A-22).
3. **HasStamina(Cost) → bHasStamina**, pura: CurrentStamina >= Max(Cost, 0).
4. **TryConsumeStamina(Cost) → bConsumed**: Branch (NOT guarda AND HasStamina(Cost)).
   - Falso → Return false. No cambia nada ni emite aviso.
   - Verdadero y Cost > 0 → Set A_RegenPauseRemaining = StaminaRegenDelay → SetStamina(Current − Cost) → Return true.
   - Verdadero y Cost <= 0 → Return true, sin gasto, sin aviso y sin reiniciar la pausa.
5. **BeginPlay** → Set A_RegenPauseRemaining=0 → SetStamina(MaxStamina).
6. **Tick(DeltaSeconds)** → Branch A_RegenPauseRemaining > 0:
   - Verdadero → A_RegenPauseRemaining = Max(Remaining − Delta, 0).
   - Falso → Branch (CurrentStamina < Max(MaxStamina, 0) AND StaminaRegenRate > 0) → SetStamina(Current + Rate × Delta).

En `BP_PlayerCharacter`, en cada una de `DoLightAttack`, `DoDodge` y `DoParry` se insertó, entre la rama existente (`K2Node_IfThenElse_0.then`) y su primera acción (`K2Node_VariableSet_0`):

`TryConsumeStamina(Target = BP_CombatComponent, Cost = BP_CombatComponent.<Acción>StaminaCost)` → Branch(bConsumed) → acción original.

Primero se evalúa la guarda original (muerto/atacando), así un clic durante un ataque no gasta resistencia.

**[PROPUESTA implementada]**

- Para actuar hace falta el **coste completo**. Con 18 no se puede esquivar (20), pero sí atacar (10).
- Gastar reinicia la pausa de 0,6 s. Durante la pausa no se regenera; después, 30/s hasta el máximo.
- Igual que Health, cada escritura aceptada emite `OnStaminaChanged` con los valores ya acotados. No se emite mientras la resistencia está llena ni en una acción rechazada. Durante la regeneración se emite una vez por frame, que es lo que necesita una barra de HUD.
- Una llamada a SetStamina o TryConsumeStamina desde un callback de `OnStaminaChanged` se ignora; TryConsume devuelve false.
- El ataque fuerte (A-09) aún no existe: el clic derecho sigue llamando a `DoLightAttack` y cuesta 10.
- La Retoma todavía no guarda ni restaura resistencia; se hará en A-14/A-15 con `SetStamina`.
- Parry y esquiva siguen sin máquina de estados (A-06). Se pueden encadenar entre sí mientras haya resistencia.

## HUD de prueba

`BP_StaminaHUDTest_A` espera 0,2 s tras BeginPlay para que el GameMode posea al jugador. Después toma el `BP_CombatComponent` del Player Character 0, salvo que `ObservedCombat` ya esté asignado, se suscribe a `OnStaminaChanged` y muestra el valor actual. Imprime en pantalla `Stamina: 90 / 100`, en inglés, con la clave `A_StaminaHUDTest` para que la línea se actualice sin repetirse. `bPrintToScreen=false` lo silencia y `bAttemptReentry` solo sirve para la validación.

Es un doble de prueba de A: no se coloca en Whitechapel ni sustituye al `WBP_HUD` de C. Para C-21, C puede enlazar su barra a `OnStaminaChanged(Current, Max)` del `BP_CombatComponent` del jugador, o leer `CurrentStamina`/`MaxStamina` al inicializar, como hace con Health.

## Evidencia automática

- [Implementación](a05_implementation_result.json): compilación, dispatchers intactos y conservación del jugador. Todos los nodos, valores y enlaces previos se mantienen, salvo los 3 enlaces de ejecución desviados. Incluye el guardado de los cuatro paquetes.
- [Parche](patch_a05_regen_guard.py) ([resultado](a05_patch_result.json)): la validación encontró que, con tasa 0 o negativa, el Tick reemitía el aviso en cada frame. Se añadió `StaminaRegenRate > 0` a la rama de regeneración. Ya está aplicado; `implement_a05.py` refleja el grafo final.
- [Validación tras recarga](a05_validation_result.json): **140 comprobaciones correctas** en un proceso nuevo con el bytecode guardado. [Validador](validate_a05.py).

Casos cubiertos:

- Valores por defecto de clase y de la plantilla del jugador. Se conservan Health 100/100 (A-04) y la rotación de A-03.
- Sin errores ni warnings de nodo en los tres Blueprints.
- BeginPlay llena la resistencia; cada acción descuenta su coste.
- La pausa de 0,6 s bloquea la regeneración; después se recuperan 30/s con tope en el máximo.
- Se rechaza una acción sin el coste completo y también en 0. El rechazo no cambia el valor, no avisa y no reinicia la pausa.
- El coste exacto se acepta. Los costes 0 o negativos se tratan como acciones gratuitas.
- SetStamina acota por arriba y por abajo. La reentrada se bloquea. Las tasas negativas o 0 no drenan ni reemiten. Se admite un máximo personalizado.
- Dos componentes y dos observadores funcionan de forma independiente.
- En un `BP_PlayerCharacter` real del mundo del editor, `DoParry`, `DoDodge` y `DoLightAttack` activan su flag y gastan 10/20/10 si hay resistencia. Sin el coste completo o en 0, ni activan el flag ni gastan. Un segundo clic durante un ataque no gasta.

Límites: son llamadas reales a funciones guardadas en contexto de editor, **no una sesión de Play**. El log tiene 0 errores. Los 22 warnings son una advertencia de API obsoleta (`get_object`) y `Accessed None` de `PlayOneShot`/`FaceCursor`: fuera de PIE no hay malla animada inicializada ni PlayerController. Son esperables y ajenos a A-05.

Para repetir la validación, cerrar Unreal y ejecutar desde la raíz del repositorio en PowerShell:

```powershell
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' "$PWD/Unscripted/Unscripted.uproject" -run=pythonscript "-script=$PWD/Scripts/A/validate_a05.py" -unattended -nullrhi -nosound -NoSplash
```

`implement_a05.py` es una migración de una sola ejecución (rechaza un proyecto ya migrado). Necesita el editor completo mediante `run_a05_editor.py` y `-ExecutePythonScript`. `patch_a05_regen_guard.py` tampoco debe repetirse. Copias de seguridad previas: carpeta temporal indicada en `a05_implementation_result.json` → `backup`.

## Prueba visual paso a paso (Mauricio)

1. Con Unreal cerrado, revisar `git status`: solo deben aparecer los cuatro assets de arriba y `Scripts/A/`.
2. Abrir `Unscripted.uproject` y `Maps/Test/L_Test_A`. En el Outliner debe existir `A_StaminaHUDTest`.
3. Abrir `BP_CombatComponent` y compilar: 0 errores. Abrir `BP_PlayerCharacter`, seleccionar el componente `BP_CombatComponent` y comprobar la categoría *Stamina* (100, 30, 0,6, 10, 25, 20, 10).
4. Play. Arriba a la izquierda debe aparecer `Stamina: 100 / 100`.
5. Clic izquierdo una vez: `90 / 100`. Esperar: tras ~0,6 s sube hasta 100 en ~0,3 s.
6. Pulsar Espacio repetidamente: 80, 60, 40, 20, 0. Con menos de 20 la esquiva **no** sale: sin desplazamiento ni animación.
7. En 0, clic izquierdo y Q no hacen nada. Al dejar de pulsar, la resistencia vuelve tras la pausa.
8. Con ~15: Q (parry) sí sale (cuesta 10), Espacio no (cuesta 20).
9. Pulsar clic muy rápido durante un ataque: solo descuenta 10 por ataque realmente iniciado.
10. Probar F (Corte) y R (Retoma): no gastan resistencia y siguen funcionando como antes.
11. Detener Play y revisar Output Log. No usar *Save All* sobre paquetes de otras divisiones.

Si todo se cumple, A-05 queda aceptado. Siguiente en el backlog: A-06, la máquina `ECombatState` (que también publicará `OnCombatStateChanged`), o A-12 si se prefiere llevar ya estos valores a `DT_PlayerBalance`.
