# 04 — Plan de cierre: del estado actual a la entrega

> Fecha: 2026-11-15. Entrega de la jam: **15-nov 17:59 PST (20:59 en Lima)**. Rama de integración: `d/props-p0` (contiene `main`, la narrativa de C y el trabajo de D y A de esta noche). Este plan **no cambia** el diseño (`docs/01`–`docs/07`) ni los contratos (`01_CONTRATOS_Y_PROPIEDAD.md`): reordena el trabajo pendiente de `00_PLAN_GENERAL.md` y de los backlogs A–D según lo que ya existe.
>
> Complementa a `03_ESTADO_Y_SIGUIENTES_PASOS.md` (diagnóstico de Mauricio): aquel describe la evidencia; este fija **qué falta, quién y en qué orden**.

## 1. Plan original frente a la realidad

| Fase (`00_PLAN_GENERAL §6`) | Hito de salida previsto | Estado real | Qué falta para cerrarla |
|---|---|---|---|
| **F0 Esqueleto** | Los 4 abren `main` y ven sus cascarones | ✅ Hecho: enums, structs, interfaces, componentes, cascarones, `L_Whitechapel` + 4 subniveles, mapas de prueba. 39 Blueprints compilan sin errores en la rama integrada | Auditoría de firmas pendiente (C-F0-02/04: `RequestFinisher.Target`, precisión de `ApplyTemporalFreeze`). No bloquea el juego |
| **F1 Sistemas aislados** | Cada división demuestra su mínimo F1 | **A** ✅ mínimo hecho hoy (movimiento, cámara, golpe, esquiva, parry, salud, muerte, Corte, Retoma) — *falta probarlo con teclado*. **B** ✅ IA, patrulla, sigilo, combate, aturdimiento, congelación, Jack (reportado por B). **C** ✅ fases, interacción, puertas, evidencias, checkpoint, HUD, diálogo, checklist, documento (rama de Daniel). **D** ✅ 28 props, 9 personajes con Idle/Walk/Run, 8 VFX, 11 SFX, texturas, música (Mauricio) | Traer lo último de C a la rama y probar A con teclado |
| **F2 Vertical slice** | Aparece, recibe órdenes, pelea con 2 Perseguidores con combo/parry/Corte/Retoma, abre una puerta, HUD y checklist reaccionan, muere y reaparece | 🟡 Nivel construido (blockout, 37 props, luz nocturna, niebla, lluvia, sonido), jugador real con cámara isométrica, 2 Perseguidores en la Plaza | Transmisión inicial y checklist en pantalla, HUD enlazado, una puerta, checkpoint y respawn |
| **F3 Contenido** | Partida completa hasta Final A y Final B sin tocar el editor | 🔴 Casi nada colocado en el mapa | Jack y su ruta, encuentros de las 5 zonas, Interventor, Supervisor, puertas, evidencias, revelación, expedientes, finales |
| **F4 Pulido y entrega** | Build probada en otro PC; code freeze 3 h antes | 🔴 Sin empezar (CREDITS al día) | Build Development pronto, Shipping al final, página de la jam |

**Conclusión:** vamos con F1 hecho y F2 a medias en el tiempo en que el plan esperaba F3. Para llegar hay que **recortar alcance** (§4) y **montar la historia directamente en `L_Whitechapel`**, sin más trabajo en mapas de prueba.

## 2. Estado por backlog (solo P0)

✅ hecho · 🟡 parcial / sin probar · 🔴 pendiente · ✂️ recortado (ver §4)

| División | Hecho | Pendiente P0 |
|---|---|---|
| **A** (la cubre D desde el 15-nov) | A-01 ✅ · A-02 ✅ · A-03 ✅ (al atacar) · A-04 ✅ · A-10 🟡 · A-11 🟡 · A-13 🟡 · A-14/15 🟡 (sin validación de geometría) · A-18 🟡 (muerte → recarga) · A-23 ✅ | A-20 probar contra Perseguidores · A-22 respawn en checkpoint · A-16 bloquear Retoma tras el expediente · ✂️ A-05, A-06, A-07 (combo por notifies), A-09, A-12, A-17, A-21 |
| **B** | B-01–B-12, B-14 reportados ✅ · B-20 ✅ (2 Perseguidores en la Plaza, recolocados por D) | B-21 integrar con el jugador real · B-22 qué se reinicia en checkpoint · B-32 encuentros de todas las zonas · B-33 ruta real de Jack · B-30 Interventor · B-31 Supervisor · interfaces en `BP_GuardBase` y Jack |
| **C** | C-01–C-09 ✅ (rama de Daniel, con validaciones PIE) · `PlayerStart` recolocado por D | C-20 transmisión, primer checkpoint, puerta lateral · C-21 HUD con el jugador real · C-22 muerte y respawn · C-30 actos I–III · C-31 expedientes ×2 · C-32 pantallas de final |
| **D** | D-01 ✅ · D-02 ✅ · D-03 ✅ (volumen ampliado) · D-04 ✅ · D-23 ✅ · D-31 ✅ · D-32 ✅ · personajes en BPs ✅ | D-05/D-20 cámara y oclusión con el jugador real · D-30 arte final (fachadas, fondo de ciudad, detalle) · D-33 música · D-22 build Development · D-40 rendimiento · D-41 Shipping · D-42 página, capturas, vídeo |

