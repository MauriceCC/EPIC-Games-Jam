# UNSCRIPTED — WHITECHAPEL 1888
## Masterplan dimensional de escenario — referencia principal: plano ilustrado proporcionado

**Versión:** propuesta espacial v1.0 · **Motor:** Unreal Engine 5.8.4 · **Nivel:** `L_Whitechapel`  
**Estado:** **DOCUMENTO DE DISEÑO PROPUESTO, NO GEOMETRÍA YA IMPLEMENTADA**.  
**Referencia visual vinculante para la composición:** la imagen adjunta por el usuario, titulada «WHITECHAPEL — LONDRES, 1888 — PLAN DE NIVEL».  
**Alcance:** redimensionar y detallar el plano ilustrado como un distrito transitable, sin quedar limitados por el antiguo blockout 60 × 40 m.  
**Aviso:** la imagen es **arte conceptual**, no un dibujo CAD. Su barra de escala y sus trazos no permiten inferir con precisión dimensiones reales de cada objeto. **Todas las medidas de este documento son decisiones nuevas propuestas** para traducir esa composición a Unreal. No fingir que están medidas directamente de la imagen.

---

# 0. OBJETIVO Y JERARQUÍA DE REFERENCIAS

Construir un nivel **amplio en apariencia, denso pero no apretado**, con varios bloques de casas victorianas, calles principales de buena lectura, callejones funcionales, patios, plazas, interiores solo donde hagan falta y un recorrido principal coherente. **No** construir una plaza gris enorme rodeada de unas cuantas paredes. **No** construir un laberinto de casas pegadas sin escala humana.

## Orden de prioridad para Claude

1. **La imagen adjunta determina la composición relativa**: sur = INICIO; suroeste = PLAZA; sureste = TALLER DE JACK; centro-este = CALLEJÓN DE ESCAPE; noreste = REFUGIO y EVIDENCIAS; norte-oeste = ARCHIVO FINAL; antepatio sur del archivo = SUPERVISOR; calle central y rutas laterales unen todo.
2. Este documento determina **dimensiones, coordenadas, distancias, envolventes, anchos y restricciones de ocupación** propuestos.
3. El juego debe conservar la **secuencia de historia y los interactuables reales existentes**. Los documentos viejos sirven para entender la narrativa, pero sus **antiguas medidas, posiciones o bloqueout no mandan**.
4. Los assets, Blueprints, actores y scripts **reales del proyecto** deben auditarse antes de alterar algo. Si la imagen contradice un objeto funcional, **conservar funcionalidad y proponer reubicación**, no eliminarlo sin comprobación.

### Diferencia entre arte conceptual y layout ejecutable

- Imagen: muestra **qué zona se sitúa cerca de qué otra**, ritmo de masas de edificios y atmósfera.
- Este masterplan: define **dónde reservar cada zona en un sistema local nuevo**.
- Editor actual: tiene su **propio origen y coordenadas**. NO asumir que `(0,0,0)` del editor coincide con el origen de este documento: primero calcular una transformación/offset y validar.
- La composición es obligatoria; **cada rectángulo se puede ajustar unos metros** en auditoría si resulta necesario para conectar con el mapa existente. Documentar todo ajuste.

---

# 1. SISTEMA DE UNIDADES, ORIENTACIÓN Y LÍMITES

## 1.1 Dimensiones maestras

| Parámetro | Valor | En Unreal (cm) |
|---|---:|---:|
| Ancho este–oeste del distrito visual | **240 m** | **24 000 uu** |
| Alto sur–norte del distrito visual | **180 m** | **18 000 uu** |
| Superficie rectangular de referencia | **43 200 m²** | — |
| Franja de fachada/fondo en perímetro | **6–12 m** | 600–1 200 uu |
| Zona caminable objetivo (conectada, irregular, estimación de diseño) | **aprox. 160 × 130 m de extensión** | No crear un único rectángulo transitable |
| Desnivel general de las calles | **0–1,2 m** | 0–120 uu |

**Importante:** «160 × 130» NO representa 20 800 m² despejados. La mayoría de la extensión está ocupada por edificios, patios y cercados; únicamente las calles, patios y estancias marcadas serán navegables.

## 1.2 Coordenadas de plano

- Origen **SO (suroeste)**: `(X=0 m, Y=0 m)`.
- `+X` = **este** (derecha de la imagen).
- `+Y` = **norte** (arriba de la imagen).
- `+Z` = arriba físicamente.
- Límites del distrito: `X ∈ [0,240]`, `Y ∈ [0,180]`.
- **Conversión a Unreal:** `UnrealX = OffsetX + 100*X`; `UnrealY = OffsetY + 100*Y`; `UnrealZ = OffsetZ + 100*Z`. Si el mapa existente tiene otra orientación, usar rotación R sobre el par `(X,Y)` y conservar offsets. No mover el proyecto al origen por la fuerza.
- Convención para rectángulos `R(xMin, yMin, xMax, yMax)`: cotas **absolutas**, no `(centro, escala)`.
- Centro de rectángulo: `((xMin+xMax)/2, (yMin+yMax)/2)`; tamaño: `(xMax-xMin, yMax-yMin)`.
- Distancias son metros, **no unidades de grid**; en UE 1 m = 100 uu por defecto.

## 1.3 Layout conceptual a conservar

```text
                              NORTE  (+Y)
       OESTE (-X)                                      ESTE (+X)
 ┌────────────────────────────────────────────────────────────┐
 │ Fachadas      ARCHIVO FINAL           Fachadas   REFUGIO   │
 │               │                           ┌─────────────┐ │
 │         PELEA SUPERVISOR -- ACCESO         │ enfermería  │ │
 │               │        ↖                  │ informe     │ │
 │  casas ───── PASO CENTRAL ───── CALLEJÓN DE ESCAPE ────── │
 │                     ↘       ↑              patios        │
 │      PLAZA/MERCADO ────── TALLER DE JACK                 │
 │            ↑                                               │
 │          INICIO                                             │
 └────────────────────────────────────────────────────────────┘
                                SUR (-Y)
```

**No es un esquema de distancias**. La tabla siguiente sí es la reserva geométrica.

---

# 2. RESERVAS DE SECTORES: MEDIDAS Y UBICACIÓN

Cada sector es una **envolvente de planificación**. En ella caben calles, edificios, patios y decoración. **NO** significa que todo su interior tenga piso libre ni que deba rellenarse de una sola malla. Algunas envolventes se tocan o se superponen intencionalmente en cruces y transiciones; no son parcelas catastrales exclusivas.

| ID | Sector | Rectángulo / eje del sector, en metros | Extensión | Función |
|---|---|---|---|---|
| Z00 | Perímetro y fachada de fondo | `R(0,0,240,180)` menos sectores activos | variable | Silueta de ciudad, cierre visual |
| Z01 | Calle de llegada / inicio | `R(94,0,114,27)` | 20 × 27 m | Llegada, checklist, primer encuadre |
| Z02 | Plaza y mercado (envolvente) | `R(29,16,113,83)` | 84 × 67 m | Acto I, exploración, combate |
| Z03 | Plaza despejada interior | `R(46,29,99,70)` | 53 × 41 m | Área legible; puestos solo en bordes |
| Z04 | Taller + patio de Jack | `R(122,17,168,69)` | 46 × 52 m | Encuentro con Jack, salida lateral |
| Z05 | Calle taller–escape | `R(151,61,181,79)` | 30 × 18 m | Puerta y preparación del escape |
| Z06 | Corredor de escape (envolvente) | `R(158,70,192,135)` | 34 × 65 m | Perseguidores, cobertura, sigilo |
| Z07 | Ruta alternativa central | `R(108,87,175,112)` | 67 × 25 m | Atajo/flanqueo transversal |
| Z08 | Tránsito al refugio | `R(175,125,209,151)` | 34 × 26 m | Entrada más silenciosa, portones |
| Z09 | Refugio y patio secreto | `R(194,139,235,176)` | 41 × 37 m | Jack a salvo, pausa narrativa |
| Z10 | Área del registro médico | `R(193,105,236,140)` | 43 × 35 m | Primer documento auténtico |
| Z11 | Área del informe fabricado | `R(193,68,237,106)` | 44 × 38 m | Segundo documento, agencia |
| Z12 | Paso central hacia archivo | `R(107,100,165,126)` | 58 × 26 m | Conexión Actos II–III |
| Z13 | Antepatio del Supervisor | `R(65,108,113,144)` | 48 × 36 m | Combate final con maniobra |
| Z14 | Acceso lateral al archivo | `R(111,120,151,149)` | 40 × 29 m | Reja, transición, checkpoint |
| Z15 | Complejo del archivo | `R(33,137,130,179)` | 97 × 42 m | Edificio institucional y decisión |
| Z16 | Sala de elección (dentro Z15) | `R(65,151,89,168)` | 24 × 17 m | Dos expedientes separados |
| Z17 | Calles escenográficas oeste | `R(0,16,29,176)` | 29 × 160 m | Profundidad, calle de fondo |
| Z18 | Calles escenográficas este | `R(237,16,240,176)` | 3 × 160 m | Cierre visual, no jugable |

