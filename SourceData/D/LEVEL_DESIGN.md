# Diseño de nivel — Whitechapel 1888 (blockout v1)

> **Dueño:** División D. **Estado:** borrador para revisar con B y C. **Fecha:** 2026-11-14.
> **Fuentes:** `docs/05` (estructura, encuentros), `docs/02` (cámara, sigilo, Jack), `docs/07` (alcance, dirección visual), `docs/plan/01_CONTRATOS §6` (subniveles).
> Todo número, coordenada o nombre que no esté en `docs/` es **[PROPUESTA]**. Los puntos reservados para B y C son **sugerencias de espacio**: cada división decide qué coloca y dónde, en su subnivel.
> Este documento es la fuente del futuro `blockout_layout.json` (T2). Si los dos difieren, manda este documento hasta que el JSON se valide en el editor.

## 1. Resumen

- Un solo nivel, lineal con algo de vuelta atrás. Tiene **10 espacios jugables**: las 7 zonas de `docs/05` más 3 tramos de conexión.
- **Huella [PROPUESTA]: 60 × 54 m** en lugar de los 60 × 40 m preliminares de `docs/05`. **Motivo:** el recorrido tiene 4 franjas en profundidad (inicio, plaza/callejón, paso central/taller y archivo) y en 40 m no caben arenas de combate de ≥ 12 m sin pegarlas. `docs/05` indica que la escala no es definitiva.
- Recorrido: **Inicio → Plaza → Callejón → Patio del taller → Taller → (puerta lateral) → Paso central → Tramo al refugio → Refugio → Paso central → Archivo**.
- La progresión se bloquea con **puertas de C** (`BP_Door`), así que no hay atajos que rompan la secuencia narrativa.

## 2. Sistema de coordenadas

| Concepto | Valor |
|---|---|
| Unidades de este documento | Metros. Unreal usa cm: multiplicar por 100 |
| Origen | Esquina inferior izquierda del plano = `(0, 0, 0)` en Unreal **[PROPUESTA]** (se puede recentrar más adelante moviendo todo el subnivel) |
| `u` (horizontal en el plano, "este") | Eje **Y** de Unreal |
| `v` (vertical en el plano, "norte") | Eje **X** de Unreal |
| Suelo | Todo plano a Z = 0 en v1 (sin escaleras ni desniveles: menos riesgo para NavMesh y cámara) |
| Rejilla | Bloques en múltiplos de 1 m; snap del editor a 50 cm |

Ejemplo: el punto `(u=18, v=3)` del plano es `Location = (X=300, Y=1800, Z=0)` en Unreal.

## 3. Métricas [PROPUESTA]

| Métrica | Valor | Por qué |
|---|---|---|
| Cápsula del personaje (referencia) | radio ~0,4 m, alto ~1,9 m | Maniquí de la plantilla; confirmar con A/B |
| Ancho mínimo de paso caminable | **3 m** | Pasan jugador y enemigo y se puede esquivar lateralmente |
| Ancho de callejón de sigilo | **4 m** | Estrecho para sentir tensión, pero sin atascar la NavMesh |
| Arena de combate (2–3 enemigos) | **≥ 12 × 12 m** de suelo libre | `docs/02`: espacio para esquivar y reposicionarse; con 3 en pantalla no deben atacar todos a la vez |
| Arena del jefe | **≥ 20 × 12 m** | Supervisor con ataques de barrido (`docs/03`) |
| Puertas | **2 m de ancho × 3 m de alto** | Una cápsula pasa con margen; Jack la cruza sin rozar |
| Cobertura alta | **≥ 2 m** (cajas apiladas, carros, columnas) | Bloquea la visión a un jugador de pie |
| Cobertura baja | **1,2 m** (muretes, barriles) | Solo oculta al jugador agachado. **Coordinar con B** a qué altura apunta la traza de visión |
| Muros exteriores, lado de cámara (sur y oeste de cada espacio) | **3 m** | Ver §4: evitan tapar al jugador |
| Muros exteriores, lado opuesto (norte y este) | **8–10 m** | Dan la sensación de ciudad victoriana sin estorbar a la cámara |
| Distancia entre checkpoints | ≤ 60 s de juego | `docs/02`: evitar reinicios largos |

