# Créditos y licencias

> Dueño: División D. Registrar **cada** asset, pack, fuente o sonido externo al importarlo.

## Equipo

| Persona | División |
|---|---|
| | A · Agente |
| | B · Oposición |
| | C · Relato |
| | D · Mundo |

## Assets de terceros

| Asset / pack | Autor | Fuente (URL) | Licencia | Usado en |
|---|---|---|---|---|
| | | | | |

## Assets generados con IA

Imágenes de referencia generadas por el equipo (División D) con **ChatGPT (generación de imágenes de OpenAI)** usando los prompts de `SourceData/D/IMAGE_PROMPTS.md`, y convertidas a 3D con herramientas de IA. Al entregar, listar en *"Tools you used"*: **ChatGPT / OpenAI**, **Meshy**, **Hyper3D Rodin**, **fal (PATINA, ElevenLabs Sound Effects)**. Responder la pregunta opcional de OpenAI en la entrega.

| Asset (`/Game/Unscripted/Art/Props/…`) | Herramienta | Modelo / ajustes | Fecha | Licencia / notas |
|---|---|---|---|---|
| `SM_Barrel_A` | Meshy (plan Pro, perk de la jam) | Image to 3D, `meshy-t2` smart topology (~4k tris) + textura `meshy-n1` | 2026-11-14 | Plan de pago: licencia privada con uso comercial, sin atribución obligatoria (verificar en meshy.ai si cambia el plan) |
| `SM_CrateStack_A` | Meshy (plan Pro, perk de la jam) | Ídem (~3,9k tris) | 2026-11-14 | Ídem |
| `SM_Handcart_A` | Meshy (plan Pro, perk de la jam) | Ídem (~6k tris) | 2026-11-14 | Ídem |
| `SM_GasLamp_A` | Hyper3D Rodin (Business, perk de la jam) | Gen-2.5 Medium, imagen de referencia, ~8k tris, PBR | 2026-11-14 | Revisar los términos de Hyper3D antes de un uso comercial |
| `SM_RecordStation_Official` | Hyper3D Rodin (Business, perk de la jam) | Gen-2.5 Medium, ~20k tris, PBR | 2026-11-14 | Ídem |
| `SM_RecordStation_Authentic` | Hyper3D Rodin (Business, perk de la jam) | Gen-2.5 Medium, ~20k tris, PBR | 2026-11-14 | Ídem |
| `SM_Cart_Overturned`, `SM_WorkshopTable_A`, `SM_ArchiveCabinet_A` (P1) | Meshy (plan Pro, perk de la jam) | Image to 3D, `meshy-t2` smart topology (~4–6k tris) + textura `meshy-n1`; referencias de ChatGPT | 2026-11-14 | Plan de pago: licencia privada con uso comercial |
| `SM_Fountain_Square`, `SM_ArchivePillar_A` (P1) | Hyper3D Rodin (Business, perk de la jam) | Gen-2.5 Medium, ~10k tris, PBR (columna con emisivo); referencias de ChatGPT | 2026-11-14 | Revisar los términos de Hyper3D antes de un uso comercial |
| `SM_Wardrobe_A`, `SM_Ledger_Nursing`, `SM_Folder_Report`, `SM_IronGate_A`, `SM_Door_Wood_Leaf`, `SM_Door_Wood_Frame`, `SM_Door_Agency_Leaf`, `SM_Door_Agency_Frame` (P0 tanda 2) | Imagen: **GPT Image (`gpt-image-2`, OpenAI) vía Meshy**; 3D: Meshy `meshy-t2` + `meshy-n1` | Texto → imagen → 3D, ~2,5–6k tris | 2026-11-14 | Plan de pago de Meshy: licencia privada con uso comercial |
| `SM_Facade_Brick_A`, `SM_Facade_Shopfront_A`, `SM_Facade_Corner_A`, `SM_LowWall_Stone_A`, `SM_Cot_A`, `SM_Chair_A`, `SM_Shelf_A`, `SM_DebrisPile_A`, `SM_Drainpipe_A` (P1 tanda 2) | Imagen: **GPT Image (`gpt-image-2`, OpenAI) vía Meshy**; 3D: Meshy `meshy-t2` + `meshy-n1` | Texto → imagen → 3D, ~1,5–5k tris | 2026-11-14 | Plan de pago de Meshy: licencia privada con uso comercial |
| `Art/Characters/SK_Agent`, `SK_Jack`, `SK_Pursuer_A`, `SK_Pursuer_B`, `SK_Interventor`, `SK_Supervisor`, `SK_Nurse`, `SK_FlowerSeller`, `SK_Vagrant` (con `M_`, `T_` y animaciones `A_SK_*_Idle/Walk/Run`) | Imagen: **GPT Image (`gpt-image-2`, OpenAI) vía Meshy**; 3D: Meshy `meshy-t2.5` + textura `meshy-7` PBR 4K, después retexturizada con Meshy Retexture (`meshy-7`, PBR 4K, UV originales, la misma imagen de referencia como estilo); rig y animaciones de caminar/correr: Meshy Auto-Rigging; idle y combate del Agente (golpes, esquiva, parry, golpe recibido, muerte): Meshy Animation (presets) | Texto → imagen en T-pose → 3D (~25k tris) → rig | 2026-11-14 | Plan de pago de Meshy: licencia privada con uso comercial |
| `Audio/Music/SW_Music_Exploration`, `SW_Music_Combat`, `SW_Music_CombatAlt`, `SW_Music_Decision` (temas *The Watchmaker's Regret*, *Twelve Strokes of Iron*, *The Winding Hour*, *Beneath the Great Gears*) | Aportados por Mauricio (`SourceData/D/Audio/Music/`); los MP3 llevan manifiesto C2PA de contenido generado con IA — **herramienta pendiente de confirmar** | Convertidos de MP3 a WAV 44,1 kHz estéreo e importados en bucle | 2026-11-15 | Confirmar herramienta y licencia antes de la entrega |
| `Audio/Waves/SW_*` (11 efectos: lluvia, viento, golpe, parry, pasos ×3, Corte, Retoma, sello, papel) y sus `SC_` | fal, modelo `fal-ai/elevenlabs/sound-effects/v2` (créditos del perk de la jam) | Texto a efecto de sonido, WAV 44,1 kHz | 2026-11-14 | Revisar los términos de fal/ElevenLabs antes de un uso comercial |
| `Materials/Blockout/T_Cobble_Wet_*`, `T_Brick_Dirty_*`, `T_WoodPlanks_Old_*` (y sus `MI_`) | fal, modelo `fal-ai/patina/material` (créditos del perk de la jam) | Texto a material PBR repetible, 1024 px: base color, normal (OpenGL, verde invertido al importar) y roughness | 2026-11-14 | Revisar los términos de fal antes de un uso comercial |
