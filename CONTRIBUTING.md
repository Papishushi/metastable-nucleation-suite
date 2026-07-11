# Contribuir

Las contribuciones deben mejorar la capacidad del proyecto para formular hipótesis falsables, ejecutar controles y reproducir análisis. No se aceptarán cambios que presenten una correlación como causalidad, una coincidencia como no localidad o una violación de Bell como señalización.

Toda hipótesis nueva debe incluir una predicción nula explícita y explicar qué resultado sería compatible con la física conocida. También debe identificar los principales confundidores, proponer controles positivos y negativos y definir qué observación justificaría una replicación más exigente.

Los análisis confirmatorios y exploratorios deben mantenerse separados. Un patrón descubierto al inspeccionar los datos puede documentarse y desarrollarse, pero debe validarse en un bloque independiente antes de presentarse como evidencia confirmatoria.

Las afirmaciones experimentales deben apoyarse preferentemente en fuentes primarias. Las revisiones pueden utilizarse para contexto, pero no deben sustituir la referencia original cuando se describe un resultado concreto.

Los cambios que afecten a cálculos críticos, emparejamiento de eventos, desigualdades de Bell, no señalización o validación estadística deben incluir datos sintéticos, pruebas automatizadas y una explicación de los supuestos matemáticos. Cuando sea posible, debe añadirse un control positivo que demuestre que el análisis detecta una señal conocida y un control negativo que muestre que no produce efectos espurios.

## Gestión del trabajo con PBIs

El equivalente a un Product Backlog Item es una GitHub Issue cuyo título comienza por `[PBI]`. Los trabajos amplios se representan mediante una issue `[EPIC]` con enlaces a los PBIs que la componen.

Cada PBI debe contener:

- un objetivo observable;
- contexto y problema;
- criterios de aceptación verificables;
- estrategia de validación;
- dependencias y épica principal;
- elementos expresamente fuera de alcance.

La plantilla `.github/ISSUE_TEMPLATE/pbi.yml` proporciona esta estructura. Un PBI debe ser suficientemente pequeño para resolverse mediante un pull request coherente. Cuando una tarea mezcle resultados independientes, debe dividirse antes de empezar la implementación.

Cada pull request debe enlazar el trabajo mediante `Closes #N` y, cuando corresponda, indicar su épica. GitHub cerrará automáticamente el PBI al fusionar el PR. Los comentarios de revisión que descubran trabajo adicional deben convertirse en un PBI cuando no puedan resolverse de forma segura dentro del alcance del PR actual.

No deben cerrarse hilos de revisión únicamente porque la CI esté verde. Primero debe responderse indicando la corrección, añadirse una prueba de regresión y comprobarse la CI sobre el nuevo commit.

## Validación antes de abrir un PR

Antes de abrir o actualizar un pull request debe ejecutarse:

```bash
make check
```

Como mínimo, la revisión debe confirmar:

- lint y tests en verde;
- validación del catálogo y las especificaciones;
- JSON Schema y SHACL cuando haya cambios semánticos;
- pruebas de regresión para cálculos críticos;
- conservación explícita de errores, exclusiones y diagnósticos en integraciones de hardware;
- documentación actualizada;
- ausencia de secretos o datos personales no controlados en artifacts y datasets.
