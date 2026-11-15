# Londres del siglo XIX: atlas de calles, objetos y plan de enriquecimiento de Whitechapel

**Documento de investigación histórica + revisión artística + instrucciones de producción para Unreal Engine**  
**Periodo de referencia principal:** Londres, especialmente Whitechapel y Spitalfields, **c. 1880–1890 (escenario objetivo: 1888)**.  
**Proyecto:** videojuego de ambientación victoriana oscura y estilizada, con elementos anacrónicos de una agencia temporal.  
**Fecha de elaboración:** 15 de noviembre de 2026.

> **Propósito.** No se trata de representar una “ciudad medieval tenebrosa”, sino una metrópoli industrial real: densa, comercial, trabajadora, húmeda, desigual, activa y contradictoria. Esta guía distingue **[H] constatación histórica**, **[I] inferencia verosímil** y **[F] propuesta de ficción/dirección artística**. Las capturas aportadas se usan como punto de partida de arte y composición, no como documentación de edificios históricos precisos.

---

## 0. Resumen ejecutivo: qué cambiar en las escenas existentes

Las capturas compartidas muestran una **base legible para un juego isométrico**: calles empedradas, edificios altos y estrechos, superficies de piedra y ladrillo, iluminación nocturna y un diseño oscuro relativamente cohesionado. La principal oportunidad no es elevar el realismo gráfico, sino **dar identidad funcional a cada tramo de calle**. En su estado actual, las escenas se leen fácilmente como un decorado victoriano genérico; deben comunicar *qué personas viven ahí, qué oficio se realiza en cada local, por dónde circulan carros y agua, qué fue reparado y qué está deteriorado*.

**Cambios de mayor impacto visual y menor costo:**

1. **Microarquitectura a nivel peatonal:** escaparates, marcos de madera, puertas de servicio, persianas, toldos, rótulos, escalones, sótanos con reja y escaparates cerrados. Las plantas bajas deben variar mucho más que las superiores.
2. **Diseño creíble del suelo:** calzada de adoquines rectangulares de granito, acera elevada con losas, bordillos, canal de desagüe, sumideros, parches y charcos localizados; evitar un único patrón de adoquín por todo el ancho.
3. **Ecología del trabajo:** carros de mano, barriles, cajas, sacos, herramientas de taller, balanzas, cestos, leña, carbón, textiles, residuos orgánicos y embalajes. Colocar objetos por actividad, no aleatoriamente.
4. **Iluminación que cuente historia:** faroles de gas ámbar tenue en ejes públicos, luz interior cálida irregular, zonas oscuras entre lámparas y **cian reservado exclusivamente** a la tecnología de la agencia temporal.
5. **Ruido visual con jerarquía:** anuncios envejecidos, un tablón de avisos, una señal esmaltada, un número de casa, humo de chimenea y manchas de humedad; no cubrir toda pared de calcomanías.
6. **Vida cotidiana indirecta:** una ventana con cortina, ropa tendida en un patio, un balde de carbón, lámpara en trastienda, puerta entornada; el escenario puede contar historias sin NPCs numerosos.
7. **Variedad de siluetas:** remates de chimenea, aleros, buhardillas puntuales, canalones, bajantes, parapetos, diferencias de dos a cuatro plantas, esquinas diagonales y medianeras visibles.
8. **Señales del conflicto narrativo:** el expediente oficial ordena y corrige; el entorno auténtico acumula huellas humanas. La agencia debe sentirse añadida sobre un Londres existente, no ser su estilo dominante.

### Matriz rápida de observación de las cinco capturas

| Área visual | Lectura general | Riesgo | Instrucción |
|---|---|---|---|
| Fachadas | Unidad estética útil; superficies relativamente repetidas | Calle con aspecto de escenario modular uniforme | Variar plantas bajas, huecos de ventanas, puertas, ladrillos y rótulos; evitar que todas las fachadas tengan la misma edad |
| Pavimento | Buen plano continuo para navegación | Todo parece la misma textura y la misma antigüedad | Separar calzada, acera y canal; hacer bandas de desgaste y reparación |
| Iluminación | Noche victoriana reconocible | Contraste demasiado uniforme o faroles decorativos sin efecto funcional | Pools cálidos localizados y áreas de sombra; interiores encendidos con criterio |
| Utilería | Espacios despejados para gameplay | Falta identidad de oficios y habitantes | Crear agrupaciones de props con relación causal: puesto → cajas → basura → lámpara |
| Atmósfera | Ambiente sombrío consistente | Niebla homogénea aplana distancia y materiales | Capas de neblina, humo localizado, siluetas y focos visuales |
| Espacios de decisión | Intersecciones/pasos útiles | Entradas y rutas pueden parecer intercambiables | Hitos narrativos, señales de dirección y arquitectura reconocible |
| Tecnología anacrónica | El cian puede dar identidad a la agencia | Si se repite, pierde valor y confunde con luz histórica | Reservar cian para anomalías, líneas de máquina y expediente alterado |

**Precaución de lectura visual:** al no contar con mediciones ni planos técnicos de las capturas, estas son recomendaciones cualitativas. No se infieren medidas exactas, materiales de fábrica ni estado de Blueprints a partir de imágenes.

---

# PARTE I — CÓMO ERAN LAS CALLES DE LONDRES EN EL SIGLO XIX

## 1. Una ciudad, muchas ciudades

### 1.1. Diferencias espaciales

[H] El Londres de fines del XIX combinaba centros financieros y administrativos, barrios acomodados, mercados, industrias y áreas densamente habitadas por trabajadores. Whitechapel y Spitalfields no eran un vacío abandonado: eran territorios de comercio, migraciones, talleres, hospedajes baratos y vías de gran tránsito. El *Survey of London* documenta el eje mercantil de Whitechapel High Street/Whitechapel Road, la fundición de campanas, el hospital y la creciente presencia de comunidades migrantes.

