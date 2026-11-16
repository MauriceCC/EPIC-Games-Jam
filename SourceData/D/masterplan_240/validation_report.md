# Validacion automatica del layout 240 x 180

Rejilla 0.25 m. Holgura del jugador 0,45 m de radio. Generado por `Scripts/D/masterplan240_layout.py`.

## Solapes edificio-edificio (0)

- Ninguno.

## Solapes solido-espacio transitable (0)

- Ninguno.

## Props en areas que deben quedar libres (0)

- Ninguno.

## Props fuera de espacio transitable (0)

- Ninguno.

## Envolventes (13)

- SP-TALLER en Z04: OK
- SP-ANEXO en Z04: OK
- SP-REFUGIO en Z09: OK
- SP-COBERTIZO en Z09: OK
- SP-ENFERMERIA en Z10: OK
- SP-INFORME en Z11: OK
- SP-ARCH-CENTRAL en Z15: OK
- SP-ARCH-ALA-O en Z15: OK
- SP-ARCH-ALA-E en Z15: OK
- SP-ARCH-PORTICO en Z15: OK
- Z16 sala dentro del cuerpo central en Z16: OK
- Arena plaza A 18x16 fuera de edificios en Z03: OK
- Arena plaza B 16x14 fuera de edificios en Z03: OK

## Huecos de 0-3 m entre volumenes independientes (20)

No son transitables: se cierran con medianera, muro o verja (no dejar grietas).

SP-TALLER/MD-N05 1.0, SP-TALLER/MJ-S03 2.0, SP-ANEXO/MJ-S02 2.0, SP-ENFERMERIA/MF-D2 2.5, SP-INFORME/MF-D1 1.0, SP-ARCH-ALA-O/MI-W01 2.0, SP-ARCH-ALA-O/MJ-N01 2.83, SP-ARCH-PORTICO/CX-ARCH-GALERIA 2.0, MA-N01/MB-R01 2.83, MA-N01/MB-R02 2.0, MA-N01/MB-05 2.0, MA-N03/MI-F01 1.0, MB-E02/MC-P 1.0, MD-W/MD-T 1.41, ME-S06/ME-B01 1.0, ME-N03/ME-M01 2.0, ME-M03/ME-A1 1.5, MF-X03/MG-B01 1.0, MF-R01/MH-04 1.0, MF-R02/MH-04 1.0

## Anchos libres tras colocar props

| Tramo | Exigido (m) | Medido (m) | Seccion mas estrecha | OK |
|---|---:|---:|---:|---|
| W-SAV Avenida visual sur 12 m (tramo navegable, cerrado con barricadas en x=84 y x=124) | 7.0 | 9.5 | 100.125 | si |
| W-Z01 Calle de llegada 10 m | 7.0 | 8.0 | 11.625 | si |
| W-PS1 Paso de servicio avenida-plaza 4 m | 2.7 | 4.0 | 15.125 | si |
| W-STE Corredor este plaza-taller 8 m | 6.0 | 7.0 | 119.625 | si |
| W-PN Calle norte plaza-antepatio 8 m (ruta amarilla de la imagen) | 5.5 | 7.25 | 78.625 | si |
| W-ALA1 Ruta azul A, tramo oeste 4,5 m | 2.7 | 3.25 | 99.375 | si |
| W-ARCP Pasaje cubierto 3,5 m (arco) | 2.7 | 3.5 | 103.125 | si |
| W-ALA3 Ruta azul A, tramo este 4,5 m | 2.7 | 4.5 | 143.125 | si |
| W-STCP Paso central 6 m | 5.0 | 5.25 | 129.625 | si |
| W-PAS Pasillo junto al taller 4 m | 2.7 | 4.0 | 41.125 | si |
| W-STX Calle taller-escape 7 m | 5.0 | 7.0 | 161.125 | si |
| W-ESC1 Escape tramo 1, 7 m | 5.0 | 5.5 | 73.375 | si |
| W-NK1 Estrechamiento 1: 4,5 m x 7 m | 4.2 | 4.5 | 85.125 | si |
| W-NK2 Estrechamiento 2: 4,5 m x 7 m | 4.2 | 4.5 | 107.125 | si |
| W-ESC2 Escape tramo 2, 7 m | 5.0 | 6.0 | 116.125 | si |
| W-SV1 Pasadizo de servicio 3,5 m | 2.2 | 3.5 | 81.125 | si |
| W-TR Transito al refugio 6 m | 5.0 | 5.0 | 185.625 | si |
| W-STEV Corredor sur-norte de evidencias 4,5 m (ruta verde) | 4.0 | 4.5 | 65.125 | si |
| W-ALB1 Ruta verde B, 4 m | 3.0 | 4.0 | 180.125 | si |
| W-ALB2 Retorno evidencias-escape 3,5 m | 2.7 | 3.5 | 184.125 | si |

## Alcance por fase (portones cerrados segun fase)

