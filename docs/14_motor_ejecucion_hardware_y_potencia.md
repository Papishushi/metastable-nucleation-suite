# 14. Motor de ejecución, adaptadores de hardware y potencia Monte Carlo

Esta capa convierte la ontología en una interfaz operativa. Una ABox ya no se limita a describir una ejecución pasada: también puede expresar una ejecución planificada que el software valida, transforma en una configuración concreta, ejecuta mediante un backend y devuelve como una nueva ABox completada.

## Flujo de ejecución

El flujo completo es:

```text
ABox Planned
  → JSON Schema
  → SHACL
  → ExecutionRequest
  → ExperimentalBackend
  → eventos NDJSON
  → manifiesto SHA-256
  → ExecutionResult
  → ABox Completed
  → SHACL
```

El ejemplo `ontology/examples/planned-e09.jsonld` declara una simulación E09, el backend `reference-simulator`, dos parámetros, veinticinco ensayos y la semilla pseudoaleatoria. Puede ejecutarse con:

```bash
python scripts/semantic_execute.py \
  ontology/examples/planned-e09.jsonld \
  artifacts/execution
```

La salida contiene el dataset evento a evento y una ABox completada. El motor rechaza planes no conformes antes de activar el backend y vuelve a validar semánticamente el resultado después de la ejecución.

## Contrato de backend

Todos los dispositivos implementan `ExperimentalBackend`. El ciclo de vida común comprende:

1. `prepare`, que configura recursos y parámetros;
2. `calibrate`, que registra el estado metrológico inicial;
3. `reset`, que recupera la condición inicial de cada ensayo;
4. `execute_trial`, que devuelve un resultado normalizado;
5. `collect_diagnostics`, que captura el estado final;
6. `close`, que libera de forma segura los recursos.

`SimulatorBackend` adapta los modelos internos. `CommandBackend` sirve como base para transporte serial, TCP, VISA, FPGA o sistemas de control de laboratorio. Una implementación física solo tiene que definir el intercambio de comandos; el motor conserva idénticos la validación, los datasets, los hashes y la procedencia.

## Dataset evento a evento

Los ensayos se escriben como NDJSON conforme a `schemas/event.schema.json`. Cada evento contiene:

- identificadores de ejecución, experimento y ensayo;
- timestamp UTC;
- backend y versión de firmware;
- ajustes aplicados;
- resultado;
- diagnósticos;
- flag de validez;
- motivos de exclusión;
- incertidumbre de reloj cuando esté disponible.

El manifiesto registra número de eventos, versión de schema, media type, ruta y SHA-256. RDF conserva la semántica y la procedencia; NDJSON conserva eficientemente el volumen de datos. Para campañas grandes puede añadirse posteriormente una representación Parquet manteniendo el mismo manifiesto ontológico.

## Extensión ontológica

`ontology/execution-extension.ttl` introduce `SuiteRun`, `ExperimentalCampaign`, `HardwareBackend`, `SimulatorBackend`, `ExecutionSummary` y `PowerAnalysis`. También define las relaciones entre campañas y subejecuciones, dependencias, backend utilizado y metadatos verificables del dataset.

`ontology/execution-shapes.ttl` valida específicamente planes, ejecuciones completadas, datasets de eventos, campañas y análisis de potencia. Las restricciones base se han hecho condicionales: una ejecución `Planned` no debe inventar tiempos ni resultados; una ejecución `Completed` sí debe declarar tiempos, agente y resultados.

## Potencia Monte Carlo

`scripts/monte_carlo_power.py` estima potencia empírica mediante simulaciones repetidas. Implementa:

- diferencias entre proporciones;
- correlaciones con memoria opcional;
- CHSH con visibilidad y pérdidas dependientes del ajuste;
- no señalización con corrección por multiplicidad.

Ejemplo:

```bash
python scripts/monte_carlo_power.py \
  --design chsh \
  --sample-size 10000 \
  --visibility 0.95 \
  --loss-by-setting 0.10 \
  --alpha 0.001 \
  --repetitions 2000
```

También puede buscar un tamaño mínimo aproximado:

```bash
python scripts/monte_carlo_power.py \
  --design correlation \
  --target-power 0.90 \
  --minimum 100 \
  --maximum 100000 \
  --rho 0.03 \
  --memory 0.20 \
  --repetitions 3000
```

La salida incluye potencia estimada y error estándar Monte Carlo. Una estimación no debe considerarse estable si el error Monte Carlo es demasiado grande para la decisión experimental; en ese caso debe aumentarse el número de repeticiones.

## Incorporación de hardware real

Un adaptador físico debe registrar explícitamente:

- transporte y protocolo;
- timeouts y política de reintentos;
- versión de firmware;
- calibraciones;
- resolución temporal;
- incertidumbre del reloj;
- estados de error y exclusión;
- secuencia de apagado seguro.

Los backends no deben ocultar pérdidas ni fallos convirtiéndolos en resultados ordinarios. Todo ensayo fallido debe conservarse con `valid=false` y motivos de exclusión normalizados. De este modo, los análisis de eficiencia, postselección y no señalización pueden auditar el flujo completo.
