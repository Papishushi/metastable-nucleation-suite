#![cfg(target_arch = "wasm32")]

mod support;

use metastable_visualizer::{
    CameraAction, CameraState, LinePattern, parse_and_validate, validate_scene_json,
};
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

#[wasm_bindgen_test]
fn e09_scene_builds_deterministic_render_and_interaction_state() {
    let scene = parse_and_validate(include_str!(
        "../../contracts/v1/fixtures/visualization-scene-e09.json"
    ))
    .expect("E09 fixture must be valid");
    let render = scene.render_scene();
    let invalid = render
        .transitions
        .iter()
        .find(|transition| !transition.valid)
        .expect("E09 fixture must retain its invalid transition");

    assert_eq!(render.entities.len(), 4);
    assert_eq!(render.transitions.len(), 3);
    assert_eq!(invalid.line_pattern, LinePattern::Dashed);

    let mut camera = CameraState::for_scene(&render);
    let initial_distance = camera.distance;
    camera.apply(CameraAction::Zoom { factor: 0.5 });
    assert!(camera.distance < initial_distance);
    camera.apply(CameraAction::Reset);
    assert!((camera.distance - initial_distance).abs() < f64::EPSILON);
}
