# 1. Marco científico

## 1.1 Nucleación y metaestabilidad

Una fase metaestable es un mínimo local de energía libre separado de estados más estables por una barrera. En la descripción clásica simplificada, la tasa de nucleación puede escribirse como

\[
J = A\exp\left(-\frac{\Delta G^*}{k_B T}\right),
\]

con prefactor cinético `A` y barrera efectiva `ΔG*`. La dependencia exponencial hace que variaciones pequeñas de temperatura, interfaz, composición, campo o impurezas produzcan cambios enormes de tasa. Eso convierte la nucleación en un amplificador sensible, pero también en un detector plagado de confundidores.

La teoría clásica de nucleación es útil como línea base, no como explicación microscópica completa. Núcleos pequeños no tienen por qué poseer propiedades de fase macroscópica; pueden existir precursores estructurados, rutas en varios pasos y selección temprana de polimorfo.

## 1.2 Polimorfismo y “polimorfos desaparecidos”

Un compuesto puede adoptar varias redes cristalinas. Una forma metaestable puede obtenerse repetidamente hasta que una forma más estable o cinéticamente favorecida aparece y pasa a dominar. Entre las explicaciones ordinarias están:

- siembra deliberada o accidental;
- nucleación heterogénea en superficies;
- impurezas, solvatos o hidratos;
- cambios de proceso o proveedor;
- precursores líquidos distintos;
- transformación posterior del cristal ya nucleado;
- estadística insuficiente y sesgo de publicación.

“Desaparecido” describe una pérdida práctica de reproducibilidad, no la eliminación ontológica de un estado permitido. El caso de ritonavir demuestra impacto industrial real, pero no prueba contaminación planetaria ni un cambio de leyes físicas.

## 1.3 Azar: operacional frente a ontológico

En esta suite, “estocástico” significa que el resultado se modela mediante distribuciones condicionadas a las variables observadas. No implica por sí solo ausencia de causa. La aleatoriedad observada puede provenir de:

- microestados clásicos no controlados;
- ruido térmico o cuántico;
- dinámica caótica;
- variables omitidas;
- azar cuántico irreducible, según la teoría e interpretación empleadas.

La distinción se prueba mediante predicciones estadísticas, no mediante intuiciones sobre lo que “debería” ser azar.

## 1.4 Correlación local, causa común y no localidad

Dos laboratorios pueden correlacionarse por una causa común ordinaria: red eléctrica, reloj, firmware, lote, vibración, campo electromagnético, radiación, presión atmosférica o actividad solar. Incluso una perturbación no registrada sigue siendo local si puede representarse mediante una variable compartida `λ` en el pasado causal:

\[
P(a,b|x,y)=\int d\lambda\,\rho(\lambda)P(a|x,\lambda)P(b|y,\lambda).
\]

Una prueba de Bell exige configuraciones locales `x,y`, resultados `a,b`, alta eficiencia de detección y separación espacio-temporal de los eventos relevantes. En CHSH:

\[
S=E_{00}+E_{01}+E_{10}-E_{11}.
\]

Los modelos locales satisfacen `|S| ≤ 2`. La mecánica cuántica alcanza `2√2` para estados y bases ideales. Una correlación simultánea sin elecciones de base no es una prueba de Bell.

## 1.5 No señalización

La mecánica cuántica estándar permite correlaciones no locales, pero no controlarlas para transmitir información superlumínica. Debe cumplirse:

\[
P(a|x,y)=P(a|x)
\]

para toda elección remota `y`, y análogamente en el otro nodo. Una dependencia reproducible de los marginales locales respecto a la elección remota sería más radical que una violación de Bell y exigiría revisar causalidad relativista, o encontrar un fallo experimental monumental.

## 1.6 Medición y retroacción

Medir requiere interacción. En sistemas ópticos la sonda puede introducir pérdidas, calentamiento, selección de fase, bloqueo por inyección o efecto Zeno. Por eso la retroacción no se trata como misterio filosófico, sino como parámetro experimental:

- intensidad y duración de sonda;
- fotones extraídos;
- calentamiento estimado;
- modificación del tiempo de vida;
- cambio en tasa de transición;
- cambio en distribución de metaestados.

Los ensayos incluyen brazos sin sonda, sonda débil, lectura tardía y lectura destructiva.

## 1.7 Qué demostraría realmente nueva física

No basta con un valor `p < 0.05`. Harían falta, como mínimo:

1. efecto preregistrado;
2. replicación independiente;
3. controles ciegos y hardware intercambiado;
4. cierre de localidad y detección cuando corresponda;
5. análisis resistente a memoria y selección adaptativa;
6. independencia respecto a lote, software y reloj;
7. predicción cuantitativa nueva confirmada fuera de muestra.

La suite está diseñada para producir antes una lista convincente de explicaciones aburridas. Esa lista es un activo, no un fracaso.
