# 05 — Nivel, progresión, objetivos e interfaz

## Estructura espacial

Un solo nivel de Whitechapel, con geometría modular de callejones, plaza, talleres, refugio y archivo. Referencia de dimensiones preliminares: **60 x 40 metros virtuales**, sin compromiso de escala final.

```text
                    [ARCHIVO / ELECCIÓN FINAL]
                              |
     [REFUGIO] ------------ [PASO CENTRAL] -------- [TALLER DE JACK]
         |                         |                      |
     [PLAZA] ---------------- [CALLEJÓN] --------------- |
                                   |
                                [INICIO]
```

Recorrido conceptual principal: **Inicio → plaza/callejón → taller → ruta de salida → refugio → archivo**. El diseño debe incluir cobertura, flanqueos y áreas suficientemente amplias para combate isométrico. La plaza puede alojar patrullas, y el callejón combate de grupos. Un edificio no requiere interior detallado si basta una zona accesible.

### Objetos ambientales

- Faroles, suelo empedrado, fachadas victorianas.
- Cajas, barriles y muros para bloquear línea de visión.
- Armarios o rincones ocultos para interacción.
- Puerta lateral que habilita ruta de Jack.
- Registro de enfermería e informe manipulado.
- Dos estaciones/mecanismos para elegir archivo final.

## Misiones y fases

Definir `EStoryPhase` con el flujo:

```text
FindJack
    ↓ interactuar con Jack
OpenEscapeRoute
    ↓ abrir puerta lateral
ProtectJack
    ↓ Jack llega al refugio
DiscoverTruth
    ↓ se registran dos evidencias / se dispara revelación
FinalChoice
    ↓ registro de uno de dos expedientes
GameEnded
```

El enfrentamiento con Supervisor ocurre dentro de la fase final como **bloqueo al acceso al archivo**, no como selector automático de final. Los documentos pueden recogerse en secuencia flexible si no destruye el ritmo narrativo.

### Variables narrativas iniciales

```text
CurrentPhase = FindJack
bJackFound = false
bEscapeRouteOpen = false
bJackSafe = false
bEvidenceFound = false
bFalseReportFound = false
bSupervisorEncountered = false
Ending = None
```

El nombre concreto de variables puede cambiar al implementarlo. El punto importante es **una fuente de verdad** para la progresión.

## Objetivos del Acto I

- Recibir la lista de órdenes.
- Explorar evitando o combatiendo perseguidores.
- Localizar el taller y hablar con Jack.
- Descubrir el mensaje firmado por el yo futuro.

**Checklist inicial:** localizar a Jack; evitar que la multitud lo capture; impedir que se conozca su identidad.

## Objetivos del Acto II

- Abrir puerta lateral mientras Jack espera.
- Despejar o evitar a los perseguidores del corredor.
- Habilitar el avance de Jack al refugio por puntos predeterminados.
- Encontrar **registro de enfermería** (hora/firma que contradicen acusación).
- Encontrar **informe fabricado** (agencia pretende inculparlo).
- Presenciar revelación del Supervisor y la orden de corrección del Interventor.

**Checklist alterado:** incriminar a Jack y eliminarlo sin exponer identidad.

## Objetivos del Acto III

- Llegar al archivo.
- Enfrentar al Supervisor para liberar el acceso.
- Examinar expediente oficial y expediente auténtico.
- Registrar uno de ellos físicamente con `E`.
- Reproducir final A o B y mostrar el periódico/mensaje correspondiente.

## Diseño de encuentros por zona

| Zona | Función | Oposición sugerida |
|---|---|---|
| Entrada/plaza | Movimiento, visión, primera pelea | Dos perseguidores básicos |
| Acceso al taller | Sigilo, esconderse, encontrar a Jack | Patrulla o perseguidor |
| Callejón de escape | Acción y control de grupos | Hasta tres perseguidores |
| Tramo al refugio | Protección y revelación | Interventor de la agencia |
| Archivo | Clímax de combate y decisión | Supervisor |

**Nota:** es un esquema de contenido y no un calendario ni una lista de tareas obligatoria.

## Diseño del HUD

### Elementos persistentes o contextuales

- Título contextual de misión «OPERACIÓN 1888».
- Objetivo actual: p. ej. «Protege a Jack y llévalo al refugio».
- Indicador de alerta o detección al estar cerca de guardias.
- Salud y resistencia para combate.
- Cargas de Retoma (**2** en versión consolidada).
- Indicador visual de cooldown de Corte de Fotograma.
- Texto contextual de interacción «E · Interactuar» o «E · Rematar».
- Checklist en panel `Tab`, con objetivos tachados y nuevas órdenes.
- Subtítulos/transmisiones del Director, Supervisor y yo futuro.

### Checklist como recurso narrativo

La interfaz **reescribe** las órdenes cuando emerge la verdad. Ese cambio explícito de texto conecta jugabilidad con el tema de manipulación del relato.

```text
OPERACIÓN 1888 — ACTUALIZACIÓN
✓ Localizar al sujeto
✓ Evitar su captura
! Atribuir los crímenes al sujeto
! Eliminar al sujeto sin revelar su identidad
```

### Aviso de desviación

Mostrar «CONTINUIDAD ALTERADA — Acción no contemplada en el procedimiento oficial» cuando el protagonista actúe contra la versión autorizada. Puede ser un evento narrativo/visual sencillo, no un sistema completo de reputación.

### Documento final

Dos representaciones interactivas distintas:

1. **Expediente oficial:** pruebas falsificadas; favorece el corte del Director.
2. **Expediente auténtico:** registro no manipulado; intenta preservar la verdad.

Mostrar confirmación clara antes de ejecutar un final si la interacción es irreversible. Después del registro, Retoma queda deshabilitada para impedir cambios retroactivos.

## Salidas y finales

- **A — Oficial:** versión manipulada conserva su lugar; periódico de cierre.
- **B — Auténtico:** borrado de memoria del agente, pero sobrevive mensaje/evidencia temporal para su próximo yo.

## Duración

Objetivo original aproximado: **10–15 minutos**. La adición de los encuentros de combate puede alterar esta duración; validar sin asumir que la cifra es fija. No es necesario un mundo grande ni múltiples niveles para sostener la experiencia.
