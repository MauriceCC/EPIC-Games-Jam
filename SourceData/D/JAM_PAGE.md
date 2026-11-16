# Página de la jam — borrador (D9)

> Dueño: División D. Todo lo que está dentro de los bloques **«PEGAR EN LA PÁGINA»** es texto para el jugador y va en **inglés**. Las notas en español son internas.
>
> Antes de publicar: ① confirmar los controles en la build final (marcados con ⚠️), ② confirmar con Mauricio la herramienta concreta de la música, ③ hacer las capturas de la lista de §4, ④ revisar que nada en las capturas tenga texto en español.

---

## 1. Título y frase corta — PEGAR EN LA PÁGINA

**Unscripted**

*History doesn't belong to those who lived it. It belongs to whoever decides how to tell it.*

Short tagline (≤ 140 characters, for cards/thumbnails):

> Whitechapel, 1888. You were sent to protect Jack. Then the script changed. Fight, rewind, and decide which record survives.

## 2. Descripción — PEGAR EN LA PÁGINA

> **Whitechapel, 1888.** You are an agent of the **Department of Continuity**, an agency that operates outside of time and edits what the world believes happened.
>
> Your orders arrive as a checklist from the **Director**: find a frightened man called **Jack**, keep him away from the mob hunting him through the fog, and make sure nobody learns who he is.
>
> But the evidence you find on the way doesn't match the official version. The agency was never trying to find the killer — only to make sure the story *had* one. And now your checklist has been rewritten.
>
> **Unscripted** is a short isometric action game with stealth and time manipulation. Fight with a combat baton, parry, dodge, and use your agency's temporal tech:
>
> - **Frame Cut** freezes a single enemy for a moment.
> - **Retake** rewinds *only you* a few seconds back — your position and health — while the rest of the world keeps going.
>
> The people chasing you aren't monsters: they're ordinary citizens stirred up by rumours, and you can take them down without killing them. Sneak past patrols or take them head-on — stealth is an option, never an obligation.
>
> In the end, the outcome isn't decided by winning a fight, but by **which file you register**: the Director's cut, or the truth.
>
> **Theme — *Director's Cut*:** the Director imposes his own interpretation of history, and the player decides whether that cut becomes the official record.

*Alternate-history fiction. The game makes no claim about the real identity of Jack the Ripper.*

## 3. Controles — PEGAR EN LA PÁGINA

Teclas leídas de `Player/Input/IMC_Default` (2026-11-15). ⚠️ = comprobar en la build final que funciona.

| Input | Action |
|---|---|
| **W A S D** | Move (camera-relative) |
| **Mouse** | Aim attacks |
| **Left click** | Attack (combo) |
| **Right click** | Heavy attack ⚠️ |
| **Space** | Dodge |
| **Q** | Parry / Counter-order |
| **F** | Frame Cut — freeze one enemy |
| **R** | Retake — rewind yourself a few seconds (2 charges per section) |
| **E** | Interact |
| **Left Ctrl** | Crouch ⚠️ |
| **Tab** | Checklist ⚠️ |
| **Esc** | Pause ⚠️ (if no pause menu: press twice to quit) |

Recommended: keyboard + mouse. Playtime: about 10–15 minutes.

## 4. Capturas (pendiente — hacer con la build o en PIE)

Formato: 1920×1080, PNG, sin HUD de depuración ni texto en español. Guardar en `SourceData/D/JamPage/` (crear carpeta) con estos nombres:

| Archivo | Qué mostrar |
|---|---|
| `01_plaza_fog.png` | **Portada.** Plaza de Whitechapel de noche con niebla, faroles y la fuente; el agente en primer plano |
| `02_combat_parry.png` | Pelea contra 2 Perseguidores, en el momento del parry o del golpe |
| `03_frame_cut.png` | Un enemigo congelado con `NS_FrameCut` visible |
| `04_retake_trail.png` | La estela de la Retoma (`NS_RetakeTrail`) |
| `05_stealth_alley.png` | Callejón en sigilo, patrulla a la vista |
| `06_checklist.png` | Checklist en pantalla (idealmente el rewrite *CONTINUITY ALTERED*) |
| `07_final_choice.png` | Las dos estaciones de expediente (`SM_RecordStation_Official` / `_Authentic`) |

Opcional: GIF de 10–15 s (parry → Frame Cut → Retake) para la cabecera.

## 5. Herramientas usadas / IA — PEGAR EN LA PÁGINA

Fuente: [`CREDITS.md`](../../CREDITS.md). Lista para el campo *"Tools you used"*:

> **Engine:** Unreal Engine 5.8 (Blueprints only).
>
> **AI tools used:**
> - **ChatGPT / OpenAI GPT Image** — concept and reference images for props, buildings and characters (also via Meshy).
> - **Meshy** — image-to-3D for props, building fronts and characters; auto-rigging and character animations; retexturing.
> - **Hyper3D Rodin** — image-to-3D for hero props (gas lamp, record stations, fountain, archive pillar).
> - **fal — PATINA** — tileable PBR materials (wet cobblestone, dirty brick, old wood).
> - **fal — ElevenLabs Sound Effects** — sound effects (rain, wind, hits, parry, footsteps, temporal powers, stamp, paper).
> - **Google generative AI** — music (4 tracks). ⚠️ confirmar el producto exacto con Mauricio (Lyria / Gemini / MusicFX)
> - **Claude (Anthropic) / Claude Code** — development assistance: planning, documentation, editor automation scripts.
>
> All AI-generated assets were reviewed, fixed and integrated by the team (scale, pivots, materials, level dressing).

Nota interna: responder también la pregunta opcional de OpenAI en el formulario de entrega (ver `CREDITS.md`).

## 6. Equipo — PEGAR EN LA PÁGINA

Cada persona confirma cómo quiere aparecer (ver `CREDITS.md §Equipo`).

| Name | Role |
|---|---|
| Mauricio | Player combat, temporal powers, animation & integration |
| Jesús | Enemies, AI, stealth & Jack |
| Daniel | Narrative, interaction & UI |
| Yizens | World, art, VFX, audio & build |

## 7. Datos técnicos — PEGAR EN LA PÁGINA

> - **Platform:** Windows 10/11, 64-bit.
> - **Download:** unzip and run `Unscripted.exe`. No installation needed.
> - **Requirements:** DirectX 12 compatible GPU; the game may ask to install the Visual C++ runtime / DirectX on first launch (included as `UEPrereqSetup` in the build). ⚠️ verificar con la prueba en otro PC (D2)
> - **Known issues:** _(rellenar tras D2)_