## 4. Cámara y altura de muros

Referencia de `docs/02`: cámara fija con **Pitch −55° y Yaw 45°**. La cámara es de A; esta sección solo saca consecuencias para la geometría.

- Con Yaw 45° la cámara queda al **suroeste** del jugador (−X −Y en Unreal) y mira hacia el noreste. **[PROPUESTA]** Queda pendiente confirmar el signo del yaw en la prueba de cámara D-05.
- Con 55° de inclinación, un muro tapa el centro del jugador cuando su altura supera ~`1 m + 1,4 × distancia`, medida hacia la cámara. Ejemplos: a 4 m de distancia (callejón) el límite es ~6,7 m; con el jugador pegado al muro, cualquier muro de más de 1 m lo tapa.
- **Regla del blockout:**
  - Los muros del **lado sur y oeste** de cada espacio caminable miden **3 m**: son "muros recortados", como en una maqueta.
  - Los del **lado norte y este** miden **8–10 m**.
  - Lo que siga tapando al jugador lo resuelve la oclusión de D-20 en F2, no subiendo o bajando muros a mano.
- **Proyección (D0.7):** se recomienda perspectiva con FOV bajo. Si se elige ortográfica, la regla de muros no cambia.

## 5. Plano

Escala: **1 carácter = 2 m**. 30 columnas = 60 m de ancho (`u`) y 27 filas = 54 m de profundidad (`v`). El norte (`v` creciente) queda arriba.

```text
 v=54 ┌──────────────────────────────┐
      |############EEEEEE############|  E  = Sala de registros (estaciones 1 y 2)
      |############E1EEE2############|  1/2 = Expediente oficial / auténtico
 v=48 |############EEDDEE############|  D  = Puerta de C (BP_Door)
      |#########SSSSSSSSSSSS#########|  S  = Archivo, arena del Supervisor
      |#########SSSSSSSSSSSS#########|
      |#########SSSSSSSSSSSS#########|
      |#########SSSSSSBSSSSS#########|  B  = Supervisor (sugerencia)
      |#########SSSSSSSSSSSS#########|
 v=36 |#########SSSSSSSSDDSS#########|
      |#RRRRRR######XXXXXXXXXX#######|  R  = Refugio      X = Paso central
      |#RRRRRR######XXXXX*XXXXTTTTTT#|  *  = Checkpoint (sugerencia)
      |#RRRRRRttttttXXXXXXXXXXTTTTTT#|  t  = Tramo al refugio
      |#RRR*RRttttttXXXXXXXXXXTTTTJT#|  T  = Taller de Jack   J = Jack
      |#RRRRRRttttttXXXXXXXXXXDTT*TT#|  D (u=46) = Puerta lateral
      |#RRRRRRttttttXXXXXXXXXXTTTTTT#|
 v=22 |#RRRGGR######XXXXXXXXXXTTDDTT#|  G  = Verja cerrada (estática, D)
      |###PPPPPPPPPP##########AAAAAA#|  P  = Plaza        A = Patio del taller
      |###PPPPPPPPPP##########AAAAAA#|
      |###PPPPPPPPPPCCCCCCCCCCAAAAAA#|  C  = Callejón (sigilo)
      |###PPPPPoPPPP*CCCCCCCCCAAAAAA#|  o  = Fuente/estatua (cobertura alta)
      |###PPPPPPPPPP####hh####AAAAAA#|  h  = Rincón/escondite
      |###PPPPPPPPPP####hh####AAAAAA#|
 v=8  |###PPPPPPPPPP##########AAAAAA#|
      |######IIIIII##################|  I  = Inicio
      |######IIIIII##################|
      |######II@III##################|  @  = PlayerStart (sugerencia)
 v=0  |######IIIIII##################|
      └──────────────────────────────┘
      u=0          u=24  u=36       u=60
```

`#` = macizo: edificios, muros o fachadas no transitables. El plano es aproximado: la tabla de §6 es la que manda.

## 6. Espacios

