# 18. Conjuntos calcogenuros codificados por nucleación

## 18.1 Distinción respecto a PCM multinivel convencional

Los materiales de cambio de fase convencionales sí utilizan nucleación y crecimiento cristalino como parte de
su mecanismo físico. Sin embargo, una celda PCM multinivel suele leerse como un único observable agregado:
resistencia, conductancia, transmisión o fase óptica. Diferentes microestructuras amorfo-cristalinas pueden
producir el mismo nivel macroscópico y, por tanto, se tratan como el mismo símbolo lógico.

En esa arquitectura:

```text
microconfiguración de núcleos y dominios
                 ↓
      resistencia/transmisión agregada
                 ↓
          uno entre K niveles
```

La capacidad funcional de la celda es aproximadamente `log2(K)` bits, aunque el material contenga muchas más
configuraciones microscópicas.

La propuesta de MNS es diferente:

> la identidad, distribución, relación y topología de los núcleos o dominios metaestables forman el código.

En esa arquitectura:

```text
configuración espacial y relacional de metaestados
                 ↓
      lectura configuracional resuelta
                 ↓
             palabra física
```

No basta con producir una fracción media de cristalización. Debe ser posible preparar y distinguir patrones
configuracionales específicos con incertidumbre y procedencia declaradas.

## 18.2 Terminología propuesta

Para evitar confundir ambos conceptos, MNS utilizará:

- **scalar multilevel PCM:** celda convencional cuyo símbolo es un nivel agregado de resistencia o respuesta óptica;
- **nucleation-encoded chalcogenide ensemble, NECE:** conjunto direccionable cuyo símbolo es una configuración
  reproducible de núcleos, dominios o metaestados locales;
- **nucleation-defined circuitry:** arquitectura donde esos conjuntos determinan memoria, pesos, acoplamientos
  u operaciones.

NECE es una hipótesis tecnológica de largo plazo, no una denominación de una tecnología ya demostrada.

## 18.3 Modelo informativo

Considérese una unidad direccionable que contiene `N` sitios metaestables. Cada sitio admite `q` estados locales.
El máximo combinatorio ideal es:

\[
\Omega=q^N,
\qquad
B_{ideal}=\log_2\Omega=N\log_2q.
\]

Ese valor no es automáticamente utilizable. Las correlaciones, la degeneración, la imposibilidad de escribir
ciertos patrones y la resolución limitada reducen la capacidad. MNS introduce tres eficiencias:

- `configurational_entropy_efficiency`: fracción de la entropía combinatoria que corresponde a configuraciones
  físicamente accesibles e independientes;
- `readout_efficiency`: fracción que puede recuperarse mediante la instrumentación;
- `coding_efficiency`: pérdidas por ECC, guardas, calibración y celdas defectuosas.

La capacidad recuperable de una unidad es:

\[
B_{recoverable}
=N\log_2q\;\eta_{config}\eta_{read}\eta_{code}.
\]

La métrica experimental definitiva no debe ser solo el número de patrones observados, sino la información mutua
entre la palabra que se intenta escribir y la palabra inferida durante la lectura:

\[
I(W;R).
\]

Un conjunto solo es memoria si una palabra escrita puede recuperarse con una tasa de error especificada.

## 18.4 Geometría de dos escalas

El modelo separa:

- `addressable_pitch`: distancia entre unidades que el sistema puede escribir y leer por separado;
- `metastable_site_pitch`: escala efectiva entre sitios locales dentro de cada unidad.

Una unidad de 100 nm puede contener un conjunto efectivo de sitios de 10 nm. Esto no implica que todos sean
átomos independientes ni que la instrumentación tenga resolución de 10 nm. Es una parametrización que deberá
sustituirse por mediciones de dominio, correlación y función de punto extendido.

Para fracción interna `f_site`:

\[
N=f_{site}\left(\frac{a_{unit}}{a_{site}}\right)^3.
\]

La existencia de una escala microscópica pequeña no mejora la capacidad si la lectura solo devuelve una media.

## 18.5 Energía

La energía de reescritura se calcula a partir del número medio de sitios que deben cambiar, no asignando a cada
palabra una transición global amorfo-cristalina:

\[
E_{word}=N f_{rewrite} E_{site}.
\]

Esto permite distinguir:

- cambiar un pequeño subconjunto de núcleos;
- reorganizar una topología completa;
- fundir y volver a solidificar toda la unidad.

La energía óptica o eléctrica de direccionamiento, lectura, refrigeración y corrección debe añadirse por separado.

## 18.6 Escenario de sensibilidad inicial

`src/metastable_suite/nucleation_encoded_capacity.py` define un escenario explícitamente especulativo:

- unidad direccionable: 100 nm;
- sitio metaestable efectivo: 10 nm;
- 500 sitios efectivos por unidad tras aplicar fracción volumétrica;
- cuatro estados locales ideales;
- solo 25 % de eficiencia entrópica configuracional;
- solo 25 % de eficiencia de lectura;
- 70 % de eficiencia de codificación.

La unidad tendría 1000 bits configuracionales ideales, pero únicamente 43,75 bits recuperables según los
descuentos declarados. El resultado ilustrativo es aproximadamente 224 PB/kg de medio activo, no 24,6 EB/kg.

La reducción es deliberada: la cifra de 24,6 EB/kg del modelo PCM sub-10 nm corresponde a celdas escalares de
5 nm con 64 niveles fiables, una extrapolación diferente. No representa todavía la idea NECE.

## 18.7 Requisitos experimentales

Para demostrar un NECE deben satisfacerse, como mínimo:

1. observar configuraciones locales distintas que no se reduzcan a un único grado medio de cristalización;
2. escribir selectivamente más de una configuración con el mismo valor agregado aproximado;
3. leer y distinguir esas configuraciones mediante imagen, espectro, dispersión, respuesta modal o tomografía;
4. demostrar retención y reproducibilidad;
5. medir la matriz de confusión escritura-lectura;
6. estimar `I(W;R)` fuera de muestra;
7. demostrar composición de varias unidades y medir cross-talk;
8. verificar que la capacidad no procede de metadatos externos ocultos.

## 18.8 Relación con E09

E09 puede aportar métodos de alta resolución para identificar metaestados, cuencas, rutas y acoplamientos. Una
microcavidad excitón-polariton no almacena necesariamente el patrón calcogenuro de forma permanente, pero puede:

- sondear ópticamente configuraciones locales;
- convertir patrones persistentes en paisajes de potencial;
- amplificar diferencias entre configuraciones;
- ejecutar dinámica no lineal sobre una topología programada;
- ayudar a definir qué rasgos configuracionales son funcionalmente distinguibles.

La arquitectura híbrida propuesta es:

```text
NECE persistente: almacena la palabra y la topología
fotónica integrada: direcciona y lee
red polaritónica: transforma y procesa
```

## 18.9 Posición científica

Los PCM actuales son un precedente material importante, pero no deben presentarse como demostración directa de
NECE. Comparten calcogenuros, nucleación, dominios y metaestabilidad; difieren en la semántica de la información.
En PCM multinivel convencional, la microconfiguración es principalmente un medio para obtener un nivel agregado.
En NECE, la microconfiguración es el objeto informativo y potencialmente el circuito.

La evaluación competitiva, los límites cuantitativos y los criterios de continuación están definidos en
`docs/19_nece_positioning_competitors_and_go_no_go.md`.
