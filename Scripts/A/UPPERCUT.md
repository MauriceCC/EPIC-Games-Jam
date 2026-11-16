# Golpe fuerte — Surprise Uppercut

Integración de división A, 2026-11-16. Animación elegida por Mauricio.
Los ajustes de tiempos, alcance, daño y recuperación son **[PROPUESTA]**.

## Resultado

- Clic derecho (`IA_HeavyAttack`, evento Started) llama a `DoHeavyAttack`.
- Animación: `/Game/Unscripted/Player/Animation/Uppercut/A_Agent_HeavyUppercut`.
- Clip adaptado al esqueleto actual del agente, conservando longitudes de huesos.
  Sin desplazamiento de raíz; entrada de 0,12 s y vuelta a idle de 0,22 s.
- Duración y bloqueo: 32 fotogramas a 30 FPS, aproximadamente 1,067 s.
  Impacto a 14/30 s, aproximadamente 0,467 s, durante el ascenso del puño.
- Coste: `HeavyAttackStaminaCost` existente del Combat, actualmente 25.
  Sin el coste completo, no se inicia; pulsar de nuevo durante el golpe no gasta más.
- Daño: 28; alcance 190 cm; arco frontal de 120 grados; comprobación Visibility
  contra paredes; un impacto como máximo por objetivo y ataque.
- Cancelación al recibir daño, esquivar, hacer parry, iniciar muerte, restaurar
  checkpoint, efectuar Retoma o bloquear entradas. Se limpian los temporizadores
  pendientes para impedir golpes tardíos y recuperaciones que corten otra acción.
- Se usan los efectos de impacto y sonido existentes, sin guardar sus assets.

Solo se guardan `Player/BP_PlayerCharacter`, `Player/BP_PlayerController` y el clip
nuevo. Los grafos del ataque ligero, movimiento, orientación, Corte y contratos
permanecen conservados. Retoma, daño y checkpoint reciben únicamente el enlace de
cancelación; también se enlaza en las acciones de esquiva y parry ya existentes.

## Compatibilidad del combate actual

La inspección del asset guardado confirmó que `BP_GuardBase` tiene la función
`B_ReceiveCombatHit`, pero **no implementa todavía `BPI_Damageable`**. Por ello el
fuerte conserva la selección de enemigos del `AttackHit` actual y usa `ApplyDamage`
para esos enemigos, igual que el ligero. Si un objetivo de esa selección implementa
la interfaz, se usa `ReceiveCombatHit`, con tipo Heavy, daño 28, postura 30 y
`bNonLethal=true`, en lugar del daño nativo; nunca se ejecutan ambas vías.

En la vía provisional de enemigos no se aplica el campo de postura de la interfaz.
Este cambio no acredita ruptura de bloqueo ni cierra A-09 completo. La conexión de
la interfaz pertenece a B/integración; no se han modificado sus assets ni Core.

La reproducción usa el `PlayOneShot` existente y temporizadores sincronizados con
el clip, como el resto de acciones actuales. No sustituye la arquitectura completa
de montages/notifies prevista para combate.

## Fuente y reproducción

El FBX original del usuario se conserva y tiene una copia en
`SourceData/A/Uppercut/SurpriseUppercut.fbx`. Su hash se guarda en los datos de
muestreo y en el informe de horneado. No se han inventado condiciones de licencia;
D puede consultar esta fuente al preparar los créditos.

1. `a_sample_uppercut.py`: lector específico del FBX binario con biblioteca estándar
   de Python; muestrea curvas horneadas a 30 FPS y comprueba las convenciones
   admitidas. No necesita paquetes adicionales.
2. En Python de Unreal, con Play detenido: ejecutar `a_build_uppercut.py`.
   Adapta las rotaciones mediante las poses de referencia, alinea los ejes
   anatómicos, conserva las proporciones del agente y hornea entrada/recuperación.
3. En el editor completo: ejecutar `a_install_uppercut.py`. Guarda solo los dos
   Blueprints de A y cierra esa sesión al terminar. No usar Save All.

Para reconstruir el clip se utiliza el script de horneado; no reimportar la copia
del idle que sirve de plantilla ni asignar el FBX Mixamo directamente al esqueleto
compartido. Las jerarquías originales son diferentes.

## Validación

`a_test_uppercut.py` abre PIE en `L_Test_A` con actores de prueba temporales; no
guarda el mapa ni assets de enemigos. Ejecutarlo en el editor completo con
`-ExecCmds="py <ruta absoluta>/Scripts/A/a_test_uppercut.py"` y `-nullrhi`.
`a_verify_uppercut_editor.py` aplica primero la integración y después esa prueba.

**Resultado observado: 116 comprobaciones aprobadas.** La prueba comprueba
compilación estricta de los dos Blueprints, esqueleto,
duración, recuperación, resistencia, golpe único, alcance frontal, pared y
cancelación ante interrupciones. Resultado: `uppercut_validation.json`.
La validación con NullRHI no acredita calidad visual renderizada.

En Play con imagen, revisar clic derecho en reposo y movimiento, transición desde
ligero, ascenso del puño, contacto a distancia corta y regreso al movimiento.
La aceptación visual en cámara isométrica sigue pendiente de la revisión humana.
