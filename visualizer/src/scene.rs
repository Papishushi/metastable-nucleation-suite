use std::collections::{HashMap, HashSet};

use serde::Deserialize;
use serde_json::Value;
use thiserror::Error;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Scene {
    pub schema_version: String,
    pub scene_id: String,
    pub generated_at_utc: String,
    pub experiment_id: String,
    pub projection_kind: ProjectionKind,
    pub coordinate_system: CoordinateSystem,
    pub provenance: Vec<SourceArtifact>,
    pub layers: Vec<Layer>,
    pub entities: Vec<Entity>,
    pub transitions: Vec<Transition>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ProjectionKind {
    Physical,
    Abstract,
    Hybrid,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CoordinateSystem {
    pub frame_id: String,
    pub kind: String,
    pub handedness: Handedness,
    pub abstract_space: bool,
    pub origin_description: String,
    pub axes: Axes,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Handedness {
    Right,
    Left,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Axes {
    pub x: Axis,
    pub y: Axis,
    pub z: Axis,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Axis {
    pub label: String,
    pub unit: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SourceArtifact {
    pub id: String,
    pub uri: String,
    pub sha256: String,
    pub semantic_role: ArtifactRole,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ArtifactRole {
    Raw,
    Calibration,
    Derived,
    Semantic,
    Model,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum ScientificRole {
    Measured,
    Derived,
    Inferred,
    Illustrative,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Layer {
    pub id: String,
    pub label: String,
    pub scientific_role: ScientificRole,
    pub visible_by_default: bool,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Entity {
    pub id: String,
    pub layer_id: String,
    #[serde(rename = "entity_type")]
    pub kind: String,
    pub label: String,
    pub position: [f64; 3],
    pub provenance_refs: Vec<String>,
    pub uncertainty: Option<Uncertainty>,
    #[serde(default)]
    pub attributes: HashMap<String, Value>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Uncertainty {
    pub standard_deviation: [f64; 3],
    pub confidence_level: f64,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Transition {
    pub id: String,
    pub layer_id: String,
    pub from_entity_id: String,
    pub to_entity_id: String,
    pub timestamp_utc: String,
    pub interpolation: Interpolation,
    pub provenance_refs: Vec<String>,
    #[serde(default)]
    pub attributes: HashMap<String, Value>,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Interpolation {
    None,
    Linear,
    Model,
}

#[derive(Debug, Error, Eq, PartialEq)]
pub enum SceneValidationError {
    #[error("unsupported scene schema version '{0}'")]
    UnsupportedSchemaVersion(String),
    #[error("duplicate {kind} identifier '{id}'")]
    DuplicateIdentifier { kind: &'static str, id: String },
    #[error("{owner_kind} '{owner_id}' references unknown {target_kind} '{target_id}'")]
    UnknownReference {
        owner_kind: &'static str,
        owner_id: String,
        target_kind: &'static str,
        target_id: String,
    },
    #[error("source artifact '{0}' does not contain a lowercase SHA-256 digest")]
    InvalidSha256(String),
    #[error("measured transition '{0}' must use interpolation 'none'")]
    MeasuredTransitionInterpolation(String),
    #[error("physical projection cannot declare an abstract coordinate system")]
    PhysicalProjectionUsesAbstractCoordinates,
    #[error("abstract projection must declare an abstract coordinate system")]
    AbstractProjectionUsesPhysicalCoordinates,
}

impl Scene {
    /// Validate cross-document invariants that JSON Schema cannot express.
    ///
    /// # Errors
    ///
    /// Returns every detected identifier, reference, provenance and scientific-integrity
    /// error so a caller can repair a scene in one pass.
    pub fn validate(&self) -> Result<(), Vec<SceneValidationError>> {
        let mut errors = Vec::new();

        if self.schema_version != "1.0.0" {
            errors.push(SceneValidationError::UnsupportedSchemaVersion(
                self.schema_version.clone(),
            ));
        }

        self.validate_projection(&mut errors);

        let provenance_ids = self.validate_artifacts(&mut errors);
        let layer_ids = unique_ids(&self.layers, |layer| &layer.id, "layer", &mut errors);
        let layer_roles: HashMap<&str, ScientificRole> = self
            .layers
            .iter()
            .map(|layer| (layer.id.as_str(), layer.scientific_role))
            .collect();
        let entity_ids = unique_ids(&self.entities, |entity| &entity.id, "entity", &mut errors);
        unique_ids(
            &self.transitions,
            |transition| &transition.id,
            "transition",
            &mut errors,
        );

        self.validate_entities(&layer_ids, &provenance_ids, &mut errors);
        self.validate_transitions(
            &layer_ids,
            &layer_roles,
            &entity_ids,
            &provenance_ids,
            &mut errors,
        );

        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }

    fn validate_projection(&self, errors: &mut Vec<SceneValidationError>) {
        match self.projection_kind {
            ProjectionKind::Physical if self.coordinate_system.abstract_space => {
                errors.push(SceneValidationError::PhysicalProjectionUsesAbstractCoordinates);
            }
            ProjectionKind::Abstract if !self.coordinate_system.abstract_space => {
                errors.push(SceneValidationError::AbstractProjectionUsesPhysicalCoordinates);
            }
            ProjectionKind::Physical | ProjectionKind::Abstract | ProjectionKind::Hybrid => {}
        }
    }

    fn validate_artifacts<'a>(
        &'a self,
        errors: &mut Vec<SceneValidationError>,
    ) -> HashSet<&'a str> {
        let provenance_ids = unique_ids(
            &self.provenance,
            |artifact| &artifact.id,
            "provenance",
            errors,
        );
        for artifact in &self.provenance {
            if artifact.sha256.len() != 64
                || !artifact
                    .sha256
                    .bytes()
                    .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
            {
                errors.push(SceneValidationError::InvalidSha256(artifact.id.clone()));
            }
        }
        provenance_ids
    }

    fn validate_entities(
        &self,
        layer_ids: &HashSet<&str>,
        provenance_ids: &HashSet<&str>,
        errors: &mut Vec<SceneValidationError>,
    ) {
        for entity in &self.entities {
            require_reference(
                layer_ids,
                "entity",
                &entity.id,
                "layer",
                &entity.layer_id,
                errors,
            );
            validate_provenance_refs(
                provenance_ids,
                "entity",
                &entity.id,
                &entity.provenance_refs,
                errors,
            );
        }
    }

    fn validate_transitions(
        &self,
        layer_ids: &HashSet<&str>,
        layer_roles: &HashMap<&str, ScientificRole>,
        entity_ids: &HashSet<&str>,
        provenance_ids: &HashSet<&str>,
        errors: &mut Vec<SceneValidationError>,
    ) {
        for transition in &self.transitions {
            require_reference(
                layer_ids,
                "transition",
                &transition.id,
                "layer",
                &transition.layer_id,
                errors,
            );
            require_reference(
                entity_ids,
                "transition",
                &transition.id,
                "entity",
                &transition.from_entity_id,
                errors,
            );
            require_reference(
                entity_ids,
                "transition",
                &transition.id,
                "entity",
                &transition.to_entity_id,
                errors,
            );
            validate_provenance_refs(
                provenance_ids,
                "transition",
                &transition.id,
                &transition.provenance_refs,
                errors,
            );

            if layer_roles.get(transition.layer_id.as_str()) == Some(&ScientificRole::Measured)
                && transition.interpolation != Interpolation::None
            {
                errors.push(SceneValidationError::MeasuredTransitionInterpolation(
                    transition.id.clone(),
                ));
            }
        }
    }
}

fn unique_ids<'a, T>(
    values: &'a [T],
    id: impl Fn(&'a T) -> &'a str,
    kind: &'static str,
    errors: &mut Vec<SceneValidationError>,
) -> HashSet<&'a str> {
    let mut ids = HashSet::new();
    for value in values {
        let value_id = id(value);
        if !ids.insert(value_id) {
            errors.push(SceneValidationError::DuplicateIdentifier {
                kind,
                id: value_id.to_owned(),
            });
        }
    }
    ids
}

fn validate_provenance_refs(
    provenance_ids: &HashSet<&str>,
    owner_kind: &'static str,
    owner_id: &str,
    references: &[String],
    errors: &mut Vec<SceneValidationError>,
) {
    for reference in references {
        require_reference(
            provenance_ids,
            owner_kind,
            owner_id,
            "provenance",
            reference,
            errors,
        );
    }
}

fn require_reference(
    known_ids: &HashSet<&str>,
    owner_kind: &'static str,
    owner_id: &str,
    target_kind: &'static str,
    target_id: &str,
    errors: &mut Vec<SceneValidationError>,
) {
    if !known_ids.contains(target_id) {
        errors.push(SceneValidationError::UnknownReference {
            owner_kind,
            owner_id: owner_id.to_owned(),
            target_kind,
            target_id: target_id.to_owned(),
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scene() -> Scene {
        serde_json::from_str(include_str!(
            "../../contracts/v1/fixtures/visualization-scene-e09.json"
        ))
        .expect("reference scene must deserialize")
    }

    #[test]
    fn rejects_unknown_entity_reference() {
        let mut scene = scene();
        scene.transitions[0].to_entity_id = "missing-state".to_owned();

        let errors = scene.validate().expect_err("scene must fail validation");

        assert!(errors.iter().any(|error| matches!(
            error,
            SceneValidationError::UnknownReference {
                target_kind: "entity",
                target_id,
                ..
            } if target_id == "missing-state"
        )));
    }

    #[test]
    fn rejects_interpolated_measured_transition() {
        let mut scene = scene();
        scene.transitions[0].interpolation = Interpolation::Linear;

        let errors = scene.validate().expect_err("scene must fail validation");

        assert!(
            errors.contains(&SceneValidationError::MeasuredTransitionInterpolation(
                "trial-000042-node-a".to_owned(),
            ))
        );
    }
}
