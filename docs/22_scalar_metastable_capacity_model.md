# 22. Modelo escalar de capacidad metaestable

## 22.1 Propósito

Este documento define un modelo paramétrico para medios tridimensionales formados por celdas metaestables **independientemente direccionables** con un número finito de niveles fiables.

El modelo estima:

- densidad de información por volumen total modelado;
- densidad de información por kilogramo de material activo;
- energía activa de reescritura con ambas bases;
- límite termodinámico de Landauer;
- techos geométricos de operaciones;
- techo energético bajo un presupuesto de potencia específico del material activo.

Es una herramienta de sensibilidad. No es un simulador de dispositivo, una estimación de sistema completo ni una predicción tecnológica.

## 22.2 Límite conceptual

Una celda escalar se representa mediante un único valor seleccionado entre \(K\) estados distinguibles. Puede corresponder a resistencia, conductancia, transmisión, fase óptica, polarización u otra observable agregada.

El modelo **no** cuenta como capacidad:

- mínimos microscópicos invisibles;
- configuraciones que no puedan escribirse de forma reproducible;
- diferencias estructurales que el protocolo de lectura no pueda recuperar;
- estados correlacionados tratados falsamente como celdas independientes;
- masa o prestaciones de sistema que no hayan sido modeladas explícitamente.

La capacidad de una **Nucleation-Encoded Chalcogenide Ensemble (NECE)**, donde la configuración interna constituye la palabra de código, se modela por separado en #50 y PR #61. El marco general de la **Metastable Nucleation Suite (MNS)**, el Metastate Atlas y la circuitería definida por nucleación se documenta en #63, #64 y PR #59.

## 22.3 Convenciones de base y valores desconocidos

El modelo utiliza dos denominadores distintos y los expone en cada nombre de salida:

- `per_total_m3`: un metro cúbico del medio modelado, incluida la fracción no activa;
- `per_active_kg`: un kilogramo del material activo únicamente.

No se calculan métricas `per_system_kg`. Para obtenerlas sería necesario declarar la masa de sustratos, aislamiento, electrodos, selectores, guías, fuentes, detectores, electrónica, control y refrigeración.

`active_volume_fraction` reduce las magnitudes por volumen total. No reduce las magnitudes por kilogramo activo, porque al disminuir el volumen activo disminuyen en la misma proporción tanto el número de celdas como la masa activa.

Una magnitud física no medida se representa mediante JSON `null`, nunca mediante cero. Por tanto:

- energía desconocida no significa operación gratuita;
- frecuencia desconocida no significa dispositivo detenido;
- un techo térmico no se calcula si falta la energía por evento;
- la salida se serializa como JSON estricto, sin `NaN` ni `Infinity`.

## 22.4 Implementación reproducible

El modelo está implementado en:

- `src/metastable_suite/metastate_capacity.py`;
- `scripts/metastate_capacity.py`;
- `tests/test_metastate_capacity.py`.

Sin argumentos personalizados, la CLI devuelve los escenarios de referencia:

```bash
python scripts/metastate_capacity.py
```

Para reproducir además el techo bajo `1000 W/kg` de material activo:

```bash
python scripts/metastate_capacity.py \
  --power-budget-w-per-active-kg 1000
```

Un escenario personalizado requiere densidad del material activo, pitch de celda y número de estados:

```bash
python scripts/metastate_capacity.py \
  --custom \
  --name example \
  --active-material-density-kg-m3 6100 \
  --cell-pitch-nm 100 \
  --states 16 \
  --active-volume-fraction 0.25 \
  --coding-efficiency 0.70 \
  --write-energy-j 1e-10 \
  --operation-energy-j 1e-14 \
  --event-rate-hz 1e9 \
  --active-utilization 1e-3 \
  --operations-per-event 2 \
  --power-budget-w-per-active-kg 1000
```

Cada escenario declara uno de estos niveles:

