# 07 — Dirección artística, audio, interfaz y alcance

> **Norma de producto:** Unscripted, UE 5.8.4, Blueprint. Todo contenido visible o audible al jugador debe estar en ingl?s. Los ejemplos en espa?ol de este documento son referencias de dise?o que deben adaptarse antes de incorporarse al juego; documentaci?n y comentarios internos pueden seguir en espa?ol.

## Dirección visual

- **Entorno:** Whitechapel victoriano oscuro; empedrados, faroles de gas, ladrillo, niebla, talleres, callejones, plazas pequeñas.
- **Tecnología de la agencia:** estética de latón y metal negro con destellos cian/azules; debe parecer **anacrónica** en 1888.
- **Personaje:** agente de abrigo oscuro con Bastón de Continuidad y dispositivo de muñeca.
- **Jack:** hombre de apariencia corriente, cansado y aterrorizado; evitar estereotipo de monstruo.
- **Supervisor:** presencia autoritaria, uniforme/abrigo distintivo, equipo temporal más avanzado.
- **Enemigos comunes:** vecinos/perseguidores victorianos; diferenciarlos claramente de los Interventores.
- **Cámara:** perspectiva isométrica para lectura de zonas de peligro, cobertura y golpes.

Los retratos mostrados en conversaciones previas eran **referencias conceptuales de apariencia**, no assets del juego ni archivos que formen parte de este paquete.

## Lenguaje visual de poderes

- **Corte de Fotograma:** silueta fragmentada, pequeño efecto de interrupción temporal, ruido visual en el enemigo objetivo.
- **Retoma:** estelas e imágenes residuales del agente, retorno visible a una posición anterior, sonido de inversión y flash moderado.
- **Salto de Fotograma** *(opcional)*: desaparición y reaparición rápida con posimagen.
- **Eco de una Toma** *(opcional)*: doble transitorio translúcido repitiendo un golpe.
- **Contraorden (parry):** impacto de bastón con pulso temporal breve e indicador claro de éxito.
- **Desviación del guion:** distorsión/aviso «CONTINUIDAD ALTERADA».

Evitar efectos demasiado abundantes que oculten al personaje o las telegráficas enemigas.

## Audio

- Ambiente: lluvia, viento, gas, pasos sobre adoquines, multitud distante.
- Combate: golpes de bastón, impactos secos, bloqueo/parry claramente diferenciados.
- Tecnología: pulso corto y artificial para Corte; inversión/eco distintivo para Retoma.
- Narrativa: transmisiones del Supervisor/Director con posible filtro tecnológico; también pueden presentarse solo como texto/subtítulos.
- Interfaz: sonido de checklist reescrito, evidencia recogida y registro final.

**No se requiere doblaje completo** para que la historia funcione.

## Interfaz

- HUD claro: salud, resistencia, carga de Retoma, cooldown Corte, objetivo y detección.
- Panel de checklist reescrito como si fuera un documento del Departamento.
- Diálogos con texto legible.
- Interacción contextual `E`, con prioridad entre objetos y remates.
- Periódico final o documento de cierre como imagen/UI de bajo costo.
- Señalización visual de enemigos que están preparando ataques.

## Versión mínima deseada

| Sistema | Mínimo de diseño |
|---|---|
| Combate | Combo 2–3 golpes, fuerte, esquiva, parry |
| Poderes | Corte de Fotograma y Retoma personal |
| Enemigos | IA básica compartida + variante Interventor/jefe |
| Sigilo | Detección por visión, cobertura y posible escondite |
| Mundo | Un nivel con taller, refugio, callejón, archivo |
| Historia | Tres actos, giro de la agencia, dos expedientes, dos finales |
| UI | Objetivos/checklist, recursos y mensajes |

No implica que esté implementado; es el objetivo del prototipo que se había formulado.

## Extensiones opcionales

- **Salto de Fotograma:** reposicionamiento instantáneo ofensivo.
- **Eco de una Toma:** repetir el último ataque con una posimagen.
- **Bomba de humo:** escape o ruptura de visión.
- Golpe fuerte cargable.
- Animaciones especiales de remate.
- Combate con cancelaciones o cadenas más largas.
- Más tipos de enemigos, rutas alternativas y encuentros.
- Sistema de consecuencias más elaborado para «desviaciones».

## Ideas descartadas del núcleo inicial

- Combate de armas múltiples, equipo con estadísticas complejas o progresión RPG completa.
- Multitud con IA individual masiva.
- Rewind global de todos los actores y acontecimientos.
- Simulación histórica/ciclo temporal general.
- Mundo abierto, múltiples niveles o misiones procedurales.
- Combate aéreo, fatalities complejas o parkour de mundo abierto.

## Indicadores de calidad del resultado

- El tema *Director's Cut* se entiende sin leer una explicación externa.
- El golpe, la esquiva y el parry comunican bien impactos/ventanas.
- Corte y Retoma tienen utilidades claramente diferentes.
- El sigilo y el combate son alternativas válidas en parte del recorrido.
- La historia deja claro por qué la agencia protege primero a Jack y después busca eliminarlo.
- El final es una **decisión visible sobre cuál relato se registra**.
- Es posible completar una partida sin bloqueos narrativos o técnicos.

## Nota sobre duración

La propuesta original apuntaba a unos 10–15 minutos. Al añadir más enfrentamientos ese tiempo puede variar; mantener el nivel compacto y medir con sesiones de prueba, no asumir duración exacta por documentación.
