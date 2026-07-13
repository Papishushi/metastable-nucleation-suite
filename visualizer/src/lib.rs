mod gpu;
mod scene;

pub use gpu::{GpuContext, browser_backends};
pub use scene::{Scene, SceneValidationError};

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

/// Validate a versioned visualization scene before it reaches the GPU.
///
/// # Errors
///
/// Returns a combined error message when JSON deserialization or any cross-reference or
/// scientific-integrity invariant fails.
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
pub fn validate_scene_json(scene_json: &str) -> Result<(), String> {
    let scene: Scene = serde_json::from_str(scene_json)
        .map_err(|error| format!("invalid visualization scene JSON: {error}"))?;
    scene.validate().map_err(|errors| {
        errors
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join("; ")
    })
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
    fn browser_policy_prefers_webgpu_and_keeps_webgl_fallback() {
        let backends = browser_backends();

        assert!(backends.contains(wgpu::Backends::BROWSER_WEBGPU));
        assert!(backends.contains(wgpu::Backends::GL));
    }
}