- `measured`;
- `engineering_scenario`;
- `speculative_bound`.

## 22.5 Capacidad por celda y por volumen total

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

Estas magnitudes utilizan volumen total modelado. `coding_efficiency` agrupa ECC, guardas, calibración, celdas defectuosas y margen entre niveles.

## 22.6 Capacidad por masa activa

Si la densidad del material activo es \(\rho\), la masa activa contenida en un metro cúbico total es:

\[
M_{active,V}=f\rho.
\]

Por tanto, el número de celdas por kilogramo activo es:

\[
N_{cell,M_a}
=
\frac{N_{cell,V}}{M_{active,V}}
=
\frac{1}{a^3\rho}.
\]

La densidad útil por kilogramo activo es:

\[
B_{M_a}
=
\frac{\eta\log_2 K}{a^3\rho}.
\]

La fracción activa \(f\) se cancela. Aplicarla de nuevo en esta ecuación mezclaría masa activa con masa de sistema y subestimaría artificialmente las magnitudes por kilogramo activo.

## 22.7 Energía de escritura

Si cada celda consume una energía conocida \(E_w\) durante su programación:

\[
E_{rewrite,V}=\frac{f}{a^3}E_w,
\qquad
E_{rewrite,M_a}=\frac{1}{a^3\rho}E_w.
\]

Estas magnitudes representan únicamente la energía activa para reescribir una vez las celdas modeladas. No incluyen distribución eléctrica u óptica, conversión, control, verificación, calibración ni refrigeración.

Cuando \(E_w\) no se ha declarado, ambas salidas de reescritura son `null`.

## 22.8 Límite de Landauer

A temperatura \(T\), borrar irreversiblemente un bit tiene el límite:

\[
E_L=k_B T\ln 2.
\]

A 300 K resulta aproximadamente \(2.87\times10^{-21}\) J por bit. Este valor no incluye barreras de retención, calentamiento, direccionamiento, láseres, pérdidas ni márgenes de error y no debe confundirse con una energía de dispositivo.

El modelo devuelve el límite por bit, por volumen total y por kilogramo activo. Son referencias termodinámicas, no objetivos de ingeniería inmediatos.

## 22.9 Densidad de cálculo

Si cada celda participa a frecuencia \(r\), con utilización \(u\), \(o\) operaciones por evento y factor de multiplexación \(m\):

\[
R_{geom,V}=\frac{f}{a^3}r u o m,
\qquad
R_{geom,M_a}=\frac{1}{a^3\rho}r u o m.
\]

Si cada evento consume una energía conocida \(E_{op}\), la eficiencia activa es:

\[
\epsilon_{op}=\frac{o m}{E_{op}}.
\]

Con un presupuesto específico de potencia activa \(P_{M_a}\), el techo energético es:

\[
R_{thermal,M_a}=P_{M_a}\epsilon_{op}.
\]

Si \(r\) o \(E_{op}\) no están declarados, las salidas dependientes permanecen `null`. La estimación utilizable debe ser el mínimo entre límites geométricos, térmicos, ópticos, eléctricos, de lectura, de comunicación y de precisión.

## 22.10 Escenarios de sensibilidad

Los escenarios incorporados muestran cómo cambian los resultados al variar pitch, estados, fracción activa, eficiencia de codificación y energía. Solo la conversión equivalente del vidrio escrito por láser está etiquetada como `measured`; el resto son escenarios o límites paramétricos cuyos valores no han sido demostrados conjuntamente.

Todas las cifras de masa de la tabla usan **kilogramos de material activo**, no kilogramos de sistema completo.

