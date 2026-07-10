# Contribuir

Las contribuciones deben mejorar la capacidad del proyecto para formular hipótesis falsables, ejecutar controles y reproducir análisis. No se aceptarán cambios que presenten una correlación como causalidad, una coincidencia como no localidad o una violación de Bell como señalización.

Toda hipótesis nueva debe incluir una predicción nula explícita y explicar qué resultado sería compatible con la física conocida. También debe identificar los principales confundidores, proponer controles positivos y negativos y definir qué observación justificaría una replicación más exigente.

Los análisis confirmatorios y exploratorios deben mantenerse separados. Un patrón descubierto al inspeccionar los datos puede documentarse y desarrollarse, pero debe validarse en un bloque independiente antes de presentarse como evidencia confirmatoria.

Las afirmaciones experimentales deben apoyarse preferentemente en fuentes primarias. Las revisiones pueden utilizarse para contexto, pero no deben sustituir la referencia original cuando se describe un resultado concreto.

Los cambios que afecten a cálculos críticos, emparejamiento de eventos, desigualdades de Bell, no señalización o validación estadística deben incluir datos sintéticos, pruebas automatizadas y una explicación de los supuestos matemáticos. Cuando sea posible, debe añadirse un control positivo que demuestre que el análisis detecta una señal conocida y un control negativo que muestre que no produce efectos espurios.

Antes de abrir un pull request, deben ejecutarse `ruff check .`, `python scripts/validate_catalog.py`, `pytest -q` y la simulación de referencia. La plantilla de pull request solicita la información mínima necesaria para revisar el cambio con rigor.
