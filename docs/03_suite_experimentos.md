# 3. Suite de experimentos

Esta suite reúne quince protocolos organizados como una escalera de evidencia. Los primeros experimentos estudian la nucleación, la metaestabilidad y el polimorfismo dentro del marco de la física y la química conocidas. Los protocolos intermedios analizan causas comunes, retroacción de medida y correlaciones distribuidas. Los últimos experimentos examinan si una transición metaestable puede conservar correlaciones cuánticas preparadas y, de manera deliberadamente especulativa, si podrían aparecer correlaciones incompatibles con los modelos locales en ausencia de una fuente común.

Cada experimento incluye una predicción nula explícita. Esa predicción describe lo que debería observarse si la física conocida es suficiente para explicar los datos. Los tamaños muestrales, criterios de exclusión, ventanas temporales y umbrales de decisión deberán calcularse con datos piloto y quedar fijados en un preregistro antes de abrir el bloque confirmatorio. Las fuentes primarias que justifican cada protocolo se recogen en `docs/09_fuentes_por_experimento.md` y en `references.bib`.

## E01 — Línea base de nucleación y repetibilidad

El primer experimento establece cómo se comporta el sistema cuando no se introduce ninguna perturbación deliberada. Su objetivo es determinar si el tiempo de transición, el estado final y la probabilidad de seleccionar cada polimorfo o metaestado son estadísticamente reproducibles. Este paso es imprescindible porque no puede hablarse de una anomalía mientras no exista una descripción fiable de la variabilidad ordinaria del dispositivo.

El protocolo puede aplicarse a microgotas químicas, suspensiones coloidales, microcavidades polaritónicas, gases de Rydberg, cristales iónicos u otras plataformas que presenten transiciones entre estados metaestables. Cada lote debe someterse a miles de ciclos de preparación, evolución y lectura. El orden de los ensayos se aleatorizará, el reinicio se verificará mediante observables independientes y se conservarán los ensayos censurados, las no detecciones y los fallos de preparación en lugar de eliminarlos silenciosamente.

El análisis debe incluir la distribución completa de tiempos de espera, la función de supervivencia, el riesgo instantáneo de transición, la probabilidad de cada estado final, la autocorrelación entre ensayos consecutivos y la deriva a lo largo del tiempo. También debe separarse la variabilidad dentro de un lote de la variabilidad entre lotes y entre sesiones experimentales.

La física conocida no predice tiempos idénticos entre repeticiones. Se espera una dispersión amplia, un riesgo que puede variar con el tiempo y una independencia aproximada únicamente después de modelar la memoria del sistema, el lote, la deriva térmica y el historial de exposición. Una aparente sincronización o un cambio abrupto solo sería relevante si no pudiera atribuirse a la instrumentación, persistiera en datos fuera de muestra y se reprodujera con un protocolo previamente fijado.

## E02 — Siembra controlada y curva dosis-respuesta

Este experimento estudia hasta qué punto una semilla material reduce la barrera de nucleación y favorece un polimorfo o metaestado concreto. La hipótesis convencional es que una superficie estructuralmente compatible facilita la formación del núcleo crítico y modifica tanto el tiempo de espera como la distribución de estados finales.

El diseño debe utilizar varias dosis de semilla distribuidas en escala logarítmica y partículas cuyo tamaño, composición, estructura superficial y área específica hayan sido caracterizados. Deben incluirse semillas compatibles con formas rivales, partículas inertes con propiedades físicas semejantes y controles sometidos al mismo proceso de preparación pero sin material activo. Los operadores responsables de la lectura deben permanecer ciegos a la condición experimental.

La predicción estándar es una respuesta monotónica o con umbral: al aumentar la cantidad de semilla compatible debería aumentar la tasa de nucleación o la probabilidad de seleccionar la forma correspondiente, hasta alcanzar una región de saturación. La magnitud del efecto dependerá de la interfaz, del tamaño de partícula, del disolvente, de la sobresaturación y del tiempo de exposición.

La interpretación debe descartar que la preparación de la semilla haya alterado la composición química del sistema. Los disolventes residuales, las impurezas, el cambio de pH, la distinta área superficial o una modificación de la agitación pueden imitar un efecto de siembra. El resultado científicamente útil no es simplemente que una forma aparezca más veces, sino obtener una relación dosis-respuesta cuantitativa, reproducible y compatible con un mecanismo físico identificable.

## E03 — Propagación de contaminación material

El objetivo de este protocolo es comprobar si el llamado “contagio” de un polimorfo puede explicarse por una ruta material ordinaria. La hipótesis de partida es que cristales, polvo, aerosoles, utensilios, ropa, filtros o superficies contaminadas pueden transportar semillas microscópicas entre experimentos y alterar la nucleación posterior.

