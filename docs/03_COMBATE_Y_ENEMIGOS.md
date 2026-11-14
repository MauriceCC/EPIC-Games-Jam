# 03 — Combate cuerpo a cuerpo y enemigos

> **Norma de producto:** Unscripted, UE 5.8.4, Blueprint. Todo contenido visible o audible al jugador debe estar en ingl?s. Los ejemplos en espa?ol de este documento son referencias de dise?o que deben adaptarse antes de incorporarse al juego; documentaci?n y comentarios internos pueden seguir en espa?ol.

## Fantasía de combate

**Combate de Continuidad:** un agente entrenado utiliza un bastón retráctil y tecnología temporal para controlar el ritmo de peleas contra uno o varios adversarios. Tres verbos: **golpear, interrumpir, repetir**.

**Referencias de mecánicas:** Final Fight (control de grupos), Assassin's Creed (contraataques y remates), Dark Souls (riesgo/ventanas/resistencia), No Rest for the Wicked (posicionamiento isométrico y peso del ataque). Son referencias de mecánicas, no contenido a reproducir.

## Arma principal: Bastón de Continuidad

Retráctil, con impulsos de energía temporal. Sirve para ataques rápidos, golpes fuertes, parry y neutralización. Evita requerir combate de armas múltiples y permite remates no letales.

## Acciones

| Acción | Regla inicial | Función |
|---|---|---|
| Ataque ligero | Combo de hasta 3 golpes | Presión y daño rápido |
| Ataque fuerte | Más lento y potente; rompe defensa | Control y apertura |
| Esquiva | Desplazamiento corto e invulnerabilidad breve | Evitar y reposicionarse |
| Parry / Contraorden | Ventana precisa ante golpe entrante | Desvío, postura enemiga y contraataque |
| Remate contextual | Requiere objetivo aturdido y cercano | Neutralización contundente |
| Ataque sigiloso | Desde posición no detectada | Iniciar con ventaja o incapacitar enemigo común |

### Combo de tres ataques ligeros

1. Golpe lateral rápido.
2. Golpe cruzado de continuación.
3. Impacto final con mayor aturdimiento, empuje y una amplitud que pueda desplazar a un segundo enemigo cercano.

La entrada debe recibirse dentro de ventanas de combo. Si falla el ataque o el jugador se excede, queda expuesto al contraataque. No se pretende una secuencia automática interminable.

### Ataque fuerte

Es útil contra Interventores que bloquean los ligeros. Tiene telegráfica y coste mayores. **Mantener pulsado para cargar** es mejora opcional, no requisito base.

### Esquiva

Debe llevar al protagonista fuera del rango del enemigo y, cuando se ejecute correctamente, permitir respuesta rápida desde un ángulo mejor. No debe otorgar invulnerabilidad durante toda la animación sin evaluación.

### Parry / Contraorden

- Anula el daño del ataque recibido cuando se activa dentro de la ventana correcta.
- Aumenta la **postura** o desequilibrio del enemigo.
- Abre un contraataque inmediato.
- Si falla, deja al agente expuesto.
- La guía visual mostró una ventana equivalente a ~0,2 segundos; ajustar con animaciones.

### Postura, aturdimiento, remate

Además de salud, cada adversario tiene un valor de desequilibrio/postura. Golpes fuertes, tercer impacto del combo y parries aumentan ese valor. Al superar un umbral, queda aturdido temporalmente y puede recibir un remate con `E` si está a rango. Un civil debe ser **incapacitado, no asesinado**.

## Valores tentativos de balance

**Del jugador:** salud 100, resistencia 100, Retoma 2 cargas. Recuperación de resistencia sugerida: 30 puntos/s después de una pausa breve sin consumirla.

| Acción | Daño sugerido | Coste de resistencia | Tiempo / efecto sugerido |
|---|---:|---:|---|
| Golpe ligero | 12 | 10 | ~0,35 s por golpe |
| Golpe fuerte | 28 | 25 | ~0,7 s |
| Esquiva | 0 | 20 | ~0,45 s |
| Parry | 0 | 10 | Ventana ~0,2 s |
| Corte de Fotograma | +10 postura | Sin coste de resistencia | Congela objetivo ~0,8 s |
| Retoma | Restaura estado personal | Una carga | Hasta 5 s atrás |

Son valores de arranque para tuning; no deben tratarse como números definitivos ni equilibrados por pruebas. Salud, resistencia, postura y cooldowns deberían ser editables.

## Arquetipos de enemigo

### 1. Perseguidor de Whitechapel

- Salud inicial sugerida: **45**.
- Civil hostil, empujado por rumores; ataca con puños/palo.
- Golpes legibles y relativamente lentos.
- Vulnerable a combos, parry y Corte de Fotograma.
- Papel: enseñar principios de lucha y ofrecer combates contra pequeños grupos.
- Al derrotarlo: neutralización **no letal**.

### 2. Interventor del Departamento

- Salud inicial sugerida: **80**.
- Equipado con bastón y defensa básica.
- Bloquea algunos ligeros y realiza ataque cargado.
- Requiere golpe fuerte, parry o manipulación temporal.
- Puede pasar de supuesto aliado a hostil al recibir la orden de corrección.

### 3. Supervisor — jefe

- Salud inicial sugerida: **180**.
- Usa tecnología temporal semejante a la del protagonista.
- Ataque simple, ataque circular y movimiento temporal corto.
- Resiste parcialmente Corte de Fotograma: interrupción reducida.
- En una fase posterior (~50 % de salud) puede repetir un ataque desde otra posición, si se llega a implementar.
- Derrotarlo habilita el acceso al archivo; **no decide el final automáticamente**.

## Comportamiento de IA en combate

- Crear estados de patrulla, sospecha, persecución, combate, aturdimiento y neutralización.
- Mostrar telegráficas visuales/animadas antes de golpes peligrosos.
- Ante tres enemigos, intentar que solo uno o dos ataquen a la vez; los demás rodean o reposicionan.
- Evitar enemigos esponja de daño.
- El contexto isométrico exige no ocultar telegráficas tras escenografía.
- Las heridas de enemigos **persisten durante Retoma**.

## Ejemplo de encuentro: callejón con tres perseguidores

1. El primero realiza un golpe frontal; el jugador puede hacer parry.
2. El contraataque aturde al primero.
3. El segundo empieza un golpe, el jugador usa **Corte de Fotograma** para interrumpirlo.
4. Un golpe fuerte derriba o desplaza a los enemigos.
5. Un tercero castiga la apertura. Si el jugador usa **Retoma**, recupera su posición y estado personal de segundos atrás; los enemigos continúan dañados.

Esto es una secuencia **ilustrativa** de decisiones, no un combate coreografiado obligatorio.

## Encuentros narrativos sugeridos

- **Acto I:** 2 civiles para enseñar el combate; un tercero puede permitir probar Corte de Fotograma.
- **Acto II:** tres perseguidores en callejón y un Interventor que puede volverse hostil tras la revelación.
- **Acto III:** enfrentamiento final contra Supervisor, seguido de elección narrativa.

## Implementación funcional esperada

- Orientación del ataque hacia cursor; alcance frontal definido.
- Ventanas de impacto con Animation Notifies.
- Sphere Trace/overlap durante ventanas activas; un único daño por actor y por ataque.
- Máquina de estados para impedir ataques superpuestos inválidos.
- Las acciones deben poder equilibrarse sin rehacer animaciones ni Blueprints.
- No es imprescindible lock-on, desmembramiento, fatalities, combos aéreos, árbol de habilidades, inventario extenso ni múltiples armas.