- **West End acomodado:** plazas, fachadas más regulares, mejores escaparates, accesos controlados y espacios de representación social. No tomarlo como plantilla para Whitechapel.
- **City comercial:** edificios de oficinas, almacenes, tráfico intenso, pavimentos reforzados, comerciantes y transportistas.
- **Whitechapel High Street / Whitechapel Road:** gran avenida de intercambio; locales sucesivos, anuncios, carros, peatones, mercados y elementos institucionales.
- **Spitalfields / calles laterales del East End:** vivienda subdividida, pequeños comercios, talleres, patios traseros, almacenes, pensiones y pasajes.
- **Entornos de muelles y ferrocarril:** depósitos, grúas, depósitos de carbón, paredones, cargas, herrería, fachadas industriales; no repartir estos elementos por todo Whitechapel.

### 1.2. Gradiente de riqueza y mantenimiento

La variación más convincente se logra **en pocos metros**: una calle principal comercial bastante transitable, seguida por un pasaje angosto más deteriorado. Las fronteras no eran estancas. Evitar el cliché de que todo el East End estaba cubierto de basura y edificios ruinosos; aun en la pobreza existían comercios prósperos, limpieza localizada y vida comunitaria. [H/I]

### 1.3. Ritmos de un mismo sitio

- **Amanecer:** descarga de mercancías, barrido, apertura de puestos, humo inicial de chimeneas.
- **Mañana:** tránsito de compradores, carros, vendedores ambulantes y trabajadores.
- **Atardecer:** retirada de toldos, cierre de persianas, lámparas interiores y faroles que comienzan a dominar.
- **Noche:** pubs, hospedajes, guardias, caminantes, transportistas tardíos; no una calle uniformemente desierta.
- **Lluvia:** charcos por pendiente, barro en juntas, reflejos rotos y huellas de ruedas.

## 2. Sección transversal de la calle

### 2.1. Calzada

[H] **No existía una superficie única universal.** Se documentan adoquines rectangulares de granito (*setts*), macadán, pavimento de madera, asfalto experimental y otras soluciones, dependiendo de época, zona y presupuesto. La City tenía extensas superficies de granito a mediados del XIX; también se probó asfalto desde 1869. Para la Whitechapel jugable de 1888, los *setts* son una elección artísticamente sólida, **pero no deben darse por obligatorios en cada calle**.

**Modelar:** unidades de granito gastado, juntas ligeramente desalineadas, bordes pulidos por ruedas, reparaciones localizadas con distinto tono y parches de grava. Diferenciar áreas con circulación frecuente de las pequeñas vías traseras.

### 2.2. Aceras y bordillos

[I] Diseñar la acera como un sistema separado: losas planas irregulares, un bordillo definido, desnivel pequeño respecto a calzada y rampas puntuales para carga. En torno a fachadas puede haber peldaños, registros de sótano, rejas y desniveles por sucesivas reparaciones. No usar el mismo adoquín en acera y calzada si no existe motivo arquitectónico.

### 2.3. Desagüe superficial

[I] Añadir pendiente visible o implícita hacia los bordes, rigolas, sumideros de hierro fundido y acumulación de hojas, paja, lodo y restos pequeños **junto** al agua. Las charcas deben aparecer donde el agua podría detenerse: juntas hundidas, bordes, zonas deprimidas o bajo una bajante defectuosa. Evitar reflejos perfectos y uniformes en todas las piedras.

### 2.4. Cruces y esquinas

[I] Un cruce plausible precisa radios pequeños, bordillos desgastados, protección de esquina en algunos edificios, puertas orientadas hacia la intersección y espacio de giro. Una esquina con pub/tienda genera un hito muy eficaz en cámara isométrica. Las calles principales pueden tener un ancho mayor y una lectura más abierta que los courts y alleys.

### 2.5. Sonido del suelo

[H] El granito soportaba tráfico, pero las ruedas y herraduras producían ruido intenso; el lodo, el polvo y el estiércol eran problemas constantes. La diferencia con callejones de suelo irregular se puede expresar mediante audio, partículas y marcas de circulación.

## 3. Materiales de construcción y cómo envejecen

### 3.1. Ladrillo

- Ladrillos rojizos, marrones y amarillentos, muchos ennegrecidos por humo.
- Variación por lotes de reparación: fragmentos de tonalidad distinta, mortero de otra edad.
- Manchas verticales bajo cornisas y bajantes; humedad concentrada cerca de suelo.
- Carbonilla en rincones protegidos y a sotavento; menos ennegrecimiento donde corre agua.
- No aplicar suciedad máxima en todas las superficies: la gradación crea historia.

### 3.2. Piedra y estuco

- Dinteles y vierteaguas de piedra; algunas fachadas con estuco envejecido.
- Desconchones en esquinas, zócalos golpeados por carros, cantos reparados.
- Diferenciar una institución reformada de una casa estrecha con mantenimiento precario.

### 3.3. Madera

- Marcos de tienda, persianas, puertas, mostradores, cajas y carros.
- Pintura descascarada en zonas de contacto; madera hinchada u oscurecida por humedad.
- Escaparates y puertas comerciales no deben parecer piezas metálicas modernas.

### 3.4. Hierro

- Rejas de sótano, barandillas, herrajes, clavos, soportes de farol, bajantes, bisagras y defensas de esquina.
- Óxido moderado y localizado, no naranja uniforme sobre todo el objeto.

### 3.5. Cristal

- Cristales pequeños o medianos según el edificio, con reflejos discretos.
- Algunas ventanas con condensación o suciedad, otras limpiadas para vender mercancía.
- Escaparates iluminados como contrapeso a la penumbra exterior.

## 4. Fachadas y composición del frente urbano

### 4.1. Tipos de edificios para kit modular

1. **Casa de ladrillo con tienda abajo:** 2–4 plantas, escaparate, entrada lateral, ventanas seriadas.
2. **Casa de hospedaje barato:** puerta ancha con cartel, ventanas desiguales, aspecto usado; no convertirla automáticamente en ruina.
3. **Pub de esquina:** rótulo dominante, vidrio, puerta en esquina o chaflán, lámpara exterior; edificio reconocible.
4. **Taller de oficio:** doble puerta, banco de trabajo interior, señales de cargas y materiales.
5. **Almacén:** vanos grandes, portón, arco de carga, marcas de transporte.
6. **Vivienda estrecha:** entradas al patio, conductos de lluvia, cortinas y ropa ocasional en interior.
7. **Edificio público/institucional:** mayor solidez, composición más regular, inscripción labrada puntual.
8. **Patio y cobertizo:** ampliación improvisada pero estructuralmente razonable detrás de la calle.

