# Calibración de potencia Monte Carlo

La calibración compara los estimadores empíricos de potencia con aproximaciones normales de referencia para cuatro diseños: dos proporciones, correlación de Pearson mediante transformación de Fisher, CHSH ideal y diferencia marginal de no señalización.

## Incertidumbre Monte Carlo

Cada estimación informa el error estándar binomial y un intervalo de Wilson del 95 %. El intervalo mide únicamente el error introducido por el número finito de repeticiones Monte Carlo; no representa incertidumbre sobre el modelo físico ni sobre los parámetros de entrada.

## Cuadrícula de regresión

`benchmarks/power-calibration.json` contiene semillas deterministas, parámetros y rangos esperados. Los rangos son deliberadamente más amplios que el intervalo Monte Carlo ordinario para tolerar variación numérica entre versiones de NumPy, pero suficientemente estrechos para detectar cambios materiales en la tasa de rechazo.

La comprobación se ejecuta con:

```bash
python scripts/calibrate_power.py
```

## Supuestos de las referencias

- **Proporciones:** grupos independientes, tamaños iguales y aproximación normal del estadístico agrupado.
- **Correlación:** observaciones gaussianas independientes y transformación `atanh(r)` asintóticamente normal.
- **CHSH:** ajustes equiprobables, correlaciones singlete ideales, sin memoria ni pérdida dependiente del ajuste y varianza aproximada con conteos equilibrados.
- **No señalización:** cuatro brazos equiprobables, marginales cercanos a 0,5 y corrección Bonferroni fija.

## Limitaciones

Las aproximaciones dejan de ser fiables con muestras pequeñas, probabilidades extremas, dependencia temporal, pérdidas selectivas, ajustes desequilibrados o estimadores distintos de los implementados. Los casos CHSH y no señalización son benchmarks del simulador ideal, no garantías para datos de laboratorio. Cualquier cambio del modelo, del estadístico o de la política de multiplicidad exige regenerar y revisar explícitamente la cuadrícula, no ampliar rangos hasta que vuelva a pasar.
