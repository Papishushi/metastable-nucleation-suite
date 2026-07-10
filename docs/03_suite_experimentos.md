# 3. Suite de experimentos

Cada protocolo contiene una predicción nula según la ciencia conocida. Las cifras finales de tamaño muestral deben calcularse con datos piloto y preregistrarse.

## E01 — Línea base de nucleación y repetibilidad

**Pregunta:** ¿el tiempo de transición y el estado final son reproducibles estadísticamente?

**Sistema:** microgotas químicas, coloides, polaritones, Rydberg o iones.

**Diseño:** miles de ciclos por lote; orden aleatorio; registro de censura; reinicio validado.

**Métricas:** función de supervivencia, riesgo instantáneo, probabilidad de cada estado, autocorrelación y deriva.

**Predicción estándar:** dispersión entre ensayos; posible riesgo no constante; independencia aproximada solo después de modelar lote, historial y deriva.

**Anomalía relevante:** cambios abruptos sincronizados no explicados por instrumentación, seguidos de predicción fuera de muestra.

---

## E02 — Siembra controlada y curva dosis-respuesta

**Pregunta:** ¿una semilla reduce la barrera y selecciona un polimorfo/metaestado?

**Diseño:** dosis logarítmicas, tamaños de partícula caracterizados, semillas inertes y semillas de formas rivales; operadores ciegos.

**Predicción estándar:** aumento monotónico o umbral de tasa para la forma compatible; saturación; fuerte dependencia de interfaz y tamaño.

**Falsos positivos:** cambio químico por la preparación de semilla, disolvente residual o diferente área superficial.

---

## E03 — Propagación de contaminación material

**Pregunta:** ¿el historial de exposición explica el “contagio” de una forma?

**Diseño:** salas A/B, flujo unidireccional, cupones testigo, personal separado, intercambio aleatorio de material esterilizado, trazadores no reactivos.

**Predicción estándar:** la probabilidad sigue rutas físicas de transferencia; cae con limpieza, filtración y cambio de consumibles.

**Anomalía relevante:** transferencia reproducible sin ruta material y sin causa ambiental compartida, confirmada por terceros.

---

## E04 — Recuperación de una forma “desaparecida”

**Pregunta:** ¿la forma sigue siendo accesible mediante otra ruta cinética?

**Diseño:** mapa de solventes, presión, temperatura, sobresaturación, confinamiento, molienda y fases intermedias.

**Predicción estándar:** algunas formas reaparecen en regiones específicas; el espacio de fases no está borrado.

**Resultado negativo interpretable:** no recuperación dentro del dominio explorado, nunca “imposibilidad ontológica”.

---

## E05 — Variables locales y modelo multicanal

**Pregunta:** ¿sensores ordinarios explican la selección?

**Sensores:** temperatura distribuida, vibración, acústica, presión, humedad, campos E/B, radiación ionizante, espectro RF, potencia láser, fase, vacío, composición y partículas.

**Predicción estándar:** parte de la varianza se atribuye a variables locales e interacciones no lineales; el rendimiento fuera de muestra será menor que el ajuste in-sample.

**Análisis:** modelo jerárquico, regularización, calibración, prueba temporal bloqueada y control de fuga de información.

---

## E06 — Retroacción de medida

**Pregunta:** ¿la observación altera la transición?

**Brazos:** sin sonda; sonda débil; sonda fuerte; lectura después de la transición; lectura destructiva; detector encendido sin luz.

**Predicción estándar:** la tasa o estado puede depender de potencia, detuning, pérdidas y calentamiento. La dependencia debe ser local y cuantificable.

**Anomalía relevante:** efecto sin intercambio energético o canal físico identificable, replicado con instrumentos distintos.

---

## E07 — Red terrestre de correlación

**Pregunta:** ¿hay una componente común entre laboratorios independientes?

**Diseño:** al menos tres nodos, hardware heterogéneo, lotes independientes y sellado temporal. Cada nodo ejecuta E01 y E05.

**Predicción estándar:** las correlaciones brutas disminuyen al condicionar por hora, clima, red, actividad geomagnética y software. Pueden quedar correlaciones débiles por causas compartidas no medidas.

**Criterio:** una señal debe predecir ventanas futuras y mostrar geometría/retardo consistente; no basta un pico post hoc.

---

## E08 — Red Tierra–órbita–espacio profundo

**Pregunta:** ¿una perturbación propagante conocida o desconocida modula la transición?

**Diseño conceptual:** nodos en Tierra, órbita y plataforma distante; relojes propios calibrados; ventanas de observación preregistradas.

**Predicción estándar:** radiación, temperatura, aceleración y entorno gravitatorio producirán diferencias locales enormes. Tras modelarlas, no se espera correlación residual universal.

**Firma de propagación:** secuencia temporal consistente con una dirección y velocidad; amplitud dependiente de geometría; recurrencia.

---

## E09 — Bifurcación óptica metaestable independiente

**Pregunta:** ¿dos cavidades independientes seleccionan estados sin correlación?