### 4.2. Gramática de fachada

**Suelo → comercio / puerta → pisos habitados → remate → chimeneas.** Variar al menos dos de esos cinco niveles entre módulos contiguos. Un conjunto de edificios puede compartir alineación sin compartir diseño. Colocar ventanas de una misma casa con ritmo coherente; el caos no equivale a aleatoriedad absoluta.

### 4.3. Cubiertas y perfil del cielo

- Chimeneas múltiples de ladrillo y sombreretes de barro.
- Canalones, bajantes, antenas modernas **prohibidas**.
- Tejados de pizarra o teja según edificio; buhardillas donde proceda.
- Siluetas escalonadas en vez de una muralla de cornisas idénticas.
- Humo visible desde puntos concretos, no desde cada chimenea.

## 5. Luz, noche, clima y visibilidad

[H] Londres incorporó iluminación de gas desde 1807; para 1842 la mayoría de las calles principales estaban iluminadas. Esto **no** significa que cada callejón fuera luminoso. El gas tuvo una presencia esencial durante 1888, mientras que las luces eléctricas existían en contextos particulares sin convertirlas en la norma visual de Whitechapel.

**Reglas para el juego:**

- **Farol público de gas:** halo amarillento limitado, vidrio algo empañado, pequeño punto de luz visible desde lejos, sombra suave e imperfecta.
- **Local abierto:** fuga cálida desde interior, diferente del farol de la vía.
- **Ventana doméstica:** baja intensidad, algunas apagadas; vida humana sugerida.
- **Puesto portátil:** farol de aceite/parafina como prop opcional, sin sustituir indiscriminadamente al alumbrado público.
- **Niebla:** densidad sutil en calle principal, algo mayor en callejón húmedo; no cubrir completamente el suelo ni ocultar interacción.
- **Cian de la agencia [F]:** color excepcional y narrativo; no añadirlo a letreros comerciales, faroles normales, agua ordinaria o luces de viviendas.

**Separar lluvia de suciedad:** pavimento mojado = material con roughness variable; suciedad = decal o capa material; niebla = volumen. Son tres sistemas distintos.

## 6. Agua, saneamiento, residuos y olores

[H] Las calles recibían estiércol de caballos, polvo, lodo y residuos; hubo barrenderos y trabajadores dedicados a retirar estos materiales. Durante el siglo XIX aumentó la infraestructura de agua y alcantarillado, pero sus condiciones y cobertura cambiaban por barrio. La presencia de desagües no convierte Whitechapel en una cloaca abierta continua.

**Agregar con moderación:** montoncitos de paja, huellas de ruedas mojadas, polvo bajo aleros, carbón cercano a almacenes, papeles atrapados en esquina, virutas cerca de carpinterías, vegetales descartados junto a un puesto, canalón que gotea. **No** colocar huesos, excrementos o basura en cada metro.

## 7. Transporte y movimiento

- **Carros tirados por caballos [H]:** reparto, carga, transporte de personas. Para el juego bastan uno estacionado y otro sugerido acústicamente.
- **Carros de mano y carretillas [H]:** excelente relación coste/valor visual.
- **Ómnibus de tracción animal [H]:** reconocible en avenida amplia; no en pasaje estrecho.
- **Trenes y ferrocarril [H]:** propios de nodos y viaductos, no omnipresentes.
- **Tranvías [H, dependiente de fecha y línea]:** comprobar cuidadosamente la fecha y localización específica antes de modelar una línea. Las fotografías de 1890–1910 **no son automáticamente pruebas de 1888**.
- **Excluir:** automóviles corrientes, semáforos eléctricos modernos, cableado tipo red contemporánea, señales viarias actuales y asfaltado moderno homogéneo.

## 8. Comercios, mercados y oficios

[H] La vida en la calle incluía vendedores de comida, ropa, mobiliario y artículos domésticos. Mayhew y la investigación sobre la vida callejera documentan formas diversas de venta y trabajo. Para arte conviene mostrar **sistemas completos de venta**.

| Tipo | Señal visual | Props vinculados |
|---|---|---|
| Verdulero | toldo de lona, cesta abierta | cajas, sacos, hojas, balanza, precios escritos a mano |
| Pescadería | mesa lavable, recipientes | cubos, barril de agua, cajas, paños |
| Ropa usada / tejidos | telas colgadas y mesas | retales, rollos, cuerda, cajones |
| Zapatero / cuero | mesa de cuero y herramienta | hormas, botas, recortes, martillos |
| Herrero / cerrajero | portón, piezas de hierro | tenazas, herraduras, piezas metálicas |
| Panadería | letrero y vitrina | bandejas, canastas, sacos de harina |
| Pub | esquina señalizada | barriles, jarras, puerta doble, lámpara |
| Casa de empeños | letrero y vitrina protegida | reja, mercancía pequeña, persiana |
| Imprenta | cartel y papel apilado | paquetes de hojas, marcos y avisos |
| Alojamiento | placa exterior | pizarra de tarifas, maletas, farol |

**Nota cultural:** Whitechapel contó con múltiples comunidades migrantes. Si hay textos, vestimenta y comercios específicos, investigar su localización y época; evitar caricaturas y etiquetas étnicas indiscriminadas.

## 9. Carteles, anuncios y lenguaje gráfico

- Rótulos **pintados a mano** sobre madera, vidrio o pared.
- Letras de época legibles, con uno o dos tamaños principales por fachada.
- Anuncios de oficio y nombre, no anuncios de marcas inventadas modernas.
- Placas de calle y números de casa donde sirvan para orientación.
- Cartelería de horarios, precios, remates y espectáculos; empapelados parcialmente cubiertos.
- Variantes limpias y deterioradas del mismo cartel para contar cambio temporal.
- **Regla de legibilidad:** textos grandes solo en puntos de interés; el resto puede ser pseudotipografía atmosférica revisada para evitar errores o palabras sin sentido.

