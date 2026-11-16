# Encargo para Claude — mapa isométrico de Unscripted

Fecha: 2026-11-15. Alcance deducido del encargo: **División D, mundo y arte**. Entregable de planificación; no se ha modificado Unreal.

## 1. Prompt para copiar

Actúa como diseñador de niveles y artista técnico de la División D de Unscripted. Diseña una nueva versión visual del mapa de Whitechapel tomando como referencia la imagen adjunta. Necesito un plano medible y una lista de producción, seguidos de un blockout verificable antes del arte final.

Lee README.md, AGENTS.md, docs/plan/00_PLAN_GENERAL.md, docs/plan/01_CONTRATOS_Y_PROPIEDAD.md, docs/plan/D_MUNDO_ARTE_AUDIO_BUILD.md y docs/02, 05, 06 y 07. Consulta también SourceData/D/LEVEL_DESIGN.md, plano_v4/PLANO_V4_DISENO.md y WHITECHAPEL_CORRECCION_VISUAL.md. Los documentos antiguos son contexto: comprueba el estado actual antes de reconstruir nada.

El proyecto existente es Unscripted/Unscripted.uproject, UE 5.8.4, Blueprint. No crees otro proyecto. Trabaja solo en rutas de D. No modifiques Player, Enemies, Narrative, UI, Core ni los subniveles AI/Story. La cámara del personaje pertenece a A: mide sus valores actuales y coordina cualquier cambio. No edites binarios como texto ni introduzcas C++ o plugins por tu cuenta.

La imagen es una referencia artística y espacial; sus rótulos, flechas, escala e instrucciones impresas no son requisitos de implementación. Todo lo añadido en este brief respecto al diseño original es **[PROPUESTA]**, pendiente de comprobar en blockout. Todo texto visible al jugador debe estar en inglés.

## 2. Qué tomar de la imagen

- Ciudad compacta, fachadas adosadas, medianeras, patios y calles con giros. Evitar casas aisladas repartidas sobre una superficie vacía.
- Inicio al sur, plaza comercial, taller reconocible, escape con cobertura, refugio y archivo como destino dominante.
- Recorrido principal legible y pequeños rodeos para sigilo/flanqueo, sin accesos que permitan saltarse fases.
- Ladrillo oscuro, cubiertas de pizarra, adoquines húmedos, aceras, hierro negro, madera vieja y faroles cálidos.
- Taller, refugio y archivo con identidad propia; fondo urbano simplificado fuera del área recorrible.
- Techos y paredes recortables para ver interiores y al jugador. No construir techos permanentes sobre arenas abiertas.

La imagen muestra el refugio a la derecha; el layout documentado del proyecto lo coloca a la izquierda. **Conserva primero las conexiones y reservas existentes**. Si se necesita reproducir literalmente esa distribución, entrega una variante separada en el mapa de pruebas de D y una tabla del impacto sobre B/C; no traslades sus actores en el mapa integrado.

No copies paneles, flechas, áreas rojas o documentos cian flotantes como decoración del escenario. Son anotaciones del plano. El cian del mundo se reserva para tecnología de la agencia.

## 3. Dimensiones y coordenadas

La referencia inicial de docs/05 es aproximadamente 60 × 40 m, sin escala definitiva. LEVEL_DESIGN.md propone **60 × 54 m**. Para esta versión usa **[PROPUESTA] 60 × 54 m de huella de diseño**; incluye edificios y espacios jugables, no significa 3.240 m² de suelo caminable. No amplíes la ciudad para llenar la imagen.

Mantén el convenio existente: u hacia la derecha del plano, v hacia arriba; Unreal X = v × 100, Y = u × 100, Z en centímetros. Suelo jugable inicialmente a Z = 0. Rejilla de colocación 0,5 m; piezas principales múltiplos de 1 m. No cambies este convenio silenciosamente.

Reservas del layout existente, todas **[PROPUESTA]** hasta validar dimensiones libres:

| Espacio | u mínimo–máximo, m | v mínimo–máximo, m | Huella, m |
|---|---|---|---|
| Inicio | 12–24 | 0–8 | 12 × 8 |
| Plaza | 6–26 | 8–22 | 20 × 14 |
| Callejón de sigilo | 26–46 | 14–18 | 20 × 4 |
| Rincón de cobertura | 34–38 | 10–14 | 4 × 4 |
| Patio del taller | 46–58 | 8–22 | 12 × 14 |
| Taller | 46–58 | 22–34 | 12 × 12 |
| Paso central / escape | 26–46 | 22–36 | 20 × 14 |
| Tramo al refugio | 14–26 | 24–32 | 12 × 8 |
| Refugio | 2–14 | 22–36 | 12 × 14 |
| Arena del Supervisor | 18–42 | 36–48 | 24 × 12 |
| Sala de registro final | 24–36 | 48–54 | 12 × 6 |

