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
