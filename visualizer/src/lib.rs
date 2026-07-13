mod gpu;
mod scene;

pub use gpu::{GpuContext, browser_backends};
pub use scene::{ValidatedScene, ValidationError, ValidationReport, parse_and_validate};

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

const ADAPTER_CAPABILITIES: &str = include_str!("../adapter-capabilities.json");

/// Validate a versioned visualization scene before it reaches the GPU.
///
/// The successful parse is retained by [`parse_and_validate`]. This WASM-safe compatibility
/// entry point serializes the structured validation report as JSON for browser callers.
///
/// # Errors
///
/// Returns a JSON object containing stable error codes, paths and messages.
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
pub fn validate_scene_json(scene_json: &str) -> Result<(), String> {
    parse_and_validate(scene_json)
        .map(|_| ())
        .map_err(|report| report.to_json())
}

/// Return adapter metadata separately from the generic scene contract.
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
#[must_use]
pub fn visualizer_adapter_capabilities_json() -> String {
    ADAPTER_CAPABILITIES.to_owned()
}

/// Report the renderer policy without exposing internal `wgpu` types to the host.
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
#[must_use]
pub fn renderer_backend_policy() -> String {
    "WebGPU preferred; WebGL2 fallback; Rust/WASM application logic only".to_owned()
}

#[cfg(test)]
mod tests {
    use super::*;

    const E09_FIXTURE: &str =
        include_str!("../../contracts/v1/fixtures/visualization-scene-e09.json");

    #[test]
    fn reference_scene_is_valid() {
        assert_eq!(validate_scene_json(E09_FIXTURE), Ok(()));
    }

    #[test]
    fn validation_errors_are_structured_json() {
        let report = validate_scene_json("{}").expect_err("empty object must fail");
        let value: serde_json::Value = serde_json::from_str(&report).expect("report must be JSON");

        assert_eq!(value["errors"][0]["code"], "scene.json.invalid");
        assert!(value["errors"][0]["path"].is_string());
    }

    #[test]
    fn capabilities_advertise_implemented_mappings_not_contract_syntax() {
        let capabilities: serde_json::Value =
            serde_json::from_str(&visualizer_adapter_capabilities_json())
                .expect("capabilities must be valid JSON");

        assert_eq!(
            capabilities["experiment_mappings"][0]["experiment_id"],
            "E09"
        );
        assert_eq!(
            capabilities["experiment_mappings"][0]["mapping_id"],
            "e09.abstract-state-space.v1"
        );
    }

    #[test]
    fn browser_policy_prefers_webgpu_and_keeps_webgl_fallback() {
        let backends = browser_backends();

        assert!(backends.contains(wgpu::Backends::BROWSER_WEBGPU));
        assert!(backends.contains(wgpu::Backends::GL));
    }
}