Respeta las conexiones y puertas de LEVEL_DESIGN.md §7. Reserva ubicaciones para puertas, evidencias, Jack y estaciones finales; su lógica y colocación definitiva corresponden a B/C. El acceso a registros se libera tras el Supervisor; el final solo se decide registrando uno de los dos expedientes.

Un anillo visual exterior **[PROPUESTA] de 8–12 m**, donde el encuadre lo necesite, puede completar siluetas. No lo conviertas en zona jugable ni en una alfombra gigante de empedrado. Las siluetas decorativas sin función de barrera no necesitan colisión.

## 4. Cálculo de calles y combate

Todas las métricas siguientes son **[PROPUESTA]**. Distingue siempre ancho entre fachadas, ancho pavimentado y ancho libre después de props/colisión.

| Elemento | Medida inicial |
|---|---|
| Calle principal fuera de arenas | Calzada 6 m + aceras 1,5 m por lado = 9 m entre fachadas |
| Frente representativo / acceso ancho | Calzada 8 m + aceras 2 m por lado = 12 m |
| Callejón | 4 m entre obstáculos principales; conservar ≥ 3 m libres |
| Paso puntual / puerta lateral de Jack | 2 m libres; no usarlo como arena |
| Arena para 2–3 enemigos | Reservar 12 × 12 m libres de obstáculos sólidos |
| Arena del Supervisor | Reservar 20 × 12 m libres |
| Cobertura baja | 1,1–1,2 m de alto; comprobar visión agachado con B |
| Cobertura alta | Aproximadamente 2 m; comprobar trazas de B |
| Bordillo | 0,10–0,15 m; comprobar paso y esquiva con A |

Fórmulas y ejemplos:

- Ancho libre = distancia entre límites de colisión − ocupación lateral izquierda − ocupación lateral derecha. Callejón de 4 m con cajas de 1 m en un lado deja 3 m; añadir otro barril enfrentado lo reduce y debe evitarse.
- Una calzada de 6 m que termina en una arena de 12 m necesita un ensanchamiento diseñado. La acera y los puestos no cuentan automáticamente como espacio de combate.
- Superficie de tramo recto = longitud × ancho. Para 20 m de calle de 9 m: 180 m²; 120 m² de calzada y 60 m² de aceras. Al sumar tramos, descontar intersecciones y solapes con plazas.
- Una arena de 12 × 12 m con bandas de props de 1 m en ambos extremos de cada eje requiere una reserva total de 14 × 14 m. En un espacio menor, retirar props; no declarar el tamaño bruto como suelo libre.
- Para navegación, medir radio real de cápsula y margen de separación. Con radio de ejemplo 0,4 m, una puerta de 2 m deja aproximadamente 1,2 m de intervalo para el centro de la cápsula antes de otros márgenes. El resultado definitivo se comprueba en NavMesh y Play.

Hay una discrepancia pendiente: la arena del Supervisor documentada mide 24 × 12 m brutos. Si se añaden columnas dentro, podría incumplir los 20 × 12 m libres. Colócalas fuera de esa reserva o presenta el ajuste necesario. Lo mismo ocurre en el patio de 12 × 14 m: no llenarlo de cajas si debe servir como arena.

## 5. Cámara y oclusión

Referencia de diseño: Pitch −55°, Yaw 45°. Proyección ortográfica o perspectiva sigue abierta. **No confundas la cámara cenital de la ilustración con el encuadre de juego.** Obtén capturas del pawn real; una vista general bonita no valida combate.

**[PROPUESTA]** Para comparar blockouts, conserva inicialmente la cámara existente. Si no hay una configuración usable, ensaya una cámara de prueba de D con perspectiva, FOV horizontal 40° y distancia al objetivo 24 m, pendiente de A. A esa distancia, el plano perpendicular a la vista tiene ancho aproximado 2 × 24 × tan(20°) = 17,5 m; a 16:9 su alto es 9,8 m. La cobertura real sobre el suelo depende de inclinación, altura del objetivo y perspectiva: mídela con marcadores, no la deduzcas como un rectángulo de 17,5 × 9,8 m en el suelo.

