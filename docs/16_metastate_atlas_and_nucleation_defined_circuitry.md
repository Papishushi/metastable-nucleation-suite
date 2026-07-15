# 16. Metastate Atlas y circuitería definida por nucleación

## 16.1 Estado de esta propuesta

Este documento formaliza una línea de investigación de largo plazo de MNS. Distingue tres niveles:

1. **establecido:** estados metaestables, nucleación selectiva, memoria de cambio de fase y procesamiento fotónico existen;
2. **investigable:** catalogar metaestados de plataformas distintas y convertir algunos en componentes reproducibles;
3. **especulativo:** programar circuitos tridimensionales complejos mediante la distribución de estados metaestables.

Las cifras incluidas son cálculos paramétricos, no predicciones de producto. Todo escenario debe conservar sus
supuestos, nivel de evidencia, procedencia y margen de incertidumbre.

## 16.2 Tesis unificadora de MNS

MNS estudia cómo los sistemas físicos acceden, seleccionan, conservan y abandonan estados metaestables.
El programa mantiene dos pilares con la misma relevancia:

- **materia, nucleación y polimorfismo:** E01–E06;
- **metaestados fotónicos y física fundamental:** E09–E15.

E07, E08 y E14 estudian redes, propagación y replicación entre plataformas. Los dos pilares comparten
metrología, estadística, contratos de datos, procedencia y visualización, pero no se confunden físicamente.

## 16.3 E09 como laboratorio de alta resolución

E09 puede utilizar microcavidades excitón-polariton para observar millones de formaciones y transiciones de
metaestados bajo condiciones controladas. Los estados candidatos incluyen polarización, fase, intensidad,
modo espacial, dominio y vorticidad.

Además de validar nodos ópticos independientes, E09 puede medir para cada familia:

- probabilidad de selección;
- tiempo de formación e instante de compromiso;
- tiempo de vida y tasa de escape;
- histéresis y memoria;
- cuencas de atracción;
- sensibilidad a semillas y perturbaciones;
- acoplamiento entre nodos;
- error de lectura y retroacción de medida.

Los condensados polaritónicos serían principalmente **componentes dinámicos**: proporcionan propagación,
no linealidad, bifurcación y dinámica colectiva mientras existe bombeo. No sustituyen por sí solos una memoria
no volátil.

## 16.4 Metastate Atlas

El **Metastate Atlas** será un catálogo transversal de estados metaestables. No afirmará que estados de
microfísicas diferentes sean equivalentes; describirá propiedades dinámicas y funcionales comparables.

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
- incertidumbre y procedencia hasta el artefacto original.

Una gran cantidad de mínimos microscópicos no equivale automáticamente a una gran memoria. Un estado solo
cuenta como símbolo informativo cuando puede prepararse, distinguirse y conservarse con un error especificado.

## 16.5 Taxonomía de conjuntos metaestables

### Estructurales y de cambio de fase

Fases amorfas, cristalinas, parcialmente cristalizadas, polimorfos y dominios estructurales. Son candidatos
para memoria no volátil, pesos analógicos e índices ópticos programables.

### Ferroicos

Dominios ferroeléctricos, ferromagnéticos, ferroelásticos y multiferroicos. Pueden almacenar orientación,
implementar histéresis y acoplar señales eléctricas, magnéticas y mecánicas.

### Magnéticos y espintrónicos

Paredes de dominio, skyrmiones y texturas de espín. Son candidatos para memoria móvil, lógica y dinámica
colectiva.

### Iónicos y memristivos

Vacantes, migración iónica y filamentos conductores. Son útiles para pesos sinápticos y computación en memoria,
con desafíos de variabilidad y deriva.

### Fotónicos pasivos

Defectos de cristales fotónicos, resonadores, guías y patrones de índice. Principalmente enrutan, filtran e
interfieren señales.

### Excitón-polariton

Condensados, fases, polarizaciones, vórtices y atractores impulsados y disipativos. Principalmente procesan y
acoplan señales con escalas temporales rápidas.

### Mecánicos y elásticos

Estructuras biestables, modos atrapados y metamateriales. Pueden actuar como memoria, sensor o lógica física.

### Vítreos y frustrados

Vidrios estructurales, vidrios de espín y redes desordenadas poseen paisajes configuracionales enormes. Su
valor informativo depende de poder aislar configuraciones locales reproducibles; el número total de mínimos
no puede contarse como capacidad direccionable.

## 16.6 Nucleation-Defined Circuitry

Se define provisionalmente **Nucleation-Defined Circuitry** como una arquitectura en la que una distribución
de fases o dominios metaestables, programada mediante nucleación selectiva, determina una o varias de estas
funciones:

- memoria;
- peso o coeficiente;
- interconexión;
- filtrado;
- no linealidad;
- topología de una red física.

La nucleación actuaría como una litografía interna potencialmente tridimensional. Una arquitectura de
referencia tendría:

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

## 16.7 Representación física de tensores

Un tensor no proporciona capacidad exponencial gratuita. Sus componentes deben materializarse en grados de
libertad distinguibles, por ejemplo:

\[
T(x,y,z,\lambda,p,m,t)
\]

con posición, longitud de onda, polarización, modo y tiempo. Los estados persistentes pueden almacenar
coeficientes; la propagación y la interferencia pueden realizar contracciones o multiplicaciones.

Para un modelo grande, miles de millones de pesos siguen requiriendo miles de millones de celdas físicas o una
compresión matemática previa. Un bloque homogéneo con un único metaestado global no contiene una LLM completa.

## 16.8 Modelo cuantitativo

El modelo reproducible está implementado en `src/metastable_suite/metastate_capacity.py` y expuesto mediante
`scripts/metastate_capacity.py`.

### Capacidad por celda

Si una celda tiene \(K\) estados fiables:

\[
b_{cell}=\log_2 K.
\]

Para un pitch cúbico \(a\), fracción activa \(f\) y eficiencia de codificación \(\eta\):

\[
N_{cell,V}=\frac{f}{a^3},
\qquad
B_V=\frac{f\,\eta\,\log_2 K}{a^3}.
\]

Para una densidad material \(\rho\):

\[
B_M=\frac{B_V}{\rho}.
\]

`coding_efficiency` reúne ECC, guardas, calibración, celdas defectuosas y margen entre niveles. La masa de
encapsulado, guías, electrodos y refrigeración debe contabilizarse aparte.

### Energía de escritura

Si cada celda consume \(E_w\) durante su programación:

\[
E_{rewrite,M}=\frac{f}{a^3\rho}E_w.
\]

Es la energía activa para reescribir una vez todas las celdas, no la energía completa de la máquina.

### Límite de Landauer

A temperatura \(T\), borrar irreversiblemente un bit tiene el límite:

\[
E_L=k_B T\ln 2.
\]

A 300 K resulta aproximadamente \(2.87\times10^{-21}\) J por bit. Este valor no incluye barreras de retención,
calentamiento, direccionamiento, láseres ni pérdidas y no debe confundirse con una energía de dispositivo.

### Densidad de cálculo

Si cada celda participa a frecuencia \(r\), con utilización \(u\), \(o\) operaciones por evento y factor de
multiplexación \(m\):

\[
R_{geom,M}=\frac{f}{a^3\rho}r u o m.
\]

Es un techo geométrico. Si cada evento consume \(E_{op}\), la eficiencia activa es:

\[
\epsilon_{op}=\frac{o m}{E_{op}}.
\]

Con un presupuesto térmico específico \(P_M\), el techo energético es:

\[
R_{thermal,M}=P_M\epsilon_{op}.
\]

La estimación utilizable es el mínimo entre límites geométricos, térmicos, ópticos, de lectura, de comunicación
y de precisión.

## 16.9 Escenarios de sensibilidad

Los siguientes resultados son por kilogramo del medio modelado, no del dispositivo completo. Se utiliza un
presupuesto ilustrativo de 1 kW/kg para el límite de cálculo. Los escenarios no medidos se eligieron para
mostrar sensibilidad a pitch, estados y energía.

| Escenario | Nivel | Densidad útil | Reescritura activa | Cálculo a 1 kW/kg |
|---|---|---:|---:|---:|
| Vidrio de sílice escrito por láser, equivalente | medido | 917 TB/kg | no estimada | no aplicable |
| PCM 3D, 100 nm, 16 estados | ingeniería | 14.3 PB/kg | 4.10 MJ/kg, 1.14 kWh/kg | 2.0e17 op/s/kg |
| PCM 3D, 20 nm, 16 estados | ingeniería agresiva | 1.28 EB/kg | 5.12 MJ/kg, 1.42 kWh/kg | 1.6e19 op/s/kg |
| PCM, 5 nm, 64 estados | límite especulativo | 24.6 EB/kg | 3.93 MJ/kg, 1.09 kWh/kg | 3.2e20 op/s/kg |
| Vidrio amorfo local, 10 nm, 8 estados | límite especulativo | 9.0 EB/kg | 800 MJ/kg, 222 kWh/kg | 2.0e18 op/s/kg |