**Lectura correcta:** por ejemplo, `Z10` y `Z09` comparten el borde próximo a Y=139–140 para permitir una transición. No colocar una pared infranqueable en esa línea. `Z13` se acerca a `Z15`: el antepatio está **delante** del archivo, como en la ilustración.

**Control de solapes:** antes de construir, Claude debe exportar una vista de las envolventes y diferenciar (a) solape intencionado de calles/zona de transición, (b) solape no permitido de sólidos. Ninguna casa invade el polígono de otra casa ni un carril de circulación.

---

# 3. RED DE CALLES: ANCHOS, NODOS Y CONECTIVIDAD

## 3.1 Anchos mínimos por tipo

| Tipo | Ancho entre fachadas/muros | Banda central libre de obstáculos | Aplicación |
|---|---:|---:|---|
| Avenida visual de acceso | 10–12 m | ≥ 7 m | Entrada y borde sur |
| Calle comercial a plaza | 8–10 m | ≥ 6 m | Llegada a mercado |
| Calle residencial principal | 7–9 m | ≥ 5,5 m | Taller/sector central |
| Calle de escape con pelea | 6–7,5 m | ≥ 5 m en encuentros | Callejón de escape, no todo estrecho |
| Callejón de sigilo | 3,5–5 m | ≥ 2,7 m | Rutas alternativas |
| Paso de servicio puntual | 2,5–3,2 m | ≥ 2,2 m | Atajo sin combate de grupos |
| Paso de puerta con Jack | ≥ 2,4 m útiles | ≥ 2,4 m | Nunca obstaculizar IA de Jack |
| Andén/acera, donde haya | 1–1,6 m | ≥ 1 m | No exigir acera en cada calle histórica |

**Regla:** el ancho libre se mide **después** de colocar farolas, barriles, cercos y carros. Un callejón de 4 m con cajas ocupando 2,5 m NO cumple.

## 3.2 Nodos de navegación propuestos

Todos son **centros guía**, no puntos exactos de spawn. Los ejes de ruta deben modelarse con curvas y ángulos naturales, no líneas diagonales que atraviesan edificios.

| Nodo | Posición XY (m) | Qué representa |
|---|---|---|
| N01 | `(104, 9)` | Spawn / farol de llegada |
| N02 | `(104, 32)` | Umbral sur de plaza |
| N03 | `(78, 48)` | Corazón de la plaza |
| N04 | `(106, 48)` | Salida este de plaza |
| N05 | `(117, 48)` | Calle de unión |
| N06 | `(140, 45)` | Taller de Jack (entrada) |
| N07 | `(158, 64)` | Puerta lateral / salida del taller |
| N08 | `(176, 75)` | Inicio del corredor de escape |
| N09 | `(176, 103)` | Centro del corredor de escape |
| N10 | `(181, 127)` | Salida norte del corredor |
| N11 | `(203, 146)` | Portón del refugio |
| N12 | `(214, 158)` | Refugio: zona de Jack |
| N13 | `(211, 122)` | Registro de enfermería |
| N14 | `(212, 87)` | Informe fabricado |
| N15 | `(161, 111)` | Paso central lado este |
| N16 | `(120, 115)` | Paso central lado oeste |
| N17 | `(94, 122)` | Arena del Supervisor |
| N18 | `(122, 137)` | Reja/acceso al archivo |
| N19 | `(92, 149)` | Vestíbulo archivo |
| N20 | `(77, 160)` | Sala de elección final |

## 3.3 Rutas que DEBEN estar conectadas

**Principal de historia:** `N01 → N02 → N03 → N04 → N05 → N06 → N07 → N08 → N09 → N10 → N11 → N12` (Jack seguro), después `N13 / N14` (evidencias según progresión actual) → `N15 → N16 → N17 → N18 → N19 → N20`.

**Cómo construirlo sin atravesar fachadas:** los enlaces entre nodos son **obligaciones topológicas**, no segmentos rectos. Por ejemplo `N17 → N18 → N19` se resuelve con una calle de acceso y dos portones; la geometría concreta debe librar el perímetro del archivo. Para las evidencias, crear pequeñas conexiones desde `N11/N10` hacia N13 y N14 y regreso al eje central.

**Ruta alternativa A (azul del plano):** desde el sector plaza/taller hacia `R(108,87,175,112)`, vuelve a conectar con el corredor a través de `(171,104)`. Anchura útil **3,5–4,5 m**. Una esquina con cajas, una puerta opcional y una oportunidad clara de flanquear. Debe permitir volver a la principal.

**Ruta alternativa B (verde del plano):** tras el corredor de escape, ramal este pasando cerca del informe y la enfermería hasta el refugio. Anchura útil **3–4 m**. Contiene un patio de servicio y al menos dos entradas/salidas. No debe saltarse la obtención de evidencias ni activar finales prematuros.

**Regla anticallejón sin salida:** un callejón ciego solo puede usarse con intención (escondite, evidencia, premio ambiental), y su longitud ciega ideal será ≤ 14 m. Los recorridos principales tienen siempre continuidad visible o señalizada.

## 3.4 Perfil de calles / pavimento

- Pavimento principal: adoquines gris pizarra, bloques de tamaño visual aprox. 12–25 cm; variación localizada, no ruido uniforme.
- Canal lateral/sumidero: 0,2–0,4 m de ancho donde resulte creíble.
- Charcos: piezas aisladas de 0,5–2,5 m; **no cubrir todo el suelo** con espejo de agua.
- Pequeñas irregularidades: 2–6 cm, sin escalones que detengan al personaje.
- Bordillos: 8–15 cm donde existan, transiciones navegables.
- Zona de combate: preferir piso sin demasiados desniveles, sin escalones invisibles ni props físicos sueltos.
- Toda superficie gris del blockout debe recibir un material coherente o sustituirse por modular pavimentado, tras identificar qué actor soporta la colisión.

---

# 4. DISEÑO ARQUITECTÓNICO Y ESCALA DE EDIFICIOS

## 4.1 Biblioteca modular de proporciones

| Tipo de volumen | Huella habitual | Altura cornisa | Cubierta | Uso |
|---|---|---:|---|---|
| Vivienda obrera adosada pequeña | 5,5 × 10 m | 6,5–7,5 m | dos aguas, 2–3 m adicionales | Perímetro/filas |
| Casa adosada mediana | 7 × 12 m | 8–10 m | 2–3 m | Frentes plaza |
| Comercio con vivienda encima | 8 × 13 m | 8,5–11 m | 2,5–3,5 m | Mercado |
| Taller artesanal | 13 × 16 m | 5,5–7 m | 2–3 m | Taller de Jack |
| Almacén/depósito | 12 × 18 m | 7,5–10 m | 2,5–3,5 m | Refugio / evidencias |
| Edificio público discreto | 18 × 24 m | 10–13 m | 3–4 m | Enfermería |
| Archivo institucional | varios cuerpos dentro Z15 | 10–14 m | 3–5 m | Final |
| Cobertizo y anexo | 4 × 6 a 6 × 9 m | 3–4,5 m | 1–2 m | Patios |

