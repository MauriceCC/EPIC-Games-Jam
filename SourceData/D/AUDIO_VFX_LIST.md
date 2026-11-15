# Inventario de audio, VFX y atmósfera (T6)

> **Dueño:** División D. **Fecha:** 2026-11-14.
> **Fuentes:** `01_CONTRATOS §5` (eventos) y `§8` (placeholders), `docs/07` (audio y efectos), `ART_BIBLE.md` §7–8, `ASSET_SOURCING.md` §4.
> **Prioridades ajustadas al plazo de la jam (entrega el 15-nov):**
> - **P0** = sin esto el juego se entiende peor; entra sí o sí.
> - **P1** = si da tiempo.
> - **P2** = solo si sobra tiempo.
>
> "Quién lo dispara" es **[PROPUESTA]**: cada división decide en su Blueprint. D solo crea y rellena el asset.

## 1. Columnas

- **Asset:** ruta bajo `/Game/Unscripted/`. Los marcados con 🔒 son placeholders de contrato (§8): no se renombran.
- **Disparo:** evento del contrato o momento de animación que lo activa.
- **Origen:** `Sonniss` · `Freesound CC0` · `MetaSound` (síntesis propia) · `Niagara` (propio) · `Material` (propio) · `Motor`.
- **Estado:** ⬜ pendiente · 🟨 placeholder vacío · ✅ final.

## 2. Combate y poderes (los usan A y B)

| Asset | Tipo | Disparo | Quién | Origen | Prioridad | Estado |
|---|---|---|---|---|---|---|
| 🔒 `Audio/SC_StaffHit` | SFX | AnimNotify de impacto del bastón con resultado `Hit` | A | Sonniss (golpe seco de madera) | **P0** | ⬜ |
| `Audio/SC_Block` | SFX | `ReceiveHit` devuelve `Blocked` (rebote) | A | Sonniss (madera contra metal) | P1 | ⬜ (nuevo, pedir vía contrato si A lo quiere) |
| 🔒 `Audio/SC_ParrySuccess` | SFX | `ReceiveHit` devuelve `Parried` | A | Sonniss (metal) + capa MetaSound cian | **P0** | ⬜ |
| 🔒 `VFX/NS_ParrySpark` | VFX | Ídem | A | Niagara: chispa blanco-dorada + anillo cian, < 0,3 s | **P0** | ⬜ |
| 🔒 `VFX/NS_HitImpact` | VFX | Golpe recibido (jugador o enemigo) | A, B | Niagara: polvo y chispa, sin sangre | P1 | ⬜ |
| 🔒 `Audio/SC_TemporalCut` | SFX | Inicio de `ApplyTemporalFreeze` | A | MetaSound: pulso corto sintético | **P0** | ⬜ |
| 🔒 `VFX/NS_TemporalCut` | VFX | Ídem, sobre el enemigo objetivo | A | Niagara: fragmentos cian y líneas horizontales | **P0** | ⬜ |
| 🔒 `Materials/M_TemporalFrozen_Overlay` | Material | Mientras dura la congelación (overlay) | B | Material translúcido cian (`Tint`, `Opacity`) | **P0** | 🟨 al crear placeholders |
| 🔒 `Audio/SC_Retake` | SFX | `OnRetakePerformed` | A | MetaSound: barrido invertido + eco | **P0** | ⬜ |
| 🔒 `VFX/NS_RetakeTrail` | VFX | Ídem: estela desde la posición antigua | A | Niagara: posimágenes (ribbon o sprites del contorno) | P1 | ⬜ |
| 🔒 `Materials/PP_Retake` | Post-proceso | Ídem, < 0,5 s | A/D | Material PP (`Tint`, `Intensity`) | P1 | 🟨 al crear placeholders |
| `Audio/SC_EnemyTelegraph` | SFX | `OnTelegraphStarted(AttackType, Duration)` | B / D | Sonniss (inhalación o "whoosh" de preparación) | **P0** (aviso sonoro del ataque) | ⬜ (nuevo, D lo engancha al dispatcher) |
| `VFX/NS_EnemyTelegraph` | VFX | Ídem: destello rojo anaranjado `#E5482F` | B | Niagara | P1 | ⬜ (nuevo) |
| `Audio/SC_Dodge` | SFX | Inicio de la esquiva | A | Sonniss (roce de tela) | P2 | ⬜ |
| `Audio/SC_EnemyStunned` | SFX | `OnEnemyStateChanged(Stunned)` | B / D | Sonniss | P2 | ⬜ |
| `Audio/SC_Finisher` | SFX | Remate (`RequestFinisher`) | A | Sonniss (golpe fuerte y sordo) | P1 | ⬜ |
| 🔒 `Audio/SC_Footstep_Cobble` | SFX | AnimNotify de paso | A, B | Sonniss o Freesound CC0 (3–4 variaciones aleatorias) | P1 | ⬜ |

## 3. Narrativa e interfaz (los usa C)

