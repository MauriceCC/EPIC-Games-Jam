# Integración de props/HUD y main — 2026-11-15

Integración autorizada por Mauricio: combinar ambas ramas conservando sus avances,
incluida la reconciliación de los binarios desde Unreal. No cambia propiedad
permanente de carpetas ni firmas de Core. Motor usado: UE 5.8.4.

Bases: `main` en `d05b0eb` e `integration/propsP0-hudHideout` en `3c42490`.

## Resolución de assets

| Asset | Resolución |
|---|---|
| `Player/BP_PlayerCharacter` | Base de main; conserva locomoción/sigilo, daño, Retoma, muerte y `B_ResumePlayerAtCheckpoint`. Se añaden A-03 y las tres guardas de resistencia de A-05. Plantillas Health 100/100 y Combat con los valores documentados por A. |
| `Maps/L_Whitechapel_Story` | Base de C: escondite, tres puertas, mensaje futuro, dos evidencias y dos estaciones finales. Se conserva una sola instancia funcional por acceso. |
| `Narrative/BP_FinalChoice` | Versión de C con confirmación/cancelación y pantallas de desenlace, en lugar de la confirmación mediante dos documentos de main. Se conserva el requisito de derrota del Supervisor. |
| `Narrative/DT_HUDText` | Reimportado desde el CSV fusionado: objetivo final de main y las nuevas filas de prompts de C. |
| `Maps/L_Whitechapel_AI` | Conserva Jack, rutas, enemigos, encuentros y demás actores de main. Se retiran únicamente las tres puertas superpuestas a las de C. |

Los componentes Health/Combat de A, los avances de enemigos de B y la UI/progresión
de C se incorporan mediante el merge normal, además de las resoluciones anteriores.

## Puertas: adaptación de integración [PROPUESTA implementada]

`B_WorkshopEscapeDoor`, `B_ArchiveGate` y `B_RecordsDoor` estaban en los mismos
accesos que `C_SideDoor`, `C_ArchiveGate` y `C_RecordsDoor`. Abrir una dejaba el
collider de la otra bloqueando el paso. Se conservan las tres puertas de C, con
su presentación, movimiento de hojas y apertura persistente.

La instancia `C_ArchiveGate` usa la subclase existente
`Enemies/BP_ArchiveEncounterDoor`, que hereda de `Narrative/BP_Door`, configurada
con la malla, dimensiones y pose de C y `bB_RequiresSupervisor=false`. Así conserva
la condición de main: FinalChoice y derrota del Interventor. La consulta concreta
al enemigo sigue dentro de la jerarquía de B. La puerta de Registros mantiene
su condición de derrota del Supervisor a través del ObjectiveManager de C.

No se añaden interfaces, enums, firmas ni referencias duras entre actores de
distintos subniveles. `BP_GuardBase` todavía tiene `IsDefeated` local sin implementar
`BPI_Damageable`; esta integración reutiliza su adaptador existente, sin migrar
esa deuda de arquitectura durante el merge.

## Validación

El informe versionado `props_hud_merge_validation.json` contiene los resultados.
Los logs y snapshots detallados permanecen en `Unscripted/Saved/PropsHudMerge/`.

- 42 Blueprints de producción compilados sin errores ni advertencias del compilador.
- 59 comprobaciones de salud y 140 de resistencia mediante las suites existentes
  de A sobre el bytecode integrado. Estas suites crean actores transitorios fuera
  de Play; sus avisos por controlador/animación sin BeginPlay no equivalen a una
  prueba visual. Los componentes inicializados se prueban también en PIE.
- Comprobación de preservación de los grafos de main para movimiento, orientación,
  daño, muerte, Retoma, sigilo y restauración del jugador; inventario de actores
  de B conservado salvo las tres puertas duplicadas.
- Dos sesiones independientes de PIE, una por desenlace: salud/resistencia reales,
  gasto/bloqueo/regeneración, muerte y recuperación en checkpoint, apertura lateral,
  revelación, bloqueo del Archivo antes de derrotar al Interventor, desbloqueo tras
  derrotar a su actor real, evento de derrota del Supervisor real, puerta de
  Registros, confirmación/cancelación y registro único de cada final.

Las pruebas de PIE suministran eventos de Jack y evidencias mediante el fixture
existente de C para aislar la integración. Usan las funciones de interacción/HUD;
no simulan teclas nativas ni constituyen una partida manual completa. Se ejecutan
con `-nullrhi`, por lo que queda pendiente la revisión visual de HUD, animaciones
y recorrido natural con teclado/mouse. No se declara una build empaquetada validada.

## Reproducción

Con Unreal cerrado, ejecutar `validate_props_hud_merge.py` mediante
`UnrealEditor-Cmd.exe <proyecto> -run=pythonscript -script=<script> -unattended
-nullrhi -nosound`. Guarda informes en Saved; no guarda assets.

Para PIE, ejecutar `play_props_hud_merge.py` con `UnrealEditor.exe
<proyecto> -ExecutePythonScript=<script> -unattended -nullrhi -nosound`, una vez
con `UNSCRIPTED_ENDING_CASE=official` y otra con `authentic`. El script mantiene
activo el editor mientras corren las comprobaciones y lo cierra al terminar.

`combine_props_hud_assets.py` documenta la migración aplicada; es de una sola
ejecución sobre las bases indicadas y aborta si ya encuentra A-03. No ejecutarlo
de nuevo sobre el resultado integrado. `props_hud_merge_baseline.json` conserva
los hashes de los grafos de main y su inventario de actores para la validación.
