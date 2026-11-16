# Encuentros por punto de la historia en `L_Test_D` — [PROPUESTA]

> División D, 2026-11-16. Base: `docs/05` (diseño de encuentros por zona y objetivos de cada acto) y las zonas y nodos de `whitechapel_layout.json`. Plano: [`encuentros_propuesta.png`](encuentros_propuesta.png), generado con `Scripts/D/encounters_plan.py`.
> Coordenadas en metros del masterplan (x = este, y = norte). En UE: `X = 100·y`, `Y = 12000 + 100·x`.
> P = Perseguidor (`BP_Pursuer`, no letal), p = patrulla con `BP_PatrolRoute`, I = Interventor, S = Supervisor.

| # | Acto | Punto de la historia | Estado | Grupo | Posición (m) | Función |
|---|---|---|---|---|---|---|
| 1 | I | Plaza | ✅ colocado | 2 P | (92, 46), (98, 50) | Primera pelea: parry y Frame Cut |
| 2 | I | Calle al taller | ✅ colocado | 1 p | ruta (112–138, 48–50) | Sigilo opcional |
| 3 | I | Puerta del taller | 🆕 | 2 P | (135, 46), (138, 50) | Vigilan la entrada del escondite de Jack: pelear o rodear |
| 4 | II | Ensanche de escape | ✅ colocado | 3 P | (170, 96), (176, 101), (180, 95) | Control de grupos con Jack |
| 5 | II | Estrechamiento 2 | 🆕 | 2 P | (178, 117), (180, 122) | Emboscada en el cuello de botella de 4,5 m |
| 6 | II | Registro de enfermería (evidencia 1) | 🆕 | 1 P + 1 p | (215, 136), patrulla en el patio | Custodian la primera prueba; se puede entrar en sigilo |
| 7 | II | Informe fabricado (evidencia 2) | 🆕 | 2 P + 1 p | (216, 99), (220, 103), patrulla en el corredor de evidencias (x = 226) | Sitio de la agencia: la prueba falsa está protegida |
| 8 | II | Tránsito al refugio | ✅ colocado | I | (195, 142) | Revelación y orden de corrección |
| 9 | II | **Refugio** | 🆕 | 3 P | (206, 149), (210, 148), (218, 149) | La multitud llega al refugio: defender la entrada. La zona de espera de Jack queda libre |
| 10 | III | Paso central hacia el archivo | ✅ patrulla + 🆕 2 P | 1 p + 2 P | (140, 114), (146, 116) | Tras el checklist reescrito, la calle ya es hostil |
| 11 | III | Reja del archivo | 🆕 | 2 P | (119, 134), (125, 134) | Guardias en el acceso lateral |
| 12 | III | Antepatio | ✅ colocado | S | (94, 124) | Jefe: duelo sin escolta |
| — | III | Archivo y sala de elección | — | ninguno | — | Espacio tranquilo para decidir el expediente |

**Totales:** 10 enemigos colocados → **26** con la propuesta (+16: 14 Perseguidores y 2 patrullas más).

## Notas

- Todos los puntos están dentro de calles o patios navegables, y fuera de las zonas que deben quedar libres (arenas, frentes de interacción, espera de Jack). Lo comprueba el script.
- Hoy los enemigos están activos desde el principio. Los grupos de los actos II y III solo los encuentra quien llegue a su zona, pero no esperan a que avance la historia. `BP_GuardBase` ya tiene `B_StoryGate` para activarlos por fase; configurarlo es trabajo de B (Jesús), no de D.
- Interventor y Supervisor son únicos: los grupos nuevos solo usan Perseguidores.
