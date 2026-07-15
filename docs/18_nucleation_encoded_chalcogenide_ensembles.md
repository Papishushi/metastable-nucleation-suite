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

### 18.1.1 Qué ha hecho realmente la PCM multinivel

La literatura de PCM describe la operación multinivel principalmente como la programación de estados intermedios
de resistencia o respuesta óptica. El controlador ajusta amplitud, duración y secuencia de pulsos hasta alcanzar
una ventana escalar. La microestructura que produce ese valor puede contener distintas fracciones amorfas y
cristalinas, tamaños de grano, conectividades, orientaciones y distribuciones de vacantes, pero normalmente no se
lee ni se utiliza como palabra independiente.

Por tanto, una igualdad como

\[
R_A\approx R_B
\]

no implica

\[
\mathcal S_A\approx\mathcal S_B.
\]

Dos configuraciones con pocos dominios grandes o muchos dominios pequeños pueden ser equivalentes para una celda
escalar y, sin embargo, ser distintas para una arquitectura que lea difracción, fase, espectro, conectividad o
respuesta modal.

Skelton et al. observaron un estado intermedio de GST formado por cristalitos microscópicos dentro de una matriz
amorfa, pero solo dentro de una ventana estrecha de voltaje y con dificultades fundamentales para obtener múltiples
niveles intermedios fiables. Ese resultado es un precedente directo de la microestructura relevante, pero su símbolo
seguía siendo el nivel de resistencia, no la configuración de cristalitos.

### 18.1.2 Precedentes parciales de selección estructural

No es correcto afirmar que nadie haya intentado controlar rutas, fases o patrones internos. Existen precedentes
importantes:

- la ingeniería de sustrato, interfaz y encapsulación puede favorecer sitios de nucleación, orientar granos y
  promover o impedir el ordenamiento de vacantes en GST;
- se han distinguido estados de rocksalt desordenado, rocksalt con vacantes ordenadas y fase trigonal con contrastes
  de resistividad;
- la microscopía *in situ* ha seguido la evolución del ordenamiento de vacantes y su impacto electrónico y óptico;
- la fotónica de cambio de fase ha avanzado desde la conmutación global hacia la escritura láser localizada de
  patrones de Sb2Se3 optimizados inversamente;
- en otros calcogenuros, como 1T-TaS2, secuencias coherentes de pulsos han modulado la eficiencia de acceso a una
  fase metaestable oculta.

Estos trabajos demuestran control de fase, ruta, interfaz o patrón. No demuestran todavía un NECE completo porque
no establecen como palabra lógica una familia de configuraciones internas isoagregadas, escritas repetidamente,
leídas con resolución configuracional y validadas mediante una matriz de confusión.

La frontera debe expresarse así:

```text
PCM multinivel:             programar un valor agregado
PCM estructural avanzada:   favorecer una fase, orden o patrón espacial
NECE:                       direccionar una configuración interna como palabra
```

### 18.1.3 Por qué el campo no convergió antes en NECE

La dirección industrial fue racional. Para fabricar memoria densa bastaba con separar ventanas de resistencia;
resolver la microestructura habría añadido instrumentación, área, energía y latencia sin mejorar necesariamente el
producto. La nucleación estocástica se trató como variabilidad que debía compensarse mediante `program-and-verify`,
no como un alfabeto configuracional.

Un NECE exige resolver simultáneamente:

1. **identificación:** definir descriptores que separen configuraciones más allá de la fracción cristalina;
2. **observabilidad:** leer posición, tamaño, orientación, conectividad u orden sin destruir el estado;
3. **controlabilidad:** dirigir muchos grados de libertad internos con pocos actuadores físicos;
4. **retención:** seleccionar una cuenca dinámica, no solo una imagen transitoria;
5. **codificación:** demostrar información recuperable después de deriva, ruido y corrección;
6. **función:** probar que la configuración aporta una respuesta que el observable escalar no contiene.

En consecuencia, la novedad defendible de NECE no es «usar nucleación» ni «tener varios estados». Es cerrar el
bucle inverso:

```text
metaestado objetivo
        ↓
atlas de configuraciones y trayectorias
        ↓
receta espacial y temporal
        ↓
nucleación y crecimiento
        ↓
lectura configuracional
        ↓
verificación y corrección
```

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

## 18.10 Referencias primarias y revisiones de apoyo

### PCM escalar y multinivel

- G. W. Burr et al., *Phase change memory technology*, Journal of Vacuum Science & Technology B 28,
  223–262 (2010), DOI: `10.1116/1.3301579`; arXiv:1001.1164.
- G. W. Burr et al., *Recent Progress in Phase-Change Memory Technology*, IEEE Journal on Emerging and Selected
  Topics in Circuits and Systems 6, 146–162 (2016), DOI: `10.1109/JETCAS.2016.2547718`.
- M. Le Gallo and A. Sebastian, *An overview of phase-change memory device physics*, Journal of Physics D:
  Applied Physics 53, 213002 (2020), DOI: `10.1088/1361-6463/ab7794`.
- J. M. Skelton, D. Loke, T. H. Lee and S. R. Elliott, *Understanding the multistate SET process in
  Ge-Sb-Te-based phase-change memory*, Journal of Applied Physics 112, 064901 (2012),
  DOI: `10.1063/1.4748961`.

### Control de estructura, rutas y patrones

- A. M. Mio et al., *Role of interfaces on the stability and electrical properties of Ge2Sb2Te5 crystalline
  structures*, Scientific Reports 7, 2616 (2017), DOI: `10.1038/s41598-017-02710-3`.
- T.-T. Jiang et al., *In situ characterization of vacancy ordering in Ge-Sb-Te phase-change memory alloys*,
  arXiv:2203.09310 (2022). Debe verificarse la referencia editorial final antes de citar una versión publicada.
- C. Wu et al., *Reconfigurable inverse designed phase-change photonics*, arXiv:2403.05649 (2024); publicado como
  artículo de APL Photonics en 2025. La escritura es espacial y pixelada, no una lectura de configuraciones
  microscópicas isoagregadas.
- J. Maklar et al., *Coherent Light Control of a Metastable Hidden Phase*, arXiv:2206.03788 (2022). Es un precedente
  de control de trayectoria en 1T-TaS2, no una demostración de PCM multinivel ni de NECE.

Las referencias deben clasificarse por la afirmación que soportan. Ningún trabajo de esta lista demuestra por sí
solo escritura repetible, lectura configuracional e información adicional de configuraciones isoagregadas; esa es
precisamente la prueba diferencial propuesta para NECE.
