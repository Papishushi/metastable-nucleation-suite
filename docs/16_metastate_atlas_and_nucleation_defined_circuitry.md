# 16. Metastate Atlas y circuitería definida por nucleación

## 16.1 Estado de esta propuesta

Este documento formaliza una línea de investigación de largo plazo de la **Metastable Nucleation Suite (MNS)**. Distingue tres niveles:

1. **establecido:** existen estados metaestables, nucleación selectiva, memoria de cambio de fase y procesamiento fotónico;
2. **investigable:** pueden catalogarse metaestados de plataformas distintas y evaluarse como componentes reproducibles;
3. **especulativo:** distribuciones controladas de estados metaestables podrían programar circuitos físicos tridimensionales complejos.

Este documento define la arquitectura científica general. No presenta una tecnología de cómputo demostrada ni una predicción de producto. Toda afirmación cuantitativa debe conservar sus supuestos, nivel de evidencia, procedencia y margen de incertidumbre.

## 16.2 Dos programas coiguales de MNS

MNS estudia cómo los sistemas físicos acceden, seleccionan, conservan y abandonan estados metaestables. Mantiene dos programas con la misma relevancia:

1. **materia, nucleación y polimorfismo:** E01–E06;
2. **metaestados fotónicos y física fundamental:** E09–E15.

E07, E08 y E14 estudian redes, propagación y replicación entre plataformas. Los dos programas comparten metrología, estadística, contratos de datos, procedencia y visualización, pero no se confunden físicamente.

La nucleación material es una ruta dentro del espacio de investigación de MNS; no define por sí sola la suite. De la misma forma, los metaestados fotónicos o polaritónicos no quedan reducidos a mecanismos de lectura o ejecución de una memoria material.

## 16.3 E09 como laboratorio de alta resolución

E09 puede utilizar microcavidades excitón-polaritón para observar grandes poblaciones de formaciones y transiciones de metaestados bajo condiciones controladas. Los estados candidatos incluyen polarización, fase, intensidad, modo espacial, dominio y vorticidad.

Además de validar nodos ópticos independientes, E09 puede medir para cada familia:

- probabilidad de selección;
- tiempo de formación e instante de compromiso;
- tiempo de vida y tasa de escape;
- histéresis y memoria;
- cuencas de atracción;
- sensibilidad a semillas y perturbaciones;
- acoplamiento entre nodos;
- error de lectura y retroacción de medida.

Los condensados polaritónicos serían principalmente **componentes dinámicos**: proporcionan propagación, no linealidad, bifurcación y dinámica colectiva mientras existe bombeo. No sustituyen por sí solos una memoria no volátil.

## 16.4 Metastate Atlas

El **Metastate Atlas** será un catálogo transversal de estados metaestables. No afirmará que estados de microfísicas diferentes sean equivalentes; describirá propiedades dinámicas y funcionales comparables.

Cada entrada deberá registrar como mínimo:

- plataforma, composición, geometría y condiciones de operación;
- variable de orden y criterio de identificación;
- número de estados distinguibles con una tasa de error declarada;
- simetría, degeneración y dimensionalidad;
- cuencas, rutas y tasas de transición;
- retención, deriva, histéresis y endurance;
- procedimiento de escritura, borrado y lectura;
- energía, latencia y potencia de mantenimiento;
- capacidad de direccionamiento y cross-talk;
- posibles operaciones físicas;
- incertidumbre y procedencia hasta el artefacto original;
- nivel de evidencia: medido, inferido, simulado, escenario de ingeniería o límite especulativo.

Una gran cantidad de mínimos microscópicos no equivale automáticamente a una gran memoria. Un estado solo cuenta como símbolo informativo cuando puede prepararse, distinguirse y conservarse con un error especificado.

## 16.5 Taxonomía de conjuntos metaestables

### Estructurales y de cambio de fase

