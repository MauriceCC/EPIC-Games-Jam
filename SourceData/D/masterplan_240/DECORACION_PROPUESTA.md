# Decoración por punto de la historia en `L_Test_D` — [PROPUESTA]

> División D, 2026-11-16. Complementa a [ENCUENTROS_PROPUESTA.md](ENCUENTROS_PROPUESTA.md).
> Generado por `Scripts/D/deco_layout.py` → `deco_placements.json` (coordenadas UE listas), `deco_propuesta.png` (plano general) y `deco_detalle.png` (los 13 lugares ampliados).
> Solo assets que ya existen en `Art/Props/` y `Art/Market/`. Todo se colocaría con la etiqueta `MP240_DECO` y en la carpeta `MP240_DECO`.

## Reglas que cumple cada objeto

- Huella real (medida en el editor, `deco_sizes.json`) completa dentro de calles o patios navegables.
- Fuera de arenas, frentes de interacción y espera de Jack (0,5 m de margen). Única excepción: en el ensanche de escape se admite **cobertura baja** (≤ 1,3 m) en una franja de 1,2 m pegada al borde; el centro sigue libre.
- Sin solapar props existentes ni nuevos (0,3 m). El pavimento de acera (`SM_StreetFlagstones`) no cuenta como obstáculo.
- A 1,5 m o más de cada enemigo y a 1,3 m o más de la ruta principal.
- No estrecha ninguna calle por debajo de su ancho mínimo.
- **Cámara:** lo que mide más de 1,8 m solo va al noreste del centro del lugar, que es el lado contrario a la cámara.

## Reparto: 82 objetos

| # | Lugar | Colocados/pedidos | Objetos |
|---|---|---|---|
| 1 | Plaza | 12/12 | carreta de flores ×2, carro de sopa ×1, carro volcado ×1, pila de cajas ×3, barril ×4, farol ×1 |
| 2 | Calle al taller | 5/5 | bajante ×2, barril ×2, carretilla ×1 |
| 3 | Puerta del taller | 4/6 | banco de trabajo ×1, pila de cajas ×2, barril ×1 |
| 4 | Ensanche de escape | 6/10 | murete ×1, pila de cajas ×1, barril ×4 (cobertura en el borde) |
| 5 | Estrechamiento 2 | 3/4 | carretilla ×1, barril ×2 |
| 6 | Registro de enfermería | 8/8 | catre ×3, mesa ×1 con el libro de enfermería encima, silla ×2, estantería ×1 |
| 7 | Informe fabricado | 8/8 | pila de cajas ×3, armario ×1, carretilla ×1, mesa ×1 con la carpeta del informe encima, barril ×1 |
| 8 | Tránsito al refugio | 5/5 | farol ×2, barril ×2, murete ×1 |
| 9 | Refugio (barricada) | 9/10 | carro victoriano ×1, carro volcado ×1, pila de cajas ×3, armario ×1, barril ×3 |
| 10 | Paso central | 3/6 | barril ×3 |
| 11 | Reja del archivo | 5/5 | farol ×2, murete ×1, armario de archivo ×2 |
| 12 | Antepatio (jefe) | 8/8 | columna de archivo ×4, farol ×2, murete ×2 (solo perímetro) |
| 13 | Sala de elección | 6/6 | armario de archivo ×4, estantería ×2 (frentes de las estaciones libres) |

Los 11 que faltan (carro volcado y escombros del ensanche, escombros del paso central, etc.) no caben sin estrechar la ruta o invadir la arena. Se dejan fuera a propósito.
