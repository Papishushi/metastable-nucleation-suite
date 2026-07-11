# Almacenamiento de eventos y registro de datasets

La plataforma separa el plano semántico del plano de datos. RDF/JSON-LD describe la ejecución, la procedencia y el manifiesto; los eventos de alta cardinalidad permanecen en NDJSON o Parquet.

## Elección de formato

Use **NDJSON** para ejecuciones pequeñas, depuración, inspección con herramientas de texto, streaming línea a línea e interoperabilidad sin dependencias opcionales. Es el formato predeterminado y cada dataset contiene una sola partición.

Use **Parquet** para campañas grandes, análisis columnar, compresión y lectura selectiva. Se instala con:

```bash
python -m pip install -e '.[storage]'
```

Los campos escalares conservan tipos Arrow explícitos. `settings`, `outcome` y `diagnostics` se almacenan como JSON canónico dentro de columnas con el mismo nombre porque sus claves son abiertas y pueden variar entre especificaciones. `read_events` y `read_manifest_events` los decodifican, por lo que el evento JSON recuperado conserva valores y estructura.

## Escritura directa

```python
from metastable_suite.datasets import DatasetRegistry, write_events

manifest = write_events(
    "artifacts/run-42.events.parquet",
    "run-42-events",
    events,
    event_schema,
    storage_format="parquet",
    partition_size=100_000,
)
DatasetRegistry("artifacts/datasets.registry.json").register(manifest)
```

`execute_request` y `scripts/semantic_execute.py` aceptan `dataset_format="parquet"` / `--dataset-format parquet` para ejecuciones individuales. El orquestador de campañas conserva actualmente su layout NDJSON de recuperación; una campaña terminada puede convertirse sin cargar todo el dataset en memoria:

```bash
python scripts/dataset_storage.py convert \
  artifacts/run-42.events.ndjson \
  artifacts/run-42.events.parquet \
  --dataset-id run-42-events-parquet \
  --target-format parquet \
  --partition-size 100000 \
  --registry artifacts/datasets.registry.json
```

## Registro e integridad

`datasets.registry.json` usa `schemas/dataset-registry.schema.json`. Cada entrada registra:

- formato y media type;
- versión del esquema de evento;
- recuento total;
- particiones ordenadas y valores comunes de partición;
- SHA-256 de cada archivo;
- hash agregado determinista del dataset.

La escritura del registro es atómica. Registrar de nuevo el mismo identificador con contenido distinto falla salvo que el llamador solicite reemplazo explícito. `verify_manifest` recalcula hashes, lee cada partición y contrasta los recuentos.

```bash
python scripts/dataset_storage.py verify artifacts/datasets.registry.json
```

## Manifiesto semántico

NDJSON y Parquet usan la misma clase `mns:Dataset`. `mns:storageFormat` y `mns:mediaType` distinguen el soporte. `mns:hasDatasetPartition` enlaza nodos `mns:DatasetPartition`, que contienen ruta, índice, número de eventos y hash. Los ABox NDJSON anteriores, sin particiones explícitas, siguen siendo válidos como representación heredada.

## Límites conocidos

- Parquet requiere `pyarrow`; el núcleo NDJSON no lo importa.
- El registro JSON es adecuado para un proceso escritor o coordinación externa. No sustituye una base de datos transaccional con múltiples escritores concurrentes.
- El particionado actual es por número máximo de filas. Los valores comunes (`run_id`, `specification_id`, `backend_id`) se registran como metadatos, pero todavía no se crean árboles Hive por clave.
- La conversión conserva el esquema de evento `1.0.0`; una migración futura debe declarar explícitamente versiones de origen y destino.