## 10. Personas y cultura material

Para un mapa de juego corto no se necesitan multitudes con IA avanzada. Funciona mejor la presencia indirecta: sombra tras una ventana, siluetas lejanas, ropa colgada en patio, un puesto atendido a través de audio, ruedas que se escuchan tras un muro. Si se incluyen NPCs, deben corresponder al tipo de calle y horario; evitar vestimenta de aristócrata en todos los habitantes.

## 11. Lo que un jugador debería escuchar

- Cascos y ruedas sobre granito, irregularidades de frecuencia.
- Voces de mercado a distancia, sin repetir una misma frase audible cada pocos segundos.
- Golpes de madera, cadenas, cierre de una puerta, campanas lejanas.
- Chisporroteo localizado de lámpara, goteo, viento entre esquinas.
- Más personas en la calle comercial, más resonancia y silencio relativo en el patio.
- **Agencia temporal [F]:** pulso metálico, cinta rebobinada, armónicos fríos y pequeños cortes en la ambientación histórica.

---

# PARTE II — WHITECHAPEL EN 1888: MICROZONAS PARA EL JUEGO

## 12. Avenida comercial

**Función:** presentar que Londres sigue vivo pese a la historia oscura. **Silueta:** frente continuo de dos a cuatro alturas con locales de planta baja heterogéneos. **Suelo:** calzada firme y aceras separadas. **Iluminación:** faroles públicos y escaparates. **Props:** 2–3 toldos, cartel de tienda, carro de mano, cajas de reparto, un caballo sugerido fuera de cuadro. **Audio:** tránsito, regateos, ruedas.

**No hacer:** avenida completamente vacía, diez faroles idénticos equidistantes, diez fachadas iguales con barro por todas partes.

## 13. Calle residencial de trabajo

**Función:** transición hacia la investigación. **Silueta:** casas estrechas, acceso a talleres y patios. **Suelo:** losas desiguales, canal y parches. **Props:** escalón gastado, cubo de carbón, persiana medio cerrada, una ventana con cortina, tendedero parcial. **Audio:** discusión al fondo, un martillo, agua.

## 14. Pasaje / court / alley

**Función:** vulnerabilidad, atajo o secreto. **Silueta:** paredes cercanas pero con pequeñas diferencias de alineación y puerta secundaria. **Iluminación:** sombra con luz indirecta desde una boca del pasaje. **Props:** desagüe, cajón, canalón, reja de sótano, dos o tres papeles. **Audio:** gotas y eco. **Gameplay:** una curva que oculte parcialmente el siguiente tramo sin romper legibilidad.

**No hacer:** callejón con basura hasta las rodillas ni charcos tan brillantes que parezcan espejos.

## 15. Patio de carga

**Función:** espacio jugable de transición, combate ligero o pista. **Silueta:** almacén, portón, pared trasera y cobertizo. **Props:** carro inclinado, pilas de barriles con soporte físico, sacos apilados, mesa de taller y lona. **Luz:** única lámpara y resplandor de ventana elevada. **Claves de interacción:** zona de evidencia sobre el banco; rutas desbloqueables con objetos entendibles.

## 16. Esquina con pub o tienda de referencia

**Función:** hito de orientación. **Silueta:** chaflán o entrada destacada, letrero colgante, cristal y cortina. **Props:** barril, letrero, marco de puerta, pequeño farol. **Composición:** cálido contra calle fría. Puede permanecer parcialmente cerrado por la hora.

## 17. Zona de expediente oficial y estación auténtica [F]

El conflicto narrativo permite representar **dos lecturas del mismo sitio**:

- **Corte oficial / estación fría:** orden excesivo, evidencia catalogada, herrajes negros bien conservados, una máquina central con cian rectilíneo y tenue. La calle circundante debe conservar materiales victorianos.
- **Versión auténtica / estación cálida:** iluminación doméstica dorada, documentos desordenados pero legibles, pertenencias personales, rastros de ocupación real y reparaciones. No es “más sucia” por definición: es más humana.

**Regla crítica:** los objetos temporalmente alterados deben contrastar con 90 % de escenario históricamente plausible. La excepción sólo funciona si existe una norma convincente.

---

# PARTE III — AUDITORÍA ARTÍSTICA DE LAS CINCO CAPTURAS

## 18. Diagnóstico general de composición

La dirección artística actual apunta a **estilizado oscuro / semirrealismo simplificado**, apropiado para cámara isométrica. En estas condiciones, la lectura de silueta y función es más importante que microdetalle PBR. Las escenas muestran una oportunidad especialmente clara para trabajar en tres capas:

1. **Macro:** variación entre fachadas, anchura de la calle, volumen de esquina y hitos.
2. **Meso:** toldos, portones, bancos, faroles, carros, pasos, chimeneas y puestos.
3. **Micro:** barro, pequeños residuos, humedad, pintura saltada, números, papel y goteo.

**Orden:** corregir macro antes de poblar con microdetalle. Un callejón con cien decals seguirá pareciendo genérico si su planta baja y su recorrido no tienen intención.

## 19. Qué mantener

- El carácter nocturno y la paleta desaturada.
- La perspectiva alta y la separación visual entre superficie transitada y obstáculos.
- El uso de materiales envejecidos, evitando su saturación y ruido excesivos.
- La regla del cian como acento extraordinario.
- El enfoque modular que permite terminar la jam sin construir una ciudad completa.

## 20. Qué intervenir en las capturas (instrucciones comunes)

