# Caídas de jugador y enemigos — 2026-11-15

Autorización puntual del usuario: integrador para A y B. **[PROPUESTA]** Pulido
de presentación sobre animaciones existentes. Los civiles conservan su
neutralización no letal. No se modifican contratos, originales de arte ni mapas.

> **Integración en `main` (2026-11-15):** solo se integraron los cinco clips,
> los scripts y esta documentación. Los cambios de `BP_GuardBase` y
> `BP_PlayerCharacter` de la rama `animations` **no** se integraron porque, con
> ellos, los enemigos dejaban de perseguir al jugador. Por eso, en `main`
> todavía no se cumplen los puntos de este documento que dependen de esos
> Blueprints (selección del clip en `B_PlayKnockoutFall`, retraso de 2,05 s de
> `PlayerDefeated`). Antes de volver a ejecutar `a_install_death_presentation.py`
> o `a_rebuild_death_presentation.py`, hay que averiguar por qué se rompía la
> persecución, y siempre coordinándolo con B (Jesús), dueño de `BP_GuardBase`.

## Cambios

- Cinco clips propios de 2 s a 60 Hz: agente, Perseguidor A, Perseguidor B,
  Interventor y Supervisor. Entrada de 0,18 s, caída articulada, asentamiento y
  último fotograma sostenido. Se respetan las proporciones de cada esqueleto.
- Se elimina el desplazamiento inicial importado de unos 127 cm de la cadera
  del agente. Se reduce el lanzamiento vertical original; una corrección de
  apoyo evita penetración de los puntos de control en suelo plano.
- Se reduce el lanzamiento de piernas y brazos. La orientación de los muslos
  mantiene los pies bajos durante la pérdida de apoyo, conservando las longitudes
  de los huesos y recuperando gradualmente la pose de reposo del clip.
- `BP_GuardBase.B_PlayKnockoutFall` elige el clip correspondiente a la malla.
  Sustituye la inclinación rígida de 87° en 0,32 s. El pequeño giro residual de
  stagger vuelve a su orientación base en 0,18 s durante la caída.
- La malla sigue evaluando animación. Se detiene CharacterMovement, se limpia
  el temporizador visual del ataque y se retira la congelación al quedar derrotado.
  La pose final queda sostenida, sin retorno accidental a locomoción.
- El jugador reproduce a velocidad normal incluso si muere durante otra acción.
  Las llamadas repetidas a `Die` no reinician la caída. `PlayerDefeated` se envía
  tras 2,05 s para permitir verla antes de que el checkpoint restaure al jugador.
  Restaurar anticipadamente cancela esa notificación y el reinicio pendiente.

## Archivos y aplicación

- `Player/Animation/Polish/A_Agent_Death`
- `Enemies/Animation/Polish/A_{Pursuer_A,Pursuer_B,Interventor,Supervisor}_Death`
- `Player/BP_PlayerCharacter` y `Enemies/BP_GuardBase`

Con Play detenido, ejecutar `Scripts/A/a_rebuild_death_presentation.py` en el
editor completo. Genera solo las cinco caídas y guarda los dos Blueprints.
El script termina cerrando el editor; usar una sesión dedicada sin cambios
pendientes. No ejecutar a la vez que otra sesión esté editando estos assets.

`a_polish_animation_assets.py` delega las caídas a este generador para que una
reconstrucción del pulido anterior no reintroduzca el desplazamiento importado.

## Verificación y límites

Resultado: **53 comprobaciones de assets y 69 comprobaciones de PIE aprobadas**
en Unreal Engine 5.8.4. Los cinco Blueprints compilan sin warnings de Blueprint.
Se revisaron también seis muestras renderizadas de los cinco modelos, desde la
entrada hasta el reposo. Esa revisión motivó la reducción del lanzamiento de piernas.

- `a_validate_death_presentation.py`: compilación estricta de cinco Blueprints,
  esqueletos, inicio de cadera, elevación, continuidad, apoyo y pose final.
  Informe: `death_asset_validation.json`.
- `a_test_death_runtime.py`: PIE sin guardar mapa; ambos Perseguidores,
  Interventor atacando, Supervisor congelado, enemigo aturdido, jugador durante
  parry, muerte repetida y restauración anticipada por checkpoint. Comprueba
  progresión de reproducción, caída real de los huesos y posición del actor.
  Informe: `death_runtime_validation.json`. Usar `-ExecCmds="py <ruta absoluta>"`,
  no `-ExecutePythonScript`, que termina antes de los callbacks de PIE.
- `a_preview_death_motion.py`: escena temporal con poses muestreadas de los cinco
  modelos; capturas en `Unscripted/Saved/DeathPreview/`. No guarda assets ni mapas.

Las caídas usan animación horneada y apoyo estimado sobre suelo plano, no ragdoll
ni adaptación a escaleras o pendientes. La entrada parte de la pose idle; no hay
mezcla dinámica desde cualquier pose de combate/agachado. La naturalidad en esos
casos y las intersecciones de ropa requieren revisión visual durante el juego.