Fases amorfas, cristalinas, parcialmente cristalizadas, polimorfos y dominios estructurales. Son candidatos para memoria no volátil, pesos analógicos e índices ópticos programables.

### Ferroicos

Dominios ferroeléctricos, ferromagnéticos, ferroelásticos y multiferroicos. Pueden almacenar orientación, implementar histéresis y acoplar señales eléctricas, magnéticas y mecánicas.

### Magnéticos y espintrónicos

Paredes de dominio, skyrmiones y texturas de espín. Son candidatos para memoria móvil, lógica y dinámica colectiva.

### Iónicos y memristivos

Vacantes, migración iónica y filamentos conductores. Son útiles para pesos sinápticos y computación en memoria, con desafíos de variabilidad y deriva.

### Fotónicos pasivos

Defectos de cristales fotónicos, resonadores, guías y patrones de índice. Principalmente enrutan, filtran e interfieren señales.

### Excitón-polaritón

Condensados, fases, polarizaciones, vórtices y atractores impulsados y disipativos. Principalmente procesan y acoplan señales con escalas temporales rápidas.

### Mecánicos y elásticos

Estructuras biestables, modos atrapados y metamateriales. Pueden actuar como memoria, sensor o lógica física.

### Vítreos y frustrados

Vidrios estructurales, vidrios de espín y redes desordenadas poseen paisajes configuracionales enormes. Su valor informativo depende de poder aislar configuraciones locales reproducibles; el número total de mínimos no puede contarse como capacidad direccionable.

## 16.6 Nucleation-Defined Circuitry

Se define provisionalmente **Nucleation-Defined Circuitry** como una arquitectura en la que una distribución de fases o dominios metaestables, programada mediante nucleación selectiva, determina una o varias de estas funciones:

- memoria;
- peso o coeficiente;
- interconexión;
- filtrado;
- no linealidad;
- topología de una red física.

La nucleación actuaría como una litografía interna potencialmente tridimensional. Una arquitectura de referencia podría combinar:

1. una capa persistente de cambio de fase, ferroica, magnética o memristiva;
2. una capa fotónica para transporte y multiplexación;
3. una capa polaritónica para bifurcaciones y operaciones no lineales;
4. electrónica para escritura, lectura, calibración, secuenciación y corrección.

La formulación compacta es:

```text
materia persistente almacena la configuración
+ fotónica conecta y multiplexa
+ polaritones ejecutan dinámica no lineal
```

Esta arquitectura es una hipótesis de investigación. Debe competir contra una implementación convencional que materialice la misma función mediante píxeles, guías, memristores, fotónica programable o CMOS.

## 16.7 Representación física de tensores

Un tensor no proporciona capacidad exponencial gratuita. Sus componentes deben materializarse en grados de libertad distinguibles, por ejemplo:

\[
T(x,y,z,\lambda,p,m,t)
\]

con posición, longitud de onda, polarización, modo y tiempo. Los estados persistentes pueden almacenar coeficientes; la propagación y la interferencia pueden realizar contracciones o multiplicaciones.

Para un modelo grande, miles de millones de pesos siguen requiriendo miles de millones de grados de libertad físicos o una compresión matemática previa. Un bloque homogéneo con un único metaestado global no contiene una LLM completa.

## 16.8 Límites de alcance y separación de modelos

La arquitectura general de MNS debe mantenerse separada de dos modelos más concretos:

1. **modelo escalar metaestable:** trata celdas independientemente direccionables con \(K\) niveles fiables. Su capacidad, energía de reescritura y techos geométricos o térmicos se documentan y prueban por separado en #65 y PR #60;
2. **Nucleation-Encoded Chalcogenide Ensemble (NECE):** implementación material específica donde una configuración interna de núcleos, dominios o metaestados locales actúa como palabra de código. Su programa experimental se documenta en #50 y PR #61.

NECE no es sinónimo de MNS ni de Nucleation-Defined Circuitry. Una arquitectura nucleation-defined puede utilizar materiales ferroicos, magnéticos, iónicos, memristivos u otros sistemas, siempre que la configuración interna sea controlable, legible y funcional.

