# 12. Matriz de fallos, sesgos y lagunas

Esta matriz resume los mecanismos capaces de producir una señal aparentemente anómala sin necesidad de nueva física. Su función es obligar a que cada protocolo declare qué falsos positivos puede generar, cómo se detectan y qué riesgo residual permanece después de aplicar los controles.

| Riesgo | Puede imitar | Señal diagnóstica | Control o mitigación | Riesgo residual |
|---|---|---|---|---|
| Deriva térmica o de bombeo | cambio de tasa, sincronización entre nodos | tendencia lenta, dependencia con orden de ensayo | validación temporal por bloques, sensores calibrados y permutaciones que preserven autocorrelación | gradientes locales no instrumentados |
| Memoria entre ensayos | correlación serial y aparente causa común | autocorrelación, dependencia con el resultado anterior | aumentar tiempo de reinicio, ensayos vacíos e incluir historia en el modelo | memoria de estados microscópicos no observados |
| Contaminación por semillas | selección persistente de un polimorfo | efecto ligado a superficies, rutas o consumibles | circuitos separados, trazadores, esterilización y controles ciegos | partículas por debajo del límite de detección |
| Reloj o disparo compartido | correlación simultánea entre laboratorios | picos alineados con fase de reloj o firmware | relojes independientes, intercambio de osciladores y reconstrucción posterior | señal externa común no registrada |
| Comunicación electrónica accidental | dependencia remota o señalización aparente | cambios con topología de red, cables o alimentación | desconexión física, aislamiento y auditoría RF | acoplamiento electromagnético residual |
| Pérdida dependiente del ajuste | violación aparente de Bell | eficiencia desigual por base o resultado | análisis event-ready, registro de no detecciones y umbral preregistrado | clasificación ambigua dependiente del estado |
| Ventana de coincidencia adaptable | Bell o señalización aparentes | resultado sensible al ancho o desplazamiento de la ventana | emparejamiento fijado antes de revelar resultados y análisis de todos los ensayos | incertidumbre en el instante de compromiso |
| Postselección | aumento artificial del tamaño del efecto | exclusiones correlacionadas con ajuste o resultado | conservar flags y no detecciones, auditar tasas de aceptación | fallos no clasificados correctamente |
| Parada opcional | significación exagerada | el resultado desaparece al incluir datos posteriores | tamaño fijo o regla secuencial válida preregistrada | decisiones operativas externas no registradas |
| Multiplicidad | pico o retardo aparentemente extraordinario | señal encontrada tras explorar muchas variables | familia de hipótesis preregistrada y corrección simultánea | espacio de análisis no documentado |
| Fuga de información | predicción fuera de muestra ilusoria | variables contienen marcas posteriores al resultado | separación temporal y auditoría de canalización | metadatos indirectos no detectados |
| Error de signo o indexado | violación de CHSH reproducible | discrepancia entre implementaciones independientes | datasets sintéticos, revisión cruzada y cálculo duplicado | error idéntico copiado entre equipos |
| Sesgo del clasificador | selección asimétrica de metaestado | dependencia con operador o versión de software | clasificador congelado, cegamiento y test de confusión | cambio físico que altera la calidad de lectura |
| Bloqueo por inyección | aparente decisión espontánea | fuerte dependencia de fase, polarización o retroreflexión | aisladores, monitorización óptica y barridos de acoplamiento | acoplamiento por debajo del monitor |
| Anisotropía del dispositivo | ruptura espontánea de simetría falsa | sesgo estable al rotar o intercambiar el dispositivo | rotación, inversión de etiquetas y mapas espaciales | defecto estructural no caracterizado |
| Instrumentación saturada | estados discretos o correlaciones espurias | clipping, tiempos muertos o histogramas truncados | monitor de rango dinámico y calibración por pulso | saturación transitoria no etiquetada |
| Modelo nulo incompleto | evidencia inflada a favor de una hipótesis exótica | mal ajuste de controles y residuos estructurados | ampliar familia de nulos y validar con perturbaciones inyectadas | mecanismo ordinario aún desconocido |

## Aplicación por niveles

Los experimentos E01–E06 deben concentrarse en deriva, memoria, contaminación, clasificación y retroacción. E07–E09 añaden riesgos de sincronización, comunicación accidental y causas comunes distribuidas. E10–E13 requieren, además, controlar eficiencia, coincidencias, postselección, localidad, memoria y no señalización. E14 debe auditar los sesgos compartidos por software y análisis entre plataformas, mientras que E15 necesita límites cuantitativos especialmente rigurosos para canales electromagnéticos y mecánicos.

Una mitigación no elimina un riesgo de manera absoluta. Cada informe debe indicar la sensibilidad del control y el tamaño máximo de efecto que todavía podría ocultarse por debajo de ese límite.
