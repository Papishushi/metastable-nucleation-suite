# 1. Marco científico

Este documento establece el vocabulario y los límites conceptuales de la suite. Su función no es defender una interpretación concreta de la mecánica cuántica ni presentar una explicación definitiva de la nucleación. Pretende separar con claridad los fenómenos ya establecidos, las hipótesis físicamente plausibles y las afirmaciones extraordinarias que requerirían evidencia nueva.

## 1.1 Nucleación y metaestabilidad

Una fase metaestable es un estado que puede persistir durante un tiempo largo aunque no sea el mínimo global de energía libre. El sistema queda retenido porque existe una barrera que separa ese estado de una configuración más estable. En una descripción clásica simplificada, la tasa de nucleación puede expresarse como

\[
J = A\exp\left(-\frac{\Delta G^*}{k_B T}\right),
\]

donde `A` representa un prefactor cinético y `ΔG*` la barrera efectiva asociada a la formación de un núcleo crítico. La dependencia exponencial implica que pequeñas variaciones en temperatura, composición, interfaz, campo externo o concentración de impurezas pueden producir cambios muy grandes en la tasa observada.

Esta sensibilidad extrema convierte la nucleación en un buen amplificador de perturbaciones microscópicas, pero también en un sistema especialmente vulnerable a confundidores. Una variación aparentemente dramática no implica necesariamente una causa exótica: puede proceder de una modificación muy pequeña de una superficie, de una impureza no registrada o de una diferencia de historial entre lotes.

La teoría clásica de nucleación proporciona una línea base útil, pero no constituye una descripción microscópica universal. Los núcleos pequeños no tienen por qué presentar todas las propiedades de la fase macroscópica. Pueden existir precursores estructurados, rutas de nucleación en varios pasos, agregados intermedios y mecanismos de selección de polimorfo que comienzan antes de la aparición de un núcleo claramente cristalino.

## 1.2 Polimorfismo y formas que dejan de reproducirse

Un mismo compuesto puede cristalizar en varias estructuras distintas. Cada polimorfo posee propiedades propias de estabilidad, solubilidad, densidad, morfología y cinética de formación. Una forma metaestable puede obtenerse repetidamente durante un periodo y dejar de aparecer cuando surge una forma más estable, cuando cambian las condiciones del proceso o cuando el entorno queda contaminado por semillas de otra estructura.

El fenómeno denominado «polimorfo desaparecido» describe una pérdida práctica de reproducibilidad. No significa que el estado haya sido eliminado del espacio de configuraciones permitidas. Entre las explicaciones ordinarias se encuentran la siembra deliberada o accidental, la nucleación heterogénea en superficies, la aparición de impurezas o solvatos, los cambios de proveedor, la modificación de las rutas de proceso, la existencia de precursores líquidos distintos y la transformación del cristal después de la nucleación inicial.

También deben considerarse causas metodológicas. Una forma rara puede parecer establemente reproducible cuando el número de ensayos es pequeño, y puede parecer «desaparecida» cuando se modifica el criterio de clasificación o cuando solo se publican los resultados positivos. El caso de ritonavir demuestra que un cambio de forma cristalina puede tener consecuencias industriales enormes, pero no demuestra que una semilla se haya propagado globalmente ni que las leyes físicas hayan cambiado.

## 1.3 Qué significa llamar aleatorio a un resultado

En esta suite, un proceso se denomina estocástico cuando sus resultados se describen mediante distribuciones de probabilidad condicionadas a las variables observadas. Esta definición es operacional. No afirma que el proceso carezca de causa ni que la aleatoriedad sea necesariamente fundamental.

La dispersión observada puede proceder de microestados clásicos no controlados, ruido térmico, ruido cuántico, dinámica caótica, variables omitidas o una combinación de todos ellos. También puede reflejar azar cuántico irreducible dentro del marco teórico utilizado. Estas posibilidades no se distinguen mediante intuiciones filosóficas, sino mediante predicciones estadísticas y experimentos que comparen modelos concretos.

Por ello, el repositorio evita identificar «impredecible» con «no causado». Un modelo puede ser incapaz de predecir cada ensayo individual y, aun así, describir correctamente las distribuciones, dependencias temporales y respuestas a perturbaciones del sistema.