| ID interno | Zona (`docs/05`) | Rect. `u` (m) | Rect. `v` (m) | Tamaño | Función | Encuentro (`docs/05`) |
|---|---|---|---|---|---|---|
| `Z_Start` | Inicio | 12–24 | 0–8 | 12 × 8 | Zona segura; primera orden del Director | Ninguno |
| `Z_Square` | Plaza | 6–26 | 8–22 | 20 × 14 | Movimiento, visión, primera pelea | 2 Perseguidores |
| `Z_Alley` | Callejón | 26–46 | 14–18 | 20 × 4 | Sigilo en línea; opción de pelear | 1 patrulla |
| `Z_AlleyNook` | Rincón del callejón | 34–38 | 10–14 | 4 × 4 | Escondite y salida lateral de la línea de visión | — |
| `Z_WorkshopYard` | Acceso al taller | 46–58 | 8–22 | 12 × 14 | Sigilo con cobertura; alternativa de combate | Patrulla o Perseguidor |
| `Z_Workshop` | Taller de Jack | 46–58 | 22–34 | 12 × 12 | Encontrar a Jack; mensaje del yo futuro | Ninguno (zona segura) |
| `Z_CentralPass` | Paso central | 26–46 | 22–36 | 20 × 14 | Ruta de escape; control de grupos | Hasta 3 Perseguidores ("callejón de escape") |
| `Z_RefugePath` | Tramo al refugio | 14–26 | 24–32 | 12 × 8 | Protección de Jack; revelación | Interventor |
| `Z_Refuge` | Refugio | 2–14 | 22–36 | 12 × 14 | Jack queda oculto; evidencias | Ninguno |
| `Z_Archive` | Archivo | 18–42 | 36–48 | 24 × 12 | Clímax de combate | Supervisor |
| `Z_RecordsRoom` | Archivo (registros) | 24–36 | 48–54 | 12 × 6 | Elección del expediente final | Ninguno |

**Nota de diseño [PROPUESTA]:** `docs/05` sitúa el encuentro "callejón de escape" en la ruta de Jack. En este plano esa ruta pasa por el **Paso central**, así que ahí se ubica el encuentro de 3 Perseguidores. El **Callejón** de la fila inferior queda para el sigilo del Acto I. El orden de `docs/05` se conserva: plaza → callejón → taller → ruta de salida → refugio → archivo.

## 7. Conexiones y bloqueos de progresión

| ID | Entre | Posición (u, v) | Ancho | Tipo | Dueño | Estado por fase **[PROPUESTA]** |
|---|---|---|---|---|---|---|
| `C_StartSquare` | Inicio → Plaza | u 14–22, v 8 | 8 m | Abertura | D | Siempre abierta |
| `C_SquareAlley` | Plaza → Callejón | u 26, v 14–18 | 4 m | Abertura | D | Siempre abierta |
| `C_AlleyYard` | Callejón → Patio | u 46, v 14–18 | 4 m | Abertura | D | Siempre abierta |
| `C_YardWorkshop` | Patio → Taller | u 50–54, v 22 | 4 m | Puerta delantera | C (o abertura D) | Abierta |
| `C_SideDoor` | Taller → Paso central | u 46, v 27–29 | 2 m | **Puerta lateral** (`docs/05`) | **C** | Se abre en `OpenEscapeRoute` |
| `C_PassPath` | Paso central → Tramo | u 26, v 24–32 | 8 m | Abertura | D | Siempre abierta (solo se llega tras la puerta lateral) |
| `C_PathRefuge` | Tramo → Refugio | u 14, v 26–30 | 4 m | Abertura o puerta | D / C | Abierta |
| `C_SquareRefuge` | Plaza ↔ Refugio | u 8–12, v 22 | 4 m | Verja **cerrada** | D | Siempre cerrada; respeta el enlace del diagrama de `docs/05` sin crear atajos. C podría convertirla en atajo si lo desea |
| `C_ArchiveGate` | Paso central → Archivo | u 34–38, v 36 | 4 m | Puerta | **C** | Se abre al entrar en `FinalChoice` |
| `C_RecordsDoor` | Archivo → Registros | u 28–32, v 48 | 4 m | Puerta | **C** | Se abre con `SupervisorDefeated` (`docs/05`: el Supervisor bloquea el acceso) |

