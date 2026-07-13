#![cfg(target_arch = "wasm32")]

mod support;

use metastable_visualizer::validate_scene_json;
use wasm_bindgen_test::wasm_bindgen_test;

wasm_bindgen_test::wasm_bindgen_test_configure!(run_in_browser);

#[wasm_bindgen_test]
fn exported_validator_runs_in_a_browser_and_matches_the_contract_corpus() {
    for (name, scene, expected) in support::scenes() {
        assert_eq!(
            validate_scene_json(&scene).is_ok(),
            expected,
            "WASM conformance case '{name}'"
        );
    }
}
