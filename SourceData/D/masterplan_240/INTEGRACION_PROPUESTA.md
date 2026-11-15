# Propuesta de integración del distrito 240 × 180 en `L_Whitechapel`

> División D · 2026-11-15 · **[PROPUESTA] — no aplicada.** El mapa integrado no se ha tocado: todo el trabajo está en `L_Test_D`.
> Requiere revisión de D (dueño del nivel), del integrador (Mauricio) y de B y C para sus actores.

## 1. Qué cambiaría de D

| Asset / mapa | Cambio | Riesgo |
|---|---|---|
| `Maps/L_Whitechapel_Geo` (D) | **Sustituir** su contenido: el blockout 60 × 54, las casas `Houses_v3` y los 565 actores ocultos con colisión dejan paso a los 1 439 actores `MP240_FINAL` (o a un subnivel nuevo `L_Whitechapel_Geo240`, recomendado) | Alto: cambia todo el recorrido. Se hace en un subnivel nuevo y el `_Geo` actual se descarga, no se borra |
| `Maps/L_Whitechapel_Light` (D) | Luna (2 lux, 9 500 K), cielo (1,8), niebla, postproceso (sesgo +1, contraste local de sombras 0,55), 17 farolas, 7 luces interiores, lluvia, viento y vapor de `L_Test_D` | Medio: la exposición se ajustó con la cámara real; repetir la revisión en Play |
| `Maps/L_Whitechapel` (persistente, D) | NavMeshBoundsVolume que cubra X −200…18 200, Y 11 800…36 200 (cm); crearlo con `BRUSH ADDVOLUME` (por MCP nace sin brocha) | Bajo |
| `Art/Kit`, `Art/Materials`, `Art/Buildings/SM_*Front_*`, `Art/Props/SM_MarketStall_01`, `SM_Cart_Victorian`, `Art/Blockout/M_BO_WorldTiling_Occl` | Assets nuevos de D, sin dependencias de otras divisiones | Bajo |
| `Art/Blockout/SM_BO_*` | Ya no se usan en el arte final; se pueden conservar para pruebas | Ninguno |

**Forma de conservar el nivel integrado:** crear `L_Whitechapel_Geo240` y `L_Whitechapel_Light240` copiando los actores `MP240_FINAL` de `L_Test_D` (copiar y pegar en el editor conserva transformaciones y materiales), dejar los subniveles actuales descargados en un commit propio y no borrarlos hasta que B y C validen. Bloqueo LFS del persistente antes de editarlo.

## 2. Transformación de coordenadas

Plano (m, x = este, y = norte, origen SO) → Unreal (cm), offset A aprobado:

```
UE_X = 100 · y        UE_Y = 12000 + 100 · x        UE_Z = 100 · z
yaw_UE = 90° − rumbo_plano   (fachada al norte = 0°, al este = 90°, al sur = 180°, al oeste = −90°)
```

`L_Test_D` usa el mismo offset, así que los actores se copian sin moverlos. Si el integrador prefiere el offset B (N01 sobre el PlayerStart actual): restar (600, 20 600) cm a X e Y de todo el conjunto.

## 3. Destinos propuestos para actores de B y C (los mueve su dueño)

| Actor | Dueño | Destino (plano m → UE cm) |
|---|---|---|
| PlayerStart | C | N01 (104, 9) → (900, 22400) |
| `C_Closure_CP0` / `CP1` | C | N02 (104, 32) → (3200, 22400) / N06 (138, 45) → (4500, 25800) |
| Checkpoints nuevos | C | N12 refugio (214, 158) → (15800, 33400); N16 (120, 115) → (11500, 24000); N18 reja (122, 137) → (13700, 24200) |
| `C_Closure_AlleyHideout` | C | Nicho NI2 (185, 121) → (12100, 30500) |
| `BP_Evidence` enfermería | C | escritorio (210, 125,5) → (12550, 33000) |
| `BP_Evidence` informe | C | escritorio (212, 92,5) → (9250, 33200) |
| `BP_FinalChoice` ×2 | C | (74,5, 163,5) y (79,5, 163,5) → (16350, 19450) y (16350, 19950) |
| `BP_Door` ×12 | C | Posiciones y anchos de `whitechapel_routes.csv` (tabla Gates); pilares de piedra ya colocados por D en cada uno |
| `B_Jack_Workshop` + `JackInteraction` | B | J0 (150, 52) → (5200, 27000) |
| Perseguidores de la plaza (2 + finishers + rutas) | B | Arenas A (55, 48) y B (96, 48) → (4800, 17500) y (4800, 21600) |
| `B_Alley_Pursuer` | B | Ensanche N09 (176, 103) → (10300, 29600) |
| `B_Yard_Pursuer` | B | Calle taller–escape (170, 63,5) → (6350, 29000) |
| Supervisor | B | N17 (94, 122) → (12200, 21400) |

## 4. Dependencias y ajustes pendientes

| # | Pendiente | Dueño |
|---|---|---|
| P1 | Encuadre de cámara en las arenas (≈ 12 × 9 m; harían falta brazos de 2 200–3 600 para ver arenas de 16–26 m) | A |
| P2 | `BP_Door` con estados por fase en los 12 portones; la validación actual es con todo abierto y **no acredita la progresión narrativa** | C |
| P3 | `BP_Pursuer` con `BP_PatrolRoute` no se movió en `L_Test_D` (estado Patrol, índice 0, velocidad 0) aunque el NavMesh es válido; en Simular, los BP de HUD dan errores de referencia nula sin jugador | B / C |
| P4 | El recorte de oclusión es por pantalla: depende de que la cámara de A mantenga al jugador en el centro (brazo sin colisión y con lag). Si A cambia el brazo o activa la colisión, hay que revisar `CutRadius` y la profundidad de corte (1 620 cm) | A + D |
| P5 | Revisar en Play los textos visibles: el arte de D no lleva rótulos (fascias en blanco a propósito); los carteles en inglés quedan para coordinar con C | C + D |
| P6 | La lluvia global (`NS_Rain`) cae dentro de los interiores. **[PROPUESTA]** Volúmenes que la anulen o lluvia con prueba de techo | D |

## 5. Riesgos

- **Coste de actores:** 1 439 actores estáticos (sin instanciado). Medido en `final/VALIDACION_FINAL.md`: 59,2 fps, GPU 7,25 ms y hilo de juego 7,45 ms en una RTX 4060 Laptop; si hiciera falta, fusionar hileras de casas por manzana (`merge_actors`) o pasarlas a ISM.
- **Arte generado por IA:** licencias de Meshy (plan de pago) y GPT Image; registrado en `CREDITS.md`.
- **Mapa integrado:** `L_Whitechapel*.umap` tiene cambios locales sin subir de sesiones anteriores (no de esta tarea). Antes de integrar, confirmar con el integrador qué versión es la buena.