## 3. Plan redefinido

Cuatro bloques. Cada uno termina con **una prueba en `L_Whitechapel` desde el mismo commit**, que hace el integrador (por ahora, D). Las horas son de Lima; si un bloque se retrasa, se recorta del siguiente, **no** del bloque 4.

### Bloque 0 — Sincronizar (ya, ~45 min)

| # | Quién | Tarea | Hecho cuando… |
|---|---|---|---|
| 0.1 | D | Traer `main` (música, `03_ESTADO`) y los 6 commits nuevos de C a `d/props-p0`; subir la rama | Compila sin errores y Play arranca |
| 0.2 | Mauricio | Fusionar `d/props-p0` en `main`; todos hacen `git pull` con Unreal cerrado | Los 4 abren el mismo commit |
| 0.3 | D | *Build → Build Geometry* en `L_Whitechapel` (quita el suelo BSP provisional) | La Plaza muestra el empedrado |
| 0.4 | D (A) | Probar el combate con teclado y corregir lo que falle (A-20) | WASD bien orientado; los golpes dañan; parry, F y R funcionan |

### Bloque 1 — Vertical slice = Acto I jugable (hasta ~12:00)

| # | Quién | Tarea | Hecho cuando… |
|---|---|---|---|
| 1.1 | C | C-20: transmisión inicial del Director + checklist inicial (en inglés), CP0 en Start, CP1 a la entrada del Callejón | Al empezar se ve la orden y el checklist |
| 1.2 | C | C-21: `WBP_HUD` enlazado a salud, cargas de Retoma y cooldown de Corte del jugador real | Las barras cambian al recibir golpes y usar F/R |
| 1.3 | B | B-21: los 2 Perseguidores de la Plaza contra el jugador real (parry, Corte, neutralización no letal) | Pelea completa sin el jugador de prueba de B |
| 1.4 | B | B-32 (Acto I): patrulla en el Callejón y en el Patio, en las posiciones de `LEVEL_DESIGN §9` | Se puede pasar en sigilo o peleando |
| 1.5 | B + C | B-14 + C-04: Jack en el Taller; E sobre Jack → `JackFound`; armario escondite en el rincón del Callejón | La fase pasa a `OpenEscapeRoute` |
| 1.6 | A + C | A-18/A-22 + C-22: morir → `PlayerDefeated` → reaparecer en el último checkpoint (sustituye la recarga provisional) | Morir no reinicia todo el nivel |
| 1.7 | D | D-20: revisar con el jugador real dónde los muros tapan la cámara; arreglar la luz del Archivo; música de exploración y combate (D-33) | Lista de puntos de oclusión resuelta o anotada |

**Prueba de salida (= hito F2):** desde Start hasta hablar con Jack, con órdenes en pantalla, pelea en la Plaza, sigilo en el Callejón, muerte y reaparición.

### Bloque 2 — Actos II y III (hasta ~17:00)