**Comprobación de secuencia:** durante el Acto I el jugador solo alcanza Inicio, Plaza, Callejón, Patio y Taller. El Paso central, el Refugio y el Archivo solo son accesibles a través de la puerta lateral y de las puertas de C. No hay forma de saltarse fases.

Las puertas que bloquean la navegación deben usar `Nav Modifier` o desactivar su colisión de navegación al abrirse (`01_CONTRATOS §6`). Coordinar con B en F2.

## 8. Flujo por acto

| Acto / fase | Recorrido | Distancia aprox. |
|---|---|---|
| I · `FindJack` | Inicio → Plaza (pelea) → Callejón (sigilo) → Patio → Taller (Jack) | ~60 m |
| II · `OpenEscapeRoute` → `ProtectJack` | Puerta lateral → Paso central (3 Perseguidores) → Tramo (Interventor) → Refugio | ~45 m |
| II · `DiscoverTruth` | Refugio: evidencias y revelación | — |
| III · `FinalChoice` | Refugio → Tramo → Paso central → Archivo (Supervisor) → Registros | ~45 m |

Hay unos 150 m de recorrido, apenas 30–40 s de caminar. Los 10–15 minutos de `docs/05` vienen de combates, sigilo y diálogos. Si hiciera falta más duración, se ampliarían los encuentros, no los pasillos.

## 9. Huecos reservados para B y C (sugerencias)

Coordenadas en metros `(u, v)`; en Unreal: `X = v·100`, `Y = u·100`.

### Para C (`L_Whitechapel_Story`)

| Elemento | Posición sugerida | Notas |
|---|---|---|
| `PlayerStart` | (18, 3), mirando al norte | Dentro del Inicio |
| Checkpoint CP0 | (18, 5) | Inicio |
| Checkpoint CP1 | (27, 16) | Entrada del Callejón, tras la primera pelea |
| Checkpoint CP2 | (52, 27) | Taller, tras encontrar a Jack |
| Checkpoint CP3 | (8, 29) | Refugio |
| Checkpoint CP4 | (36, 33) | Paso central, antes de la puerta del Archivo |
| Escondite interactivo (`BP_Hideout`) | (36, 11) en el rincón; segundo opcional en (57, 20) del Patio | `docs/05`: armarios o rincones ocultos |
| Evidencia: registro de enfermería | (4, 34) | Refugio |
| Evidencia: informe fabricado | (12, 24) | Refugio, junto a la verja. Alternativa: (20, 31) en el Tramo |
| Expediente oficial (estación 1) | (26, 52) | Sala de registros, pared norte |
| Expediente auténtico (estación 2) | (34, 52) | Sala de registros, pared norte; separado 8 m del oficial para que la elección sea visible |
| Triggers de historia | Entrada de cada zona | P. ej. revelación al entrar en el Refugio |

### Para B (`L_Whitechapel_AI`)

| Elemento | Posición sugerida | Notas |
|---|---|---|
| Perseguidores ×2 (Plaza) | (12, 14) y (20, 18) | Patrulla circular alrededor de la fuente (16, 15) |
| Patrulla del Callejón | Ruta (28, 16) ↔ (44, 16) | Paso estrecho: el jugador usa cobertura o el rincón |
| Patrulla del Patio | Ruta (48, 10) → (56, 10) → (56, 20) | Rodea las cajas |
| Perseguidores ×3 (Paso central) | (30, 26), (36, 32), (42, 26) | Aparecen o se activan en `ProtectJack` (decide B) |
| Interventor | (20, 28) | Tramo al refugio |
| Supervisor | (30, 42) | Centro del Archivo |
| Jack: espera | W0 (54, 30) | Taller, lejos de la puerta lateral |
| Jack: waypoints | W1 (48, 28) → W2 (42, 28) → W3 (36, 29) → W4 (28, 29) → W5 (20, 28) → W6 (5, 31) | W6 = escondite del Refugio. Todos a ≥ 1 m de muros y coberturas |

## 10. Cobertura y obstáculos (D-04)

Todos bloquean el canal **Visibility** y tienen colisión `BlockAll`.