| Frente | Acción en escena | Asset / implementación | Resultado |
|---|---|---|---|
| Suelo | Romper uniformidad entre acera/calle | `SM_Curb_Straight_A`, `SM_Curb_Corner_A`, `MI_GraniteSetts_Wet`, `MI_SidewalkSlab` | Calle con jerarquía y circulación creíble |
| Bordes | Añadir canal y uno o dos sumideros en puntos bajos | `SM_Gutter_Straight_A`, `SM_Drain_CastIron_A` | Agua situada con lógica |
| Fachadas | Diferenciar 30–50 % de plantas bajas visibles | `BP_Shopfront_Modular`, `SM_Shutter_Wood_A`, `SM_Door_Service_A` | Identidad comercial y doméstica |
| Alturas | Variar chimeneas y aleros | `SM_Chimney_Stack_A/B`, `SM_GutterPipe_A` | Silueta menos repetitiva |
| Trabajo | Crear 2 grupos coherentes de oficio | `BP_PropCluster_Greengrocer`, `BP_PropCluster_Leatherworker` | Escena habitada sin saturación |
| Iluminación | Reducir fill general y concentrar luz cálida | `BP_GasLamp_Street`, `BP_WindowLight_Warm` | Atmosfera victoriana legible |
| Señalización | Incorporar 1 hito principal y 3 detalles secundarios | `SM_ShopSign_Bracket`, `DEC_StreetName`, `DEC_Poster_1880s` | Orientación sin HUD excesivo |
| Narrativa | Una microhistoria por recorrido | marcas de reparación, ventana habitada, puesto abandonado | Contexto ambiental |

### Por qué no conviene agregar cientos de objetos de inmediato

En cámara isométrica el jugador resuelve primero geometría y contraste. Un adorno exagerado puede tapar huellas, puertas, marcadores o rutas. La densidad de props debe crecer en **bolsas funcionales** (fachada comercial, patio de carga, puesto, umbral) y disminuir en el centro de circulación. Cada bolsa tiene un propósito arquitectónico o narrativo.

---

# PARTE IV — CATÁLOGO DE ASSETS PROPUESTOS

## 21. Convención de producción

- `SM_` Static Mesh; `BP_` Blueprint; `M_` Material maestro; `MI_` Material Instance; `DEC_` Decal; `FX_` Niagara/VFX; `SFX_` sonido.
- Categorizar por `Street`, `Facade`, `Commerce`, `Domestic`, `Industrial`, `Narrative`.
- Preparar variantes A/B/C de objetos repetibles, reutilizando materiales.
- Pivote en base del objeto y orientaciones constantes para ensamblado en editor.
- Mantener escala coherente con el personaje y ajustar proporciones **por lectura de cámara**; no falsear medidas que no se han medido.

## 22. P0 — imprescindible para la escena

| ID | Asset | Diseño visible | Dónde colocarlo | Implementación económica |
|---|---|---|---|---|
| P0-01 | `SM_Curb_Kit` | bordillo piedra recto, esquina y terminación | límites acera/calle | kit de 3–4 piezas |
| P0-02 | `SM_Gutter_Drain` | canal oscuro, rejilla de hierro | puntos bajos | 2 meshes + decal húmedo |
| P0-03 | `SM_Shopfront_Kit` | marco escaparate, puerta, dintel | plantas bajas | 3 módulos + 4 materiales |
| P0-04 | `SM_Awning_Fabric_A/B` | lona beige/manchada sostenida en varillas | puestos y tiendas | malla ligera, 2 variantes |
| P0-05 | `SM_ShopSign_Hanging` | rótulo madera/metal colgante | pub, tienda, taller | texto por textura |
| P0-06 | `SM_Cart_Hand_A` | carro manual de dos ruedas, madera | comercio, patio | una malla, prop estático |
| P0-07 | `SM_Crate_Sack_Barrel_Set` | cajas, sacos, barriles cohesionados | reparto | kit modular con instancias |
| P0-08 | `SM_Chimney_Pots` | chimeneas y sombreretes | tejados visibles | 2–3 tipos reutilizables |
| P0-09 | `SM_Downpipe_Iron` | bajante de hierro y abrazaderas | fachada y esquina | módulos rectos/codos |
| P0-10 | `BP_GasLamp_Street` | poste negro + caja de vidrio ámbar | vía principal | mesh + luz + estado on/off |
| P0-11 | `DEC_SurfaceStory_Set` | suciedad, marcas de rueda, humedad | puntos lógicos | decals reutilizables |
| P0-12 | `BP_WindowLife` | cortina/silueta/emisión tenue | ventanas seleccionadas | material unlit/emissive sutil |

## 23. P1 — mucho valor si hay tiempo

| ID | Asset | Descripción | Relación con el escenario |
|---|---|---|---|
| P1-01 | `SM_HorseTrough_Granite` | abrevadero pétreo con placa pequeña | esquina o vía de tránsito de animales |
| P1-02 | `SM_DrinkingFountain_IronStone` | fuente pública victoriana sobria | cruce/plazoleta; colocar sólo si hay espacio |
| P1-03 | `SM_FilingCart_Parcel` | carro de reparto con bultos y lona | almacén/mercado |
| P1-04 | `SM_Pub_Corner_Set` | puerta, rótulo, cristales y barriles | esquina memorable |
| P1-05 | `SM_BasementGrate_CellarDoor` | reja, trampilla, escalón | viviendas y tiendas |
| P1-06 | `SM_WoodenShutter_Closed` | persiana de tienda | horarios nocturnos |
| P1-07 | `SM_CoalBin_Bucket` | carbón, cubeta, pala | puerta de servicio |
| P1-08 | `SM_Washline_BackCourt` | cuerda con prendas discretas | patio interior |
| P1-09 | `SM_Greengrocer_Stall` | puesto de verduras, cestas, balanza | eje comercial |
| P1-10 | `SM_Leatherworker_Props` | banco, hormas, recortes, lámpara | taller/escena de investigación |
| P1-11 | `SM_WallNoticeBoard` | anuncios superpuestos | cerca de tienda/plaza |
| P1-12 | `SM_CornerProtector_Iron` | defensa metálica en arista | rutas de carro |
| P1-13 | `FX_ChimneySmoke_Low` | humo leve estacional | 2–3 chimeneas destacadas |
| P1-14 | `FX_GutterDrip` | goteo localizado con charquito | tubería defectuosa |

## 24. P2 — opcional y de alto costo