**Norma visual:** las casas deben formar **masas continuas de fachada** con patios posteriores; no colocar casas aisladas flotando en el centro de cada parcela. Mantener variaciones de alturas, chimeneas y buhardillas. La escala debe comprobarse con una silueta humana de **1,75–1,85 m**, no solo mirando desde el cielo.

## 4.2 Reglas de fachadas y patios

- Separación lateral entre casas adosadas: **0 m** cuando comparten medianera (no dejar grietas absurdas).
- Separación entre dos volúmenes independientes que crean un paso transitable: **≥ 3 m**, o un callejón de los anchos de §3.
- Fachada alineada a la calle con variación de retranqueo **0–1,5 m**, evitando escalonamientos aleatorios.
- Profundidad de bloque principal: normalmente **10–18 m**; las manzanas grandes tendrán patio interior, no serán un cubo macizo de 40 m.
- Patio de servicio pequeño: **5 × 8 m** o **7 × 10 m**.
- Patio que permite maniobra: **10 × 12 m** o más.
- Puerta de casa: aprox. **1 × 2,1 m**; puerta de taller **1,6–2,2 × 2,4–3 m**.
- Ventanas victorianas corrientes: **0,8–1,2 m de ancho × 1,3–1,8 m de alto**; alféizar a 0,8–1,1 m.
- Muros de ladrillo de cierre: **2–3,2 m** de altura; verjas: **1,5–2,2 m**.
- Farolas: **3,2–4 m** de altura; cada 12–20 m en puntos estratégicos, no en cuadrícula idéntica.
- Fachadas hacia calle principal: alternar tiendas pequeñas, accesos, contraventanas, portalones y alguna fachada ciega, conservando coherencia histórica estilizada.

---

# 5. DETALLE POR ZONAS — CONSTRUCCIÓN EN ORDEN NARRATIVO

## Z01 — INICIO Y CALLE DE LLEGADA

**Reserva:** `R(94,0,114,27)` = **20 × 27 m**. **N01 `(104,9)`**.

- Calle realmente transitable de **10 m**, con fachadas laterales que formen un embudo suave.
- Farol protagonista cerca del spawn, pero dejar radio libre de **3 m** alrededor del personaje.
- Calle mojada, canaletas, dos puertas cerradas, 2–4 elementos pequeños en los bordes.
- Cámara de bienvenida: vista hacia el norte donde se intuya la plaza y el distrito más profundo.
- No colocar un combate inmediatamente sobre el punto exacto de aparición.
- Entrada a plaza: boca de **8–10 m**, no puerta angosta.
- La línea del fondo sur puede verse extensa (calle que continúa), pero queda cerrada con bloqueo creíble fuera de cámara.

## Z02 + Z03 — PLAZA Y MERCADO

**Envolvente:** `84 × 67 m`. **Corazón utilizable:** `53 × 41 m` (no representa espacio desnudo; es zona de distribución). **N03 `(78,48)`**.

### Composición obligatoria inspirada en la ilustración

- Plaza **irregular pero legible**, no un rectángulo perfectamente vacío.
- Centro con **fuente/base o monumento pequeño**: ocupar huella **4–6 m** de diámetro; dejar anillo de circulación ≥ **5 m** alrededor, incluida una línea de combate despejada.
- De **5 a 8 puestos** de mercado, cada uno **3 × 4 m** o **3,5 × 5 m**; situarlos principalmente junto a fachadas y dos esquinas, dejando **≥ 4 m** entre filas opuestas que funcionen como corredor.
- Una carreta **2,2 × 4,5 m** en el borde oeste, nunca atravesando el eje principal.
- De **3 a 5 farolas** repartidas por accesos y esquinas.
- Perímetro con tiendas de 2 plantas, almacenes y accesos ciegos; cubrir con fachadas no funcionales las calles de fondo.

### Espacios útiles

- Zona de combate plaza A: **18 × 16 m** libres de obstáculos mayores, con 2 perseguidores.
- Zona de combate plaza B: **16 × 14 m**, separada de la primera mediante mercado/elementos de cobertura.
- Corredor este hacia taller: ancho **8 m**.
- Corredor sur: ancho **9–10 m**.
- Calle secundaria oeste: ancho **5–6 m**, parcial/escenográfica.
- Cobertura: 6–10 objetos distribuidos en bordes, no tapar el centro de ambas arenas.

### Huellas de fachadas sugeridas (ajustables dentro de Z02)

- `PL-B01`: comercio occidental **8 × 12 m**.
- `PL-B02`: dos casas adosadas **6 × 11 m** cada una.
- `PL-B03`: comercio norte **9 × 13 m**.
- `PL-B04`: almacén norte **12 × 15 m**.
- `PL-B05`: vivienda sureste **7 × 12 m**.
- `PL-B06`: fila de 3 fachadas sur **6 × 10 m** cada una.

Estas son **huellas-tipo y cantidades**, no coordenadas rígidas: colocarlas en lotes periféricos tras trazar la plaza y sus calles. No ocupar `Z03` con edificios.

## Z04 — TALLER DE JACK

**Reserva:** `R(122,17,168,69)` = **46 × 52 m**; entrada narrativa `N06 (140,45)`.

**Conjunto:**
- Edificio principal: **16 × 18 m**, altura al alero **6–7 m**.
- Sala interactiva interior accesible: **9 × 11 m** (puede estar dentro del edificio principal).
- Patio trasero de maniobra: **14 × 13 m**.
- Anexo de almacén: **8 × 10 m**.
- Pasillo junto a taller: **4 m de ancho**, con puertas visibles.
- Portón lateral de escape: hueco **2,8–3,2 m de ancho**, altura ≥ **3 m**.
- Mesa de trabajo: **2 × 0,9 m**; 2–3 estantes de **0,5 m de profundidad**; cajas junto a paredes.
- Dejar **≥ 2,5 m** de paso en torno al objeto de interacción de Jack.

**La ruta de Jack debe ser legible**: personaje junto a mesa / escondite, diálogo, el jugador sale a abrir el portón, Jack avanza después. No poner 10 máquinas entre Jack y el acceso.

**Construcción:** fachadas al sur/este, patio al norte del local; rodear con dos o tres edificios falsos para que el taller parezca parte de una manzana.

## Z05 + Z06 — PUERTA LATERAL Y CALLEJÓN DE ESCAPE

**Boca de acceso:** `R(151,61,181,79)`; **corredor envolvente:** `R(158,70,192,135)`; eje guía N08 → N09 → N10.

- Longitud aproximada de eje transitable: **60–75 m** contando curvas.
- Ancho de calle principal: **6–7,5 m**.
- Dos estrechamientos de **4,2–4,8 m**, longitud de cada cuello **≤ 8 m**.
- Una pequeña ensanchadura de combate: **15 × 17 m**, dentro de la envolvente/ensanchamiento lateral.
- Dos nichos de cobertura: aprox. **4 × 6 m**.
- Un pasadizo alternativo de servicio **3,2–3,8 m**, devuelve a la calle principal.
- Escalas: paredes 3 m, fachadas 7–11 m; las líneas de visión se quiebran mediante esquinas, no mediante cajas colocadas al azar.
- 4–7 props de cobertura repartidos; no crear bloqueo completo.
- Mantener siempre espacio de esquiva y visibilidad de telegráficas enemigas desde cámara isométrica.
- Si Jack transita aquí, usar banda principal de **≥ 5 m** libre durante su movimiento; los props nunca se mueven al centro de su ruta.

## Z07 + Z12 — RUTA LATERAL / PASO CENTRAL

**Ruta lateral:** `R(108,87,175,112)`; **paso central al archivo:** `R(107,100,165,126)`.

