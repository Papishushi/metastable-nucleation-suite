# 19. Posicionamiento del Nucleation-Encoded Chalcogenide Ensemble (NECE), alternativas y criterios go/no-go

## 19.1 Relación con MNS

La **Metastable Nucleation Suite (MNS)** es un marco científico general con dos programas coiguales: materia/nucleación/polimorfismo y metaestados fotónicos/física fundamental.

El **Nucleation-Encoded Chalcogenide Ensemble (NECE)** es una hipótesis material específica dentro del primer programa y una posible interfaz con el segundo. Este documento evalúa únicamente esa rama. Sus conclusiones no deben extrapolarse a todo MNS, al Metastate Atlas ni a cualquier forma de circuitería definida por nucleación.

## 19.2 Conclusión ejecutiva

**NECE es una buena hipótesis de investigación, pero todavía no es una tecnología superior demostrada.**

No debe justificarse afirmando que será la memoria más densa, el tensor core más rápido o el dispositivo de menor energía. Para cada una de esas métricas existen plataformas más maduras:

- NAND y almacenamiento óptico para capacidad;
- phase-change memory (PCM) escalar, ReRAM y ECRAM para memoria analógica y cálculo en memoria;
- fotónica programable y metasuperficies para transformaciones de ondas;
- espintrónica para estados no volátiles y dinámica de baja energía;
- CMOS para control general, precisión y fabricación.

La oportunidad específica de NECE es distinta:

> Una misma microconfiguración material podría almacenar información, definir topología, modificar propagación, codificar un operador y condicionar la dinámica posterior.

La propuesta solo será valiosa si esa **densidad funcional** supera el coste adicional de escribir, observar, calibrar y corregir configuraciones de núcleos y dominios.

## 19.3 Qué ya hacen mejor otras plataformas

| Plataforma | Ventaja principal | Estado relativo | Limitación frente a la visión NECE |
|---|---|---|---|
| NAND/SSD | almacenamiento direccionable, coste y madurez | comercial | el dato no define normalmente la estructura de cálculo |
| PCM escalar | no volatilidad, niveles analógicos, integración BEOL | chips experimentales avanzados | colapsa la microestructura a resistencia o transmisión agregada |
| ReRAM/memristores | crossbars compactos y producto matriz-vector | prototipos integrados | variabilidad, ADC/DAC y estados principalmente escalares |
| ECRAM | actualizaciones analógicas relativamente simétricas | investigación avanzada | menor densidad por celda de tres terminales y retos de integración |
| fotónica programable | propagación rápida y transformaciones lineales | demostraciones integradas | pesos y topología suelen depender de actuadores discretos o control externo |
| metasuperficies PCM | función óptica no volátil y reconfigurable | demostraciones de laboratorio | patrones normalmente programados como píxeles o resonadores prediseñados |
| espintrónica | no volatilidad, dinámica y potencial de baja energía | investigación avanzada | direccionamiento, lectura y escalado de texturas complejas |
| NECE | configuración como dato, topología y función | hipótesis específica dentro de MNS | máxima complejidad de escritura, lectura y validación |

NECE no sustituye automáticamente a estas tecnologías. La arquitectura más defendible es híbrida.

## 19.4 Competidor conceptual más próximo

La alternativa más próxima no es una memoria PCM convencional, sino la combinación de:

1. **fotónica de propagación libre programable**, donde una distribución espacial continua del índice realiza el cálculo sin dividir el chip en componentes tradicionales;
2. **mallas fotónicas no volátiles con PCM**, donde materiales calcogenuros programan acoplamientos y fases;
3. **metasuperficies reescribibles**, donde un patrón material realiza una función óptica completa;
4. **analog in-memory computing**, donde pesos persistentes participan directamente en multiplicaciones.

Onodera et al. demostraron un sustrato fotónico bidimensional con aproximadamente `10^4` grados de libertad programables y clasificación en una sola propagación. Chen et al. propusieron NEO-PGA, una malla fotónica no volátil basada en Sb2Se3 con programación cerrada `program-and-verify`. Zarei propuso una red difractiva reescribible con metasuperficies de cambio de fase.

Estos trabajos muestran que la idea general «el material programado es el circuito óptico» ya existe en formas importantes.

La afirmación diferencial de NECE debe ser más precisa:

> No solo programar valores locales de índice o conductancia, sino explotar configuraciones reproducibles de nucleación, dominios, relaciones y topología como grados de libertad informativos y funcionales.

Esta diferencia debe demostrarse experimentalmente; no puede establecerse solo por terminología.

## 19.5 Por qué NECE todavía puede merecer la pena

### Densidad funcional

Un voxel NECE puede contener más información recuperable que una celda escalar del mismo pitch si varias configuraciones internas pueden escribirse y distinguirse. Además, esos mismos grados de libertad podrían modificar el operador físico ejecutado sobre una señal.

