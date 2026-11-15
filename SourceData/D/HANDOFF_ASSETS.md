# Entrega de assets de D para otras divisiones

> Dueño: División D. Fecha: 2026-11-14. Todos en `/Game/Unscripted/Art/Props/<nombre>/`, con colisión convexa y pivote en la base.
> Los valores de escala y rotación son **[PROPUESTA]** de punto de partida: ajústalos en el componente de tu Blueprint, no en el asset (no lo muevas ni lo renombres).

## Para C (Narrativa / interacción)

| Asset | Uso | Tamaño importado | Ajuste recomendado en el componente |
|---|---|---|---|
| `SM_Door_Wood_Frame` | Marco fijo de la puerta delantera y la lateral del Taller (`BP_Door`) | 1,30 × 0,18 × 1,40 m (achatado por la estimación de Meshy) | Escala ≈ **(1,7, 1,0, 2,2)** → hueco de ~2 × 3 m (`LEVEL_DESIGN §3`) |
| `SM_Door_Wood_Leaf` | Hoja que gira en `BP_Door` | 1,17 × 0,25 × 2,00 m | Escala ≈ **(0,85, 0,3, 1,45)** → ~1 × 0,08 × 2,9 m. Pivote de giro en el canto de las bisagras (≈ X −50 cm) |
| `SM_Door_Agency_Frame` | Marco de las puertas del Archivo y de la Sala de registros | 2,56 × 0,95 × 3,00 m | Ninguno |
| `SM_Door_Agency_Leaf` | Hoja (usar 2, la segunda en espejo con escala X −1) | 1,00 × 0,25 × 2,00 m | Escala ≈ **(1,0, 0,3, 1,25)** |
| `SM_Wardrobe_A` | Escondite interactivo (`BP_Hideout`) | 1,30 × 0,65 × 2,10 m | Ninguno |
| `SM_Ledger_Nursing` | Evidencia: registro de enfermería (`BP_Evidence`) | Sale **inclinado** (~30 cm de alto) | Girar para que quede plano sobre una mesa; probar Rotación X/Y ≈ 25–35° |
| `SM_Folder_Report` | Evidencia: informe fabricado (`BP_Evidence`) | Sale **inclinado** (~25 cm de alto) | Igual que el anterior |
| `SM_RecordStation_Official` / `_Authentic` | Estaciones del expediente final (`BP_FinalChoice`) | ~1,6 × 1,0 × 1,4 m, emisivo cian | Ninguno |

## Personajes (para A, B y C)

Todos en `/Game/Unscripted/Art/Characters/SK_<Nombre>/`: malla esquelética (~25k vértices, pivote en los pies, mirando a +X), `SK_<Nombre>_Skeleton`, `SK_<Nombre>_PhysicsAsset`, material `M_<Nombre>` (PBR 4K: base color, normal y rugosidad) y en `Anims/` tres bucles: `A_SK_<Nombre>_Idle` (4 s), `A_SK_<Nombre>_Walk` y `A_SK_<Nombre>_Run` (~1 s cada uno).

| Malla | Personaje | Altura | División que lo usa |
|---|---|---|---|
| `SK_Agent` | Agente (protagonista) | 1,80 m | A |
| `SK_Jack` | Jack | 1,72 m | B (escolta) / C |
| `SK_Pursuer_A`, `SK_Pursuer_B` | Perseguidores (civiles manipulados) | 1,80 / 1,76 m | B |
| `SK_Interventor` | Interventor de la agencia | 1,88 m | B |
| `SK_Supervisor` | Supervisor (jefe) | 1,95 m | B |
| `SK_Nurse`, `SK_FlowerSeller`, `SK_Vagrant` | NPCs de época (enfermera, vendedora de flores, vagabundo) | 1,65 / 1,60 / 1,68 m | C (ambiente y diálogo) |

Notas:

- El esqueleto es el de Meshy (25 huesos: `Hips`, `Spine`…`Head`, brazos, piernas y `LeftToeBase`/`RightToeBase`; **sin dedos ni huesos IK**). Es el mismo en los 9, pero cada uno tiene su propio asset de esqueleto.
- Para golpes, parry o muerte, **[PROPUESTA]**: crear un IK Rig de este esqueleto y otro de `SKM_Manny` y usar un IK Retargeter para pasar animaciones del maniquí de la plantilla. Alternativa: marcar los esqueletos como compatibles para compartir las animaciones de uno.
- En `BP_` del personaje: asignar la malla al `Mesh` del Character con Z ≈ −90 y Yaw −90 (Unreal mira a +X; comprobar en la vista previa), y un Blend Space 1D Idle/Walk/Run (velocidad 0 / ~150 / ~450) para la locomoción.
- Para los NPCs con diálogo (C), la conversación es **[PROPUESTA]** de C: D solo entrega la malla y las animaciones.
- Más animaciones (golpes, esquivar, sentado, etc.): Meshy tiene una biblioteca de presets (3 créditos por acción y personaje); pedírselas a D.

### Personajes ya asignados (2026-11-15)

- `BP_PlayerCharacter` → `SK_Agent`; `BP_Pursuer` → `SK_Pursuer_A`; `BP_Jack` → `SK_Jack`; `BP_Interventor` → `SK_Interventor`; `BP_Supervisor` → `SK_Supervisor`. Malla en Z = −88 y Yaw −90; modo de animación *Single Node*.
- Componente `Art/Characters/Shared/BP_LocomotionAnim`: reproduce Idle/Walk/Run según la velocidad (umbrales 15 y 320 cm/s). Para una acción puntual (golpe, muerte…) llamar `PlayOneShot(Anim)`: reproduce la animación una vez y vuelve a la locomoción.
- **[PROPUESTA] para B:** para el segundo Perseguidor con otro aspecto, cambiar en la instancia del nivel la malla a `SK_Pursuer_B` y las tres animaciones de su `LocomotionAnim` a las de `SK_Pursuer_B`.

## Jugador (A) — versión mínima jugable (2026-11-15, hecha desde D por acuerdo del equipo)

- `BP_PlayerController`: las acciones del contrato llaman al personaje (antes solo imprimían texto). WASD mover, clic izq. golpe, clic der. golpe fuerte (de momento = ligero), Espacio esquiva, Q parry, F Corte de Fotograma, R Retoma.
- `BP_PlayerCharacter`: cámara isométrica (brazo de 17 m, Pitch −55°, Yaw 45°, FOV 40), movimiento relativo a la cámara (340 cm/s, gira hacia donde camina), golpe hacia el cursor que alterna dos animaciones y hace 25 de daño nativo a los `BP_GuardBase` a ≤1,7 m delante, esquiva con impulso e invulnerabilidad 0,45 s, parry con ventana 0,25 s.
- `ReceiveCombatHit` (contrato): devuelve `Dodged` durante la esquiva, `Parried` en la ventana de parry si el golpe es parryable (chispas y sonido), y si no, aplica el daño y devuelve `Hit`.
- Salud en `BP_HealthComponent` (`MaxHealth` 100, `ApplyHealthDamage`, `SetHealth`, dispatchers del contrato). Al llegar a 0: animación de muerte, `ReportStoryEvent(PlayerDefeated)` y recarga del nivel a los 3 s **[PROPUESTA provisional]** hasta que C conecte los checkpoints.
- Corte de Fotograma: congela al enemigo más cercano a ≤15 m con `ApplyTemporalFreeze(1.2, 10)`, `NS_TemporalCut` y 10 s de recarga (`OnTemporalCutCooldown`).
- Retoma: guarda posición y salud cada 0,1 s (3 s); R devuelve al jugador a hace 3 s con su salud de entonces, `NS_RetakeTrail`, 2 cargas (`OnRetakeChargesChanged`, `OnRetakePerformed`). Los enemigos no se rebobinan.
- Pendiente de A: golpe fuerte propio, resistencia, combo con ventanas por notify, `DT_PlayerBalance`, remates.

## Nivel `L_Whitechapel` (2026-11-15)