| Escenario | Nivel | Densidad útil activa | Reescritura activa | Techo con 1 kW/kg activo |
|---|---|---:|---:|---:|
| Vidrio de sílice escrito por láser, equivalente | medido | 917 TB/kg | desconocida | desconocido |
| PCM 3D, 100 nm, 16 estados | ingeniería | 57.4 PB/kg | 16.4 MJ/kg; 4.55 kWh/kg | 2.0e17 op/s/kg |
| PCM 3D, 20 nm, 16 estados | ingeniería agresiva | 5.12 EB/kg | 20.5 MJ/kg; 5.69 kWh/kg | 1.6e19 op/s/kg |
| PCM, 5 nm, 64 estados | límite especulativo | 246 EB/kg | 39.3 MJ/kg; 10.9 kWh/kg | 3.2e20 op/s/kg |
| Vidrio amorfo local, 10 nm, 8 estados | límite especulativo | 45.0 EB/kg | 4.00 GJ/kg; 1111 kWh/kg | 2.0e18 op/s/kg |

El valor equivalente del vidrio procede de convertir 4.84 TB almacenados en una placa de 12 cm² y 2 mm de espesor, con densidad aproximada de 2200 kg/m³. Equivale a unos \(1.61\times10^{19}\) bits/m³ o a un pitch cúbico efectivo de aproximadamente 396 nm si cada voxel representara un bit.

Esa conversión no demuestra una matriz de celdas nanométricas independientemente direccionables. Solo transforma una densidad archivística publicada a unidades comparables. La energía y el rendimiento permanecen desconocidos en el JSON del escenario, en vez de convertirse en cero o infinito.

## 22.11 Interpretación correcta

Las cifras nanométricas por kilogramo activo pueden resultar enormes porque excluyen toda masa auxiliar. En un sistema real deben reducirse al incluir:

- aislamiento y separación térmica;
- selectores, electrodos, heaters y guías;
- fuentes, moduladores, detectores y convertidores;
- ECC, referencias y capacidad de reserva;
- calibración y ciclos de verificación;
- ancho de banda de entrada y salida;
- refrigeración;
- utilización instantánea limitada para evitar calentamiento acumulativo.

Un techo geométrico puede exigir una potencia dinámica varios órdenes de magnitud superior al presupuesto térmico. En ese caso, añadir más celdas no aumenta el rendimiento útil: el sistema queda limitado por energía y evacuación de calor.

## 22.12 Reglas de uso

Un resultado solo puede presentarse como estimación de sistema cuando:

1. la masa total incluye soporte, direccionamiento, lectura, control y refrigeración;
2. las energías incluyen escritura, verificación, conversión y mantenimiento;
3. el ancho de banda permite acceder a la densidad calculada;
4. el número de estados está respaldado por una tasa de error y retención declaradas;
5. la utilización térmica es físicamente compatible con el encapsulado;
6. el nivel de evidencia queda visible junto al resultado.

El modelo actual no recibe suficientes entradas para satisfacer estas condiciones. Sus resultados son techos del medio activo o análisis de sensibilidad.

## 22.13 Referencias de partida

- R. Landauer, *Irreversibility and Heat Generation in the Computing Process*, IBM Journal of Research and Development 5, 183–191 (1961).
- K. Stern et al., *Uncovering Phase Change Memory Energy Limits by Sub-Nanosecond Probing of Power Dissipation Dynamics*, arXiv:2104.11545.
- R.-G. Nir-Harwood et al., *Energy and Scaling Limits of Phase-Change Memory*, arXiv:2605.28336.
- X. Li et al., *Non-volatile silicon photonic memory with more than 4-bit per cell capability*, arXiv:1904.12740.
- J. Meng et al., *Electrical Programmable Multi-Level Non-volatile Photonic Random-Access Memory*, arXiv:2203.13337.
- H. Zhang et al., *Optimization of all-optical phase-change waveguide devices for photonic computing from the atomic scale*, arXiv:2603.18468.
- F. Chen and B. Wu, *Laser-written glass tablets can preserve data for millennia*, Nature (2026), DOI: 10.1038/d41586-026-00286-5.

Las referencias soportan límites físicos o ejemplos parciales. Ninguna demuestra por sí sola todos los escenarios paramétricos incluidos en el modelo.