### Fabricación volumétrica

La nucleación selectiva podría, en principio, programar estructuras internas tridimensionales sin fabricar cada interconexión mediante litografía planar. Esta es una ventaja potencial, no demostrada.

### Cómputo estructural

Una configuración podría representar simultáneamente:

- parámetros;
- conectividad;
- restricciones;
- respuesta espectral;
- transformación de ondas;
- memoria del historial.

### Compatibilidad con la infraestructura de MNS

MNS ya contiene herramientas para estudiar selección, contaminación, memoria, backaction, procedencia y replicación. La rama NECE reutiliza esas herramientas para medir una plataforma programable concreta; no redefine el alcance general de la suite.

## 19.6 Por qué NECE puede fracasar

NECE dejaría de ser competitiva si ocurre cualquiera de estas situaciones:

- la lectura espacial cuesta más área, energía o tiempo que almacenar los bits externamente;
- la mayoría de microconfiguraciones colapsa al mismo observable funcional;
- las configuraciones no pueden escribirse de forma repetible;
- la longitud de correlación hace que los supuestos sitios locales no sean independientes;
- los núcleos crecen, coalescen o derivan durante la retención;
- el control necesario equivale a fabricar un selector convencional por cada sitio;
- una metasuperficie PCM pixelada o una malla fotónica ofrece la misma función con menor complejidad;
- ADC, DAC, láseres, tomografía y corrección dominan la energía y la masa;
- la función óptica solo puede calibrarse para una muestra concreta y no puede transferirse o recompilarse.

En esos casos, NECE sería científicamente interesante como estudio de materia metaestable, pero no una buena plataforma de computación.

## 19.7 Comparación por objetivo

### Almacenamiento puro

La mejor opción probable seguirá siendo una memoria escalar altamente optimizada. NECE solo gana si puede recuperar bastantes bits configuracionales adicionales sin que la lectura requiera instrumentación desproporcionada.

**Conclusión:** NECE no debe venderse primero como sustituto de SSD o NAND.

### Producto matriz-vector

PCM, ReRAM y fotónica programable ya realizan esta operación de forma directa. Un chip PCM integrado de 64 núcleos ha demostrado `63.1 TOPS` máximos y `9.76 TOPS/W` para multiplicaciones con entrada/salida de ocho bits. Un tensor core fotónico integrado de niobato de litio ha demostrado `120 GOPS` y actualización de pesos a `60 GHz`.

**Conclusión:** para un tensor core convencional, NECE parte por detrás hasta demostrar una operación que use su configuración interna y no solo un valor escalar por voxel.

### Circuito físico reconfigurable

Aquí NECE tiene su mejor oportunidad. Si una receta de nucleación puede crear un paisaje tridimensional que implemente simultáneamente memoria, acoplamientos y transformación de señales, la comparación deja de ser «bits por celda» y pasa a ser «función útil por volumen, masa y julio».

**Conclusión:** la métrica central debe ser densidad funcional.

### Computación dinámica y no lineal

Los polaritones, espines, osciladores y dispositivos memristivos son candidatos más naturales para dinámica rápida. NECE puede programar el paisaje persistente sobre el que esos sistemas operan.

**Conclusión:** el papel inicial de NECE debe ser configuración persistente, no reemplazo universal de la capa dinámica.

## 19.8 Métricas correctas

### Información recuperable

\[
I(W;R)
\]

Información mutua entre la palabra intentada y la palabra leída.

### Ganancia configuracional

\[
G_{config}
=
\frac{I(W;R)}{\log_2 K_{aggregate}}
\]

Compara la información configuracional recuperada con la capacidad de una celda agregada de `K` niveles.

### Densidad funcional

\[
D_F
=
\frac{I(W;R)\,C_{verified}}{V}
\]

`C_verified` representa una medida declarada de complejidad funcional verificada, por ejemplo número de coeficientes independientes, rango del operador o dimensión de transformación. No debe elegirse después de ver los resultados.

### Energía amortizada

\[
E_{amortized/op}
=
E_{read/op}
+
\frac{E_{program}+E_{verify}+E_{calibration}}{N_{reuse}}
\]

Una estructura persistente puede ser valiosa aunque sea cara de escribir si se reutiliza muchas veces.

### Masa y volumen de sistema

Las cifras deben incluir dos resultados separados:

- medio activo;
- sistema completo con direccionamiento, óptica, electrónica y refrigeración.

## 19.9 Envolvente cuantitativa provisional

Los siguientes intervalos son **objetivos exploratorios de la rama NECE**, no resultados publicados, objetivos generales de MNS ni predicciones:

