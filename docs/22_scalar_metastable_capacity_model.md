# 22. Modelo escalar de capacidad metaestable

## 22.1 Propósito

Este documento define un modelo paramétrico para medios tridimensionales formados por celdas metaestables **independientemente direccionables** con un número finito de niveles fiables.

El modelo estima:

- densidad de información por volumen y por masa activa;
- energía activa de reescritura;
- límite termodinámico de Landauer;
- techo geométrico de operaciones;
- techo energético o térmico bajo un presupuesto de potencia.

Es una herramienta de sensibilidad, no un simulador de dispositivo ni una predicción tecnológica.

## 22.2 Límite conceptual

Una celda escalar se representa mediante un único valor seleccionado entre \(K\) estados distinguibles. Puede corresponder a resistencia, conductancia, transmisión, fase óptica, polarización u otra observable agregada.

El modelo **no** cuenta como capacidad:

- mínimos microscópicos invisibles;
- configuraciones que no puedan escribirse de forma reproducible;
- diferencias estructurales que el protocolo de lectura no pueda recuperar;
- estados correlacionados tratados falsamente como celdas independientes.

La capacidad de una **Nucleation-Encoded Chalcogenide Ensemble (NECE)**, donde la configuración interna constituye la palabra de código, se modela por separado en #50 y PR #61. El marco general de la Metastable Nucleation Suite (MNS), el Metastate Atlas y la circuitería definida por nucleación se documenta en #63, #64 y PR #59.

## 22.3 Implementación reproducible

El modelo está implementado en:

- `src/metastable_suite/metastate_capacity.py`;
- `scripts/metastate_capacity.py`;
- `tests/test_metastate_capacity.py`.

Sin argumentos personalizados, la CLI devuelve escenarios de referencia en JSON:

```bash
python scripts/metastate_capacity.py
```

Un escenario personalizado requiere densidad, pitch y número de estados:

```bash
python scripts/metastate_capacity.py \
  --custom \
  --name example \
  --density-kg-m3 6100 \
  --pitch-nm 100 \
  --states 16 \
  --active-volume-fraction 0.25 \
  --coding-efficiency 0.70 \
  --write-energy-j 1e-10 \
  --operation-energy-j 1e-14 \
  --event-rate-hz 1e9 \
  --active-utilization 1e-3 \
  --operations-per-event 2 \
  --power-budget-w-per-kg 1000
```

Cada escenario declara un nivel de evidencia:

- `measured`;
- `engineering_scenario`;
- `speculative_bound`.

## 22.4 Capacidad por celda

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

`coding_efficiency` agrupa ECC, guardas, calibración, celdas defectuosas y margen entre niveles. La masa de encapsulado, guías, electrodos, selectores, fuentes, detectores y refrigeración debe contabilizarse por separado.

## 22.5 Energía de escritura

Si cada celda consume \(E_w\) durante su programación:

\[
E_{rewrite,M}=\frac{f}{a^3\rho}E_w.
\]

Esta magnitud representa la energía activa para reescribir una vez todas las celdas del medio modelado. No incluye distribución eléctrica u óptica, conversión, control, verificación, calibración ni refrigeración.

## 22.6 Límite de Landauer

A temperatura \(T\), borrar irreversiblemente un bit tiene el límite:

\[
E_L=k_B T\ln 2.
\]

A 300 K resulta aproximadamente \(2.87\times10^{-21}\) J por bit. Este valor no incluye barreras de retención, calentamiento, direccionamiento, láseres, pérdidas ni márgenes de error y no debe confundirse con una energía de dispositivo.

El modelo devuelve tanto `landauer_j_per_erased_bit` como `landauer_full_erase_j_per_kg`, pero estas magnitudes son referencias termodinámicas, no objetivos de ingeniería inmediatos.

## 22.7 Densidad de cálculo

Si cada celda participa a frecuencia \(r\), con utilización \(u\), \(o\) operaciones por evento y factor de multiplexación \(m\):

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

La estimación utilizable debe ser el mínimo entre límites geométricos, térmicos, ópticos, eléctricos, de lectura, de comunicación y de precisión.

## 22.8 Escenarios de sensibilidad

