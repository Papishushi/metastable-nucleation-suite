# 13. Ontología semántica de simulaciones y experimentos

La capa semántica representa el dominio científico y cada ejecución concreta como grafos RDF consultables por personas, scripts y sistemas de agentes.

## TBox y ABox

`ontology/tbox.ttl` contiene la TBox OWL. Define especificaciones, ejecuciones, simulaciones, experimentos físicos, ensayos, observaciones, resultados, hipótesis, controles, parámetros, agentes, datasets y procedencia. El vocabulario reutiliza PROV-O para relacionar planes, actividades, agentes y entidades generadas.

Las ABoxes contienen hechos de ejecuciones concretas y se serializan en JSON-LD. Una ejecución declara qué especificación ejecuta, qué agente la produjo, el número de ensayos, la semilla, los tiempos reales y los resultados generados.

## Validación

`ontology/abox.schema.json` valida la estructura JSON-LD. `ontology/abox-shapes.ttl` aplica SHACL al grafo RDF para comprobar cardinalidades, datatypes y reglas operativas. OWL describe significado e inferencias bajo mundo abierto; SHACL exige la información mínima necesaria para ejecutar pipelines fiables.

Una `SimulationRun` debe tener semilla. Una ejecución completada debe incluir fecha final y resultados. Un parámetro debe contener un valor numérico o textual, pero no ambos. Los objetos y listas se representan mediante literales JSON-LD 1.1 con `@type: "@json"`.

## Materialización

```bash
python scripts/run_suite.py --trials 50000 --seed 7
python scripts/semantic_graph.py from-report \
  artifacts/reference_report.json \
  artifacts/reference_run.jsonld \
  --run-id reference-seed-7
```

El informe agregado se divide en ejecuciones semánticas por especificación. Los resultados de siembra se asocian a E02, las causas comunes a E07, los resultados ópticos a E09, el benchmark cuántico a E11, el modelo local a E12 y no señalización a E13. De este modo, una ABox válida también mantiene una atribución científica correcta.

## Validación y consultas

```bash
python scripts/semantic_graph.py validate ontology/examples/reference-run.jsonld
python scripts/semantic_graph.py query \
  ontology/examples/reference-run.jsonld \
  ontology/queries/completed-runs.rq
```

Las consultas SPARQL devuelven JSON para facilitar su consumo por agentes. `src/metastable_suite/semantic.py` expone las mismas operaciones como API Python.

## Regla de extensión

Los conceptos del dominio pertenecen a OWL, las obligaciones de calidad del grafo pertenecen a SHACL y las restricciones de serialización pertenecen a JSON Schema. Las URIs deben permanecer estables y las nuevas plataformas deben ampliar el modelo mediante subclases y propiedades compatibles.
