use serde::Deserialize;
use serde_json::Value;

const CORPUS: &str =
    include_str!("../../../contracts/v1/fixtures/visualization-scene-conformance.json");
const BASE_SCENE: &str =
    include_str!("../../../contracts/v1/fixtures/visualization-scene-e09.json");

#[derive(Debug, Deserialize)]
struct Corpus {
    base_scene: String,
    cases: Vec<Case>,
}

#[derive(Debug, Deserialize)]
struct Case {
    name: String,
    valid: bool,
    operations: Vec<Operation>,
    #[serde(default)]
    suffix: String,
}

#[derive(Debug, Deserialize)]
struct Operation {
    op: String,
    path: String,
    value: Value,
}

pub fn scenes() -> Vec<(String, String, bool)> {
    let corpus: Corpus = serde_json::from_str(CORPUS).expect("conformance corpus must parse");
    assert_eq!(
        corpus.base_scene,
        "contracts/v1/fixtures/visualization-scene-e09.json"
    );
    let base: Value = serde_json::from_str(BASE_SCENE).expect("base scene must parse");

    corpus
        .cases
        .into_iter()
        .map(|case| {
            let mut scene = base.clone();
            for operation in case.operations {
                assert_eq!(operation.op, "replace", "unsupported corpus operation");
                let target = scene
                    .pointer_mut(&operation.path)
                    .unwrap_or_else(|| panic!("unknown JSON pointer {}", operation.path));
                *target = operation.value;
            }
            let mut document = serde_json::to_string(&scene).expect("scene must serialize");
            document.push_str(&case.suffix);
            (case.name, document, case.valid)
        })
        .collect()
}
