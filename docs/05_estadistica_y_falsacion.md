# 5. Estadística y falsación

El análisis estadístico de esta suite no se limita a calcular valores `p`. Su objetivo es definir de antemano qué observación sería compatible con la física conocida, qué resultado indicaría un problema instrumental y qué evidencia justificaría una replicación más exigente. Esto requiere separar análisis confirmatorios y exploratorios, conservar todos los ensayos relevantes y utilizar modelos que respeten la estructura temporal de los datos.

## 5.1 Preregistro

Antes de abrir un bloque confirmatorio deben quedar fijados la variable primaria, las reglas de exclusión, el número de ensayos o la regla de parada, las ventanas temporales, el procedimiento de emparejamiento, el modelo nulo y la corrección por comparaciones múltiples. También debe definirse un umbral de escalado científico, no solo un umbral de significancia.

Los análisis exploratorios son legítimos, pero deben identificarse como tales. Cualquier patrón descubierto durante una exploración debe validarse en un bloque de datos nuevo. Esta separación evita que una hipótesis construida después de observar los datos se presente como si hubiera sido predicha.

## 5.2 Tiempos de nucleación, supervivencia y riesgo

Cuando el resultado principal es el tiempo de transición `T`, la descripción adecuada utiliza la función de supervivencia y el riesgo instantáneo:

\[
S(t)=P(T>t),\qquad h(t)=\lim_{dt\to0}\frac{P(t\le T<t+dt|T\ge t)}{dt}.
\]

Un proceso de Poisson estacionario presenta riesgo constante y supervivencia exponencial. Las desviaciones de este comportamiento pueden indicar envejecimiento del sistema, mezcla de poblaciones, heterogeneidad entre recipientes, memoria o covariables que cambian con el tiempo. No constituyen por sí mismas evidencia de nueva física.

El análisis debe incorporar censura derecha cuando un ensayo termina antes de observar la transición. También debe incluir efectos aleatorios por lote, nodo y día, además de covariables dependientes del tiempo. La validación debe respetar el orden temporal; una división aleatoria que mezcle periodos antiguos y futuros puede ocultar deriva y producir una capacidad predictiva artificial.

## 5.3 Selección de polimorfo o metaestado

La identidad del estado final debe modelarse mediante riesgos competitivos, regresión multinomial u otro método que distinga correctamente las etapas del proceso. Es necesario separar el tiempo hasta la primera nucleación, la identidad del primer núcleo, las transformaciones posteriores y el estado observado al final.

Confundir estas etapas puede atribuir la selección al mecanismo equivocado. Un polimorfo puede nuclear primero y transformarse después, o puede aparecer tarde porque otra forma ha actuado como precursor. La clasificación debe apoyarse en medidas temporales o estructurales suficientes para distinguir estas posibilidades.

## 5.4 Correlaciones distribuidas

Una correlación de Pearson aislada es insuficiente para estudiar una red de laboratorios. El análisis debe examinar coherencia espectral, correlaciones con retardos, capacidad predictiva temporal, permutaciones por bloques, controles negativos y modelos de variables latentes.

La geometría de una perturbación debe predecirse antes de explorar todos los retardos posibles. Si primero se buscan miles de ventanas y luego se selecciona la más llamativa, el resultado queda afectado por multiplicidad. Una señal distribuida adquiere valor cuando predice datos futuros y mantiene su estructura temporal y espacial en periodos independientes.

## 5.5 Desigualdad CHSH

Para cada par de ajustes `(x,y)`, la correlación se calcula como

\[
E_{xy}=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{xy}}.
\]

El parámetro CHSH se obtiene mediante

\[
S=E_{00}+E_{01}+E_{10}-E_{11}.
\]

Los modelos locales satisfacen `|S| ≤ 2` en el límite ideal. Sin embargo, una muestra finita puede producir valores ligeramente superiores a dos. La significación debe calcularse con un método compatible con la estructura real del experimento.

No deben utilizarse errores gaussianos ingenuos cuando existe memoria, parada adaptativa, baja tasa de eventos o selección compleja. Dependiendo del protocolo, pueden ser necesarios métodos basados en martingalas, análisis event-ready o pruebas robustas frente a dispositivos con memoria.

## 5.6 Visibilidad y fidelidad global

En un modelo ideal con visibilidad `V`, la predicción es

\[
S=2\sqrt{2}V.
\]

Para superar el límite local se requiere `V>1/\sqrt{2}≈0.707`, antes de considerar pérdidas, errores de clasificación y sesgos. La fidelidad relevante es la de toda la cadena: preparación, transmisión, acoplamiento, bifurcación y lectura.

Un amplificador metaestable puede aumentar la robustez macroscópica del resultado y, al mismo tiempo, reducir la visibilidad si introduce decoherencia o mezcla. Por eso la comparación antes y después del amplificador debe formar parte del diseño y no limitarse a observar la salida final.

## 5.7 Detección y postselección

Ningún ensayo debe eliminarse utilizando información correlacionada con el ajuste o con el resultado. Las no detecciones, clasificaciones ambiguas, saturaciones, reinicios fallidos y pulsos fuera de rango deben registrarse explícitamente.

El protocolo debe indicar de antemano cómo se incorporan estos eventos a la desigualdad o al diseño event-ready. Seleccionar solo los ensayos «buenos» puede fabricar correlaciones y violaciones aparentes. La eficiencia y la probabilidad de aceptación deben examinarse por ajuste, estado, nodo y periodo temporal.

## 5.8 No señalización

La prueba de no señalización utiliza los marginales locales de todos los ensayos válidos definidos previamente. Para A puede calcularse, por ejemplo,

\[
\Delta_A(x)=P(a=+1|x,y=0)-P(a=+1|x,y=1).
\]

El análisis debe proporcionar intervalos de confianza simultáneos, comprobar sensibilidad a deriva y estratificar por tiempo cuando sea necesario. La estación A debe poder analizar sus datos antes de conocer las elecciones remotas de B.

Las ventanas de coincidencia y la latencia pueden crear dependencias artificiales. Por ello, la prueba principal no debe depender de emparejamientos ajustados después de revelar los datos conjuntos.

## 5.9 Criterio de descubrimiento

Para las hipótesis extraordinarias H7 y H8 no existe un único umbral numérico suficiente. Como mínimo, la señal debe aparecer en un bloque preregistrado, presentar un tamaño estable, superar un modelo nulo robusto y replicarse de forma independiente.

Además, el código y el hardware deben someterse a auditoría, la hipótesis debe producir una predicción nueva y los datos crudos junto con el análisis deben publicarse. Una evidencia estadística muy intensa puede seguir siendo insuficiente si el modelo nulo omite una familia plausible de fallos instrumentales.

## 5.10 Uso responsable de métodos bayesianos

Las probabilidades previas de contaminación, deriva, error de reloj y violación de causalidad no son comparables. Un Bayes factor elevado a favor de una hipótesis extraordinaria puede dejar una probabilidad posterior baja si las explicaciones ordinarias no están modeladas adecuadamente.

El enfoque bayesiano resulta útil cuando obliga a declarar modelos, incertidumbres y probabilidades previas. Se vuelve decorativo cuando se utiliza una alternativa exótica detallada frente a un nulo ordinario demasiado pobre. Por eso la suite amplía agresivamente la familia de modelos nulos y exige replicación externa.