**Sistema preferido:** microcavidad de excitón-polaritones o polaritones de Rydberg con dos atractores simétricos.

**Salida:** polarización ±, vorticidad ±, fase 0/π o modo espacial A/B.

**Predicción estándar:** cada nodo produce una secuencia local sesgada por imperfecciones; la correlación cruzada es cero tras descontar fuentes comunes.

**Objetivo:** validar reinicio, simetría, velocidad y lectura antes de cualquier test fundamental.

---

## E10 — Amplificación de entrelazamiento preparado

**Pregunta:** ¿una entrada cuántica entrelazada puede determinar el metaestado macroscópico sin destruir la correlación?

**Diseño:** una fuente entrelazada distribuye entradas a A/B; cada nodo transforma el resultado microscópico en una bifurcación óptica.

**Predicción estándar:** puede observarse Bell si la cadena completa —fuente, acoplamiento, selección y lectura— conserva suficiente visibilidad y eficiencia. La bifurcación no genera no localidad adicional; actúa como amplificador.

**Criterio:** comparar Bell antes y después del amplificador; cuantificar fidelidad de transferencia.

---

## E11 — Bell con salida metaestable

**Pregunta:** ¿la salida macroscópica conserva correlaciones incompatibles con modelos locales?

**Requisitos:** elecciones `x,y` rápidas y locales; ventana espacio-separada; resultado definido dentro de la ventana; alta eficiencia; análisis event-ready o desigualdad adecuada.

**Predicción cuántica estándar:** con entrelazamiento preparado, `2 < |S| ≤ 2√2` según visibilidad. Con entradas separables, `|S| ≤ 2`.

**Punto crítico:** la lectura tardía del cristal no define el instante de decisión; debe identificarse el evento físico irreversible que fija el resultado.

---

## E12 — Búsqueda de no localidad espontánea

**Pregunta:** ¿dos nodos preparados independientemente violan Bell sin una fuente común?

**Diseño:** láseres, relojes, QRNG, alimentación, control y fabricación independientes; configuraciones locales tardías; comparación posterior.

**Predicción estándar:** `|S| ≤ 2`. Cualquier aparente violación inicial debe hacer sospechar selección de coincidencias, memoria, pérdida dependiente del ajuste, sincronización compartida o error de código.

**Umbral de escalado:** replicación ciega en una segunda plataforma física y análisis independiente antes de interpretar.

---

## E13 — Test explícito de no señalización

**Pregunta:** ¿la elección remota cambia la distribución local?

**Diseño:** la estación B modula `y` con una secuencia preregistrada y oculta a A; A analiza solo sus marginales antes de recibir datos de B.

**Predicción estándar:** ninguna dependencia: `P(a|x,y=0)=P(a|x,y=1)` dentro de incertidumbre y correcciones.

**Advertencia:** relojes o filtros de coincidencia pueden fabricar señalización aparente. El análisis marginal debe usar todos los ensayos, no solo parejas aceptadas post hoc.

---

## E14 — Replicación cruzada de plataforma

**Pregunta:** ¿una anomalía depende del dispositivo?

**Plataformas:** polaritones, átomos de Rydberg, iones zig/zag, moléculas polares y sistemas electrónicos.

**Predicción estándar:** los detalles cambian; no aparece una correlación universal entre nodos independientes. Una causa ambiental específica puede acoplarse solo a algunas plataformas.

**Valor:** una misma firma adimensional y temporal en sistemas con acoplamientos distintos sería mucho más informativa que repetir el mismo aparato.

---

## E15 — Canal gravitacional cuántico, fase futura

**Pregunta:** ¿la gravedad media correlaciones cuánticas entre masas?

**Diseño conceptual:** dos osciladores/masas coherentes; blindaje electromagnético extremo; testigo de entrelazamiento leído ópticamente.

**Predicción estándar efectiva:** la gravedad clásica produce fuerza y fase; varias propuestas sostienen que un mediador estrictamente clásico no genera cierto tipo de entrelazamiento, aunque la interpretación depende del marco. No es un experimento de “cristal de gravitones” y no permite atrapar gravitones.

**Estado:** fuera del alcance del laboratorio óptico inicial; mantener como línea separada para evitar contaminar la hipótesis principal.

## Tabla resumida de resultados esperados

| Experimento | Física conocida espera | Resultado que NO basta | Resultado potencialmente decisivo |
|---|---|---|---|
| E02 Siembra | dosis-respuesta y memoria material | una forma aparece más a menudo | efecto reproducible y caracterizado |
| E07 Red | correlaciones por entorno compartido | simultaneidad | retardo geométrico predictivo |
| E10 Amplificación | Bell si entra entrelazamiento y se conserva | correlación simple | violación con salida metaestable |
| E12 Espontánea | `S ≤ 2` | `S > 2` tras múltiples análisis | violación preregistrada, sin lagunas, replicada |
| E13 Señalización | marginales invariantes | diferencia en coincidencias filtradas | dependencia marginal local, ciega y replicada |
