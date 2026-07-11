# Metastable Nucleation Suite

[![CI](https://github.com/Papishushi/metastable-nucleation-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Papishushi/metastable-nucleation-suite/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS)

Suite abierta de protocolos, modelos de referencia y diseño experimental para estudiar **nucleación, metaestabilidad, selección de polimorfos, contaminación por semillas, variables ambientales latentes, retroacción de medida y posibles correlaciones no locales**.

El repositorio separa explícitamente tres cosas que suelen mezclarse:

1. **Fenómenos establecidos:** nucleación estocástica, barreras de energía libre, nucleación heterogénea, siembra, polimorfismo, decoherencia y correlaciones de Bell en sistemas preparados.
2. **Hipótesis plausibles pero no demostradas:** variables ambientales conocidas combinadas no linealmente, perturbaciones físicas compartidas o sensibilidad extrema de la nucleación a microcondiciones no registradas.
3. **Hipótesis extraordinarias:** correlaciones Bell-no-locales espontáneas entre sistemas preparados independientemente, violación de no señalización o acoplamientos no descritos por la física estándar.

> **Posición científica de partida:** la física conocida predice que dos sistemas independientes, sin entrelazamiento ni canal causal compartido, no violarán Bell y no permitirán señalización superlumínica. Una coincidencia temporal o una correlación residual no basta para demostrar no localidad.

## Qué contiene

- `docs/01_marco_cientifico.md`: términos, supuestos y límites.
- `docs/02_matriz_hipotesis.md`: hipótesis ordenadas desde química ordinaria hasta nueva física.
- `docs/03_suite_experimentos.md`: desarrollo científico de los 15 experimentos.
- `docs/04_laboratorio_metaestados_opticos.md`: diseño conceptual del laboratorio óptico distribuido.
- `docs/05_estadistica_y_falsacion.md`: análisis preregistrado, Bell, no señalización y control de multiplicidad.
- `docs/06_hoja_de_ruta.md`: fases de implementación y criterios go/no-go.
- `docs/07_seguridad_y_limites.md`: seguridad láser, criogenia, vacío y límites epistemológicos.
- `docs/09_fuentes_por_experimento.md`: trazabilidad de cada protocolo a literatura primaria.
- `docs/10_plantilla_preregistro.md`: preregistro para análisis confirmatorios.
- `docs/11_contrato_de_datos.md`: formato común de eventos, tiempos, flags y metrología.
- `docs/12_matriz_de_fallos_y_lagunas.md`: amenazas experimentales, falsos positivos y mitigaciones.
- `docs/13_ontologia_semantica.md`: arquitectura TBox/ABox, validación SHACL y uso por agentes.
- `references.bib`: bibliografía primaria y revisiones verificables por DOI.
- `experiments/catalog.yaml`: índice resumido legible por máquina.
- `experiments/specifications.yaml`: especificaciones ejecutables de E01–E15.
- `ontology/tbox.ttl`: ontología OWL del dominio científico.
- `ontology/abox-shapes.ttl`: contrato SHACL para ABoxes.
- `ontology/abox.schema.json`: JSON Schema para JSON-LD.
- `ontology/context.jsonld`: contexto JSON-LD reutilizable.
- `ontology/queries/`: consultas SPARQL para humanos y agentes.
- `src/metastable_suite/semantic.py`: API semántica.
- `scripts/semantic_graph.py`: materialización, validación y consulta de ABoxes.

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .[dev]
make check
```

Para generar y validar una ABox:

```bash
python scripts/run_suite.py --trials 50000 --seed 7
python scripts/semantic_graph.py from-report \
  artifacts/reference_report.json \
  artifacts/reference_run.jsonld \
  --run-id reference-seed-7
```

El materializador divide el informe agregado en ejecuciones semánticas separadas y enlaza cada resultado con la especificación E02, E07, E09, E11, E12 o E13 que realmente lo produjo.

Para consultar ejecuciones completadas:

```bash
python scripts/semantic_graph.py query \
  artifacts/reference_run.jsonld \
  ontology/queries/completed-runs.rq
```

La capa semántica usa PROV-O, validación JSON Schema y SHACL, inferencia RDFS controlada, literales JSON-LD `@json` y consultas SPARQL reutilizables.

## Estado del proyecto

Diseño conceptual y software de referencia. **No afirma que exista no localidad espontánea en la nucleación.** Define cómo intentar refutar primero las explicaciones ordinarias y qué observación sería realmente extraordinaria.

## Licencia

Código bajo MIT. Documentación bajo CC BY 4.0; véase `LICENSE` y `LICENSE-DOCS`.