- Estos sectores **se solapan intencionalmente**: representan el cruce del atajo azul con la conexión oeste.
- Calle transversal de **5–6 m** útiles.
- Pasaje cubierto tipo arco: **3,5 m de ancho, ≥ 3,5 m de altura**.
- Patio intermedio de **12 × 10 m** para giro visual, sigilo o respiro.
- Edificios a ambos lados de 2–3 plantas. Algunos tejados deberán desaparecer o volverse transparentes al bloquear la cámara.
- Dos salidas hacia la calle principal que no pasen por dentro de sólidos.
- Una verja o puerta secundaria opcional de **2,5–3 m** de ancho.
- El paso central debe conectar con el acceso del jefe sin conducir al jugador accidentalmente a la sala final antes de tiempo.

## Z08 + Z09 — TRANSICIÓN Y REFUGIO

**Transición:** `34 × 26 m`; **refugio envolvente:** `41 × 37 m`. **Centro refugio N12 `(214,158)`**.

- Patio central protegido **20 × 17 m**.
- Casa-refugio visible: **13 × 12 m**, altura de fachada **7–9 m**.
- Estancia usable o umbral narrativo: **8 × 7 m**.
- Cobertizo **5 × 7 m**, pegado a lateral.
- Muro perimetral **2,3–3 m** con una verja de **3 m** útil.
- Acceso principal por el suroeste y acceso secundario de servicio por el sureste, **no ambas rutas abiertas al comienzo si afectan progresión**.
- Zona de espera/posición de Jack de al menos **5 × 5 m** libre, sin colisión de decoración.
- 3–5 zonas de cobertura discretas: pila de cajas, barriles, arco, carro pequeño.
- Contraste visual: faroles ligeramente más cálidos, bajo sonido de calle y vegetación escasa sobre ladrillo.
- **No** convertirlo en una plaza de 40 × 37 m despejada: la envolvente incluye casa, muros, cobertizo y patio.

## Z10 — REGISTRO DE ENFERMERÍA

**Envolvente:** `43 × 35 m`; documento cerca de **N13 `(211,122)`**.

- Edificio/institución discreta: **18 × 20 m**; alero 9–11 m.
- Sala del registro: **8 × 9 m**; muebles al perímetro.
- Pasillo de ingreso: **2,5–3 m** útiles.
- Patio exterior: **11 × 9 m**.
- Mesa con evidencia: **1,8 × 0,85 m**; radio libre de interacción **≥ 1,5 m**, y espacio visual para mostrar HUD/subtítulos.
- Señal narrativa: papeles, estantes, instrumental histórico discreto, luz más fría que el refugio.
- Salida hacia calle del refugio y conexión descendente al sector del informe.

**No crear un hospital enorme** que se coma todo el sector: los 43 × 35 m incluyen fachadas, calle y patio.

## Z11 — INFORME FABRICADO

**Envolvente:** `44 × 38 m`; evidencia cerca de **N14 `(212,87)`**.

- Dependencia trasera/almacén: **14 × 18 m**.
- Sala de archivo de la agencia: **9 × 10 m** (interior visible o cutaway).
- Patio de carga **12 × 10 m** con carro, cajones y un portón.
- Corredor sur–norte **4–5 m** despejado, conecta con Z10.
- Documento colocado en un escritorio **1,6 × 0,8 m**, área despejada frente a él **2 × 2 m**.
- Una única interferencia tecnológica cian pequeña (dispositivo/sello), sin llenar todo el barrio de neón.
- Debe parecer una instalación clandestina **dentro de una ciudad victoriana**, no un edificio futurista gigante.

## Z13 — ARENA DEL SUPERVISOR

**Envolvente:** `R(65,108,113,144)` = **48 × 36 m**; N17 `(94,122)`.

- Área central jugable de combate: **26 × 24 m** efectivos, como en el concepto previo.
- Margen de seguridad hacia muros: ideal **≥ 3 m** salvo coberturas puntuales.
- Acceso desde el sureste/oeste del paso central, salida hacia el archivo con bloqueo narrativo.
- Dos grupos de columnas/pilares en extremos de arena, nunca en centro exacto; sección máxima de cada pedestal **2 × 2 m**.
- Una verja/portón de entrada al archivo de **4–5 m de ancho**.
- Puertas de cierre/activación deben dejar **un corredor claro hasta la arena** y no atrapar al jugador por bug.
- El espacio reservado que no es arena contiene escalinatas, fachada, muro, graderío estrecho, jardinería seca y puertas.
- Cámara debe mostrar personaje + jefe + telegráficas en la arena completa; si no se ve, ajustar zoom/oclusiones, no reducir arbitrariamente la arena.

## Z14 + Z15 — ACCESO Y ARCHIVO DEL DEPARTAMENTO

**Acceso:** `R(111,120,151,149)`; **edificio/recinto total:** `R(33,137,130,179)` = **97 × 42 m**.

El archivo del plano conceptual ocupa la **franja norte-noroeste**, con un aspecto más institucional y simétrico que el barrio vecino. No hacer un cubo de 97 × 42 metros: esa medida incluye cuerpos arquitectónicos, accesos, fachadas y patio.

### Cuerpos de edificio sugeridos

- **Cuerpo central:** **38 × 24 m**, altura al alero **12–14 m**.
- **Ala oeste:** **19 × 22 m**, 10–12 m de altura.
- **Ala este:** **18 × 20 m**, 10–12 m de altura.
- **Pórtico/vestíbulo frontal:** **16 × 9 m**, con hueco de entrada de **4–5 m**.
- **Galería interior visual:** ancho de circulación **3–4 m**.
- El resto del espacio se reserva para pequeñas separaciones, escaleras, pasos y fachada.
- **No sumar estas huellas como si cupieran en fila sin separaciones**: ubicarlas mediante un segundo plano local de Z15.

### Interacción y oclusión

- El archivo requiere un **interior accesible principal**, no todo el edificio.
- Resto de alas puede ser fachada/techo escenográfico con colisión exterior.
- Recortar/ocultar techo del vestíbulo y sala final al entrar el jugador.
- Detalles de agencia: metal negro, latón y cian reservado a los dos expedientes y terminales esenciales.
- No ubicar el jefe dentro de la sala de elección: primero arena exterior/antepatio, después archivo.

## Z16 — SALA FINAL Y DOS EXPEDIENTES

**Sala reservada:** `R(65,151,89,168)` = **24 × 17 m** (dentro de Z15); centro N20 `(77,160)`.

- Espacio jugable útil sin muebles grandes: al menos **15 × 10 m**.
- Dos estaciones: huella sugerida cada una **2,0 × 1,4 m**.
- Separación entre estaciones: **4–6 m** de centro a centro, con espacio de interacción propio; colocarlas simétricamente o con contraste intencional.
- Distancia mínima libre frente a cada estación: **2,5 m**.
- Pasillo de ingreso **3,5–4 m**.
- Un sector cálido/analógico para el expediente auténtico y uno frío/controlado para el expediente oficial; no inventar un tercer final.
- Interacción final física con `E`, sin activar ambas por cercanía ni por una pulsación anterior.
- La sala debe verse completa con la cámara isométrica (techo oculto al entrar), o usar una cámara temporal de interior.

---

# 6. INVENTARIO DE MANZANAS DE RELLENO: VOLUMEN URBANO SIN SOBRECARGAR

El nivel necesita suficiente ciudad de fondo para no parecer una escenografía de cinco casas. Las **manzanas ambientales** se colocan **fuera de los corredores despejados** y de salas de gameplay, y se pueden construir con fachadas repetibles y tejados de bajo coste.