| ID | Asset/sistema | Condición para incluirlo |
|---|---|---|
| P2-01 | carruaje con caballo animado | sólo si cruza realmente una vía visible y requiere gameplay |
| P2-02 | multitud de mercado con IA | sólo si se puede controlar cámara, colisiones y rendimiento |
| P2-03 | infraestructura de tranvía | sólo tras verificar ubicación y año histórico exactos |
| P2-04 | cielo industrial volumétrico | sólo si mejora siluetas sin nublar la navegación |
| P2-05 | estructura interior completa de pub | sólo si el jugador entra |
| P2-06 | sistema dinámico de lluvia y charcos | preferir material y VFX puntuales salvo que la lluvia sea mecánica central |

## 25. Assets hero para el relato de la agencia [F]

1. `SM_TemporalFilingCabinet_Hero`: archivador negro lacado, latón envejecido, cian mínimo; colocarlo en estación de expediente, no en la calle ordinaria.
2. `SM_TemporalPillar_Hero`: pilar de maquinaria con engranajes, tuberías y franja cian; integrado en una sala o rincón intervenido.
3. `SM_VictorianWorkbench_Hero`: banco de trabajo con cuero y herramientas; puente entre oficio real y pistas de la historia.
4. `SM_OverturnedCart_Hero`: carro volcado que justifica bloqueo, cobertura u obstáculo legible.
5. `SM_DrinkingFountain_Hero`: hito urbano distinto de un farol, adecuado si el mapa incluye espacio público.
6. `SM_InvestigationEvidence_Kit`: expediente, sello, tablero de evidencia y documentos que cambian entre versión oficial y auténtica.

**Importante:** los objetos tecnológicos son una capa secundaria sobre la reconstrucción histórica y sus diseños actuales de la biblia de arte. El carácter anacrónico debe percibirse intencional.

---

# PARTE V — COMPOSICIONES PROPUESTAS PARA TRANSFORMAR LAS CAPTURAS

## 26. Propuesta A: “Calle comercial viva, noche húmeda”

**Antes (lectura):** calle victoriana oscura con poca especificidad comercial.  
**Después (objetivo):** calles y tiendas de Whitechapel que siguieron funcionando en 1888.

**Montaje, de fondo a primer plano:**

1. Diversificar cuatro fachadas consecutivas: una tienda de tejidos, una casa con acceso lateral, un taller de cuero y una pequeña tienda cerrada.
2. Colgar dos toldos de lona desiguales; no hacerlos idénticos.
3. Incluir un farol de gas en un punto focal y luces cálidas de interiores distintos.
4. Colocar carro manual con dos sacos, tres cestas y una balanza frente a **una** tienda.
5. Añadir bordillos, canal de agua y un sumidero cerca de la esquina.
6. Crear un área de charco roto en el borde; textura de calzada semihúmeda pero no espejo completo.
7. Integrar un letrero colgante a un tercio de la vista y un anuncio mural pequeño al fondo.
8. Reservar el centro libre para locomoción y lectura de combate.

**Paleta:** ladrillo rojo humo, ocre gastado, madera pardo oscuro, granito gris azulado, ámbar suave; nada cian salvo un elemento narrativo excepcional.

## 27. Propuesta B: “Callejón de evidencia, Londres real bajo una anomalía”

**Antes (lectura):** corredor oscuro y atmosférico.  
**Después (objetivo):** callejón plausible y localizable, con una evidencia precisa.

**Montaje:**

1. Reducir uniformidad de ambas paredes: una bajante, una puerta de sótano, una ventana con reja y un arco o pequeño retranqueo.
2. Colocar un farol **fuera** del callejón que ilumine su entrada; conservar oscuridad interior.
3. Añadir un peldaño desgastado, canal de agua lateral y goteo bajo tubería.
4. Situar una caja abierta con una pieza de evidencia que el jugador distinga por material, silueta o interacción.
5. En la anomalía, un único hilo cian de máquina/agencia en la parte posterior, sin teñir toda la escena.
6. Diferenciar corte oficial y auténtico cambiando 2–3 evidencias, una lámpara y un documento, **sin rehacer todo el nivel**.

**Paleta:** piedra y ladrillo gris carbón, marrón mojado, ámbar distante; cian focal y controlado.

## 28. Propuesta C: “Patio de carga y taller”

**Montaje:** portón de almacén + carro volcado + banco de trabajo + pilas de sacos. Añadir un canalón, una escalera corta, ventana alta cálida y residuos de madera alrededor de la mesa. Es un sitio ideal para esconder un objetivo que se descubra al girar una esquina, pero debe dejar un corredor limpio hacia la salida.

## 29. Propuesta D: “Esquina reconocible con fuente pública”

**Montaje:** hito de piedra (fuente/abrevadero), poste de gas, fachada de pub cerrada, rótulo perpendicular y un carro de reparto al fondo. No usar simultáneamente fuente, monumento, quiosco y gran máquina en un cruce pequeño: se pierde jerarquía.

---

# PARTE VI — INSTRUCCIONES DIRECTAS PARA UNREAL ENGINE

## 30. Construcción por capas

**Paso 1 — Greybox:** fijar recorrido principal, bifurcaciones, visibilidad de hitos, zonas de colisión y anchura jugable.  
**Paso 2 — Calle:** suelo por secciones, acera, bordillo, canal y esquinas.  
**Paso 3 — Fachadas:** sustituir 30–50 % de las plantas bajas del tramo central por módulos de comercio y servicio.  
**Paso 4 — Props funcionales:** colocar kits según oficio y tipo de vía.  
**Paso 5 — Luz:** faroles cálidos, algunas ventanas; sombras leíbles.  
**Paso 6 — Decals y VFX:** suciedad motivada por física, goteo y humo limitado.  
**Paso 7 — Narrativa:** añadir props de agencia y variaciones de expediente.  
**Paso 8 — Optimización y QA:** revisar desde cámara final y con iluminación de gameplay.

## 31. Blueprints reutilizables recomendados

### `BP_GasLamp_Street`

**Componentes:** StaticMesh, PointLight o SpotLight, material emissive del vidrio, volumen opcional de niebla/partículas. **Variables:** `bLit`, `IntensityPreset`, `FlickerStrength` (normalmente muy bajo), `WarmColor`. **Uso:** definir encendido sin reconstruir farol; la lámpara no debe parpadear como neón averiado de manera permanente.

### `BP_Shopfront_Modular`