Del mismo modo, el modelo escalar no puede apropiarse de una entropía configuracional microscópica que no sea escribible y recuperable. La capacidad configuracional exige un protocolo de lectura, información mutua y error explícito.

## 16.9 Anclajes experimentales

La literatura proporciona anclajes parciales, no una demostración de la arquitectura completa:

- existen memorias eléctricas y fotónicas multinivel de cambio de fase;
- existen dispositivos de interfaz, dominios ferroicos, texturas magnéticas y elementos memristivos programables;
- existen circuitos fotónicos reconfigurables y sistemas polaritónicos no lineales;
- existen demostraciones de almacenamiento volumétrico en vidrio;
- existen aceleradores fotónicos que ejecutan operaciones tensoriales bajo arquitecturas externas de direccionamiento y control.

Estas líneas justifican investigar componentes, contratos de datos y experimentos comparativos. No justifican afirmar que ya pueda fabricarse una materia tridimensional autoenrutada comparable a un procesador moderno.

## 16.10 Hoja de ruta

### Fase A: catálogo

- definir el contrato `metastate-atlas.v1`;
- registrar estados, energía, error, retención y procedencia;
- producir entradas de referencia para E02, E04 y E09.

### Fase B: componente

- demostrar varios estados reproducibles dentro de una plataforma;
- medir escritura, lectura, borrado y deriva;
- comprobar que los estados aportan información o función recuperable.

### Fase C: acoplamiento

- conectar dos componentes;
- medir signo, intensidad, latencia y cross-talk;
- distinguir interacción causal de correlación ambiental.

### Fase D: operador pequeño

- programar una matriz, filtro, topología o función física pequeña;
- comparar precisión, energía y latencia con una referencia digital o fotónica convencional;
- contabilizar direccionamiento, calibración y lectura.

### Fase E: híbrido persistente-dinámico

- programar un paisaje mediante una capa no volátil;
- hacer que una capa fotónica, polaritónica o memristiva ejecute una transformación conocida;
- verificar estabilidad tras ciclos y apagados.

### Fase F: compilación material

- traducir una operación matemática a topología y receta física;
- verificar, recalibrar y reparar dominios o componentes;
- mantener un manifiesto completo del circuito físico resultante.

## 16.11 Criterio de éxito

La línea progresa solo si demuestra, de forma reproducible, al menos una ventaja que no pueda obtenerse con menor complejidad mediante una arquitectura convencional:

- mayor información recuperable por unidad direccionable;
- función física adicional por configuración;
- menor energía amortizada;
- menor latencia o mayor paralelismo útil;
- integración tridimensional o reconfiguración que compense su coste de control.

Un resultado negativo también es útil: permite reclasificar una plataforma como laboratorio de metastabilidad sin sostener una ventaja computacional inexistente.

## 16.12 Referencias de partida

- R. Landauer, *Irreversibility and Heat Generation in the Computing Process*, IBM Journal of Research and Development 5, 183–191 (1961).
- X. Li et al., *Non-volatile silicon photonic memory with more than 4-bit per cell capability*, arXiv:1904.12740.
- J. Meng et al., *Electrical Programmable Multi-Level Non-volatile Photonic Random-Access Memory*, arXiv:2203.13337.
- Y. Zhang et al., *Reconfigurable ultrafast perovskite polariton logic gates via nonlinear dynamics*, arXiv:2604.21445.
- S. Ning et al., *A Hardware-Efficient Photonic Tensor Core*, arXiv:2502.01670.
- A. Sun et al., *Fully multiplexed photonic tensor computing*, arXiv:2604.22660.

Las referencias específicas de capacidad escalar, fabricación de NECE y comparación tecnológica se mantienen en sus documentos y ramas correspondientes para evitar que este documento conceptual aparente validar una implementación concreta.