## 1.4 Correlación, causa común y localidad

Dos laboratorios separados pueden producir resultados correlacionados sin que exista influencia instantánea entre ellos. Una red eléctrica compartida, un reloj común, una versión de firmware, un lote de material, una perturbación geomagnética, una variación atmosférica o una señal de radio pueden actuar como causas comunes.

Incluso una perturbación que no haya sido medida sigue siendo compatible con una explicación local si puede representarse mediante una variable `λ` situada en el pasado causal de ambos resultados:

\[
P(a,b|x,y)=\int d\lambda\,\rho(\lambda)P(a|x,\lambda)P(b|y,\lambda).
\]

Una correlación temporal, por intensa que sea, no constituye por sí sola una prueba de no localidad. Para realizar una prueba de Bell es necesario definir ajustes locales `x` e `y`, resultados `a` y `b`, una regla de ensayo válida, una eficiencia de detección suficiente y una separación espacio-temporal adecuada entre los eventos relevantes.

En el escenario CHSH, el parámetro se construye a partir de cuatro correlaciones:

\[
S=E_{00}+E_{01}+E_{10}-E_{11}.
\]

Los modelos locales satisfacen `|S| ≤ 2`, mientras que la mecánica cuántica puede alcanzar `2√2` en condiciones ideales. Sin embargo, una correlación simultánea entre dos secuencias, sin elecciones de base válidas y sin control de las lagunas experimentales, no es una prueba de Bell.

## 1.5 No señalización

La mecánica cuántica permite correlaciones que no pueden reproducirse mediante ciertos modelos locales, pero no permite utilizarlas como un canal controlable de comunicación superlumínica. En términos estadísticos, la distribución local de A no debe depender de la elección realizada en B:

\[
P(a|x,y)=P(a|x).
\]

La misma condición se aplica de forma simétrica al otro nodo. Esto significa que las correlaciones conjuntas pueden cambiar con los ajustes, mientras que los marginales locales permanecen invariantes.

Una dependencia reproducible de los marginales respecto a la elección remota sería más radical que una violación ordinaria de Bell. Antes de atribuirla a una modificación de la causalidad relativista habría que excluir errores de emparejamiento, ventanas de coincidencia, deriva temporal, pérdidas dependientes del ajuste, filtrado de datos y comunicación instrumental no registrada.

## 1.6 Medición y retroacción

Toda medición requiere una interacción física. En un sistema óptico, la sonda puede introducir pérdidas, calentamiento, fotones adicionales, selección de fase, presión de radiación, bloqueo por inyección o una modificación del tiempo de vida. Por tanto, la observación no se trata aquí como un acto abstracto, sino como una intervención experimental cuantificable.

Cada protocolo que emplee una sonda debe registrar su intensidad, duración, frecuencia, polarización, fase y momento de aplicación. También debe estimar la energía depositada o extraída, el calentamiento inducido, la modificación de las pérdidas y cualquier cambio en la tasa de transición o en la distribución de metaestados.

Los ensayos de retroacción compararán condiciones sin sonda, con sonda débil, con sonda intensa, con detector activado pero sin iluminación y con lectura realizada únicamente después de la transición. De este modo puede separarse el efecto de la medición del efecto del dispositivo de lectura.

## 1.7 Qué sería necesario para hablar de nueva física

Un valor aislado de `p < 0.05` no constituye evidencia suficiente para una afirmación extraordinaria. El resultado debe proceder de un análisis preregistrado, sobrevivir a controles ciegos, mantenerse al intercambiar hardware y replicarse en un laboratorio independiente.

Cuando el experimento implique Bell, será necesario demostrar que las elecciones y los resultados relevantes cumplen la separación temporal exigida, que la eficiencia de detección es adecuada y que el análisis es resistente a memoria, parada adaptativa y postselección. También deberá mostrarse que el efecto no depende de un lote, una versión de software, un reloj compartido o una regla de emparejamiento concreta.

La señal más convincente no sería una anomalía estadística aislada, sino una predicción cuantitativa nueva confirmada fuera de muestra. La suite está diseñada para producir primero una explicación detallada de las causas ordinarias. Encontrar que el supuesto fenómeno procede de contaminación, deriva o instrumentación no representa un fracaso: significa que el experimento ha cumplido su función científica.