El laboratorio se dividirá en al menos dos circuitos físicamente separados. Cada circuito tendrá personal, consumibles, ventilación y material de manipulación independientes. Se instalarán cupones testigo en puntos críticos, se emplearán trazadores no reactivos para reconstruir rutas de transferencia y se introducirán intercambios aleatorios de material esterilizado y no esterilizado. El flujo de trabajo deberá ser unidireccional para evitar que el propio muestreo propague la contaminación que se pretende medir.

La física conocida predice que la aparición de una forma seguirá las rutas materiales de exposición. El efecto debería disminuir al renovar filtros, sustituir consumibles, limpiar superficies, cambiar de vestimenta o aislar los circuitos. También debería mostrar una dependencia razonable con la distancia, el flujo de aire, el tiempo de exposición y la concentración de partículas.

Una transferencia aparente sin ruta física solo sería relevante después de demostrar que los controles de contaminación tienen sensibilidad suficiente y que no existe una causa ambiental compartida. Incluso entonces, la prioridad sería buscar fallos de sellado, errores de etiquetado, contaminación cruzada en reactivos o sesgos de clasificación. Una interpretación extraordinaria exigiría replicación independiente en otro laboratorio con procedimientos y personal distintos.

## E04 — Recuperación de una forma “desaparecida”

Este experimento investiga si un polimorfo que ha dejado de obtenerse mediante una receta concreta sigue siendo accesible a través de otra trayectoria cinética. La pregunta no es si el estado ha sido eliminado de la naturaleza, sino si el procedimiento habitual ha dejado de atravesar la región del espacio de fases en la que esa forma puede nuclear.

El protocolo debe explorar de manera sistemática el disolvente, la temperatura, la presión, la sobresaturación, la velocidad de enfriamiento, la agitación, el confinamiento, la molienda, la presencia de superficies, los aditivos y las posibles fases intermedias. Cuando sea posible, se utilizarán métodos de diseño experimental para cubrir el espacio de parámetros sin depender de una búsqueda manual sesgada.

La expectativa estándar es que algunas formas reaparezcan en regiones específicas del espacio de condiciones, mientras que otras permanezcan inaccesibles dentro del dominio explorado. La recuperación puede requerir una trayectoria multietapa, un precursor distinto o un confinamiento que estabilice transitoriamente una estructura que no aparece en el proceso convencional.

Un resultado negativo solo demuestra que la forma no fue recuperada bajo las condiciones ensayadas y con la sensibilidad disponible. No demuestra que haya dejado de existir como estado permitido. La conclusión debe formularse siempre en términos del dominio experimental explorado y de los límites de detección.

## E05 — Variables locales y modelo multicanal

Este protocolo determina cuánto de la selección de estado puede explicarse mediante variables ambientales ordinarias. Su finalidad es sustituir la noción vaga de “algo externo” por una medición multicanal capaz de cuantificar temperatura, vibración, presión, campos electromagnéticos, radiación, composición, potencia óptica y otras perturbaciones relevantes.

El sistema de metrología debe registrar temperatura distribuida, vibración, acústica, presión, humedad, campos eléctricos y magnéticos, espectro de radiofrecuencia, radiación ionizante, potencia y fase láser, estado de vacío, composición química y concentración de partículas. Cada canal deberá tener una calibración, una resolución, una frecuencia de muestreo y una incertidumbre temporal documentadas.

El análisis utilizará modelos jerárquicos y regularizados para separar efectos locales, interacciones no lineales, lote, sesión y deriva. El rendimiento se evaluará sobre bloques temporales futuros que no hayan intervenido en el ajuste. También se comprobará que no exista fuga de información desde la clasificación final hacia las variables predictoras.

La predicción de la física conocida es que una fracción de la varianza será explicable por variables locales y por interacciones entre ellas. El rendimiento fuera de muestra será normalmente inferior al obtenido durante el ajuste. Una asociación que desaparece al cambiar de sesión o de dispositivo debe considerarse un artefacto del modelo, no una nueva ley física.

## E06 — Retroacción de medida

El sexto experimento estudia si el propio proceso de observación modifica la transición. En sistemas metaestables, una sonda puede introducir calor, pérdidas, fotones adicionales, presión de radiación, excitaciones, bloqueo por inyección o cambios en el tiempo de vida. Por tanto, observar no puede tratarse como una operación pasiva.

