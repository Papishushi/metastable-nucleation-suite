mod support;

use metastable_visualizer::validate_scene_json;

#[test]
fn rust_validator_matches_the_shared_contract_corpus() {
    for (name, scene, expected) in support::scenes() {
        assert_eq!(
            validate_scene_json(&scene).is_ok(),
            expected,
            "conformance case '{name}'"
        );
    }
}
