# 5. Estadística y falsación

## 5.1 Preregistro

Antes de abrir datos críticos se fijan:

- variable primaria;
- exclusiones y fallos de hardware;
- número de ensayos o regla secuencial;
- ventanas temporales;
- emparejamiento de eventos;
- corrección por comparaciones múltiples;
- modelo nulo;
- umbral de escalado, no solo de “significancia”.

Los análisis exploratorios se etiquetan como tales y se validan en un bloque nuevo.

## 5.2 Nucleación: supervivencia y riesgo

Para ensayos con tiempo de transición `T`, usar supervivencia:

\[
S(t)=P(T>t),\qquad h(t)=\lim_{dt\to0}\frac{P(t\le T<t+dt|T\ge t)}{dt}.
\]

Un proceso Poisson estacionario tiene riesgo constante y supervivencia exponencial. Desviaciones pueden indicar envejecimiento, mezcla de poblaciones, heterogeneidad o memoria; no implican nueva física.

Incluir:

- censura derecha;
- efectos aleatorios por lote, nodo y día;
- covariables dependientes del tiempo;
- validación temporal, no división aleatoria que mezcle drift.

## 5.3 Selección de polimorfo/metaestado

Modelar el estado `k` mediante riesgo competitivo o regresión multinomial. Separar:

- tiempo hasta primera nucleación;
- identidad del primer núcleo;
- transformación posterior;
- estado observado al final.

Confundir el primer núcleo con el cristal final puede atribuir selección a la etapa equivocada.

## 5.4 Correlaciones distribuidas

No buscar únicamente correlación de Pearson. Evaluar:

- coherencia espectral;
- correlación con retardos;
- causalidad temporal predictiva;
- permutaciones por bloques;
- controles negativos;
- replicación en periodos futuros;
- modelos de variable latente.

La geometría de una perturbación debe predecirse antes de inspeccionar todos los retardos posibles.

## 5.5 CHSH

Para cada par de ajustes `(x,y)`:

\[
E_{xy}=\frac{N_{++}+N_{--}-N_{+-}-N_{-+}}{N_{xy}}.
\]

Luego:

\[
S=E_{00}+E_{01}+E_{10}-E_{11}.
\]

No usar errores gaussianos ingenuos si hay memoria, parada adaptativa o baja cuenta. Preferir pruebas válidas frente a dispositivos con memoria, martingalas o métodos event-ready según el protocolo.

## 5.6 Umbral de visibilidad

En un modelo ideal con visibilidad `V`:

\[
S=2\sqrt{2}V.
\]

Para superar 2 se requiere `V>1/\sqrt{2}≈0.707`, sin contar pérdidas y sesgos. El amplificador metaestable debe conservar una fidelidad global suficientemente alta.

## 5.7 Detección y postselección

Nunca eliminar ensayos según información correlacionada con el resultado o el ajuste. Registrar explícitamente:

- no detección;
- resultado ambiguo;
- saturación;
- reinicio fallido;
- pulso fuera de rango.

Una desigualdad o diseño event-ready debe incorporar estos eventos. “Nos quedamos con los buenos” es una máquina de fabricar fantasmas.

## 5.8 No señalización

Comprobar marginales con todos los ensayos válidos definidos de antemano:

\[
\Delta_A(x)=P(a=+1|x,y=0)-P(a=+1|x,y=1).
\]

La prueba debe incluir:

- intervalo de confianza simultáneo;
- sensibilidad a drift;
- estratificación temporal;
- análisis ciego de A antes de revelar `y`;
- control de emparejamiento y latencia.

## 5.9 Criterio de descubrimiento

Para H7/H8 no se recomienda un único umbral universal. El paquete mínimo sería:

1. efecto en bloque preregistrado;
2. evidencia secuencial o `p` extremadamente bajo bajo un nulo robusto;
3. tamaño del efecto estable;
4. replicación independiente;
5. auditoría de código y hardware;
6. predicción nueva acertada;
7. publicación de datos crudos y análisis.

## 5.10 Bayesianismo útil, no decorativo

Asignar probabilidades previas muy distintas a contaminación, drift y violación de causalidad. Un Bayes factor grande puede seguir dejando baja probabilidad posterior a una hipótesis extraordinaria si el modelo alternativo ordinario está incompleto. Por eso hay que ampliar agresivamente la familia de nulos y usar replicación externa.