El protocolo comparará varios brazos: ausencia de sonda, sonda débil, sonda intensa, detector encendido sin iluminación, lectura retardada hasta después de la transición y lectura destructiva. La potencia, duración, frecuencia, polarización, desfase y geometría de la sonda deberán variar de manera controlada. También se medirán el calentamiento, la energía extraída y cualquier cambio en las pérdidas del sistema.

La predicción estándar es que la tasa de transición o la probabilidad de cada estado puede depender de la intensidad de la medición, del detuning, de las pérdidas y del calentamiento. Ese efecto debería ser local, reproducible y escalable con una magnitud física cuantificable.

Una dependencia que aparentemente carezca de intercambio energético no debe interpretarse de inmediato como un efecto fundamental. Primero deben excluirse acoplamientos parásitos, ruido electrónico, perturbaciones mecánicas, retroalimentación del software y diferencias en el tiempo de lectura. Solo una anomalía replicada con instrumentos y principios de detección diferentes justificaría una investigación más profunda.

## E07 — Red terrestre de correlación

Este protocolo busca una componente común entre laboratorios físicamente separados. La finalidad no es demostrar no localidad, sino cuantificar hasta qué punto sistemas independientes pueden mostrar correlaciones debido a clima, red eléctrica, actividad geomagnética, señales de tiempo, software o perturbaciones globales ordinarias.

La red deberá incluir al menos tres nodos con hardware heterogéneo, lotes independientes y relojes propios. Cada nodo ejecutará primero los protocolos E01 y E05 para caracterizar su comportamiento local. Los datos se sellarán temporalmente antes de compartirse, y los análisis confirmatorios se fijarán antes de conocer las series de los otros laboratorios.

La física conocida predice que las correlaciones brutas disminuirán al condicionar por hora, temperatura, presión, actividad geomagnética, estado de la red, firmware y calendario operativo. Pueden persistir correlaciones débiles debido a variables compartidas no medidas, pero esas correlaciones no deberían mostrar una estructura incompatible con una causa común clásica.

Una señal solo justificaría escalar el experimento si predijera ventanas futuras y presentara una geometría, un retardo o una dependencia direccional definidos de antemano. Un pico encontrado después de explorar muchas escalas temporales no constituye evidencia. La prueba debe sobrevivir a la corrección por multiplicidad y a la replicación en nodos adicionales.

## E08 — Red Tierra–órbita–espacio profundo

Este experimento extiende la red distribuida para comprobar si una perturbación propagante, conocida o desconocida, podría modular la transición de forma coherente en plataformas situadas en entornos muy diferentes. Se trata de un diseño conceptual de largo plazo, no de una fase inmediata del laboratorio.

La arquitectura incluiría nodos terrestres, orbitales y, si fuera viable, una plataforma más distante. Cada estación utilizaría relojes propios calibrados y conservaría una metrología completa de radiación, temperatura, aceleración, campos y entorno gravitatorio. Las ventanas de observación, las direcciones de búsqueda y los modelos de retardo se preregistrarían.

La expectativa estándar es que las diferencias locales sean enormes. La radiación, los ciclos térmicos, la microgravedad, las vibraciones y la exposición a partículas afectarán de manera distinta a cada plataforma. Después de modelar esas diferencias, no se espera una correlación residual universal entre sistemas independientes.

Una firma de propagación convincente tendría que aparecer en el orden temporal correcto, con un retardo compatible con una velocidad determinada, una amplitud dependiente de la geometría y recurrencia en eventos futuros. La coincidencia aproximada de dos transiciones no sería suficiente.

## E09 — Bifurcación óptica metaestable independiente

El objetivo de este experimento es construir y caracterizar dos sistemas ópticos capaces de seleccionar repetidamente entre dos atractores metaestables. Esta fase sirve para demostrar que cada nodo puede reiniciarse, mantenerse cerca de la simetría, evolucionar rápidamente y producir una lectura inequívoca antes de introducir entrelazamiento o pruebas de Bell.

La plataforma preferida es una microcavidad de excitón-polaritones o de polaritones de Rydberg con dos estados aproximadamente simétricos. La salida puede codificarse en polarización positiva o negativa, vorticidad opuesta, fase relativa `0/π` o dos modos espaciales equivalentes. Cada nodo debe utilizar su propio bombeo, control y adquisición.

La física conocida predice que las secuencias serán localmente aleatorias o estocásticas, pero estarán ligeramente sesgadas por imperfecciones de fabricación, deriva, campos residuales y ruido técnico. Tras modelar las fuentes comunes, la correlación cruzada entre nodos independientes debe ser compatible con cero.

