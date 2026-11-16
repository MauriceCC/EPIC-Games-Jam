# Pulido de animaciones A/B — 2026-11-15

Autorización del usuario: A y B para esta tarea. **[PROPUESTA]** Ajustes de presentación con clips existentes; no modifica contratos, mapas ni originales de D.

## Cambios

- `Player/Animation/Polish/`: seis copias de ataques, esquiva, parry, impacto y muerte. Entrada suavizada; recuperación hacia idle salvo muerte, que conserva la caída final.
- Golpes ligeros: contacto en 0,30 s en ambos clips, duración de 0,60 / 0,75 s. El segundo recorta su cola de recuperación original. Duraciones visuales y bloqueo coinciden.
- La selección del combo usa el booleano ya actualizado: evita reevaluar su negación tras escribirlo.
- La muerte limpia el temporizador visual anterior para que no libere la pose final.
- `Enemies/Animation/Polish/`: golpe adaptado a los cuatro esqueletos existentes. `BP_GuardBase` selecciona según la malla actual y reproduce al iniciar el aviso. Contacto al 60 % del clip; duración calculada como `B_WindupSeconds / 0.6`. Conserva alcance, daño, cooldown y avisos de parry.
- Corte detiene el temporizador de recuperación; al descongelar se cancela el golpe visual. Aturdimiento y caída cancelan también la reproducción pendiente.
- Locomoción de pie/agachada y pasos conservan el BlendSpace continuo existente. No se han creado animaciones adicionales para poderes temporales ni un ataque fuerte independiente.

## Aplicación reproducible

Con Play detenido, ejecutar en Python de Unreal, en orden:

1. `Scripts/A/a_polish_animation_assets.py`
2. `Scripts/B/b_install_attack_animation.py`
3. `Scripts/A/a_install_animation_polish.py`
4. `Scripts/A/a_validate_animation_polish.py`

No ejecutar simultáneamente con otro editor que tenga estos assets modificados. Los scripts solo guardan assets concretos propios; nunca usar Save All para esta operación.

## Validación

`animation_polish_validation.json`: recarga de assets, compilación estricta de cinco Blueprints, esqueletos, asignaciones y regreso de cadera/manos a idle.

`a_test_animation_runtime.py`: prueba temporal en PIE sobre `L_Test_B`, sin guardar el mapa; comprueba reproducción, retorno, interrupción y muerte. El resultado se escribe en `animation_runtime_validation.json`. Usa editor completo y se cierra al terminar.

Resultado: **48 comprobaciones de assets y 31 de PIE aprobadas**. Ejecutar la prueba con `-ExecCmds="py <ruta absoluta al script>"`; `-ExecutePythonScript` cierra el editor antes de completar los callbacks. La prueba usa NullRHI, por lo que no acredita calidad visual renderizada.

La comprobación automática no sustituye la valoración visual en cámara isométrica. Revisar movimiento→golpe→movimiento, combo alternado, parry, esquiva, impactos, muerte y congelación cerca del contacto. Los clips tienen entrada/salida horneada hacia idle; no hay todavía mezcla dinámica de combate por capas con locomoción.
