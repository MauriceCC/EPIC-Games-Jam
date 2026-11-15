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

Todos en `/Game/Unscripted/Art/Characters/SK_<Nombre>/`: malla esquelética (~25k vértices, pivote en los pies, mirando a +X), `SK_<Nombre>_Skeleton`, `SK_<Nombre>_PhysicsAsset`, material `M_<Nombre>` (PBR 4K: base color, normal y rugosidad) y en `Anims/` dos bucles: `A_SK_<Nombre>_Walk` y `A_SK_<Nombre>_Run` (~1 s cada uno).

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
- En `BP_` del personaje: asignar la malla al `Mesh` del Character con Z ≈ −90 y Yaw −90 (Unreal mira a +X; comprobar en la vista previa), y un Blend Space 1D Walk/Run para la locomoción.
- Para los NPCs con diálogo (C), la conversación es **[PROPUESTA]** de C: D solo entrega la malla y las animaciones.
- No hay animación de reposo (idle). Si hace falta, se puede pedir a Meshy (3 créditos por acción) o retargetear la del maniquí.

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