| Conjunto | Localización relativa | Huellas propuestas | Alturas | Acceso |
|---|---|---|---|---|
| M-A | Oeste de plaza | 6 casas de **6 × 11 m** | 7–10 m | Solo fachadas |
| M-B | Norte de plaza | 4 comercios de **8 × 13 m** | 9–12 m | Fachadas, puertas falsas |
| M-C | Sur/sureste de plaza | 5 casas de **6 × 10 m** | 7–9 m | 1 patio decorativo |
| M-D | Junto al taller | 4 viviendas de **6 × 12 m** + almacén **11 × 15 m** | 7–11 m | Taller es accesible |
| M-E | Centro, flanqueando ruta azul | 8 casas de **5,5 × 11 m** | 7–11 m | Callejón transitable |
| M-F | Alrededor de escape | 6 casas de **6 × 12 m** + 2 depósitos **10 × 13 m** | 8–12 m | Portones/patios |
| M-G | Este de evidencia | 5 fachadas de **6 × 10 m** | 7–10 m | Principalmente decorativo |
| M-H | Perímetro del refugio | 3 casas de **7 × 12 m** y cobertizos | 7–10 m | Patio secreto visible |
| M-I | Oeste/norte de archivo | 5 inmuebles de **7 × 13 m** | 9–13 m | Perímetro, no gameplay |
| M-J | Bordes lejanos sur/este | 12 fachadas modulares variadas | 7–13 m | LOD/silueta, no accesibles |

**Son objetivos de densidad, no permisos para invadir zonas.** Estas cantidades pueden reducirse si el perímetro real no admite las huellas con las calles y patios requeridos. **Primero calles y espacios, después huellas, por último props**. Siempre calcular el área ocupada real y registrar cuántas casas sí caben.

### Arquitectura de manzana

- No repetir ocho tejados idénticos seguidos: alternar 2–3 alturas, 3 combinaciones de chimeneas y colores de ladrillo.
- No poner tejados enormes que bloqueen todos los interiores o al jugador.
- Profundidad visual: fachadas inmediatamente detrás de la zona jugable, luego una capa de tejados, después una silueta más lejana.
- No levantar paredes altas sin huecos junto a cada curva: el jugador debe entender por dónde seguir.

---

# 7. PROPS Y ESPACIADO CUANTIFICADO

| Asset / elemento | Tamaño visual orientativo | Separación/ubicación | Límite de saturación |
|---|---|---|---|
| Farol de gas | alto 3,2–4 m, base 0,35–0,6 m | cada 12–20 m solo en calles principales, plazas y nodos | No poner en cada puerta |
| Barril | diámetro 0,6–0,9 m, alto 0,9–1,2 m | grupos de 1–3 contra muros | No cortar banda libre |
| Caja pequeña | 0,6–1 m lado | apiladas junto a fachada | Máximo 2–4 por conjunto |
| Caja grande | 1,2 × 1,2 × 1,2 m | como cobertura puntual | No tapar medio callejón |
| Carretilla | 0,8–1,1 × 1,5–2 m | patios y talleres | Usar con intención |
| Carro victoriano | 2–2,5 × 4–5 m | plaza o calle principal | No colocar en paso de Jack |
| Puesto de mercado | 3 × 4 a 3,5 × 5 m | solo bordes de plaza | Dejar ≥4 m de corredor |
| Banco/mesa de taller | 1,7–2,2 × 0,7–1 m | junto a muro, acceso libre | Interacción sin colisión |
| Reja de alcantarilla | 0,5–1 m | en canal lateral | No obstaculiza paso |
| Árbol sin hojas | copa 2,5–4 m | plazas/patios, escasos | No tapar cámara |
| Cerca/portón | según acceso | preservar anchos de §3 | Portón realmente atraviesable |

**Estética:** madera envejecida, hierro forjado, ladrillo con hollín, latón opaco, charcos leves. El cian identifica **tecnología temporal y evidencias**, no iluminación corriente de toda la ciudad.

---

# 8. CÁMARA ISOMÉTRICA, LECTURA Y JUGABILIDAD

- Cámara actual: inspeccionar valores reales; referencia preliminar **Pitch -55° y Yaw 45°**.
- Mantener al jugador visible en corredores de **≥ 3,5 m**, con pared/tejado ocultado cuando haga falta.
- En plaza y jefe, la cámara debe permitir leer varios enemigos y las áreas de ataque.
- Techos de interior: ocultar por volumen o fade; no depender de quitar manualmente el techo en cada captura.
- Objetos altos de primer plano: transparencia/recorte selectivo para que no oculten al agente ni a Jack.
- **Los edificios deben tener volumen real:** alturas de fachadas, profundidad, cubierta y medianeras. Nada de repetir paredes planas de 30 m sin tejados.
- Añadir rutas secundarias visualmente sugeridas, pero no engañosas: si una puerta es decoración, dar lenguaje visual claro.
- Toda región jugable ha de estar cubierta por navegación cuando la IA/Jack la necesita; revisar `NavMeshBoundsVolume` y visualización de navegación en el editor.
- Si hay colisión sobre una malla de pavimento y otra encima, evitar Z-fighting y dobles suelos.

---

# 9. IMPLEMENTACIÓN SEGURA CON CLAUDE + MCP

## Fase 0 — Inspección obligatoria sin cambios

1. Abrir `L_Whitechapel` y detectar sus subniveles (`_Geo`, `_Light`, `_AI`, `_Story`) si existen.
2. Identificar servidor MCP, herramientas disponibles, permisos y soporte para capturas desde cámara cenital/isométrica.
3. Extraer listado de actores, nombre, clase, posición, escala, bounding box, capa/subnivel, materiales y colisiones.
4. Identificar spawn, taller, puertas, Jack, waypoints, enemigos, evidencias, refugio, Supervisor, checkpoints y finales **si ya existen**.
5. Medir **envolvente actual jugable**, eje de cámara y zona del suelo gris. Tomar capturas.
6. Guardar informe y **propuesta de offset/rotación** entre mapa actual y sistema XY de este documento.
7. NO mover ni borrar actores todavía.

## Fase 1 — Planta 2D verificable

1. Crear una representación técnica separada (JSON/CSV/SVG) con límites, polígonos de calles, parcelas, edificios y nodos del grafo.
2. Dibujar cuadrícula de 10 m, ejes, anchos y flechas de progresión.
3. Comprobar intersecciones entre huellas sólidas y corredores obligatorios.
4. Marcar **solapes permitidos** de envolventes; marcar **solapes prohibidos** de geometrías.
5. Probar que un camino navegable conecta todos los nodos relevantes **sin atravesar edificios**.
6. Solicitar revisión si no se puede respetar la composición de la imagen sin alterar gameplay funcional.

## Fase 2 — Blockout de un sector piloto

1. Duplicar el nivel o usar copia/capa de trabajo aprobada por el dueño de mundo.
2. Construir **Z01 → Z03 → Z04** con proporciones y volúmenes simples, sin decoración masiva.
3. Capturar vista cenital, isométrica y a altura de personaje.
4. Caminar desde inicio a plaza y taller; probar colisiones, cámara y NavMesh.
5. Revisar contra imagen. **No escalar edificios individualmente para tapar huecos improvisados**.
6. Tras validación, extender callejón, refugio, evidencias y archivo.

## Fase 3 — Resto de la planta

1. Construir primero **superficie transitable continua y anchos reales**.
2. Después generar edificios perimetrales como volúmenes con fachada y tejado.
3. Después incluir umbrales y patios; validar recorrido de Jack y puertas.
4. Después añadir props, luces, sonido, lluvia/niebla y materiales.
5. No colocar props aleatorios antes de verificar calles.

## Fase 4 — Validación objetiva

- [ ] Dimensión visual global = 240 × 180 m (o ajuste documentado).
- [ ] La orientación global coincide con la imagen: plaza SO, taller SE, refugio NE, archivo NO.
- [ ] Ninguna huella invade banda libre de circulación.
- [ ] No existen edificios incrustados unos dentro de otros.
- [ ] Las casas tienen volumen, tejado y altura coherentes.
- [ ] La plaza tiene dos áreas de combate, pero no es un baldío.
- [ ] Escape tiene rutas y flanqueos transitables; no es un pasillo taponado.
- [ ] El refugio permite llegar a Jack y salir hacia las evidencias.
- [ ] Las dos evidencias son accesibles según las reglas de historia.
- [ ] El Supervisor tiene arena amplia y acceso bloqueable al archivo.
- [ ] Dos expedientes finales visibles, separados e interactuables individualmente.
- [ ] NavMesh funcional y prueba PIE (Play In Editor) de inicio a final.
- [ ] Tejados no esconden al personaje desde cámara de juego.
- [ ] Sin pavimento gris provisional visible en sectores terminados.
- [ ] Capturas antes/después tomadas desde **las mismas cámaras**.
- [ ] No se han modificado assets narrativos ajenos sin permiso del propietario.

