# Placeholders compartidos (D-01)

> Dueño: División D. Fuente: `docs/plan/01_CONTRATOS_Y_PROPIEDAD.md §8`. Script: [`create_placeholders.py`](create_placeholders.py).

**Objetivo:** que existan los 16 assets con su **nombre y ruta definitivos**, para que A, B y C los referencien ya. D sustituye después su **contenido** (efecto real, sonido real) **sin moverlos ni renombrarlos**.

**No depende de F0:** solo usa carpetas de D (`VFX/`, `Audio/`, `Materials/`). Se puede hacer en cuanto tengas `main` actualizado.

## Lista y quién los usa

Las columnas "Lo usa" y "Cuándo" son **[PROPUESTA]** deducidas de los flujos del contrato. Cada división decide dónde los dispara.

| Asset (`/Game/Unscripted/…`) | Tipo | Lo usa | Cuándo (flujos de `01_CONTRATOS §5`) |
|---|---|---|---|
| `VFX/NS_TemporalCut` | Niagara System | A | Corte de Fotograma sobre el enemigo |
| `VFX/NS_RetakeTrail` | Niagara System | A | Estela de Retoma |
| `VFX/NS_ParrySpark` | Niagara System | A | Parry con éxito |
| `VFX/NS_HitImpact` | Niagara System | A, B | Golpe recibido |
| `VFX/NS_ContinuityGlitch` | Niagara System | C | Aviso de continuidad alterada |
| `VFX/NS_FinalRegister` | Niagara System | C | Registro del expediente final |
| `Audio/SC_StaffHit` | Sound Cue | A | Golpe de bastón |
| `Audio/SC_ParrySuccess` | Sound Cue | A | Parry con éxito |
| `Audio/SC_TemporalCut` | Sound Cue | A | Corte de Fotograma |
| `Audio/SC_Retake` | Sound Cue | A | Retoma |
| `Audio/SC_ChecklistRewrite` | Sound Cue | C | Checklist reescrito |
| `Audio/SC_EvidencePickup` | Sound Cue | C | Evidencia recogida |
| `Audio/SC_Footstep_Cobble` | Sound Cue | A, B | Pasos sobre adoquines (AnimNotify) |
| `Audio/MS_Ambience_Whitechapel` | MetaSound Source | D | Ambiente del nivel |
| `Materials/M_TemporalFrozen_Overlay` | Material | B | Overlay al congelar a un enemigo |
| `Materials/PP_Retake` | Material (post-proceso) | A, D | Post-proceso durante la Retoma |

## Opción A: con el script (requiere el Python Editor Script Plugin)

1. Unreal cerrado → `git pull` → abrir el proyecto.
2. **Tools → Execute Python Script…** → `Scripts/D/create_placeholders.py`.
3. En el **Output Log**, filtrar por `D_Placeholders`. Debe terminar con `16 creados, 0 ya existian, 0 fallos`. Si se ejecuta otra vez, no toca los existentes.
4. Abrir `M_TemporalFrozen_Overlay` y `PP_Retake` y comprobar que compilan sin errores (el script los compila).

El plugin **no** está activado hoy en `Unscripted.uproject`, y activarlo es tarea del integrador. Si todavía no está, usa la opción B.

## Opción B: a mano en el editor (~15 min)

En el Content Browser, crear las carpetas `Unscripted/VFX`, `Unscripted/Audio` y `Unscripted/Materials` si no existen. Escribir los nombres **exactamente** como en la tabla.

**Niagara (×6):** clic derecho → **FX → Niagara System** → *Create empty system* → nombre. No añadir emisores.

**Sound Cue (×7):** clic derecho → **Audio → Sound Cue** → nombre. Dejarlo vacío.

**MetaSound (×1):** clic derecho → **Audio → MetaSound Source** → `MS_Ambience_Whitechapel`. Dejarlo vacío.

**`M_TemporalFrozen_Overlay`:**
1. Clic derecho → **Material** → abrirlo.
2. En los detalles del material: **Blend Mode = Translucent**, **Shading Model = Unlit**.
3. Añadir un **Vector Parameter** llamado `Tint`, valor (R 0, G 0,8, B 1) → conectarlo a **Emissive Color**.
4. Añadir un **Scalar Parameter** llamado `Opacity`, valor 0,35 → conectarlo a **Opacity**.
5. Apply y Save.

**`PP_Retake`:**
1. Clic derecho → **Material** → abrirlo → **Material Domain = Post Process**.
2. Añadir un nodo **SceneTexture** con *Scene Texture Id = PostProcessInput0*.
3. Añadir un **Vector Parameter** `Tint` (0,6 / 0,95 / 1,1) y un **Scalar Parameter** `Intensity` (0,5).
4. Añadir un nodo **Multiply**: A = Color de SceneTexture, B = `Tint`.
5. Añadir un nodo **Lerp**: A = Color de SceneTexture, B = Multiply, Alpha = `Intensity` → conectarlo a **Emissive Color**.
6. Apply y Save.

## Después

1. `git status`: solo deben aparecer archivos en `Unscripted/Content/Unscripted/VFX/`, `Audio/` y `Materials/`.
2. Commit: `[D] D-01 Placeholders compartidos (01_CONTRATOS §8)`. Añadir solo esas rutas, nunca `git add .`.
3. Avisar al equipo:

   > Ya están en `main` los 16 placeholders de `01_CONTRATOS §8` (VFX, Audio, Materials). Referenciadlos por su ruta; están vacíos o son provisionales y yo cambiaré su contenido sin moverlos. El overlay de congelación tiene parámetros `Tint`/`Opacity` y `PP_Retake` tiene `Tint`/`Intensity`.

## Reglas

- **Nunca** mover ni renombrar estos assets: rompería las referencias de A, B y C.
- Para el efecto real, editar el **contenido** del mismo asset (emisores, nodos de sonido, nodos de material).
- Mantener los nombres de parámetros (`Tint`, `Opacity`, `Intensity`) o avisar a A y B si cambian, porque pueden usarlos desde Blueprint.
- Si alguien necesita otro placeholder, lo pide en "Solicitudes de contrato" de `D_MUNDO_ARTE_AUDIO_BUILD.md §8`.
