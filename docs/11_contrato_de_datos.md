# 11. Contrato de datos experimental

El objetivo es impedir que cada plataforma invente su propio significado de «ensayo válido», «resultado» o «tiempo de compromiso».

## Registro por ensayo

| Campo | Tipo | Descripción |
|---|---|---|
| `trial_id` | string | Identificador global inmutable. |
| `node_id` | string | Nodo físico de adquisición. |
| `protocol_id` | string | ID E01–E15 o extensión versionada. |
| `local_setting` | integer/string | Ajuste local elegido. |
| `outcome` | integer/string/null | Resultado bruto; `null` si no existe lectura válida. |
| `outcome_class` | string | `positive`, `negative`, `ambiguous`, `no_detection` u otra clase preregistrada. |
| `t_prepare_ps` | integer | Preparación en reloj local. |
| `t_setting_ps` | integer | Elección local. |
| `t_commit_ps` | integer/null | Estimación del compromiso físico. |
| `t_read_ps` | integer | Lectura. |
| `validity_flags` | array | Fallos y advertencias sin eliminar el ensayo. |
| `environment_ref` | string | Referencia al bloque multisensor. |
| `config_hash` | string | Hash de configuración, firmware y análisis. |

## Registro ambiental

Los canales deben conservar datos crudos y calibrados, resolución, frecuencia de muestreo, incertidumbre y desfase respecto al reloj del evento.

Canales mínimos para el laboratorio óptico:

- energía, espectro, fase y polarización del pulso;
- temperatura de cavidad y bancada;
- vibración y acústica;
- campos eléctricos, magnéticos y RF;
- presión, humedad o vacío;
- estado de criogenia y fuentes;
- detección de radiación cuando sea relevante.

## Reglas de integridad

1. Escritura append-only durante el bloque.
2. Hash encadenado por lote.
3. Conservación de no detecciones y resultados ambiguos.
4. Separación entre datos brutos, calibración y datos derivados.
5. Ningún emparejamiento entre nodos se modifica después de revelar resultados.
6. Los relojes se reconstruyen con incertidumbre explícita.
7. La versión del clasificador de metaestado queda fijada antes del análisis confirmatorio.

## Esquema mínimo de ejemplo

```json
{
  "trial_id": "A-000001",
  "node_id": "A",
  "protocol_id": "E11",
  "local_setting": 1,
  "outcome": -1,
  "outcome_class": "negative",
  "t_prepare_ps": -200,
  "t_setting_ps": 0,
  "t_commit_ps": 420,
  "t_read_ps": 900,
  "validity_flags": [],
  "environment_ref": "env-A-000001",
  "config_hash": "sha256:..."
}
```