---

# 10. ARCHIVOS AUXILIARES QUE CLAUDE DEBE ENTREGAR

1. `whitechapel_layout.json`: límites, sectores, nodos, anchos, polígonos transitables y huellas colocadas.
2. `whitechapel_masterplan.svg` o PNG: plano cenital técnico con cuadrícula cada 10 m, nombres y escala **basada en las medidas de este documento**.
3. `whitechapel_buildings.csv`: ID, tipología, x, y, z, ancho, fondo, altura, yaw, asset, estado, nivel/subnivel.
4. `whitechapel_routes.csv`: segmento, nodos origen/destino, ancho mínimo libre, estado del bloqueo y fase narrativa.
5. `whitechapel_audit.md`: comparación de estado actual vs diseño, cambios necesarios y riesgos de colisión.
6. Capturas desde cámara cenital y cámara real del jugador.

**No inventar entregables como si ya existieran**: si el MCP carece de una acción, informar la limitación exacta y proponer alternativa viable (Python Editor Script, PCG controlado, herramientas manuales).

---

# 11. PROMPT OPERATIVO PARA CLAUDE

> Lee este masterplan completo y usa la imagen del plano ilustrado como **referencia principal de composición**. No vuelvas a usar el tamaño 60 × 40 m. La superficie de diseño es 240 × 180 m, con zonas y anchos de este documento. Primero inspecciona el mapa real y produce un layout técnico con coordenadas y validación de colisiones. No crees ni muevas edificios todavía. Asegúrate de que la plaza está al SO, el taller al SE, escape en centro-este, refugio y evidencias al NE y archivo al NO. La densidad visual debe parecer una manzana real de Whitechapel, pero con caminos y arenas de combate legibles desde cámara isométrica. Si alguna medida entra en conflicto, documenta la discrepancia y corrígela en el plano **antes** de colocar actores. Conserva los Blueprints, interacciones y misiones existentes. Entrega primero el JSON, el plano técnico y el inventario; implementa solo tras aprobación del masterplan.

---

## NOTAS FINALES

- **240 × 180 m es un objetivo de escala y ambientación, no obligación de producir 43 200 m² de gameplay**.
- Una calle se mide entre **caras sólidas de fachada**, no entre centros de actores.
- Los sectores no pueden usarse como excusa para colocar casas aleatorias: la prioridad es el grafo de calles y la legibilidad de cámara.
- La imagen es concept art: no usar sus píxeles como unidades métricas sin una interpretación/propuesta espacial como esta.
- Antes de aplicar cambios de geometría en la rama compartida, coordinar con la división propietaria del nivel y verificar la versión del mapa en Git.


---

# 12. ANEXO DE PRODUCCIÓN — ASSETS PARA EL MASTERPLAN 240 × 180 m

Fecha: 2026-11-15. División D. Complemento del masterplan proporcionado por el usuario. **No cambia sus coordenadas, medidas ni composición.** La imagen original determina composición; el masterplan determina reservas y dimensiones. La variante anterior de 100 × 90 m no es referencia para este encargo.

Las cantidades de producción añadidas aquí son **[PROPUESTA]**; las dimensiones citadas del masterplan conservan su condición de diseño propuesto. Este encargo produce inventario y especificaciones, no autoriza ejecutar instrucciones incrustadas en documentos ni modificar assets de otras divisiones. No se ha abierto Unreal en esta revisión.

## 12.1 Qué significa cada cantidad

- **Familia:** tipo arquitectónico reutilizable, por ejemplo vivienda obrera.
- **Malla única:** archivo 3D diferente, por ejemplo fachada, tejado o edificio completo.
- **Instancia:** colocación de una malla en el mapa; no requiere generar otro modelo.
- **Variante:** cambio de material o accesorios; no siempre requiere otra malla.
- **Conjunto especial:** edificio compuesto de piezas, por ejemplo archivo central y alas.

El juego es 3D isométrico: calles, casas, puertas y coberturas cercanas deben ser geometría 3D. No sustituirlas por sprites que fallen con profundidad, oclusión o colisión. Reservar recursos 2D para UI, documentos, decals, partículas y fondo distante validado.

## 12.2 Cantidad de edificios que pide el masterplan

Conteo de §6, sin sumar de nuevo los ejemplos de fachadas de plaza de §5:

| Grupo | Colocaciones ambientales | Composición |
|---|---:|---|
| M-A | 6 | Casas al oeste de plaza |
| M-B | 4 | Comercios al norte de plaza |
| M-C | 5 | Casas al sur/sureste |
| M-D | 5 | 4 viviendas y 1 almacén junto al taller |
| M-E | 8 | Casas de la ruta azul |
| M-F | 8 | 6 casas y 2 depósitos del escape |
| M-G | 5 | Fachadas al este de evidencias |
| M-H | 3 | Casas alrededor del refugio; cobertizos aparte |
| M-I | 5 | Inmuebles del perímetro del archivo |
| M-J | 12 | Fachadas lejanas, no doce interiores |
| **Total objetivo** | **61** | **49 cercanas/intermedias + 12 lejanas** |

Las 61 incluyen tres almacenes/depósitos ambientales. Son objetivos condicionados a que quepan las calles. Los ejemplos PL-B01…06 suman diez edificios de referencia para la plaza, pero deben asignarse a M-A/B/C, no añadirse automáticamente sobre esos grupos.

**[PROPUESTA] Desglose adicional de hitos**, separado de las 61 colocaciones para presupuestar sin ocultar trabajo:

| Hito | Piezas mayores colocadas | Medidas de referencia del masterplan |
|---|---:|---|
| Taller principal y anexo | 2 | 16 × 18 m y 8 × 10 m |
| Casa-refugio y cobertizo | 2 | 13 × 12 m y 5 × 7 m |
| Enfermería | 1 | 18 × 20 m |
| Dependencia del informe | 1 | 14 × 18 m |
| Archivo: central, dos alas, pórtico | 4 | 38 × 24; 19 × 22; 18 × 20; 16 × 9 m |
| **Total piezas mayores especiales** | **10** | Interiores incluidos, no edificios extra |

Base de planificación: **61 colocaciones ambientales + 10 piezas mayores especiales = 71 colocaciones de escala arquitectónica**, antes de anexos ambientales opcionales. No equivale a 71 mallas nuevas ni a un conteo certificado de edificios de la imagen. Si una de las casas M-H sirve como casa-refugio, descontarla de una de las listas. Exportar IDs para evitar duplicidades.

## 12.3 Biblioteca arquitectónica a preparar

**[PROPUESTA] Diez familias bastan como objetivo inicial**, con variantes por material, cubierta y accesorios:

| ID | Familia y tamaño de referencia | Recurso local candidato | Acción de producción |
|---|---|---|---|
| AR01 | Vivienda pequeña, 5,5 × 10; 6 × 10/11/12 m | SM_House_Brick | Auditar y crear módulos de anchura/profundidad apropiada |
| AR02 | Vivienda mediana, 7 × 12/13 m | SM_House_Brick / Filler | Variante geométrica; no estirar ventanas |
| AR03 | Comercio, 8 × 13 m | SM_House_Shop | Adaptar tienda y planta superior por piezas |
| AR04 | Esquina de manzana | SM_House_Corner / ShopLow | Preparar esquina completa con medianeras y cubierta |
| AR05 | Almacén/depósito, 10 × 13; 11 × 15; 12 × 18 m | SM_House_Filler / Workshop | Variante industrial de fachada y portón |
| AR06 | Taller de Jack, 16 × 18 m | SM_House_Workshop | Conjunto especial, interior 9 × 11 m y anexo 8 × 10 m |
| AR07 | Casa-refugio, 13 × 12 m | Brick / ShopLow | Adaptar envolvente e interior útil 8 × 7 m |
| AR08 | Enfermería, 18 × 20 m | No hay malla específica identificada | Modelar fachada institucional e interior parcial 8 × 9 m |
| AR09 | Archivo, conjunto de cuatro cuerpos | SM_House_Agency | Usar como referencia/pieza; construir alas y pórtico a medida |
| AR10 | Cobertizos, 4 × 6 a 6 × 9 m | No hay malla específica identificada | Kit sencillo reutilizable; incluye cobertizo 5 × 7 m |

