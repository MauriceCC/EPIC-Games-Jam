# A-04 — Salud reutilizable

Implementado el 2026-11-15 sobre `e95d5b9` (A-03 confirmado funcional por Mauricio). Solo se guardaron assets de A. No se modificaron Core, enemigos, HUD ni mapas compartidos.

## Qué se corrigió

- `Player/BP_HealthComponent`: el cálculo puro de daño se evaluaba nuevamente después de asignar CurrentHealth. El HUD podía recibir 50 cuando realmente quedaban 75 tras un golpe de 25, y OnDepleted podía dispararse antes de llegar a cero.
- `Player/BP_PlayerCharacter`: su plantilla instalada de Health tenía MaxHealth=0 y CurrentHealth=0 aunque la clase del componente tenía 100/100. Ahora la plantilla guarda 100/100, valores iniciales propuestos en docs/03.
- `Player/Test/BP_HealthObserver_A`: fixture para registrar los dispatchers reales y comprobar sus argumentos. Hereda Health para reutilizar las firmas al construir los callbacks, pero observa la instancia externa indicada en ObservedHealth. No se instala en el jugador.

Se conservaron las firmas existentes de ApplyHealthDamage, SetHealth, OnHealthChanged y OnDepleted, y todos los grafos de PlayerCharacter, incluido A-03.

## Lógica nodo a nodo

En `/Game/Unscripted/Player/BP_HealthComponent`:

1. **BeginPlay** → Get MaxHealth → **SetHealth**. Inicializa salud al máximo y publica el estado.
2. **SetHealth(Value)** calcula Maximum = Max(MaxHealth, 0), NewHealth = Clamp(Value, 0, Maximum). Invoca la función privada **A_CommitHealth** con PreviousHealth=CurrentHealth y esos dos valores.
3. **ApplyHealthDamage(Amount)** calcula Maximum del mismo modo y NewHealth = Clamp(CurrentHealth - Max(Amount, 0), 0, Maximum). Invoca la misma función privada.
4. **A_CommitHealth(PreviousHealth, NewHealth, Maximum)** recibe valores capturados antes de cambiar las propiedades: Branch NOT bA_UpdatingHealth → Set bA_UpdatingHealth=true → Set MaxHealth=Maximum → Set CurrentHealth=NewHealth → Call OnHealthChanged(Current=NewHealth, Max=Maximum).
5. Branch `(PreviousHealth > 0) AND (NewHealth <= 0)` → si verdadero, Call OnDepleted. Ambas salidas terminan con Set bA_UpdatingHealth=false.

**[PROPUESTA implementada]** Daño negativo no cura; para restaurar salud se usa SetHealth. Un máximo negativo se normaliza a cero. Cada actualización explícita aceptada publica OnHealthChanged, incluso si no cambia la cifra. OnDepleted solo se publica al pasar de positivo a cero, también mediante SetHealth; después de restaurar salud positiva puede volver a emitirse. Una llamada anidada a SetHealth/ApplyHealthDamage durante una notificación se ignora para evitar recursión y valores contradictorios entre suscriptores; si un consumidor necesita reaccionar modificando salud, debe hacerlo después de terminar la notificación. No implementar curaciones síncronas dentro de esos callbacks.

MaxHealth se configura antes de BeginPlay. Para cambiarlo en ejecución, actualizarlo y llamar SetHealth para normalizar/publicar el estado. No escribir CurrentHealth directamente desde consumidores.

## Evidencia automática

- [Informe de implementación](a04_implementation_result.json): compilación, firmas públicas y dispatchers preservados, grafos del jugador intactos, guardado de los tres paquetes.
- [Informe tras recarga](a04_validation_result.json): ejecución del bytecode guardado en un proceso nuevo; 59 comprobaciones correctas.
- [Validador](validate_a04.py): crea dos actores dummy transitorios con instancias independientes de Health y dos observadores reales. Ejecuta BeginPlay, daño, restauración y límites; no guarda mapas ni usa enemigos de B.