| Métrica | Primer prototipo | Horizonte avanzado |
|---|---:|---:|
| capacidad de medio activo | 10–500 PB/kg | 0.1–10 EB/kg |
| capacidad de sistema completo | no prioritaria | 10–500 PB/kg |
| energía de transición funcional | 1–100 pJ | 10 fJ–1 pJ |
| cálculo especializado de sistema | demostración funcional | `10^15–10^17 op/s/kg` |
| bits configuracionales extra por voxel | >1 | decenas o centenas |

La cota atómica no es una especificación útil. El límite real vendrá dado por la longitud de correlación, el número de configuraciones accesibles, la resolución de lectura y el presupuesto térmico.

## 19.10 Experimento mínimo decisivo

El primer experimento NECE no debe intentar maximizar densidad. Debe demostrar que la microconfiguración posee información y función no reducibles a un nivel PCM convencional.

### Diseño

1. fabricar una unidad calcogenura con al menos dos configuraciones `A` y `B`;
2. igualar aproximadamente su fracción cristalina y su resistencia o transmisión media;
3. demostrar que `A` y `B` son espacial o espectralmente distinguibles;
4. escribir cada configuración repetidamente desde una condición inicial común;
5. medir matriz de confusión, retención, deriva y energía;
6. hacer que `A` y `B` produzcan dos transformaciones ópticas o acoplamientos diferentes;
7. verificar el resultado fuera de muestra y con lectura ciega.

La condición mínima es:

\[
R_A\approx R_B,
\qquad
\mathcal S_A\neq\mathcal S_B,
\qquad
F_A\neq F_B.
\]

`R` es el observable PCM agregado, `S` la configuración y `F` la función física verificada.

### Criterio go

Continuar hacia matrices si se demuestra:

- al menos un bit configuracional adicional recuperable por unidad;
- error de clasificación preregistrado y estable;
- escritura repetible;
- retención compatible con la aplicación;
- función distinta que no pueda explicarse por el observable agregado;
- energía amortizada competitiva después de un número declarado de reutilizaciones.

### Criterio no-go tecnológico

Reclasificar NECE como plataforma científica, no computacional, si tras optimización:

- `I(W;R)` no supera de forma reproducible la capacidad del observable agregado;
- la función distinta desaparece al controlar tamaño, temperatura y fracción cristalina;
- escribir la configuración requiere direccionar cada sitio con hardware equivalente a una matriz convencional;
- una plataforma PCM pixelada produce el mismo operador con menor coste total.

## 19.11 Arquitectura recomendada

La vía más sólida no es un NECE aislado, sino:

```text
NECE o PCM morfológico persistente
        ↓ programa
paisaje fotónico / espectral / de acoplamientos
        ↓ ejecuta
fotónica integrada y dinámica polaritónica
        ↓ controla y corrige
electrónica digital
```

En esta arquitectura:

- NECE almacena configuración y topología de larga duración;
- la fotónica realiza operaciones lineales y multiplexadas;
- los polaritones u otros elementos proporcionan no linealidad y dinámica;
- CMOS gestiona calibración, secuenciación y corrección.

Es una arquitectura candidata de la rama NECE, no la arquitectura obligatoria de todo MNS.

## 19.12 Juicio científico

NECE es una idea suficientemente diferenciada para justificar una línea de investigación dentro de MNS, pero no suficientemente validada para presentarla como una arquitectura superior.

Su valor no está probado por las cifras combinatorias. Quedará probado únicamente si se demuestra:

> información configuracional recuperable + función física adicional + ventaja de sistema después de incluir escritura, lectura, calibración y control.

Hasta entonces, la formulación correcta es:

- **buena hipótesis científica:** sí;
- **programa experimental defendible:** sí;
- **mejor memoria que PCM/NAND:** no demostrado;
- **mejor tensor core que crossbars o fotónica:** no demostrado;
- **posible plataforma multifuncional nueva:** plausible y falsable.

## 19.13 Literatura primaria de comparación

- M. Le Gallo et al., *A 64-core mixed-signal in-memory compute chip based on phase-change memory for deep neural network inference*, Nature Electronics 6, 680–693 (2023); arXiv:2212.02872.
- T. Onodera et al., *Scaling on-chip photonic neural processors using arbitrarily programmable wave propagation*, arXiv:2402.17750.
- Z. Lin et al., *120 GOPS Photonic Tensor Core in Thin-film Lithium Niobate for Inference and in-situ Training*, Nature Communications 15 (2024); arXiv:2311.16896.
- R. Chen et al., *NEO-PGA: Nonvolatile electro-optically programmable gate array*, arXiv:2506.18592.
- S. Zarei, *On-chip rewritable phase-change metasurface for programmable diffractive deep neural networks*, arXiv:2411.05723.
- M. Onen et al., *Nanosecond protonic programmable resistors for analog deep learning*, Science 377, 539–543 (2022).
- J. Grollier et al., *Neuromorphic spintronics*, Nature Electronics 3, 360–370 (2020); arXiv:2007.06092.