El resultado principal de esta fase no es una anomalía, sino una caracterización fiable del tiempo de compromiso, la fidelidad de lectura, el sesgo residual, la memoria entre ciclos y la eficiencia de detección. Sin estas magnitudes no puede formularse un test fundamental interpretable.

## E10 — Amplificación de entrelazamiento preparado

Este protocolo examina si una entrada cuántica entrelazada puede dirigir una bifurcación macroscópica sin perder las correlaciones originales. La pregunta no es si la bifurcación crea no localidad, sino si puede actuar como un amplificador que convierte un resultado microscópico en un metaestado óptico robusto.

Una fuente central distribuirá estados entrelazados hacia los nodos A y B. En cada nodo, la entrada cuántica se acoplará a una variable que determine la rama de la bifurcación. Se medirá la correlación antes del amplificador, durante la transferencia y en la salida metaestable final.

La mecánica cuántica estándar permite observar una violación de Bell si la fuente, el canal, el acoplamiento, la selección de estado y la lectura conservan suficiente visibilidad y eficiencia. La bifurcación no añade una no localidad nueva; únicamente amplifica una correlación que ya estaba presente en la entrada.

El criterio de éxito consiste en demostrar una fidelidad de transferencia cuantificada y comparar el parámetro de Bell antes y después de la amplificación. Una pérdida de violación puede deberse a decoherencia, ineficiencia, sesgo de detección o mezcla entre estados y no implica que la mecánica cuántica falle.

## E11 — Bell con salida metaestable

Este experimento estudia si una salida macroscópica puede conservar correlaciones incompatibles con un modelo local. La diferencia respecto a E10 es que aquí el metaestado final se convierte en la variable de resultado utilizada directamente en la desigualdad de Bell.

Las elecciones locales `x` e `y` deben realizarse de manera rápida e independiente. El intervalo entre la elección de ajuste y el evento que fija el resultado tiene que estar separado espacialmente del evento correspondiente en el otro nodo. La eficiencia debe ser suficientemente alta y el protocolo deberá utilizar una arquitectura `event-ready` o una desigualdad adecuada al patrón real de detección.

La predicción cuántica estándar es que, con una entrada entrelazada y suficiente visibilidad, el parámetro CHSH puede satisfacer `2 < |S| ≤ 2√2`. Con entradas separables o con un modelo local, debe cumplirse `|S| ≤ 2`, salvo fluctuaciones estadísticas finitas.

El punto más delicado es definir el instante físico de compromiso. La lectura tardía de la cavidad no determina cuándo quedó fijado el resultado. El experimento debe identificar un evento irreversible o, al menos, una ventana acotada en la que el sistema deja de poder cambiar de rama. Sin esa definición no puede afirmarse que se haya cerrado la localidad.

## E12 — Búsqueda de no localidad espontánea

Este protocolo plantea la hipótesis extraordinaria de que dos sistemas preparados independientemente podrían mostrar correlaciones de Bell sin compartir una fuente entrelazada ni un canal causal común. La física estándar no predice este comportamiento, por lo que el experimento está diseñado principalmente para encontrar errores y límites instrumentales.

Los nodos deben utilizar láseres, relojes, generadores aleatorios, alimentación, electrónica de control y fabricación independientes. Las configuraciones locales se elegirán en el último momento y los datos solo se compararán después de cerrar cada bloque. Los criterios de coincidencia, exclusión y emparejamiento deben quedar fijados antes de observar los resultados conjuntos.

La predicción estándar es `|S| ≤ 2`. Una violación inicial debe hacer sospechar selección de coincidencias, memoria, pérdidas dependientes del ajuste, sincronización compartida, errores de software, filtrado post hoc o una definición incorrecta del ensayo válido.

Ningún resultado se interpretará como nueva física sin una replicación ciega en una segunda plataforma, un análisis independiente y una auditoría completa de la cadena temporal y de detección. El umbral epistemológico debe ser mucho más alto que en un experimento ordinario, porque la hipótesis contradice una estructura muy bien establecida de la teoría actual.

## E13 — Test explícito de no señalización

Este experimento comprueba si la elección realizada en una estación modifica la distribución local observada en la otra. Se trata de una prueba distinta de Bell: una violación de Bell puede ser compatible con la mecánica cuántica, mientras que una dependencia controlable de los marginales remotos sería incompatible con el principio de no señalización.

La estación B modulará su ajuste `y` mediante una secuencia preregistrada que permanecerá oculta para A. La estación A analizará sus resultados locales sin recibir ninguna información de B. El procedimiento se repetirá de forma simétrica y se conservarán todos los ensayos, incluidas las no detecciones.