Casos: 100−25 comunica 75; 25−15 deja 10 sin agotar; sobre-daño limita a cero; golpes repetidos en cero no repiten OnDepleted; restauración por encima del máximo y por debajo de cero; daño negativo/cero; segunda transición a cero tras curación; reentrada desde un callback; máximo 250, cero y negativo; segundo actor independiente y BeginPlay con máximo 45. También verifica la plantilla instalada 100/100 y la rotación de A-03 deshabilitada hacia WASD.

Las pruebas ejecutan eventos y funciones reales en contexto de editor, **no una sesión de combate en Play**. El log final de validación tiene cero errores y una advertencia de API de editor obsoleta (`get_object`), sin fallo de comprobaciones. El lanzamiento completo del editor también registra problemas preexistentes de arte/plataformas ajenos a A; no se declara limpio el proyecto completo.

Para repetir solo la validación, cerrar Unreal y ejecutar desde la raíz en PowerShell:

```powershell
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' "$PWD/Unscripted/Unscripted.uproject" -run=pythonscript "-script=$PWD/Scripts/A/validate_a04.py" -unattended -nullrhi -nosound -NoSplash
```

`implement_a04.py` es una migración de una sola ejecución: rechaza un proyecto ya migrado. Necesita editor completo mediante `run_a04_editor.py` y `-ExecutePythonScript`, porque Unreal deshabilita el registro de acciones de Blueprint en commandlets. No volver a ejecutarla para probar. `configure_a04_observer.py` registra el ajuste de los dos campos editables del fixture; ya está aplicado e incorporado al constructor.

## Comprobación visual paso a paso

1. Abrir Unreal y `L_Test_A`. Abrir BP_PlayerCharacter, seleccionar Health y comprobar MaxHealth=100 y CurrentHealth=100 en sus valores predeterminados.
2. Abrir BP_HealthComponent, compilar y comprobar que no hay errores. En Play, elegir la instancia Health del jugador en **Debug Object** y observar CurrentHealth y MaxHealth: deben iniciar en 100.
3. Para una prueba visual aislada, crear un Actor Blueprint propio en `Player/Test/BP_HealthDummy_A`, añadir BP_HealthComponent y configurar MaxHealth=100. Colocarlo únicamente en `L_Test_A`.
4. En su EventGraph: BeginPlay → Bind Event to OnHealthChanged (Target=Health) → Bind Event to OnDepleted (Target=Health) → Delay 1 s → ApplyHealthDamage(25, Target=Health). Los callbacks imprimen, respectivamente, `Health: {Current}/{Max}` mediante Format Text y `Health depleted`. El primer daño debe mostrar 75/100.
5. Después del daño: Delay 1 s → ApplyHealthDamage(100) → Delay 1 s → ApplyHealthDamage(10). Debe aparecer 0/100 dos veces, pero `Health depleted` solo una vez. Añadir después SetHealth(100) y ApplyHealthDamage(100): entonces se admite una segunda notificación de agotamiento.
6. Probar el HUD existente en Play con el jugador: debe empezar en 100/100 y reflejar el mismo CurrentHealth después de recibir daño. No usar esta comprobación para dar por terminado respawn o Retoma.

Los actores transitorios automáticos ya cubren el criterio técnico de reutilización en dummies; el Blueprint visual del paso 3 es opcional y no fue creado ni colocado por esta migración. Falta la aceptación visual de Mauricio del HUD/juego.

## Siguiente paso

A-05: revisar resistencia, costes y regeneración en BP_CombatComponent. Muerte/Retoma y checkpoint siguen siendo A-18/A-22: esta entrega no corrige el evento narrativo equivocado de Die ni decide qué ocurre al llegar a cero con cargas de Retoma. El handoff de C sobre salud cero y notificaciones incorrectas queda atendido por A-04; su adaptación del HUD puede seguir leyendo el valor canónico.
