# Control plane distribuido

El servicio opcional `metastable-control-plane` expone la frontera operacional HTTP de la suite sobre ASP.NET Core/Kestrel. El CLI y la ejecución standalone no dependen del servicio.

## Arranque

```bash
docker compose --profile distributed up --build --wait control-plane
```

El perfil inicia el worker científico, el control plane y volúmenes distintos para artefactos científicos y estado operacional. La imagen del control plane es Ubuntu Noble chiseled, se ejecuta sin privilegios y solo necesita escritura en `/state`.

## API v1

- `GET /v1/capabilities`: capacidades versionadas.
- `POST /v1/runs`: acepta el contrato `experiment-request.schema.json`; requiere `Idempotency-Key`.
- `GET /v1/runs/{runId}`: estado durable y transiciones.
- `POST /v1/runs/{runId}/cancel`: cancelación explícita e idempotencia terminal.
- `GET /v1/runs/{runId}/artifacts/{artifactId}`: metadatos derivados del artefacto.
- `GET /openapi/v1.json`: OpenAPI generado por la aplicación y validado en CI.

Ejemplo:

```bash
curl -i http://127.0.0.1:8080/v1/runs \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: example-e09-001' \
  --data '{
    "schema_version": "1.0.0",
    "request_id": "11111111-1111-1111-1111-111111111111",
    "experiment_id": "E09",
    "submitted_at_utc": "2026-07-15T00:00:00Z"
  }'
```

Repetir la misma solicitud con la misma clave devuelve el run original. Reutilizar la clave con otro envelope devuelve `409 Conflict`.

## Orquestación Extend0

La ejecución no la coordina Kestrel. El proceso crea un `CrossProcessSingleton<IRunOrchestrator>` de Extend0:

- existe un solo owner del scheduler en la máquina;
- instancias Kestrel adicionales resuelven el owner mediante IPC local;
- Windows usa named pipes y Linux/macOS usan Unix domain sockets;
- el contrato IPC solo transporta JSON y tipos serializables;
- el owner posee la cola, los dispatch activos, la cancelación y las tablas MetaDB.

El worker científico sigue recibiendo exclusivamente el envelope JSON v1 por HTTP. Ningún tipo Extend0 cruza hacia Python.

## Persistencia y recuperación

MetaDB mantiene dos índices operacionales reconstruibles:

- `runs.meta`: request, clave de idempotencia, estado y transiciones;
- `artifacts.meta`: referencia de artefacto y hash de la respuesta del worker.

Los artefactos, datasets y ABoxes no se almacenan en MetaDB y siguen siendo la fuente de verdad. Un reinicio vuelve a encolar runs `queued`; un run que estaba `running` pasa a `recovery_required` para impedir una repetición física silenciosa. El operador puede inspeccionarlo antes de decidir una nueva ejecución.

CI comprueba idempotencia, despacho real, índice de artefactos, persistencia tras reinicio y la transición `running → recovery_required` sobre Windows, Linux y macOS.