| Asset | Tipo | Disparo | Quién | Origen | Prioridad | Estado |
|---|---|---|---|---|---|---|
| 🔒 `Audio/SC_ChecklistRewrite` | SFX | `OnChecklistUpdated` con la versión reescrita | C | Sonniss (máquina de escribir o sello) + glitch | **P0** (es el giro narrativo) | ⬜ |
| 🔒 `Audio/SC_EvidencePickup` | SFX | `ReportStoryEvent(EvidenceCollected)` | C | Sonniss (papel) | P1 | ⬜ |
| 🔒 `VFX/NS_ContinuityGlitch` | VFX | `ReportStoryEvent(ContinuityAltered)` | C | Niagara + aberración cian/magenta | P1 | ⬜ |
| 🔒 `VFX/NS_FinalRegister` | VFX | Registro del expediente (`FinalDocumentRegistered`) | C | Niagara: pulso cian tipo sello | **P0** (momento clave) | ⬜ |
| `Audio/SC_FinalRegister` | SFX | Ídem | C | Sello + pulso MetaSound | **P0** | ⬜ (nuevo) |
| `Audio/SC_Transmission` | SFX | `OnDialogueStarted` con hablante Director, Supervisor o FutureSelf | C | MetaSound: estática o filtro de radio | P2 | ⬜ |
| `Audio/SC_UI_Confirm` / `SC_UI_Back` | SFX | Menús y confirmación del final | C | Freesound CC0 | P2 | ⬜ |

## 4. Mundo y ambiente (los usa D)

| Asset | Tipo | Disparo | Quién | Origen | Prioridad | Estado |
|---|---|---|---|---|---|---|
| 🔒 `Audio/MS_Ambience_Whitechapel` | Ambiente (bucle) | `BeginPlay` en `L_Whitechapel_Light` | D | MetaSound que mezcla lluvia y viento | **P0** | ⬜ |
| `Audio/SW_Rain_Loop` | Onda | Dentro del MetaSound | D | Sonniss o Freesound CC0 | **P0** | ⬜ |
| `Audio/SW_Wind_Loop` | Onda | Ídem | D | Sonniss | P1 | ⬜ |
| `Audio/SW_Crowd_Distant` | Onda | Plaza y Paso central (Ambient Sound con atenuación) | D | Sonniss | P1 | ⬜ |
| `Audio/SC_GasLamp_Hiss` | SFX 3D | Junto a 2–3 faroles (atenuación ~6 m) | D | Freesound CC0 | P2 | ⬜ |
| `Audio/SC_Archive_Hum` | SFX 3D | Archivo | D | MetaSound: zumbido grave | P2 | ⬜ |
| Música por fase | Música | `OnStoryPhaseChanged`, `OnEndingTriggered` | D | WeLoveIndies (no comercial) o capas de ambiente | P2 | ⬜ |
| `VFX/NS_Rain` | VFX | Siempre; anclado a la cámara o al jugador (no a todo el mapa) | D | Niagara GPU, gotas finas y salpicaduras en el suelo | **P0** | ⬜ |
| Niebla | Motor | Exponential Height Fog + Volumetric Fog | D | Motor | **P0** | ⬜ |
| Faroles | Luces | Point Light ámbar `#F2B25C`, pocas con sombra | D | Motor + malla simple o Quaternius | **P0** | ⬜ |
| Post-proceso global | PP Volume | Persistente: exposición fija, bloom leve, tono frío | D | Motor | **P0** | ⬜ |
| `Materials/M_Decal_Puddle` | Decal | Charcos que reflejan los faroles | D | Material propio | P2 | ⬜ |

## 5. Cómo engancha D lo suyo sin tocar assets ajenos [PROPUESTA]

Para ambiente, música y respuestas a eventos (por ejemplo, la telegráfica sonora), D puede crear **su propio actor** `World/BP_AudioDirector` en `L_Whitechapel_Light` que:

1. En `BeginPlay`, obtiene el `BP_ObjectiveManager` mediante `GetObjectiveManager` (interfaz `BPI_StoryEvents` del GameState) y se enlaza a `OnStoryPhaseChanged` y `OnEndingTriggered` para cambiar ambiente o música.
2. Opcional: para cada `BP_GuardBase` del nivel se enlaza a `OnTelegraphStarted` y reproduce `SC_EnemyTelegraph` en la posición del enemigo.

Así D no abre ningún Blueprint de A, B o C. Los SFX ligados a animaciones (golpe, pasos, parry) los dispara A o B **referenciando** los assets de D.

## 6. Orden de trabajo sugerido (tras crear los placeholders)

1. **Atmósfera P0:** niebla, faroles, post-proceso global, `NS_Rain` y el ambiente de lluvia. Es lo que más cambia la percepción del juego.
2. **Feedback de combate P0:** `SC_StaffHit`, `SC_ParrySuccess`, `NS_ParrySpark`, `SC_EnemyTelegraph`.
3. **Poderes P0:** `SC_TemporalCut`, `NS_TemporalCut`, `SC_Retake`.
4. **Narrativa P0:** `SC_ChecklistRewrite`, `NS_FinalRegister`, `SC_FinalRegister`.
5. Todo lo P1 que quepa; lo P2 solo si sobra tiempo.

## 7. Assets nuevos que no están en el contrato

`SC_Block`, `SC_EnemyTelegraph`, `NS_EnemyTelegraph`, `SC_Dodge`, `SC_EnemyStunned`, `SC_Finisher`, `SC_FinalRegister`, `SC_Transmission`, `SC_UI_*` y los de ambiente.

- Son **de D** (carpetas `Audio/` y `VFX/`). Crearlos no cambia ningún contrato.
- Para que A, B o C los referencien, D los anuncia en el chat del equipo. Si alguien necesita uno que no está en esta lista, lo pide en "Solicitudes de contrato" de `D_MUNDO_ARTE_AUDIO_BUILD.md §8`.