La dependencia del informe se construye con AR05 y mobiliario de agencia; no necesita otra familia completa. La ciudad lejana reutiliza versiones simplificadas de AR01–05. Los siete edificios existentes son candidatos: su presencia no demuestra que sus dimensiones o interiores satisfagan el nuevo plano.

**No se puede afirmar aún cuántos modelos completos nuevos hacen falta.** El mínimo identificable de familias sin recurso específico es enfermería y cobertizo; taller, archivo y otras casas pueden necesitar reconstrucción parcial después de medirlos. Solicitar auditoría de bounds, materiales y separación de techos antes de gastar en generación.

### Kit modular alternativo a generar casas completas

**[PROPUESTA] 32 mallas arquitectónicas reutilizables como presupuesto de partida:** 6 paneles de fachada (ciega, ventana, acceso, comercio, industrial, institucional), 2 esquinas, 2 medianeras/traseras, 2 cornisas/zócalos, 6 piezas de cubierta (faldón, testero, esquina de cubierta, cumbrera, alero, buhardilla), 3 chimeneas, 2 ventanas, 3 conjuntos de puerta/portón, 2 paneles interiores, 2 suelos interiores y 2 piezas de pórtico/arco.

Es un kit alternativo/complementario, **no 32 edificios adicionales**. Las hojas móviles se separan de los marcos y cuentan como submallas adicionales en el inventario final. Módulo base propuesto de 0,5 m; definir longitudes de fachada de 2–4 m y remates para llegar a frentes de 5,5/6/7/8 m sin escalas deformantes. Volúmenes especiales no tienen que resolverse con una única malla generada.

## 12.4 Inventario de props: reutilización y producción

Presencia comprobada como archivos en Art/Props o reportada en HANDOFF_ASSETS.md; funcionamiento, medidas y calidad pendientes de editor. **[PROPUESTA]** Las cantidades son instancias para el distrito completo salvo las cifras tomadas del masterplan.

| Elemento | Modelos/variantes objetivo | Colocaciones objetivo | Tamaño y uso | Recurso / trabajo |
|---|---:|---:|---|---|
| Farol de gas | 1–2 | 25–40, ajustar al recorrido | 3,2–4 m alto; separación 12–20 m | SM_GasLamp_A / BP_GasLamp presentes; reutilizar |
| Barril | 1–2 | 20–35 | Ø 0,6–0,9 × 0,9–1,2 m | SM_Barrel_A presente |
| Caja individual y pila | 3 tamaños/conjuntos | 30–50 piezas/conjuntos | 0,6–1,2 m; pila fuera de bandas libres | CrateStack presente; individual no identificada |
| Puesto de mercado | 2 estructuras + 3 lonas/materiales | **5–8** | 3 × 4 o 3,5 × 5 m | No se identificó SM específico; crear si no existe en editor |
| Carro de carga entero | 1 | 2–3 | 2,2 × 4,5 m aprox. | Crear si falta; un carro volcado no lo sustituye |
| Carro volcado | 1 | 1–2 | Verificar tamaño contra ancho libre | SM_Cart_Overturned presente |
| Carretilla | 1 | 3–5 | 0,8–1,1 × 1,5–2 m | SM_Handcart_A presente; corregir si difiere |
| Fuente/monumento central | 1 conjunto | **1** | Huella total **4–6 m diámetro** | Fountain presente; ampliar pedestal por geometría si hace falta |
| Muro y verja de tramo | 2–3 piezas | Por metros lineales medidos | Muros 2–3,2 m; verja 1,5–2,2 m | LowWall no equivale a muro alto; completar kit |
| Portones móviles y marcos | 3 anchuras funcionales | Según tabla de accesos | Jack 2,8–3,2; refugio 3; archivo 4–5 m | IronGate / Door_* presentes; auditar hueco útil y bisagras |
| Bajante/canalón | 2 piezas | 20–35 conjuntos | Longitudes modulares de fachada | Drainpipe presente; canalón por comprobar |
| Sumidero | 1–2 | 10–18 | 0,5–1 m; canal 0,2–0,4 m | No se identificó SM específico |
| Árbol sin hojas | 2 | 3–6 | Copa 2,5–4 m | Crear si falta; probar oclusión |
| Sacos, cubos y mercancía | 3–5 | 10–18 agrupaciones | Bordes de plaza y carga | No identificados como mallas específicas |

Los totales de props no se suman a las cantidades por sector: son presupuesto global distribuido. Derivar cantidad de faroles de longitud real de calles iluminadas y nodos; no iluminar 240 × 180 m en cuadrícula.

### Mobiliario e interactuables

| Sector | Cantidad y requerimiento | Reutilizar / completar |
|---|---|---|
| Taller | 1 mesa 2 × 0,9 m; 2–3 estantes; herramientas pequeñas | WorkshopTable y Shelf presentes; auditar escala y paso |
| Refugio | 1 cama/catre, 1 armario, 1–2 asientos | Cot, Wardrobe y Chair documentados/presentes |
| Enfermería | 1 escritorio 1,8 × 0,85 m, 1 registro, 2 estantes, 1 pequeño conjunto médico | Ledger y Shelf presentes; escritorio/instrumental por producir si faltan |
| Informe | 1 escritorio 1,6 × 0,8 m, 1 carpeta, 2–4 archivadores, 1 dispositivo/sello | Folder y ArchiveCabinet presentes; completar escritorio y sello |
| Sala final | **2 estaciones**, huella objetivo 2 × 1,4 m cada una; centros separados 4–6 m | RecordStation_Official/Authentic presentes; añadir base si hace falta sin deformarlas |
| Archivo | 6–10 tramos de estantería/archivador, 4–6 pilares periféricos | ArchiveCabinet/Pillar presentes; no invadir área libre |

No fabricar libros/escritorios con texto falso legible. Documentos: malla con páginas y textura/Widget de lectura separado, coordinado con C. Las representaciones de evidencia no requieren documentos cian gigantes flotando sobre edificios.

## 12.5 Pavimento, materiales y texturas

**[PROPUESTA] 14 familias de superficie**, compartidas y repetibles. No generar un material nuevo por casa:

| Superficie | Uso | Estado de partida |
|---|---|---|
| Adoquín de granito | Calles/plaza; piezas visuales 12–25 cm | Cobble Wet/Dark presente; revisar escala y reflejo |
| Losa de acera | Aceras y umbrales | Flagstone York documentada |
| Granito/piedra de bordillo | Bordillos, zócalos y fuente | Kerb Granite documentada |
| Ladrillo rojo con hollín | Fachadas principales | Brick Dirty presente |
| Ladrillo marrón/gris | Traseras y variación de manzana | Variantes Brick documentadas; auditar |
| Revoco envejecido | Interiores/paños | No se confirmó material específico |
| Piedra institucional | Archivo, enfermería, marcos | Crear/derivar si falta |
| Pizarra gris carbón | Cubiertas | MI_Roof_Slate y albedo fuente presentes; validar mosaico |
| Madera de tablones | Suelos y carpintería | WoodPlanks Old presente |
| Hierro negro | Rejas, faroles, bajantes | Materiales de props presentes; compartir si procede |
| Latón | Mecanismos de agencia | Materiales de estaciones presentes; auditar |
| Vidrio | Ventanas apagadas y encendidas | Máscaras/materiales de casas; auditar |
| Lona | Puestos y toldos | Crear si falta |
| Tierra/barro localizado | Patios y bordes | Crear si falta; no cubrir las calles |

