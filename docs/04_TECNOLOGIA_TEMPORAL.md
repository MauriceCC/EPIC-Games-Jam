# 04 — Tecnología de la agencia y poderes temporales

> **Norma de producto:** Unscripted, UE 5.8.4, Blueprint. Todo contenido visible o audible al jugador debe estar en ingl?s. Los ejemplos en espa?ol de este documento son referencias de dise?o que deben adaptarse antes de incorporarse al juego; documentaci?n y comentarios internos pueden seguir en espa?ol.

## Justificación diegética

El **Departamento de Continuidad** desarrolló instrumentos que alteran intervalos pequeños del tiempo para asegurar el desenlace de hechos históricos. La tecnología contrasta con Whitechapel 1888: metal oscuro, latón, componentes retráctiles, pulsos cian/azules y artefactos compactos.

### Equipo

1. **Bastón de Continuidad:** arma retráctil con impulsos temporales, ataques, empuje y parry.
2. **Manipulador Cronal:** guantelete/dispositivo de brazo que aplica habilidades temporales.
3. **Bobinas de Continuidad:** reserva de energía asociada a las acciones temporales de alto impacto; en el prototipo pueden representarse mediante cargas de Retoma.

## Poderes prioritarios

### Poder 1: Corte de Fotograma

**Fantasía:** «Eliminar del montaje el instante en el que el enemigo iba a atacar».

- Entrada: `F`.
- Afecta a **un enemigo cercano y visible**, no a todo el mundo.
- Interrumpe movimiento/ataque y lo deja vulnerable unos **0,8 segundos**.
- Coste inicial: cooldown de **10 segundos**, sin cuarto medidor de recurso.
- Efecto sobre postura sugerido: **+10**.
- Puede usarse para abrir combo, impedir golpe fuerte, escapar o ayudar a Jack.
- Algunos ataques especiales pueden resistirse. Supervisor sufre una interrupción más corta.
- Representación: congelación local de animación y desplazamiento, distorsión de silueta y fragmentación cian.
- Implementación conceptual: estado `TemporalFrozen` del enemigo, detener temporalmente movimiento/animación y restaurarlos con coherencia.

**No implementar como:** `GlobalTimeDilation` que congele indiscriminadamente todos los objetos, a menos que cambie explícitamente el diseño.

### Poder 2: Retoma

**Fantasía:** «El jugador no retrocede el mundo: recupera su propia toma anterior».

- Entrada: `R`.
- Máximo: **5 segundos** en el tiempo personal.
- Cargas iniciales consolidadas: **2 por sección**, recuperadas en checkpoints.
- Restaura posición y orientación del protagonista, además de salud y resistencia que tenía en el instante almacenado, sujetos a sus máximos.
- **No** revierte movimiento, salud ni heridas de enemigos.
- **No** revierte puertas abiertas persistentes, evidencias, misiones, diálogos ni elecciones.
- No puede activarse durante diálogos, registro del final u otras secuencias irreversibles.
- El estado actual puede restaurarse en forma visual de imágenes residuales; no exige que el mapa entero se anime en reversa.
- Evita morir o permite ataques agresivos: golpear, recibir daño, volver a un instante favorable y mantener el daño causado.

**Cambio respecto al concepto inicial:** la primera propuesta hablaba de devolver cinco segundos de todos los actores y tres cargas. La propuesta posterior, diseñada para combate, **sustituye expresamente** esa idea por Retoma personal y **dos cargas**. Es la decisión vigente.

### Buffer de Retoma

Snapshot tentativo:

```text
ST_RewindSnapshot
  Timestamp / RelativeTime
  PlayerTransform
  PlayerVelocity          # opcional si la restauración lo necesita
  PlayerHealth
  PlayerStamina
```

Cada **0,1 segundos** tomar un snapshot y conservar los **últimos 50** (~5 segundos), idealmente en buffer circular. En la activación:

1. Confirmar que existen historial, carga y estado de juego permitido.
2. Elegir un snapshot elegible hasta cinco segundos atrás.
3. Deshabilitar temporalmente entradas/iniciar efecto visual.
4. Verificar que la posición almacenada sigue siendo alcanzable y no produce penetración en geometría.
5. Restaurar transform, salud y resistencia personal.
6. Consumir una carga, reanudar control y actualizar HUD.

**Precauciones necesarias:**

- Vaciar el historial después de interacciones narrativas irreversibles o cuando se cambia de nivel/área invalidante.
- No permitir recuperar cargas gastadas simplemente restaurando un snapshot antiguo (las cargas **no** forman parte del snapshot).
- El mundo continúa en su estado actual y debe permitir una posición segura de destino.
- En caso de no existir snapshot seguro, cancelar la restauración o usar una política de fallback coherente; no teletransportar dentro de paredes.
- Evitar duplicación de evidencias, checkpoints, eventos o remates.
- Tratar salud y resistencia como valores acotados [0, máximo].

## Poderes de ampliación (no obligatorios)

### Poder 3: Salto de Fotograma

- Desplazamiento instantáneo corto junto a enemigo cercano.
- Reaparece en posición válida, acompañado de un ataque inmediato.
- Permite flanqueo, alcance y continuidad ofensiva.
- Requiere comprobar navmesh, colisiones y posibles destinos imposibles.

### Poder 4: Eco de una Toma

- Una imagen residual repite el último ataque tras un retardo breve.
- Permite golpes dobles o ruptura de defensa.
- Requiere guardar el tipo de ataque, origen/dirección y resolver impactos duplicados.

### Idea original opcional: Bomba de humo

Estaba presente en el brainstorming como herramienta de escape o sigilo. No constituye un pilar del diseño actual y se incorpora solo si hay tiempo y resulta útil al combate.

## Ejemplo de uso conjunto

- Hay tres perseguidores.
- El protagonista hace parry al primero y golpea.
- El segundo prepara un ataque: Corte de Fotograma lo interrumpe.
- El protagonista consigue derribarlo, pero un tercero lo hiere.
- Retoma le devuelve su posición/salud anterior; **los enemigos conservan sus heridas**.

## Distinción narrativa vs física

Los mensajes de un «yo futuro» y la copia enviada al siguiente ciclo de memoria son **elementos de historia**. No obligan a implementar una simulación completa de líneas temporales, viajes causales o un sistema de persistencia entre partidas.