Los escenarios incorporados muestran cómo cambian los resultados al variar pitch, estados, fracción activa, eficiencia de codificación y energía. Solo la conversión equivalente del vidrio escrito por láser está etiquetada como `measured`; el resto son escenarios o límites paramétricos.

| Escenario | Nivel | Densidad útil | Reescritura activa | Cálculo con 1 kW/kg |
|---|---|---:|---:|---:|
| Vidrio de sílice escrito por láser, equivalente | medido | 917 TB/kg | no estimada | no aplicable |
| PCM 3D, 100 nm, 16 estados | ingeniería | 14.3 PB/kg | 4.10 MJ/kg; 1.14 kWh/kg | 2.0e17 op/s/kg |
| PCM 3D, 20 nm, 16 estados | ingeniería agresiva | 1.28 EB/kg | 5.12 MJ/kg; 1.42 kWh/kg | 1.6e19 op/s/kg |
| PCM, 5 nm, 64 estados | límite especulativo | 24.6 EB/kg | 3.93 MJ/kg; 1.09 kWh/kg | 3.2e20 op/s/kg |
| Vidrio amorfo local, 10 nm, 8 estados | límite especulativo | 9.0 EB/kg | 800 MJ/kg; 222 kWh/kg | 2.0e18 op/s/kg |

El valor equivalente del vidrio procede de convertir 4.84 TB almacenados en una placa de 12 cm² y 2 mm de espesor, con densidad aproximada de 2200 kg/m³. Equivale a unos \(1.61\times10^{19}\) bits/m³ o a un pitch cúbico efectivo de aproximadamente 396 nm si cada voxel representara un bit.

Esa conversión no demuestra celdas nanométricas independientemente direccionables. Solo transforma una densidad archivística publicada a unidades comparables.

## 22.9 Interpretación correcta

Las cifras nanométricas pueden resultar enormes porque dividen por la masa del material activo. En un sistema real deben reducirse al incluir:

- aislamiento y separación térmica;
- selectores, electrodos, heaters y guías;
- fuentes, moduladores, detectores y convertidores;
- ECC, referencias y capacidad de reserva;
- calibración y ciclos de verificación;
- ancho de banda de entrada y salida;
- refrigeración;
- utilización instantánea limitada para evitar calentamiento acumulativo.

Por ejemplo, un techo geométrico puede exigir una potencia dinámica varios órdenes de magnitud superior al presupuesto térmico. En ese caso, añadir más celdas no aumenta el rendimiento útil: el sistema queda limitado por energía y evacuación de calor.

## 22.10 Reglas de uso

Un resultado solo puede presentarse como estimación de sistema cuando:

1. la masa total incluye soporte, direccionamiento, lectura, control y refrigeración;
2. las energías incluyen escritura, verificación, conversión y mantenimiento;
3. el ancho de banda permite acceder a la densidad calculada;
4. el número de estados está respaldado por una tasa de error y retención declaradas;
5. la utilización térmica es físicamente compatible con el encapsulado;
6. el nivel de evidencia queda visible junto al resultado.

En ausencia de estas condiciones, el resultado es un techo del medio activo o un análisis de sensibilidad.

## 22.11 Referencias de partida

- R. Landauer, *Irreversibility and Heat Generation in the Computing Process*, IBM Journal of Research and Development 5, 183–191 (1961).
- K. Stern et al., *Uncovering Phase Change Memory Energy Limits by Sub-Nanosecond Probing of Power Dissipation Dynamics*, arXiv:2104.11545.
- R.-G. Nir-Harwood et al., *Energy and Scaling Limits of Phase-Change Memory*, arXiv:2605.28336.
- X. Li et al., *Non-volatile silicon photonic memory with more than 4-bit per cell capability*, arXiv:1904.12740.
- J. Meng et al., *Electrical Programmable Multi-Level Non-volatile Photonic Random-Access Memory*, arXiv:2203.13337.
- H. Zhang et al., *Optimization of all-optical phase-change waveguide devices for photonic computing from the atomic scale*, arXiv:2603.18468.
- F. Chen and B. Wu, *Laser-written glass tablets can preserve data for millennia*, Nature (2026), DOI: 10.1038/d41586-026-00286-5.

Las referencias soportan límites físicos o ejemplos parciales. Ninguna demuestra por sí sola todos los escenarios paramétricos incluidos en el modelo.