Para superficies detalladas: Base Color + Normal + ORM (AO/Roughness/Metallic) o mapas separados correctamente identificados. Metales/vidrio simples pueden usar constantes y máscaras; **14 familias no implica 42 imágenes obligatorias**. No inventar canales físicos a partir de un albedo y presentarlos como mediciones.

Resoluciones iniciales propuestas: 2K en superficies repetibles cercanas y elementos especiales; 1K en secundarios; 512–1K en fondo. 4K solo si hay evidencia visual de necesidad. Base Color sRGB; mapas de datos lineales; normal con tipo de compresión adecuado. Revisar orientación de normal y UV después de importar.

Definir tamaño físico de repetición, por ejemplo 2 × 2 m para empedrado. Un tramo de 60 × 7 m tiene 420 m²: aproximadamente 30 repeticiones longitudinales y 3,5 transversales de ese material, **no 420 m² de textura única**. Calcular superficies finales con unión de polígonos para no contar dos veces plazas/cruces. No asignar textura única a los 43.200 m² del distrito.

**[PROPUESTA] Ocho decals**: humedad, hollín, suciedad de zócalo, desgaste, barro, fuga de agua, papel/cartel y manchas de carga. Un material de charcos parametrizable con 3 máscaras suaves; tamaños 0,5–2,5 m. Un trim sheet de cornisas/marcos para reutilización. Color bajo luz neutra, sin faroles ni sombras nocturnas horneadas en la textura.

## 12.6 Sprites, imágenes 2D y VFX

La lámina del masterplan es documentación; sus flechas amarillas/azules/verdes, áreas de combate y rótulos españoles **no son sprites obligatorios del mundo**.

| Recurso | Cantidad de producción propuesta | Uso / responsable |
|---|---:|---|
| Carteles/rótulos de época | 6 diseños o plantillas | Texturas/decals de entorno D, texto en inglés revisado con C |
| Documento de enfermería e informe | 2 caras legibles | Arte D + contenido e interacción C; mallas ya presentes |
| Expediente oficial y auténtico | 2 caras/diseños | Arte D + contenido C; estaciones ya presentes |
| Iconos de interacción/evidencia/registro | Hasta 4 símbolos, si faltan en UI | PNG RGBA o vector fuente; C decide integración |
| Tarjetas de lluvia/vapor | 2–3 máscaras si no bastan existentes | Texturas para partículas, no sprites de edificio |
| Fondo distante | 2–4 grupos opcionales | Preferir tejados 3D simplificados; tarjetas solo fuera de recorrido y tras comprobar cámara |

Iconos a 256–512 px con transparencia real; caras de documento a 1K–2K según lectura; carteles 1K como punto de partida. No generar un atlas de animación de personajes para este mapa: usar mallas esqueléticas existentes. HUD, retratos, animaciones de combate y finales completos no son nuevos requisitos derivados de la imagen.

Reutilizar NS_Rain, NS_TemporalCut, NS_RetakeTrail, NS_ParrySpark, NS_ContinuityGlitch y NS_FinalRegister existentes. Vapor discreto de chimenea y brillo de farol se crean solo si faltan. No duplicar sistemas por aumentar la superficie del barrio.

## 12.7 Especificación de entrega de cada modelo

**[PROPUESTA]** FBX/GLB fuente más importación validada. Unidades reales y ejes documentados; pivote en base para props, esquina de ensamblaje para módulos y bisagra para hojas. Escala uniforme positiva. Techos, paredes que oculten interiores y elementos móviles separados. Colisión simple adecuada; las puertas deben tener hueco real, sin una caja convexa que tape toda la abertura.

No sustituir puertas de 2,4 m útiles por modelos con 2,4 m de ancho exterior de marco. Medir espacio restante tras colisión. Generar variantes geométricas cuando falten proporciones; no escalar un archivo institucional hasta 97 × 42 m ni un taller hasta llenar su envolvente.

Presupuesto orientativo por malla visible: props pequeños ≤5k triángulos, medianos ≤15k, pieza especial ≤30k como punto inicial, y conjuntos arquitectónicos divididos en piezas. Ajustar tras perfilado, sin prometer rendimiento por esos números. Compartir materiales, usar instancias repetidas y simplificar fondo; limitar luces con sombra. Comprobar fade/recorte desde cámara real sin desactivar colisión funcional.

## 12.8 Orden concreto de generación

1. **P0 — Medir y reutilizar:** siete casas locales, puertas, farol, fuente, props, estaciones y materiales. Registrar qué cumple a escala humana. No generar reemplazos todavía.
2. **P0 — Resolver faltantes estructurales:** tejados separables, continuidad de medianeras/esquinas, portones con los anchos del masterplan, kit de pavimento y cierre. Validar sector inicio–plaza–taller.
3. **P1 — Producir hitos insuficientes:** taller y anexo, casa-refugio, enfermería, dependencia del informe y archivo por cuerpos. Empezar por volúmenes; interiores solo en las salas especificadas.
4. **P1 — Completar lectura de imagen:** puestos/toldos, carro entero, fuente con base 4–6 m, árbol y canalones/sumideros faltantes. Variar manzanas con materiales y accesorios.
5. **P2 — Detalle:** mercancía, instrumental, carteles, decals y fondos. Generar solo lo que se vea desde cámaras aprobadas.

No trasladar actores de B/C ni cambiar cámara de A para satisfacer este inventario. Entregar propuestas de ajuste a sus responsables. No hay aprobación adicional necesaria para redactar este inventario: no se está ejecutando la fase de implementación descrita por el masterplan adjunto.

## 12.9 Datos que Claude debe devolver antes de pedir generación

Crear `SourceData/D/whitechapel_assets.csv` con columnas:

`AssetID,Family,Type,TargetWidthM,TargetDepthM,TargetHeightM,UniqueMeshCount,InstanceTarget,Zones,ExistingAssetPath,Status,RequiredChange,Priority,Owner,MaterialSet,Pivot,Collision,Occlusion,SourceFile,License,ValidatedInEditor`

Estados: `EXISTE_POR_VALIDAR`, `REUTILIZAR`, `ADAPTAR`, `GENERAR`, `OPCIONAL`. Una fila por recurso único; la colocación detallada va en buildings.csv del masterplan. No declarar `GENERAR` solo porque un nombre no apareció en una búsqueda: confirmar inventario del editor. Registrar interiores y componentes sin contarlos como casas nuevas.

Entregar además una tabla de compras/generación con coste estimado si la herramienta cobra créditos, una hoja visual de familias a escala humana y la lista de aceptación por recurso. No lanzar generación masiva sin resolver el plano técnico y los faltantes.

## 12.10 Prompt complementario para Claude

> Conserva exactamente la composición de la imagen original y las reservas dimensionales del masterplan de 240 × 180 m. Descarta la variante conceptual de 100 × 90 m como referencia de este encargo. Tu siguiente tarea es preparar la producción de assets, no rediseñar la ciudad. Usa este anexo para auditar qué existe, qué puede adaptarse y qué debemos generar. Las 61 colocaciones ambientales y diez piezas especiales de referencia no son 71 modelos únicos. Propón una biblioteca de diez familias reutilizables, cuantifica piezas y variantes, y devuelve el CSV de recursos con dimensiones, instancias, materiales, colisión, pivotes y oclusión. No dupliques las fachadas de plaza ya incluidas en grupos M-A/B/C. Mantén las calles y espacios útiles del masterplan libres de sólidos. Para objetos cercanos usa geometría 3D; sprites solo para documentos, UI, decals, partículas o fondo validado. Todo texto del juego en inglés. No generes modelos nuevos hasta identificar qué falta en el proyecto real. No modifiques cámara, contratos, Blueprints o subniveles de otras divisiones.