| # | Quién | Tarea | Hecho cuando… |
|---|---|---|---|
| 2.1 | C | Puerta lateral del Taller (`C_SideDoor`), verja del Archivo (`C_ArchiveGate`), puerta de Registros (`C_RecordsDoor`) con sus condiciones de fase | Las puertas se abren solo en su fase |
| 2.2 | B | B-32 (Acto II): hasta 3 Perseguidores en el Paso central · B-33: ruta de Jack Taller → Refugio | Jack llega al Refugio → `JackReachedRefuge` |
| 2.3 | B | B-30: Interventor en el Tramo al Refugio (y hostil con `Correction_Order`) | Encuentro jugable |
| 2.4 | C | C-30: mensaje del yo futuro en el Taller, 2 evidencias en el Refugio (posiciones de `LEVEL_DESIGN §9`), revelación del Supervisor, **reescritura del checklist**, aviso *CONTINUITY ALTERED* | La fase llega a `FinalChoice` |
| 2.5 | B | B-31: Supervisor en el Archivo; al vencerlo → `SupervisorDefeated` | Se abre la sala de Registros |
| 2.6 | C + A | C-31/C-32 + A-16: dos `BP_FinalChoice` (mallas de D) con confirmación; al registrar se desactiva la Retoma; pantallas Final A (periódico) y Final B (mensaje al próximo yo) | Los dos finales se pueden ver |
| 2.7 | D | D-30: fachadas victorianas en los muros altos, canalones, más detalle en Plaza y Paso central, fondo de ciudad oscuro fuera de los muros; NPCs de ambiente (Enfermera, Vendedora de flores, Vagabundo) | El mapa deja de parecer un laberinto de cajas |
| 2.8 | D | **D-22: primera build Development** en cuanto el Bloque 1 esté en `main`, sin esperar al final | El .exe arranca en otro PC |

**Prueba de salida (= hito F3, *feature freeze*):** dos partidas completas, una hasta cada final, sin tocar el editor. Desde aquí no entran mecánicas nuevas.

### Bloque 3 — Pulido y entrega (17:00–20:59)

| # | Quién | Tarea | Hecho cuando… |
|---|---|---|---|
| 3.1 | Todos | Solo bugs que bloqueen la partida; ajuste rápido de daño y salud | Ninguna partida se atasca |
| 3.2 | D | D-40: 60 fps en el PC más débil (sombras de faroles, niebla) | Medido |
| 3.3 | C + D | Revisión de idioma: **todo texto visible en inglés**; créditos en el juego o en la página | Sin español en pantalla |
| 3.4 | D | **Code freeze ~17:59 Lima** · D-41 build Shipping · prueba en PC limpio | Build final probada |
| 3.5 | D | D-42: capturas, GIF o vídeo corto, página de la jam con la lista de herramientas de IA usadas (de `CREDITS.md`) | Entrega enviada antes de las 20:59 |

## 4. Recortes de alcance [PROPUESTA — confirmar en el sync]

Para llegar a tiempo se aplazan (quedan en el backlog, fuera de la entrega):

| Recortado | Sustituto en la entrega |
|---|---|
| A-05 resistencia, A-06 tabla `ECombatState`, A-07 combo ×3 por notifies, A-09 golpe fuerte, A-12 `DT_PlayerBalance` | Combo de 2 golpes por temporizador; clic derecho = golpe ligero; valores en el Blueprint |
| A-15 validación de destino seguro de la Retoma | Se rebobina a una posición ya recorrida (por definición transitable) |
| A-17 agacharse, A-21 remate, A-24 ataque sigiloso | Sigilo por evitar la visión y esconderse en el armario |
| B-13 `DT_EnemyBalance` como DataTable, B-34 fase 2 del Supervisor | Valores por defecto de B |
| C-33 menú principal completo, C-34 subtítulos estilizados | Pantalla de título mínima o arranque directo |
| D-34 post-proceso de Retoma | `NS_RetakeTrail` + `SC_Retake` |

## 5. Decisiones abiertas que hay que cerrar ya

Tomar en el primer sync (propuesta entre corchetes):

1. ¿Morir con cargas de Retoma? **[Derrota directa → checkpoint; la Retoma solo se usa a mano antes de morir.]**
2. ¿Ser detectado en sigilo inicia combate o falla? **[Inicia combate.]**
3. ¿Qué se reinicia al reaparecer? **[Los enemigos neutralizados siguen neutralizados; los heridos recuperan salud; Jack vuelve a su último punto alcanzado.]**
4. ¿El Interventor es opcional u obligatorio? **[Obligatorio en el Tramo al Refugio (`docs/05`).]**
5. ¿Quién cierra A desde ahora? **[D, como hasta ahora; A-20/A-22 los prueba junto con B y C.]**

## 6. Reglas para estas horas

- Cada uno coloca actores **solo en su subnivel** (`_AI` B, `_Story` C, `_Geo`/`_Light` D) para no pisar binarios.
- Ventana de integración cada ~2 h: subir lo terminado, D fusiona y prueba 2 minutos en `L_Whitechapel`, Mauricio pasa a `main`.
- Nada de mecánicas nuevas después del Bloque 2.
- Posiciones de todo lo colocable: `SourceData/D/LEVEL_DESIGN.md §9` y `SourceData/D/HANDOFF_ASSETS.md`.
