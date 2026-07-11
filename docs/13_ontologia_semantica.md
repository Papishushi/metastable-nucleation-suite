# 13. Ontología semántica de simulaciones y experimentos

La capa semántica permite representar el dominio científico y cada ejecución concreta como un grafo RDF consultable. Su objetivo es que una persona, un script o un sistema de agentes puedan inspeccionar, comparar, validar y transformar simulaciones sin depender de la estructura interna de un fichero Python.

## Separación entre TBox y ABox

La TBox se encuentra en `ontology/tbox.ttl`. Define el vocabulario estable del dominio mediante OWL: especificaciones experimentales, ejecuciones, simulaciones, experimentos físicos, ensayos, observaciones, resultados, hipótesis, controles, parámetros, reglas de parada, planes de análisis, amenazas, agentes, datasets y artifacts.

La ABox representa hechos concretos. Cada ejecución declara qué especificación ejecuta, qué agente la produjo, cuántos ensayos contiene, qué semilla utilizó, qué parámetros aplicó y qué resultados generó. Las ABoxes se serializan en JSON-LD para que sigan siendo razonablemente legibles y manipulables por aplicaciones convencionales.

Esta separación permite cambiar o añadir ejecuciones sin modificar la ontología del dominio. También permite evolucionar la TBox de forma versionada sin mezclar conceptos generales con resultados de una corrida concreta.

## Capas de validación

El documento ABox pasa por dos niveles de validación complementarios.

`ontology/abox.schema.json` valida la estructura JSON-LD antes de construir el grafo. Comprueba que exista `@context`, que `@graph` contenga nodos identificados y tipados y que las propiedades tengan valores RDF representables.

`ontology/abox-shapes.ttl` aplica SHACL sobre el grafo RDF. Esta capa valida restricciones semánticas que JSON Schema no puede expresar de forma natural. Por ejemplo, una `SimulationRun` debe tener exactamente una semilla, una ejecución completada debe tener fecha final y al menos un resultado, un parámetro debe contener un valor numérico o textual pero no ambos y un resultado de validación debe mantener coherencia entre `conforms` y su estado semántico.

OWL y SHACL cumplen funciones diferentes. OWL describe conocimiento abierto e inferencias; SHACL comprueba si una ABox satisface el contrato operativo que el proyecto exige.

## Estructura del vocabulario

Las clases principales son:

- `mns:ExperimentSpecification`, `mns:SimulationSpecification` y `mns:PhysicalExperimentSpecification` para describir planes;
- `mns:Execution`, `mns:SimulationRun` y `mns:ExperimentRun` para actividades concretas;
- `mns:Trial`, `mns:Observation` y `mns:Measurement` para granularidad experimental;
- `mns:Result`, `mns:StatisticalResult` y `mns:ValidationResult` para salidas;
- `mns:Hypothesis`, `mns:Control`, `mns:Observable`, `mns:Parameter`, `mns:StoppingRule` y `mns:AnalysisPlan` para diseño científico;
- `mns:Agent`, `mns:Dataset` y `mns:Artifact` para procedencia y automatización.

La ontología reutiliza PROV-O para conectar planes, agentes, actividades y entidades. Esto permite integrar el grafo con herramientas de procedencia existentes sin inventar un modelo paralelo.

## Generación de una ABox desde un informe

Después de ejecutar la suite:

```bash
python scripts/run_suite.py --trials 50000 --seed 7
```

puede materializarse una ABox:

```bash
python scripts/semantic_graph.py from-report \
  artifacts/reference_report.json \
  artifacts/reference_run.jsonld \
  --run-id reference-seed-7
```

El informe de referencia es agregado, por lo que el materializador no lo atribuye artificialmente a un único experimento. Crea una `SimulationRun` independiente para cada especificación realmente representada y enlaza los resultados con E02, E07, E09, E11, E12 o E13 según corresponda.

El comando genera JSON-LD, aplica el JSON Schema y ejecuta SHACL con inferencia RDFS controlada. Si la ABox no cumple el contrato, el proceso termina con código distinto de cero.

## Validación manual

```bash
python scripts/semantic_graph.py validate ontology/examples/reference-run.jsonld
```

El informe SHACL indica el nodo, la propiedad y la restricción que ha fallado. Esto permite usar la misma validación desde CI, desde una interfaz humana o desde un agente autónomo.

## Consultas SPARQL

Las consultas reutilizables están en `ontology/queries/`. Por ejemplo:

```bash
python scripts/semantic_graph.py query \
  ontology/examples/reference-run.jsonld \
  ontology/queries/completed-runs.rq
```

Para consultar conjuntamente la TBox y la ABox:

```bash
python scripts/semantic_graph.py query \
  ontology/examples/reference-run.jsonld \
  ontology/queries/results-by-run.rq \
  --include-tbox
```

El resultado se devuelve como JSON, lo que facilita su consumo por sistemas de agentes, pipelines y herramientas de evaluación.

## Patrón de trabajo para agentes

Un agente debería seguir esta secuencia:

1. seleccionar una especificación E01–E15;
2. ejecutar o importar una simulación;
3. materializar una ABox con identificadores persistentes;
4. validar primero contra JSON Schema y después contra SHACL;
5. ejecutar consultas SPARQL o reglas de decisión;
6. adjuntar el informe de validación y el grafo a los artifacts de la ejecución.

Los agentes no deben inferir que una ABox incompleta es falsa. OWL utiliza el supuesto de mundo abierto. Cuando el proyecto necesita exigir presencia, cardinalidad o coherencia operativa, esa obligación se expresa mediante SHACL.

## Extensión del modelo

Las futuras extensiones deben conservar URIs estables y añadir términos de forma compatible. Una nueva plataforma puede introducir subclases de `mns:ExperimentRun`, nuevos observables o amenazas específicas sin cambiar las relaciones nucleares entre especificación, ejecución, agente, resultado y procedencia.

Cuando una restricción sea una regla de calidad del dato debe añadirse a SHACL. Cuando describa significado o jerarquía conceptual debe añadirse a OWL. Cuando afecte únicamente a la serialización JSON-LD debe incorporarse al JSON Schema del ABox.