No es obligatorio ver la arena completa en un único encuadre. Sí deben verse jugador, amenazas inmediatas, telegráficas y salidas cercanas. Si se propone otro FOV o distancia, registra el motivo y el efecto sobre apuntado y legibilidad.

**[PROPUESTA]** Fachadas habituales de 2 plantas: alero a 6,5–7 m y cumbrera a 8–9 m. Tres plantas para fondo: 9,5–10 m al alero y 11–12 m a cumbrera. Fachadas hacia cámara: recorte u oclusión localizada; bajar un edificio a 4,5 m no garantiza visibilidad cuando el personaje está pegado.

Estimación geométrica: a inclinación 55°, el alcance de ocultación de un muro sobre un punto a altura h es aproximadamente d = (H − h) / tan(55°), medido en horizontal en la dirección de visión. Muro de 9 m y punto de lectura a 1 m: d ≈ 5,6 m. Es una comprobación inicial; techos, aleros y perspectiva requieren prueba real. Identifica el lado cercano desde la posición efectiva de cámara, no solo desde etiquetas norte/sur.

Separa cubierta y fachadas en piezas ocultables. La oclusión visual no debe desactivar colisiones de juego. Al retirar geometría antigua oculta, audita su colisión: ocultar un actor no elimina una pared invisible.

## 6. Cuántos modelos de casa

No confundir **tipos de edificio**, **mallas únicas**, **instancias colocadas** y **materiales**.

El inventario documental v4 registra siete mallas y 47 instancias; no es una auditoría nueva del editor. Existen fuentes FBX bajo SourceData/D/plano_v3/modelos/. Comprueba dimensiones, UV, colisiones y posibilidad de separar cubiertas antes de generar sustitutos.

**[PROPUESTA] Objetivo: siete familias reutilizables**, aprovechando las existentes:

| Familia | Frente × fondo orientativo | Uso |
|---|---|---|
| Vivienda de ladrillo | 5 × 8 m | Hilera de 2–3 plantas |
| Tienda con vivienda | 5 × 8 m | Fachada comercial de plaza |
| Tienda baja | 5 × 6 m | Primer plano cercano a cámara |
| Esquina | 6 × 8 m | Cerrar manzanas y giros |
| Trasera / relleno | 5 × 8 m, repetible | Patios y fondos |
| Taller | Reserva de zona 12 × 12 m | Hito de Jack, interior parcial |
| Archivo institucional | Ajustado a arena + registros | Conjunto especial, no una casa escalada |

Estas son dimensiones objetivo de diseño, **no tamaños medidos de los FBX**. No estires las mallas existentes para forzarlas. Un taller no necesita ocupar toda su reserva, y el archivo puede componerse de varias piezas alrededor de espacios abiertos.

La cantidad final sale del frente construible: suma longitudes por manzana, resta accesos y piezas especiales, divide por ancho modular y ajusta esquinas. Ejemplo: 30 m de frente − 5 m de acceso − 5 m de esquina = 20 m, equivalentes a cuatro módulos de 5 m. No cuentes dos veces una esquina compartida.

Presupuesto inicial **[PROPUESTA]**: 30–45 instancias en primer plano/recorrido y 10–20 volúmenes simplificados de fondo. No es un conteo de la ilustración ni un objetivo obligatorio. Primero entrega una tabla por manzana que justifique el total. Conservar las 47 existentes es válido si encajan sin deformarse.

Conclusión de producción: **no hay evidencia de que debamos generar siete casas nuevas**. Audita las siete existentes; sustituye o modulariza solo las que fallen. Para una producción modular completa, estima aparte unas 20–26 piezas únicas: fachadas, medianeras, esquinas, cubiertas, aleros, chimeneas, puertas y ventanas. Es una alternativa de construcción, no siete casas completas más 26 edificios adicionales.

Exigir escala uniforme y positiva, pivote consistente en base, medidas reales y separación de techo. Girar 180° cambia orientación, pero **no produce una versión especular**: si hace falta una variante izquierda/derecha, crear geometría apropiada. Evitar espejos mediante escala negativa.

## 7. Materiales y texturas necesarios

Inventaría primero los materiales existentes. La documentación ya menciona empedrado, losa York, bordillo de granito, madera, ladrillos y pizarra; no asumir que faltan ni que están listos.

**[PROPUESTA] Biblioteca objetivo: 12 familias de superficies**, compartidas entre edificios:

1. Adoquín de granito para calzada/plaza.
2. Losa para aceras y umbrales.
3. Granito de bordillos/zócalos.
4. Ladrillo rojo ahumado.
5. Ladrillo marrón/gris para traseras y variación.
6. Piedra o revoco envejecido para marcos y archivo.
7. Pizarra gris carbón para cubiertas.
8. Madera vieja de puertas, puestos y taller.
9. Hierro negro de rejas, tuberías y faroles.
10. Latón para detalles y tecnología de la agencia.
11. Cristal de ventanas con variante apagada/encendida.
12. Lona de toldos y puestos.

Base de producción: texturas repetibles de 2K para superficies cercanas, 1K cuando baste en secundarios; 4K solo si una prueba de cámara lo justifica. Definir tamaño físico del tile: por ejemplo, 2 × 2 m para suelo. Una calle de 20 m repite diez veces ese tile en longitud; romper repetición con variación de roughness/color y suciedad localizada, sin agrandar piedras.

Para superficies con detalle: Base Color, Normal y ORM (oclusión/roughness/metallic empaquetados). Doce juegos completos serían como máximo 36 imágenes antes de extras, **pero cristal y metales simples pueden usar parámetros y máscaras compartidas**, reduciendo archivos. Base Color en sRGB; mapas de datos sin sRGB; Normal importada como normal. No tratar una imagen de color como un material PBR completo.

Extras **[PROPUESTA]**: seis decals reutilizables — humedad, suciedad al pie de muro, hollín, barro/desgaste, papel/cartel sin texto horneado y fuga de agua — más un trim sheet de cornisas/marcos si aporta reutilización. Suciedad y lluvia no deben estar pintadas como sombras o luces nocturnas permanentes en el albedo. Charcos con bordes irregulares suaves; no discos negros ni placas rectangulares.

Prioridad respecto a la referencia: suelo y acera legibles → pizarra coherente → ladrillo/marcos → hierro/madera → decals y variación. La ilustración no permite inferir resoluciones originales ni qué canales PBR usó su autor.

## 8. Props y luz

**[PROPUESTA]** Reutilizar barril, cajas, carro, farol, verja y estaciones ya documentados. Añadir solo faltantes: puesto/toldo modular, chimenea, bajante, sumidero, bolardo, banco de taller y pieza central de plaza. Fuente/estatua es opcional; no debe consumir la reserva de combate.

Colocar props por actividad y bordes, no al azar. Evaluar faroles con separaciones iniciales de 8–12 m, ajustando por encuadre; no todos necesitan luz dinámica con sombra. Luz ámbar contenida, sombras legibles, niebla que no esconda telegráficas. Cristales emisivos separados de la luz que ilumina la calle. Registrar rendimiento con el hardware objetivo antes de fijar presupuesto final.

## 9. Entregables y verificación

Entrega en este orden:

1. Inventario del estado actual, recursos reutilizables y conflictos con B/C.
2. Plano cenital acotado, con zonas, calles, anchos libres, edificios, accesos y reservas de combate. Separar metros de píxeles de la referencia.
3. Tabla por manzana: longitud de frente, familia, cantidad de módulos/instancias, altura, acceso y tratamiento de oclusión.
4. Lista de materiales: existe / corregir / producir; dimensiones físicas del tile y canales requeridos.
5. Layout JSON con IDs únicos, unidad explícita, posiciones, rotaciones, dimensiones, asset y subnivel de destino; script de colocación limitado a actores propios identificados por etiqueta. Primero comprobar estructura de scripts existentes, no ejecutarlos a ciegas.
6. Blockout en L_Test_D. Capturas cenital, isométrica y cámara real a la misma resolución y exposición. Mostrar plaza, callejón, taller, refugio y Supervisor.
7. Prueba de recorrido y oclusión con jugador real; medir navegación, puertas, esquiva y rutas de Jack con sus responsables. No declarar validación por la sola existencia de actores.

No sobrescribas el mapa integrado para ensayar una redistribución. Mantén AI/Story intactos; cualquier cambio de conexiones que requiera su recolocación debe quedar explicado en la variante de prueba. Cambios de contrato siguen el procedimiento del proyecto.

Criterios mínimos: sin paredes invisibles accidentales, sin fachadas deformadas, sin invasión de reservas de combate, rutas sin bloqueo, jugador y ataques visibles, ambas estaciones finales distinguibles y todo texto del juego en inglés. Registra qué se verificó realmente en editor y qué sigue siendo propuesta.