**Componentes:** base modular, cartel, toldo, persiana opcional, escaparate. **Variables:** `ShopType`, `OpenState`, `SignMaterial`, `AwningVariant`, `WindowWarmth`. **Uso:** cambiar el carácter de cada fachada con un mismo Blueprint.

### `BP_StreetPropCluster`

**Componentes:** instancias de barril/caja/saco/cesta/carteles; colisión sólo donde aporta al gameplay. **Variables:** `ClusterType` (mercado/taller/carga/doméstico), `Seed`, `Density`, `BlockNavigation`. **Uso:** variación controlada, no dispersión puramente aleatoria.

### `BP_TemporalEvidenceState`

**Componentes:** objetos de evidencia y luces de agencia. **Variables:** `NarrativeState = Official | Authentic`, `bInteractable`. **Uso:** sustituir elementos de evidencia y respuesta audiovisual entre finales sin duplicar el nivel entero.

## 32. Materiales maestros

- `M_Brick_Victorian`: parámetro de color base, mortero, suciedad inferior, hollín superior y desgaste localizado; 3 instancias.
- `M_GraniteSetts`: variación de piedra y juntas, máscara de ruedas, roughness humedad; 2 instancias.
- `M_SlabStone`: losas de acera, cantos menos contrastados.
- `M_Wood_PaintedAged`: capa de pintura, desgastes en bordes de contacto, roughness irregular.
- `M_Iron_BlackAged`: hierro fundido negro, reflejos mínimos y oxidación localizada.
- `M_Glass_GasLamp`: emisivo controlado; vidrio ámbar translúcido o apariencia opaca según coste.

**Regla de optimización:** preferir instancias de materiales y texturas trim/atlas compartidas antes que una textura 4K distinta por caja o puerta.

## 33. Decals y lógica de emplazamiento

| Decal | Sitio lógico | Error común |
|---|---|---|
| `DEC_WaterRunoff` | bajo bajantes y aleros | hacer chorrear paredes sin fuente de agua |
| `DEC_WheelTrack` | calle de carros y accesos de carga | marcar entradas peatonales estrechas |
| `DEC_SootCorners` | rincones y zonas de humo | cubrir cada fachada idénticamente |
| `DEC_DampPlinth` | 20–80 cm inferiores, variable | generar banda horizontal uniforme |
| `DEC_PaperPoster` | tablones y muros concurridos | repetir el mismo póster diez veces |
| `DEC_StreetMud` | bordes y zonas hundidas | convertir toda la superficie en barro profundo |

## 34. Iluminación y postproceso

- Mantener **exposición estable** para que el jugador identifique rutas y enemigos.
- No destruir siluetas con bloom; cian debe ser fino y definido.
- Reflexiones húmedas en parches, con roughness alta-media en el resto.
- Separar intensidad del farol de intensidad del vidrio: puede verse encendido sin proyectar luz excesiva.
- Fondo no totalmente negro: mostrar cubiertas, humos y contornos de chimeneas.
- Niebla por profundidad y zona, no filtro global uniforme.

## 35. Rendimiento para jam

- HISM/ISM en adoquines o props repetidos, cuando convenga; evitar miles de actores pequeños separados.
- LODs/Nanite si el proyecto y plataforma lo admiten; no usar detalle invisible desde cámara.
- Colisiones simplificadas para sacos, carros, barriles y elementos fuera de alcance.
- Luces dinámicas **solo donde aportan**; ventanas decorativas pueden usar emisivo.
- Evitar VFX de humo en cada salida de chimenea.
- Comprobar FPS **en la cámara real de juego**, no solamente desde la vista de editor.
- Priorizar carga de mapas, finales completos y legibilidad sobre ornamento opcional.

---

# PARTE VII — PLAN DE PRODUCCIÓN POR IMPACTO

## 36. Primer pase: mejoras que más se notan

**Objetivo:** que la calle deje de parecer un bloque gris genérico.

- Rehacer dos plantas bajas distintas y duplicarlas con variaciones.
- Añadir bordillo/canal y revisar roughness de agua.
- Introducir una bolsa de mercado y una bolsa de carga.
- Añadir un letrero de esquina y 1–2 faroles de gas donde tengan sentido.
- Revisar la silueta de tejados con chimeneas y bajantes.
- Comparar capturas desde **la misma posición de cámara, hora, FOV y exposición**.

## 37. Segundo pase: vida ambiental

- Activar 2–4 ventanas cálidas por manzana visible, no todas.
- Colocar un banco, una persiana cerrada, un cubo de carbón y una puerta de servicio.
- Trabajar audio espacial: ruedas y mercado distantes.
- Aplicar tres familias de decals: humedad, desgaste y anuncios.
- Añadir un goteo y un humo localizado por secuencia.

## 38. Tercer pase: integración narrativa

- Fijar un hito de agencia con tecnología cian en un sitio concreto.
- Hacer que una evidencia cambie entre versión oficial y auténtica.
- Señalizar discretamente el camino hacia ambos finales.
- Probar que no se confunda elemento decorativo con elemento interactivo.

## 39. Criterios de aceptación de arte

- [ ] Se distinguen a simple vista calle principal, callejón y patio.
- [ ] Se reconocen al menos tres oficios o usos de edificio.
- [ ] Aceras, calzada, bordillos y drenajes tienen jerarquía geométrica.
- [ ] Las fachadas no parecen una repetición de un mismo módulo.
- [ ] Las fuentes de humedad explican la ubicación de charcos y manchas.
- [ ] Faroles de gas cálidos contrastan con luz cian exclusiva de agencia.
- [ ] Dos puntos de referencia permiten al jugador orientarse sin mapa.
- [ ] El recorrido principal no tiene props que oculten el personaje.
- [ ] La escena mantiene rendimiento aceptable en hardware objetivo.
- [ ] Elementos jugables y pruebas de narrativa funcionan antes de aumentar detalle.

---

# PARTE VIII — REFERENCIAS HISTÓRICAS, ANACRONISMOS Y VERIFICACIÓN

## 40. Fuentes principales