La mecánica cuántica estándar predice que `P(a|x,y=0)=P(a|x,y=1)` dentro de la incertidumbre estadística y de las correcciones previamente definidas. Las correlaciones conjuntas pueden cambiar con los ajustes, pero los marginales locales no deben permitir inferir la elección remota.

Los relojes, las ventanas de coincidencia y los filtros de aceptación pueden fabricar una señalización aparente. Por eso el análisis principal debe utilizar todos los ensayos locales y no únicamente las parejas seleccionadas después de comparar marcas temporales. Una dependencia marginal solo sería relevante si fuera ciega, reproducible y resistente a cambios en el procedimiento de emparejamiento.

## E14 — Replicación cruzada de plataforma

El objetivo de este protocolo es determinar si una anomalía pertenece al fenómeno investigado o al dispositivo concreto que la produjo. Una señal que solo aparece en una microcavidad determinada es mucho más probable que se deba a su fabricación, electrónica o entorno que a una propiedad universal de la nucleación.

La replicación deberá trasladar la misma hipótesis operacional a plataformas con mecanismos físicos distintos, como polaritones, átomos de Rydberg, transiciones lineal–zigzag en iones, moléculas polares o sistemas electrónicos. No es necesario que los observables microscópicos sean idénticos, pero sí deben definirse variables adimensionales y ventanas temporales comparables.

La física conocida predice que los detalles de la dinámica cambiarán entre plataformas y que no aparecerá una correlación universal entre nodos independientes. Una causa ambiental concreta puede acoplarse con intensidad a una plataforma y ser prácticamente invisible en otra.

Una firma con la misma dependencia temporal, geométrica y estadística en sistemas con acoplamientos diferentes sería mucho más informativa que repetir indefinidamente el mismo aparato. Aun así, la consistencia entre plataformas no elimina por sí sola las causas comunes de software, análisis o sincronización.

## E15 — Canal gravitacional cuántico, fase futura

El último protocolo se mantiene como una línea separada de investigación. Su objetivo es estudiar si la interacción gravitatoria entre masas coherentes puede mediar correlaciones cuánticas o generar un testigo de entrelazamiento. No constituye un experimento de “cristal de gravitones” ni presupone que los gravitones puedan atraparse, reflejarse o detectarse individualmente.

El diseño conceptual utiliza dos masas u osciladores preparados en estados coherentes o superpuestos, con blindaje electromagnético extremo y lectura óptica de un testigo de entrelazamiento. El desafío principal consiste en demostrar que cualquier correlación no procede de fuerzas electrostáticas, magnéticas, Casimir, vibracionales o de acoplamientos mecánicos convencionales.

En la descripción efectiva estándar, la gravedad clásica produce fuerzas y fases. Diversas propuestas sostienen que un mediador estrictamente clásico no puede generar ciertos tipos de entrelazamiento, aunque la interpretación depende del marco teórico y de los supuestos sobre medición y causalidad.

Este protocolo está fuera del alcance del laboratorio óptico inicial. Debe conservarse como una fase futura independiente para evitar mezclar una prueba de mediación gravitatoria cuántica con la hipótesis principal sobre nucleación y metaestados ópticos.

## Resumen de la escalera de evidencia

| Experimento | Predicción de la física conocida | Observación insuficiente | Resultado que justificaría escalar |
|---|---|---|---|
| E02 — Siembra controlada | La tasa y la selección de forma dependen de la dosis, la interfaz y el tamaño de semilla. | Que una forma aparezca más veces en un único lote. | Una curva dosis-respuesta reproducible con controles químicos y superficiales. |
| E07 — Red terrestre | Las correlaciones disminuyen al modelar las causas ambientales y operativas compartidas. | Una coincidencia temporal encontrada después de explorar muchas ventanas. | Una señal preregistrada que prediga datos futuros y presente retardo o geometría coherentes. |
| E10 — Amplificación | El entrelazamiento preparado puede conservarse si la cadena mantiene visibilidad y eficiencia. | Una correlación simple entre dos salidas macroscópicas. | Una violación de Bell conservada y cuantificada después de la amplificación. |
| E12 — No localidad espontánea | Dos nodos independientes satisfacen <code>&#124;S&#124; ≤ 2</code>. | Un valor `S > 2` obtenido tras selección, filtrado o múltiples análisis. | Una violación preregistrada, sin lagunas relevantes y replicada en otra plataforma. |
| E13 — No señalización | Las distribuciones marginales locales son independientes del ajuste remoto. | Una diferencia observada únicamente en coincidencias filtradas. | Una dependencia marginal local, ciega, reproducible y resistente a cambios de análisis. |