- `_Geo`: blockout de las 11 zonas generado desde `SourceData/D/blockout_layout.json` (82 piezas con etiqueta `D_Blockout`) y 37 props de vestido (etiqueta `D_Dressing`). Origen (0,0) en la esquina suroeste; el nivel ocupa X −100…5500 y Y 100…5900 cm.
- `_Light`: 18 `BP_GasLamp`, luces cálidas en Taller y Refugio, cian en Archivo y Registros, niebla volumétrica y ambiente de lluvia y viento (etiqueta `D_Light`).
- Persistente: luna fría (0,8 lux), SkyLight 0,2, `PP_Whitechapel_Night` (exposición fija, viñeta, grano) y `NavMeshBoundsVolume` ampliado a todo el nivel.
- **Movido por integración (revisar B y C):** `PlayerStart` a (300, 1800) en la zona Start; los dos `BP_Pursuer` a (1200, 2200) y (1900, 1200) y `BP_PatrolRoute` a (1500, 2000), en la Plaza. Resto de posiciones sugeridas en `LEVEL_DESIGN.md §9`.
- Pendiente: **Build → Build Geometry** para eliminar el suelo BSP provisional que aún se ve en el centro.

## Para D (colocación en `_Geo` / `_Light`)

`SM_IronGate_A` (verja Plaza–Refugio, 3,4 × 2,5 m), `SM_Fountain_Square`, `SM_Cart_Overturned`, `SM_WorkshopTable_A`, `SM_ArchiveCabinet_A`, `SM_ArchivePillar_A`, barril, cajas, carretilla y `World/BP_GasLamp` (farol con luz).

Tanda P1 (vestir el nivel):

| Asset | Tamaño importado | Notas |
|---|---|---|
| `SM_Facade_Brick_A` | 4,8 × 1,1 × 7,0 m | Fachada de 2 plantas para los muros altos (lado norte/este, `LEVEL_DESIGN §4`) |
| `SM_Facade_Shopfront_A` | 5,1 × 1,2 × 7,0 m | Escaparate con rótulo en blanco |
| `SM_Facade_Corner_A` | 1,2 × 1,2 × 1,2 m | **Escala uniforme ≈ 5,8** al colocarla (→ ~7 m) |
| `SM_LowWall_Stone_A` | 3,1 × 0,7 × 1,0 m | Cobertura baja |
| `SM_Cot_A` | 1,4 × 2,4 × 1,1 m | Refugio (escondite de Jack) |
| `SM_Chair_A`, `SM_Shelf_A` | 0,5 × 0,4 × 0,9 m · 0,6 × 0,3 × 1,8 m | Taller y Refugio |
| `SM_DebrisPile_A` | 2,9 × 2,9 × 0,8 m | Callejón y Paso central |
| `SM_Drainpipe_A` | 0,6 × 0,8 × 3,0 m | Pegar a las fachadas; apilar 2 para 6 m |

## Audio y VFX disponibles

- Sonidos (`Audio/`): `SC_StaffHit`, `SC_ParrySuccess`, `SC_TemporalCut`, `SC_Retake`, `SC_ChecklistRewrite`, `SC_EvidencePickup`, `SC_Footstep_Cobble` (aleatorio), `SC_Rain_Loop`, `SC_Wind_Loop`.
- VFX (`VFX/`), todos de un solo disparo salvo la lluvia:
  - `NS_ParrySpark` (A): chispas blanco-doradas + pulso cian.
  - `NS_TemporalCut` (A/B): fragmentos cian flotando ~0,8 s; adjuntar al pecho del enemigo.
  - `NS_HitImpact` (A/B): polvo y astillas, sin sangre.
  - `NS_EnemyTelegraph` (B): destello rojo anaranjado para `OnTelegraphStarted`.
  - `NS_RetakeTrail` (A): posimagen cian + motas que suben; generarlo en la posición **antigua** del agente al hacer Retoma.
  - `NS_ContinuityGlitch` (C): destellos cian/magenta ~0,3 s junto al aviso de continuidad alterada.
  - `NS_FinalRegister` (C): pulso cian tipo sello + chispas al registrar el expediente; generarlo sobre la estación elegida.
  - `NS_Rain` (D): lluvia en bucle; adjuntar a la cámara o al jugador.
- Placeholder aún vacío: `MS_Ambience_Whitechapel` (para el ambiente se usan `SC_Rain_Loop` y `SC_Wind_Loop`).