1. **Survey of London / UCL — Whitechapel.** Transformaciones urbanas, comercio, instituciones, inmigración y pobreza.  
   https://www.ucl.ac.uk/bartlett/architecture/research/histories-and-theories-architecture/survey-london/whitechapel
2. **Tower Hamlets — Whitechapel High Street Conservation Area.** Historia morfológica y edificios de la arteria principal; describe la iglesia de St Mary reconstruida en el XIX y Gardener’s Corner desde 1870. **Atención:** fotografías del siglo XX no prueban los mismos detalles en 1888.  
   https://www.towerhamlets.gov.uk/Documents/Planning-and-building-control/Development-control/Conservation-areas/Whitechapel-High-Street.pdf
3. **London Museum — How gas lamps illuminated London.** Desarrollo y alcance de la iluminación de gas.  
   https://www.londonmuseum.org.uk/collections/london-stories/gas-lamps-illuminated-london/
4. **London Museum — Henry Mayhew brings Victorian London to life.** Vendedores y trabajadores ambulantes, gastronomía y ocupaciones urbanas.  
   https://www.londonmuseum.org.uk/collections/london-stories/henry-mayhew-brings-victorian-london-life/
5. **MyLearning — Streets of London 1870–1900.** Vida cotidiana documentada, transporte, venta y trabajo en la vía.  
   https://www.mylearning.org/stories/streets-of-london-1870-1900/street-life-introduction
6. **Wellcome Collection — Medical Officer of Health for Whitechapel (1888).** Registro documental de casas de alojamiento en calles concretas: Dorset Street, Flower and Dean Street, Brick Lane, Hanbury Street y otras. **Importante:** la fuente acredita establecimientos y condiciones sociales, no el aspecto visual exacto de cada fachada.  
   https://wellcomelibrary.org/moh/report/b19883638/14
7. **City of London — documento de conservación/pavimentos.** Granito, macadán, pruebas de asfalto y pavimento de madera durante el XIX, limpieza de calles.  
   https://democracy.cityoflondon.gov.uk/documents/g17751/Public%20reports%20pack%2011th-Jan-2016%2011.30%20Streets%20and%20Walkways%20Sub%20Planning%20and%20Transportation%20Com.pdf?T=10
8. **Historic England — Victorian drinking fountain and horse trough.** Uso y tipología de abrevaderos urbanos.  
   https://historicengland.org.uk/education/schools-resources/educational-images/drinking-fountain-and-horse-trough-mitcham-greater-london-ioe01-02201-27
9. **London Museum — The Fountain, Victoria Park.** Expansión de fuentes públicas y abrevaderos.  
   https://www.londonmuseum.org.uk/collections/v/object-769600/the-fountain-victoria-park/

## 41. Advertencias historiográficas

- **“Londres victoriano” no describe una sola década.** Una imagen de 1830, 1888 y 1905 puede representar cosas distintas.
- **Un grabado puede idealizar o dramatizar.** Una fotografía puede mostrar otro año o haberse tomado en una avenida más rica.
- **La palabra “cobblestone” es imprecisa.** Granito rectangular (*setts*) y canto rodado no son equivalentes visuales.
- **El gas no significa oscuridad total.** Pero tampoco luz LED moderna.
- **No introducir una estación de metro, tranvía o infraestructura particular** sin comprobar su fecha exacta.
- **No atribuir a Whitechapel todos los rasgos del West End** ni suponer que todas las calles pobres eran idénticas.
- **No usar el miedo y la pobreza como única identidad del barrio.** Comercio, oficio, migración y comunidad son imprescindibles.
- **La agencia temporal no es histórica [F].** Toda máquina con cian debe identificarse en la producción como parte de la ficción.

## 42. Briefs de imagen para generar referencias visuales de producción

### Lámina 1 — Calle comercial corregida

> Environment concept art for a stylized dark Victorian isometric action game, Whitechapel London 1888, three-quarter high isometric camera, a believable busy commercial street at dusk after rain, varied 3-4-storey soot-stained brick buildings, distinct shopfronts, wooden shop signs, two canvas awnings, fruit and textile stalls, granite setts on roadway, separate large stone slab sidewalks and clear curbs, side gutters with localized puddles, horse handcart, crates, sacks, subtle warm gas lamps, few softly lit residential windows, realistic functional street layout, hand-painted game textures, medium-detail chunky readable architecture, muted smoke-red brown charcoal palette with warm amber only, not crowded with people, clean central playable lane, no text, no modern objects, no electric tram, no neon, no cyan.

### Lámina 2 — Callejón narrativo corregido

> Environment concept art for a stylized dark Victorian isometric action game, Whitechapel London 1888, three-quarter high isometric game camera, narrow damp brick alley with worn cellar door, basement iron grating, uneven steps, cast-iron rain downpipe leaking into a drainage channel, modest crate and scattered papers, indirect amber light spilling from street entrance, dark stone setts with sparse localized puddles, one subtle anachronistic black brass temporal-agency mechanism hidden against back wall with a very thin cyan light line, atmosphere and shadows but clear playable route, hand-painted stylized textures, authentic Victorian construction, readable silhouettes, no characters, no text, no modern fixtures.

### Lámina 3 — Patio y taller (opcional)

> Victorian Whitechapel 1888 rear loading courtyard, stylized dark isometric game environment, leatherworker bench, small warehouse arch, sacks and barrels arranged logically, handcart tipped on its side, stone slabs and drainage channel, worn brick walls and a warm upper window, wet atmosphere, cinematic but gameplay-readable composition, no modern objects.

---

# CONCLUSIÓN OPERATIVA

**La transformación buscada no es “más suciedad” sino “más Londres”.** En una primera fase, invertir en **tipología de plantas bajas, sección de calle, oficios, iluminación funcional y señales de ocupación**. En la segunda, clima, desgaste y audio. Sólo después añadir tecnología cian y estados narrativos. Así la ciudad funciona como espacio histórico convincente, mientras que la agencia se vuelve una interrupción visual deliberada.

**Prioridad de entrega para la jam:** si el tiempo es escaso, construir **un tramo memorable y completamente jugable** con 12 assets P0 antes que cinco calles vacías con 70 props decorativos.