El valor de vidrio medido procede de convertir 4.84 TB almacenados en una placa de 12 cm² y 2 mm de espesor,
con densidad aproximada de 2200 kg/m³. Equivale a unos \(1.61\times10^{19}\) bits/m³ o a un pitch cúbico de
aproximadamente 396 nm si cada voxel efectivo representara un bit.

Los escenarios nanométricos producen cifras enormes porque dividen por la masa del material activo. En un
sistema real deben caer al añadir:

- aislamiento y separación térmica;
- selectores, electrodos y guías;
- fuentes, detectores y convertidores;
- ECC y niveles de referencia;
- ancho de banda de entrada y salida;
- refrigeración;
- baja utilización instantánea para evitar calentamiento acumulativo.

Por ejemplo, el techo geométrico del escenario PCM de 100 nm requeriría cientos de megavatios por kilogramo
con los parámetros ilustrativos; su cifra térmica de 1 kW/kg es aproximadamente seis órdenes de magnitud
menor. El cálculo no desaparece: cambia de estar limitado por celdas a estar limitado por energía y evacuación
de calor.

## 16.10 Anclajes experimentales

La literatura proporciona anclajes, no una demostración de la arquitectura completa:

- memorias fotónicas de cambio de fase con más de cuatro bits por celda han sido demostradas;
- dispositivos GSSe de cuatro bits han mostrado operación no volátil y medio millón de ciclos;
- un trabajo de 2026 informa más de siete bits de precisión óptica en una celda Sb2Te;
- PCM sub-10 nm ha alcanzado energías del orden de decenas de femtojulios por bit en resultados de frontera,
  mientras los parásitos térmicos y eléctricos siguen dominando;
- un dispositivo polaritónico de perovskita publicado como preprint en 2026 informa puertas reconfigurables
  con respuesta de 6.7 ps;
- núcleos tensoriales fotónicos recientes informan decenas de TOPS a escala de núcleo, muy lejos todavía de
  una materia tridimensional autoenrutada.

Estas observaciones justifican investigar componentes. No justifican afirmar que ya pueda fabricarse un
circuito tridimensional comparable a un procesador moderno.

## 16.11 Hoja de ruta

### Fase A: catálogo

- definir el contrato `metastate-atlas.v1`;
- registrar estados, energía, error, retención y procedencia;
- producir entradas de referencia para E02, E04 y E09.

### Fase B: celda

- demostrar varios estados reproducibles;
- medir escritura, lectura, borrado y deriva;
- comprobar que los niveles aportan información mutua utilizable.

### Fase C: acoplamiento

- conectar dos celdas;
- medir signo, intensidad, latencia y cross-talk;
- distinguir interacción causal de correlación ambiental.

### Fase D: matriz

- almacenar una matriz pequeña;
- realizar un producto matriz-vector;
- comparar precisión, energía y latencia con una referencia digital.

### Fase E: híbrido persistente-polaritónico

- programar un paisaje mediante una capa no volátil;
- hacer que una red polaritónica ejecute una transformación conocida;
- verificar estabilidad tras ciclos y apagados.

### Fase F: compilación material

- traducir una operación matemática a topología y receta de nucleación;
- verificar, recalibrar y reparar dominios;
- mantener un manifiesto completo del circuito físico resultante.

## 16.12 Referencias de partida

- R. Landauer, *Irreversibility and Heat Generation in the Computing Process*, IBM J. Res. Dev. 5, 183–191 (1961).
- K. Stern et al., *Uncovering Phase Change Memory Energy Limits by Sub-Nanosecond Probing of Power Dissipation Dynamics*, arXiv:2104.11545.
- R.-G. Nir-Harwood et al., *Energy and Scaling Limits of Phase-Change Memory*, arXiv:2605.28336.
- X. Li et al., *Non-volatile silicon photonic memory with more than 4-bit per cell capability*, arXiv:1904.12740.
- J. Meng et al., *Electrical Programmable Multi-Level Non-volatile Photonic Random-Access Memory*, arXiv:2203.13337.
- H. Zhang et al., *Optimization of all-optical phase-change waveguide devices for photonic computing from the atomic scale*, arXiv:2603.18468.
- Y. Zhang et al., *Reconfigurable ultrafast perovskite polariton logic gates via nonlinear dynamics*, arXiv:2604.21445.
- S. Ning et al., *A Hardware-Efficient Photonic Tensor Core*, arXiv:2502.01670.
- A. Sun et al., *Fully multiplexed photonic tensor computing*, arXiv:2604.22660.
- F. Chen and B. Wu, *Laser-written glass tablets can preserve data for millennia*, Nature (2026), DOI: 10.1038/d41586-026-00286-5.
