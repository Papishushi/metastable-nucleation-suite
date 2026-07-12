# 15. Adaptadores de hardware Serial, TCP y VISA

La capa de hardware utiliza un contrato común de petición y respuesta JSON. Cada mensaje contiene un comando y un objeto `payload`, y cada dispositivo devuelve un objeto JSON terminado por salto de línea. Este protocolo permite reutilizar el mismo ciclo de vida en dispositivos serie, sockets TCP e instrumentos VISA.

## Instalación

Para Serial y VISA:

```bash
pip install -e .[hardware]
```

Para usar VISA mediante un backend Python sin drivers del fabricante:

```bash
pip install -e .[visa-py]
```

TCP utiliza únicamente la biblioteca estándar de Python.

## Protocolo

Petición:

```json
{"command":"execute_trial","payload":{"run_id":"run-1","specification_id":"E09","trial_index":0,"settings":{}}}
```

Respuesta:

```json
{"timestamp_utc":"2026-07-11T12:00:00Z","outcome":{"count":2},"diagnostics":{"temperature_c":21.5},"valid":true}
```

Las respuestas deben ser objetos JSON. Una respuesta malformada es un error de protocolo y no se reintenta, porque repetir una orden desconocida puede duplicar una operación física. Los timeouts y fallos de conexión sí pueden reintentarse y fuerzan una reconexión previa.

## Ejecución desde un plan semántico

La ABox describe qué backend lógico debe utilizarse mediante `mns:usesBackend`, pero no contiene direcciones de red, puertos serie, recursos VISA ni credenciales. Esos detalles pertenecen a una configuración externa validada contra `schemas/backend-config.schema.json`.

El ejemplo `ontology/examples/planned-e09-hardware.jsonld` selecciona el backend `lab-counter-tcp`. Su despliegue se configura en `examples/hardware-backends.json`:

```json
{
  "schema_version": "1.0.0",
  "backends": [
    {
      "id": "lab-counter-tcp",
      "transport": "tcp",
      "host": "127.0.0.1",
      "port": 9000,
      "timeout_s": 2.0,
      "firmware_version": "counter-firmware-1.0.0",
      "supported_specifications": ["E09"],
      "retry_policy": {
        "attempts": 3,
        "initial_delay_s": 0.05,
        "backoff": 2.0,
        "maximum_delay_s": 1.0
      }
    }
  ]
}
```

Ejecución:

```bash
python scripts/semantic_execute.py \
  ontology/examples/planned-e09-hardware.jsonld \
  artifacts/hardware-run \
  --backend-config examples/hardware-backends.json
```

El ejecutor valida primero el plan, el esquema de configuración, los identificadores únicos y la compatibilidad entre backend y especificación. Solo después crea el adaptador seleccionado. Una configuración que intente redefinir `reference-simulator`, repita identificadores o declare campos desconocidos se rechaza antes de abrir conexiones.

Los mismos backends configurados están disponibles para campañas semánticas. Cada subejecución resuelve el `backend_id` de su ABox contra el registro externo y conserva las políticas de recuperación de campaña existentes.

La materialización final distingue explícitamente:

- simuladores: `mns:SimulationRun`, `mns:SimulationSpecification` y `mns:SimulatorBackend`;
- dispositivos físicos: `mns:ExperimentRun`, `mns:PhysicalExperimentSpecification` y `mns:HardwareBackend`.

En ambos casos se generan eventos válidos, manifiesto de integridad y ABox completada conforme con SHACL.

## TCP

```python
from metastable_suite.hardware_adapters import TCPCommandBackend
from metastable_suite.transports import RetryPolicy

backend = TCPCommandBackend(
    host="192.168.1.50",
    port=9000,
    timeout_s=2.0,
    backend_id="photon-counter-a",
    firmware_version="1.4.2",
    retry_policy=RetryPolicy(attempts=3, initial_delay_s=0.1),
)
```

El transporte usa mensajes JSON delimitados por `\n`, limita el tamaño máximo de respuesta y diferencia timeout, desconexión y error de protocolo.

## Serial

```python
from metastable_suite.hardware_adapters import SerialCommandBackend

backend = SerialCommandBackend(
    port="/dev/ttyUSB0",
    baudrate=115200,
    timeout_s=2.0,
    backend_id="fpga-node-a",
    firmware_version="2026.07",
)
```

El adaptador detecta escrituras parciales, respuestas vacías y errores de apertura. Antes de comenzar limpia el buffer de entrada para evitar interpretar una respuesta antigua como resultado del ensayo actual.

## VISA

```python
from metastable_suite.hardware_adapters import VisaCommandBackend

backend = VisaCommandBackend(
    resource_name="TCPIP0::192.168.1.80::INSTR",
    timeout_s=3.0,
    backend_id="oscilloscope-a",
    firmware_version="3.2.1",
)
```

VISA configura terminaciones de lectura y escritura y expresa el timeout en milisegundos, como requiere PyVISA. El recurso y el `ResourceManager` se cierran incluso cuando la ejecución falla.

## Errores normalizados

- `TransportTimeout`: no hubo respuesta dentro del límite.
- `TransportConnectionError`: no se pudo conectar o se perdió el canal.
- `TransportProtocolError`: la respuesta no es JSON válido, no es un objeto o contiene un error declarado por el dispositivo.

Los errores de transporte no deben convertirse silenciosamente en resultados científicos. El motor de ejecución debe registrar el fallo de ensayo o de ejecución, sus diagnósticos y la política aplicada.

## Seguridad operacional

Los comandos físicos deben ser idempotentes cuando puedan reintentarse. Operaciones irreversibles, disparos, cambios de potencia o movimientos deben usar identificadores de petición o confirmaciones del dispositivo para evitar duplicados después de una reconexión. El comando `close` debe llevar el sistema a un estado seguro y no depender de que la ejecución haya terminado correctamente.

Los secretos no forman parte del contrato actual y los campos desconocidos están prohibidos por el esquema. Cuando un dispositivo requiera autenticación, debe usarse un proveedor externo de secretos o variables de entorno referenciadas por el despliegue, nunca valores sensibles dentro de la ABox o de archivos versionados.
