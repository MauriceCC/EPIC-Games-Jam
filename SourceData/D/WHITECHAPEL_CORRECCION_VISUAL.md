# Whitechapel — corrección visual sobre las referencias del usuario

Fecha: 2026-11-15. División D. **[PROPUESTA]** de producción; no modifica contratos ni layout.

## Lectura correcta de las imágenes

Las imágenes 1–5 son el objetivo artístico; 2 y 3 repiten referencia. Las imágenes 6–7 muestran el estado actual en Unreal. No interpretar las primeras como assets existentes ni como resultado alcanzado. El documento adjunto es material de referencia, no autorización para implementar sus Blueprints narrativos o modificar otras divisiones.

La referencia 1 orienta composición y distribución; las referencias de calle orientan materiales, escala de detalle y luz. No copiar el mapa incrustado, sus rótulos ni el panel español. Todo texto al jugador sigue siendo inglés.

## Diagnóstico de las capturas actuales

| Prioridad | Observación visible | Corrección y comprobación |
|---|---|---|
| P0 | Plaza con gran superficie lisa y polígonos de humedad de límites duros | Inspeccionar primero geometría y asignaciones. No asumir que Build Geometry resuelve el problema. Asegurar pavimento continuo; limitar humedad a bordes y depresiones. Revisar solapes, z-fighting, UV y límites de decals. |
| P0 | Fachadas amarillo-blancas, pérdida de detalle alrededor de luces | Comparar exposición fija y luces aisladas. Separar emisivo del cristal de luz proyectada; reducir intensidad por grupos y comprobar conservación de detalle. No multiplicar luces para compensar sombras. |
| P0 | Tejados azules, repetitivos y brillantes; gran tapiz exterior visible | Revisar material/UV bajo luz neutra antes de regenerar. Usar pizarra gris carbón de baja variación, roughness alta y relieve moderado. Corregir escala y limitar superficies continuas; no cubrir el exterior con una textura de cubierta a ras de suelo. |
| P1 | Muros altos y superficies vacías alrededor de patios; aspecto de laberinto | Completar volúmenes coherentes detrás de fachadas con alero, medianera, cumbrera y chimenea donde corresponda. Conservar acceso y visibilidad del jugador. No colocar tejados sobre espacios jugables abiertos. |
| P1 | Luces y escaparates de brillo parecido | Variar locales abiertos/cerrados, ventanas apagadas y temperatura cálida moderada; mantener un foco dominante por encuadre. |
| P1 | Vapor concentrado en manchas blancas | Reducir opacidad/emisión y comprobar sobre fondo oscuro. Pocos focos suaves, sin ocultar siluetas. |
| P2 | Falta variedad comercial y detalle de uso | Dos o tres agrupaciones de oficio, toldos distintos, rótulos, sacos y bajantes. Colocación por actividad; mantener carril y áreas de combate despejados. |

Estas son observaciones visuales; no se han medido intensidades, materiales ni geometría en el editor. Las casillas de entregas previas en MEJORAS_MUNDO.md no acreditan calidad visual actual.

## Orden de ejecución

1. Capturar una vista general y una vista jugable de la plaza con cámara, exposición y resolución reproducibles. Usar Game View para ocultar iconos del editor.
2. Inspeccionar suelo y techos en Unlit y Lit: separar problemas de albedo/UV de iluminación. Comprobar material asignado en cada slot y dimensiones reales de las mallas.
3. Corregir pavimento de plaza y quitar apariencia de láminas de agua planas. Conservar colisiones y rutas.
4. Equilibrar luz con exposición estable: ladrillo visible junto al farol, sombras legibles, tejado sin dominante azul intensa. Ajustar primero luces existentes.
5. Probar la nueva pizarra en una sola cubierta y comparar con la anterior desde cámara jugable. Aplicarla al conjunto solo tras comprobar escala y repetición.
6. Resolver volúmenes, aleros y remates visibles. Después añadir variación de comercio y props.
7. Comparar mismos encuadres antes/después y recorrer plaza → callejón → taller → refugio → archivo con jugador real. Comprobar que no se oculta y que siguen funcionando rutas y encuentros.

No guardar assets de Player, Enemies, Narrative, UI, Core ni subniveles AI/Story. Persistente solo con lock LFS. No ejecutar scripts de reconstrucción global del blockout sobre este nivel vestido.

## Prompt operativo corregido para el agente/editor

> Trabajo en División D de Unscripted, Unreal Engine 5.8.4, Blueprint. Lee AGENTS.md y los planes obligatorios. Usa las imágenes 1–5 como referencias artísticas y 6–7 como estado actual. Mejora el nivel existente para aproximarlo a una calle victoriana densa y legible: ladrillo rojo ahumado, pizarra gris carbón, calzada de granito con aceras de losa, charcos puntuales y luz ámbar contenida. Conserva distribución, conexiones, colisiones útiles, áreas de combate y actores de otras divisiones. Primero audita y corrige suelo liso de la plaza, charcos poligonales, luces quemadas y escala/color/brillo de tejados. No ocultes estos errores agregando props o niebla. Después completa volúmenes y remates de edificios y añade variedad de comercios mediante agrupaciones pequeñas. Cian exclusivamente para agencia. No recrees el nivel ni cambies cámara del jugador. Toda ampliación ajena al diseño es [PROPUESTA]. Solo edita assets de D; no modifiques contratos ni grafos como texto. Trabaja por pases reversibles, registra qué actores/materiales cambias y entrega capturas comparables desde la cámara real y limitaciones pendientes. No declares éxito solo por crear actores o generar texturas.

## Textura nueva de cubierta

**[PROPUESTA]** Primera pieza: albedo de pizarra. Una imagen generada no es un material PBR completo ni garantiza repetición perfecta. Verificar unión en mosaico 3×3 antes de uso masivo. No conectar el color a Normal o Roughness ni presentar canales derivados del brillo como mediciones físicas.

Importar en `/Game/Unscripted/Art/Textures/Roofs/` con sRGB activado para Base Color y crear material nuevo en `/Game/Unscripted/Materials/`, sin sobrescribir el maestro compartido existente. Primer ensayo: Metallic 0, Roughness 0.75–0.9, Specular por defecto; sin emisivo. Son valores orientativos para comparar, no balance final. Normal inicialmente plano; añadir normal de pizarra solo si mejora a distancia de juego. Las juntas deben leerse sin convertir cada pieza en un escalón exagerado.

Escala orientativa del tile: diez piezas de ancho, catorce hiladas visibles; si cada pieza mide 25 cm de ancho y cada hilada expone 18 cm, un tile cubre aproximadamente 2.5 × 2.52 m. Medir la malla y sus UV antes de elegir el multiplicador. La textura no reemplaza la geometría de cumbrera, alero o chimenea.

## Criterios de aceptación

- Plaza pavimentada sin zonas lisas accidentales ni agua de contorno rectangular evidente.
- Ladrillo y escaparates conservan detalle junto a lámparas; no hay focos blancos dominantes.
- Pizarra gris, escala de tejas consistente y sin patrón brillante tipo damero a distancia de juego.
- No se ve una alfombra infinita de tejado exterior desde los encuadres previstos.
- Contraste ámbar/frío moderado y cian localizado en agencia.
- Personaje, enemigos y entradas se distinguen; rutas y superficies transitables se conservan.
- Capturas comparables y recorrido en Play antes de considerar cerrado el pase. Pendiente de validación en editor.