| Zona | Elemento | Posición (u, v) | Tamaño (m) | Tipo |
|---|---|---|---|---|
| Plaza | Fuente/estatua | (16, 15) | 2 × 2 × 2,5 | Alta |
| Plaza | Barriles | (9, 11), (23, 20) | 1 × 1 × 1,2 | Baja |
| Callejón | Cajas apiladas, pegadas al muro sur | (31, 14,5), (41, 14,5) | 1,5 × 1 × 2 | Alta (deja 3 m de paso) |
| Callejón | Carretilla, pegada al muro norte | (36, 17,5) | 2 × 1 × 1,2 | Baja (deja 3 m de paso) |
| Patio | Cajas | (49, 13), (56, 12) | 2 × 2 × 2 | Alta |
| Patio | Murete | u 50–54, v 19 | 4 × 0,5 × 1,2 | Baja |
| Patio | Barriles | (53, 16) | 1 × 1 × 1,2 | Baja |
| Paso central | Columnas o farolas gruesas | (32, 32), (40, 32) | 1 × 1 × 3 | Alta; sirven para rodear en el 3 contra 1. Quedan a 3 m de la ruta de Jack (v ≈ 28–29) |
| Paso central | Carro volcado | (36, 24) | 3 × 1,5 × 1,5 | Media |
| Archivo | Columnas | (22, 40), (38, 40), (22, 45), (38, 45) | 1 × 1 × 4 | Alta; el centro queda libre para el jefe |

Regla: mantener el **centro de cada arena libre** (al menos 8 × 8 m) y poner la cobertura en los bordes.

## 11. Ambiente por zona (para F3)

| Zona | Lectura de luz | Audio ambiente |
|---|---|---|
| Inicio | Farol único, calma | Lluvia ligera |
| Plaza | La más iluminada (faroles alrededor): pelea legible | Multitud distante |
| Callejón y Patio | Oscuros, islas de luz pequeñas: sigilo | Goteo, viento |
| Taller | Interior cálido (vela/lámpara) | Interior apagado |
| Paso central | Niebla densa, faroles a los lados | Lluvia fuerte |
| Refugio | Interior tenue | Silencio relativo |
| Archivo | Frío, destellos **cian** de la tecnología de la agencia (`docs/07`) | Zumbido de máquinas |

El **cian se reserva** para la tecnología de la agencia. No usarlo en faroles ni en el entorno victoriano.

## 12. Criterios de validación del blockout (D-02 a D-05)

- [ ] Se puede recorrer a pie desde `@` hasta las dos estaciones con las puertas de C abiertas (en prueba: puertas desactivadas).
- [ ] `P` en el editor: la NavMesh verde cubre los 10 espacios, cruza todas las aberturas y puertas y no tiene islas sueltas.
- [ ] Cada arena cumple las medidas de §3 con la cobertura colocada.
- [ ] Las coberturas altas bloquean una traza de visión (comprobar con B y su método de percepción).
- [ ] Prueba de cámara (D-05) con el pawn de la plantilla: anotar dónde el jugador queda oculto más de 1 s.
- [ ] Ningún actor del blockout en `_AI` ni en `_Story`; todo en `L_Whitechapel_Geo`.

## 13. Preguntas abiertas

| # | Pregunta | Para | Afecta a |
|---|---|---|---|
| Q1 | ¿Se acepta la huella de 60 × 54 m? | Equipo | Todo el plano |
| Q2 | ¿Signo del yaw y proyección de la cámara (D0.7)? | A | Regla de muros (§4) |
| Q3 | ¿A qué altura apunta la traza de visión de los guardias? | B | Altura de la cobertura baja |
| Q4 | ¿El Interventor es opcional (`docs/01`) u obligatorio en el Tramo (`docs/05`)? | Equipo / C | Si es opcional, el Tramo necesita un rodeo |
| Q5 | ¿Posiciones definitivas de evidencias y checkpoints? | C | §9 |
| Q6 | ¿Se reinician los enemigos al reaparecer en un checkpoint? | B | Vuelta atrás del Acto III por el Paso central |
| Q7 | ¿La verja Plaza ↔ Refugio será un atajo en el Acto III? | C | §7 |