- **Acto I**: alcanzables N01, N02, N03, N04, N05, N06, N07. Faltan: ninguno. Fugas: ninguna.
- **Acto II escape**: alcanzables N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, N11, N12, N15, N16. Faltan: ninguno. Fugas: ninguna.
- **Acto II evidencias**: alcanzables N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, N11, N12, N13, N14, N15, N16. Faltan: ninguno. Fugas: ninguna.
- **Acto III jefe**: alcanzables N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, N11, N12, N13, N14, N15, N16, N17. Faltan: ninguno. Fugas: ninguna.
- **Acto III archivo**: alcanzables N01, N02, N03, N04, N05, N06, N07, N08, N09, N10, N11, N12, N13, N14, N15, N16, N17, N18, N19, N20. Faltan: ninguno. Fugas: ninguna.

## Rutas (todos los portones abiertos)

- **R-MAIN-1** (Llegada, plaza y calle al taller, holgura 1.0 m): CONECTADA - N01>N02 30.0 m; N02>N03 36.8 m; N03>N04 39.6 m; N04>N05 13.9 m; N05>N06 24.7 m
- **R-MAIN-2** (Escape con Jack (cuellos 4,5 m), holgura 1.0 m): CONECTADA - N06>N07 27.6 m; N07>N08 28.4 m; N08>N09 35.2 m; N09>N10 29.2 m; N10>N11 41.2 m; N11>N12 20.8 m
- **R-MAIN-3** (Evidencias y regreso al eje, holgura 1.0 m): CONECTADA - N12>N13 60.3 m; N13>N14 55.4 m; N14>N15 75.0 m; N15>N16 44.9 m
- **R-MAIN-4** (Jefe, reja, archivo, eleccion, holgura 1.0 m): CONECTADA - N16>N17 34.3 m; N17>N18 39.2 m; N18>N19 36.5 m; N19>N20 21.2 m
- **R-ALT-A** (Ruta azul: ensanche -> AL-A3 -> patio -> arco -> paso central, holgura 2.7 m): CONECTADA - N09>N15 27.7 m
- **R-ALT-B** (Ruta verde: escape -> informe -> enfermeria -> refugio, holgura 2.2 m): CONECTADA - N08>N14 71.5 m; N14>N13 57.8 m; N13>N12 61.4 m
- **R-JACK** (Trayecto de Jack desde su puesto en el taller (J0) al refugio, holgura 2.4 m): CONECTADA - J0>N07 19.6 m; N07>N08 28.6 m; N08>N09 34.8 m; N09>N10 28.6 m; N10>N11 41.3 m; N11>N12 20.6 m

## Nodos (ajuste al punto libre mas cercano)

- N01 (104, 9): desplazado 0.0 m, holgura 4.16 m
- N02 (104, 32): desplazado 0.0 m, holgura 4.88 m
- N03 (78, 48): desplazado 0.0 m, holgura 0.62 m
- N04 (106, 48): desplazado 0.0 m, holgura 5.12 m
- N05 (117, 48): desplazado 0.0 m, holgura 3.88 m
- N06 (140, 45): desplazado 0.0 m, holgura 1.12 m
- N07 (158, 64): desplazado 0.0 m, holgura 2.25 m
- N08 (176, 75): desplazado 0.0 m, holgura 2.83 m
- N09 (176, 103): desplazado 0.0 m, holgura 2.98 m
- N10 (181, 127): desplazado 0.0 m, holgura 1.88 m
- N11 (205.5, 143): desplazado 0.0 m, holgura 2.5 m
- N12 (214, 158): desplazado 0.0 m, holgura 4.38 m
- N13 (211, 122): desplazado 0.0 m, holgura 2.98 m
- N14 (212, 87): desplazado 0.0 m, holgura 3.12 m
- N15 (161, 115): desplazado 0.0 m, holgura 2.88 m
- N16 (120, 115): desplazado 0.0 m, holgura 2.88 m
- N17 (94, 122): desplazado 0.0 m, holgura 15.7 m
- N18 (122, 137): desplazado 0.0 m, holgura 7.88 m
- N19 (92, 149): desplazado 0.0 m, holgura 1.69 m
- N20 (77, 160): desplazado 0.0 m, holgura 3.25 m

## Recuento de colocaciones

| Grupo | Objetivo masterplan | Colocadas |
|---|---:|---:|
| M-A | 6 | 11 |
| M-B | 4 | 7 |
| M-C | 5 | 15 |
| M-D | 5 | 10 |
| M-E | 8 | 21 |
| M-F | 8 | 17 |
| M-G | 5 | 20 |
| M-H | 3 | 4 |
| M-I | 5 | 22 |
| M-J | 12 | 12 |
| HITO | 10 | 10 |
| Siluetas (no cuentan) | - | 6 |

Por familia: AR01 108, AR02 11, AR03 7, AR04 2, AR05 8, AR06 1, AR07 1, AR08 1, AR09 4, AR10 6

Huella construida (sin siluetas): 13027 m2 de 43 200 m2 (30.2 %).
