#![allow(
    dead_code,
    reason = "validated scene fields are retained for the upcoming renderer boundary"
)]

use std::collections::{HashMap, HashSet};

use serde::{Deserialize, Serialize};
use thiserror::Error;
use time::{OffsetDateTime, format_description::well_known::Rfc3339};

use crate::render::{
    LinePattern, ProvenanceRef, RenderAxis, RenderCoordinates, RenderEntity, RenderHandedness,
    RenderLayer, RenderScene, RenderTransition, RenderUncertainty, VisualRole,
};

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Scene {
    schema_version: String,
    #[serde(rename = "scene_id")]
    id: String,
    generated_at_utc: String,
    experiment_id: String,
    projection_kind: ProjectionKind,
    coordinate_system: CoordinateSystem,
    provenance: Vec<SourceArtifact>,
    layers: Vec<Layer>,
    entities: Vec<Entity>,
    transitions: Vec<Transition>,
}

/// A scene that has been parsed and passed every contract and scientific invariant.
///
/// The inner scene is deliberately private: GPU upload and rendering code can only receive
/// this validated, immutable boundary rather than a freely constructed scene.
#[derive(Debug)]
pub struct ValidatedScene {
    scene: Scene,
}

impl ValidatedScene {
    #[must_use]
    pub fn scene_id(&self) -> &str {
        &self.scene.id
    }

    #[must_use]
    pub fn experiment_id(&self) -> &str {
        &self.scene.experiment_id
    }

    #[must_use]
    pub fn entity_count(&self) -> usize {
        self.scene.entities.len()
    }

    #[must_use]
    pub fn transition_count(&self) -> usize {
        self.scene.transitions.len()
    }

    /// Build deterministic render state without exposing unvalidated scene internals.
    #[must_use]
    pub fn render_scene(&self) -> RenderScene {
        let layers = self
            .scene
            .layers
            .iter()
            .map(|layer| RenderLayer {
                id: layer.id.clone(),
                label: layer.label.clone(),
                role: layer.scientific_role.into(),
                visible_by_default: layer.visible_by_default,
            })
            .collect();
        let layer_roles: HashMap<&str, ScientificRole> = self
            .scene
            .layers
            .iter()
            .map(|layer| (layer.id.as_str(), layer.scientific_role))
            .collect();
        let entities = self
            .scene
            .entities
            .iter()
            .map(|entity| RenderEntity {
                id: entity.id.clone(),
                layer_id: entity.layer_id.clone(),
                label: entity.label.clone(),
                position: entity.position,
                role: layer_roles[entity.layer_id.as_str()].into(),
                provenance: render_provenance(&entity.source_refs),
                uncertainty: entity.uncertainty.as_ref().map(RenderUncertainty::from),
            })
            .collect::<Vec<_>>();
        let entity_indices = entities
            .iter()
            .enumerate()
            .map(|(index, entity)| (entity.id.as_str(), index))
            .collect::<HashMap<_, _>>();
        let transitions = self
            .scene
            .transitions
            .iter()
            .map(|transition| RenderTransition {
                id: transition.id.clone(),
                layer_id: transition.layer_id.clone(),
                from_entity: entity_indices[transition.from_entity_id.as_str()],
                to_entity: entity_indices[transition.to_entity_id.as_str()],
                observation_role: transition.observation_role.into(),
                geometry_role: transition.geometry_mapping.scientific_role.into(),
                valid: transition.valid,
                line_pattern: if transition.valid {
                    LinePattern::Solid
                } else {
                    LinePattern::Dashed
                },
                exclusion_reasons: transition.exclusion_reasons.clone(),
                provenance: render_provenance(&transition.source_refs),
                geometry_provenance: render_provenance(&transition.geometry_mapping.source_refs),
                uncertainty: transition.uncertainty.as_ref().map(RenderUncertainty::from),
            })
            .collect();
        drop(entity_indices);
        let coordinate = &self.scene.coordinate_system;

        RenderScene {
            scene_id: self.scene.id.clone(),
            coordinates: RenderCoordinates {
                frame_id: coordinate.frame_id.clone(),
                handedness: coordinate.handedness.into(),
                abstract_space: coordinate.abstract_space,
                warning: coordinate.origin_description.clone(),
                axes: [
                    render_axis(&coordinate.axes.x),
                    render_axis(&coordinate.axes.y),
                    render_axis(&coordinate.axes.z),
                ],
            },
            layers,
            entities,
            transitions,
        }
    }
}

impl From<Handedness> for RenderHandedness {
    fn from(handedness: Handedness) -> Self {
        match handedness {
            Handedness::Right => Self::Right,
            Handedness::Left => Self::Left,
        }
    }
}

impl From<ScientificRole> for VisualRole {
    fn from(role: ScientificRole) -> Self {
        match role {
            ScientificRole::Measured => Self::Measured,
            ScientificRole::Derived => Self::Derived,
            ScientificRole::Inferred => Self::Inferred,
            ScientificRole::Illustrative => Self::Illustrative,
        }
    }
}

impl From<&Uncertainty> for RenderUncertainty {
    fn from(uncertainty: &Uncertainty) -> Self {
        Self {
            standard_deviation: uncertainty.standard_deviation,
            confidence_level: uncertainty.confidence_level,
        }
    }
}

fn render_axis(axis: &Axis) -> RenderAxis {
    RenderAxis {
        label: axis.label.clone(),
        unit: axis.unit.clone(),
    }
}

fn render_provenance(references: &[SourceReference]) -> Vec<ProvenanceRef> {
    references
        .iter()
        .map(|reference| ProvenanceRef {
            artifact_id: reference.artifact_id.clone(),
            run_id: reference.run_id.clone(),
            record_id: reference.record_id.clone(),
            event_id: reference.event_id.clone(),
            partition: reference.partition.clone(),
            row_group: reference.row_group,
        })
        .collect()
}

#[derive(Clone, Copy, Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ProjectionKind {
    Physical,
    Abstract,
    Hybrid,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct CoordinateSystem {
    frame_id: String,
    kind: CoordinateKind,
    handedness: Handedness,
    abstract_space: bool,
    origin_description: String,
    axes: Axes,
}

#[derive(Debug, Deserialize)]
enum CoordinateKind {
    #[serde(rename = "cartesian_3d")]
    Cartesian3d,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
enum Handedness {
    Right,
    Left,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Axes {
    x: Axis,
    y: Axis,
    z: Axis,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Axis {
    label: String,
    unit: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct SourceArtifact {
    id: String,
    uri: String,
    sha256: String,
    semantic_role: ArtifactRole,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
enum ArtifactRole {
    Raw,
    Calibration,
    Derived,
    Semantic,
    Model,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
enum ScientificRole {
    Measured,
    Derived,
    Inferred,
    Illustrative,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Layer {
    id: String,
    label: String,
    scientific_role: ScientificRole,
    visible_by_default: bool,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Entity {
    id: String,
    layer_id: String,
    #[serde(rename = "entity_type")]
    kind: String,
    label: String,
    position: [f64; 3],
    source_refs: Vec<SourceReference>,
    uncertainty: Option<Uncertainty>,
    #[serde(default)]
    attributes: HashMap<String, AttributeValue>,
}

#[derive(Clone, Debug, Deserialize, Eq, Hash, PartialEq)]
#[serde(deny_unknown_fields)]
struct SourceReference {
    artifact_id: String,
    run_id: String,
    record_id: String,
    event_id: Option<String>,
    partition: Option<String>,
    row_group: Option<u64>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Uncertainty {
    standard_deviation: [f64; 3],
    confidence_level: f64,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct GeometryMapping {
    scientific_role: ScientificRole,
    method_id: String,
    source_refs: Vec<SourceReference>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Transition {
    id: String,
    layer_id: String,
    from_entity_id: String,
    to_entity_id: String,
    timestamp_utc: String,
    interpolation: Interpolation,
    observation_role: ScientificRole,
    geometry_mapping: GeometryMapping,
    trial_id: String,
    correlation_id: String,
    trial_index: u64,
    node_id: String,
    device_id: Option<String>,
    valid: bool,
    exclusion_reasons: Vec<String>,
    source_refs: Vec<SourceReference>,
    uncertainty: Option<Uncertainty>,
    #[serde(default)]
    attributes: HashMap<String, AttributeValue>,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq)]
#[serde(rename_all = "snake_case")]
enum Interpolation {
    None,
    Linear,
    Model,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum AttributeValue {
    String(String),
    Number(serde_json::Number),
    Boolean(bool),
    Null(()),
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ValidationError {
    pub code: &'static str,
    pub path: String,
    pub message: String,
}

impl ValidationError {
    fn new(code: &'static str, path: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code,
            path: path.into(),
            message: message.into(),
        }
    }
}

#[derive(Clone, Debug, Eq, Error, PartialEq, Serialize)]
#[error("visualization scene validation failed")]
pub struct ValidationReport {
    pub errors: Vec<ValidationError>,
}

impl ValidationReport {
    /// # Panics
    ///
    /// Panics only if Serde cannot serialize this fixed, data-only report structure.
    #[must_use]
    pub fn to_json(&self) -> String {
        serde_json::to_string(self).expect("validation report must serialize")
    }
}

/// Parse and validate a scene exactly once, returning the only scene type accepted by renderers.
///
/// # Errors
///
/// Returns stable error codes and paths for JSON shape, contract and scientific failures.
pub fn parse_and_validate(scene_json: &str) -> Result<ValidatedScene, ValidationReport> {
    let mut deserializer = serde_json::Deserializer::from_str(scene_json);
    let scene: Scene =
        serde_path_to_error::deserialize(&mut deserializer).map_err(|error| ValidationReport {
            errors: vec![ValidationError::new(
                "scene.json.invalid",
                serde_path_to_json_path(&error.path().to_string()),
                error.inner().to_string(),
            )],
        })?;
    deserializer.end().map_err(|error| ValidationReport {
        errors: vec![ValidationError::new(
            "scene.json.trailing_data",
            "/",
            error.to_string(),
        )],
    })?;

    let errors = scene.validation_errors();
    if errors.is_empty() {
        Ok(ValidatedScene { scene })
    } else {
        Err(ValidationReport { errors })
    }
}

impl Scene {
    fn validation_errors(&self) -> Vec<ValidationError> {
        let mut errors = Vec::new();

        self.validate_document_fields(&mut errors);
        self.validate_projection(&mut errors);

        let provenance_ids = self.validate_artifacts(&mut errors);
        let layer_ids = self.validate_layers(&mut errors);
        let entity_ids = unique_ids(
            &self.entities,
            |entity| &entity.id,
            "entity",
            "/entities",
            &mut errors,
        );
        unique_ids(
            &self.transitions,
            |transition| &transition.id,
            "transition",
            "/transitions",
            &mut errors,
        );

        self.validate_entities(&layer_ids, &provenance_ids, &mut errors);
        self.validate_transitions(&layer_ids, &entity_ids, &provenance_ids, &mut errors);
        errors
    }

    fn validate_document_fields(&self, errors: &mut Vec<ValidationError>) {
        require_equal(
            &self.schema_version,
            "1.0.0",
            "/schema_version",
            "scene.schema_version.unsupported",
            errors,
        );
        validate_identifier(&self.id, "/scene_id", errors);
        validate_timestamp(&self.generated_at_utc, "/generated_at_utc", errors);
        if !is_experiment_identifier(&self.experiment_id) {
            errors.push(ValidationError::new(
                "scene.experiment_id.invalid",
                "/experiment_id",
                "experiment identifier must match E followed by at least two digits",
            ));
        }
        if self.provenance.is_empty() {
            errors.push(ValidationError::new(
                "scene.provenance.empty",
                "/provenance",
                "at least one source artifact is required",
            ));
        }
        if self.layers.is_empty() {
            errors.push(ValidationError::new(
                "scene.layers.empty",
                "/layers",
                "at least one layer is required",
            ));
        }

        let coordinate = &self.coordinate_system;
        validate_identifier(
            coordinate.frame_id.as_str(),
            "/coordinate_system/frame_id",
            errors,
        );
        require_non_empty(
            &coordinate.origin_description,
            "/coordinate_system/origin_description",
            errors,
        );
        for (name, axis) in [
            ("x", &coordinate.axes.x),
            ("y", &coordinate.axes.y),
            ("z", &coordinate.axes.z),
        ] {
            require_non_empty(
                &axis.label,
                &format!("/coordinate_system/axes/{name}/label"),
                errors,
            );
            require_non_empty(
                &axis.unit,
                &format!("/coordinate_system/axes/{name}/unit"),
                errors,
            );
        }
    }

    fn validate_projection(&self, errors: &mut Vec<ValidationError>) {
        match self.projection_kind {
            ProjectionKind::Physical if self.coordinate_system.abstract_space => {
                errors.push(ValidationError::new(
                    "scene.projection.physical_abstract",
                    "/coordinate_system/abstract_space",
                    "physical projection cannot use abstract coordinates",
                ));
            }
            ProjectionKind::Abstract if !self.coordinate_system.abstract_space => {
                errors.push(ValidationError::new(
                    "scene.projection.abstract_physical",
                    "/coordinate_system/abstract_space",
                    "abstract projection must use abstract coordinates",
                ));
            }
            ProjectionKind::Physical | ProjectionKind::Abstract | ProjectionKind::Hybrid => {}
        }
    }

    fn validate_artifacts<'a>(&'a self, errors: &mut Vec<ValidationError>) -> HashSet<&'a str> {
        let ids = unique_ids(
            &self.provenance,
            |artifact| &artifact.id,
            "source artifact",
            "/provenance",
            errors,
        );
        for (index, artifact) in self.provenance.iter().enumerate() {
            let base = format!("/provenance/{index}");
            validate_identifier(&artifact.id, &format!("{base}/id"), errors);
            if !is_bundle_relative_path(&artifact.uri) {
                errors.push(ValidationError::new(
                    "scene.artifact.path.invalid",
                    format!("{base}/uri"),
                    "artifact path must be normalized, bundle-relative and scheme-free",
                ));
            }
            if !is_lowercase_sha256(&artifact.sha256) {
                errors.push(ValidationError::new(
                    "scene.artifact.sha256.invalid",
                    format!("{base}/sha256"),
                    "SHA-256 digest must contain exactly 64 lowercase hexadecimal characters",
                ));
            }
        }
        ids
    }

    fn validate_layers<'a>(&'a self, errors: &mut Vec<ValidationError>) -> HashSet<&'a str> {
        let ids = unique_ids(&self.layers, |layer| &layer.id, "layer", "/layers", errors);
        for (index, layer) in self.layers.iter().enumerate() {
            validate_identifier(&layer.id, &format!("/layers/{index}/id"), errors);
            require_non_empty(&layer.label, &format!("/layers/{index}/label"), errors);
        }
        ids
    }

    fn validate_entities(
        &self,
        layer_ids: &HashSet<&str>,
        provenance_ids: &HashSet<&str>,
        errors: &mut Vec<ValidationError>,
    ) {
        for (index, entity) in self.entities.iter().enumerate() {
            let base = format!("/entities/{index}");
            validate_identifier(&entity.id, &format!("{base}/id"), errors);
            validate_identifier(&entity.layer_id, &format!("{base}/layer_id"), errors);
            validate_identifier(&entity.kind, &format!("{base}/entity_type"), errors);
            require_non_empty(&entity.label, &format!("{base}/label"), errors);
            require_reference(
                layer_ids,
                &entity.layer_id,
                &format!("{base}/layer_id"),
                "scene.reference.layer_unknown",
                errors,
            );
            validate_source_refs(
                &entity.source_refs,
                provenance_ids,
                &format!("{base}/source_refs"),
                errors,
            );
            if let Some(uncertainty) = &entity.uncertainty {
                validate_uncertainty(uncertainty, &format!("{base}/uncertainty"), errors);
            }
        }
    }

    fn validate_transitions(
        &self,
        layer_ids: &HashSet<&str>,
        entity_ids: &HashSet<&str>,
        provenance_ids: &HashSet<&str>,
        errors: &mut Vec<ValidationError>,
    ) {
        for (index, transition) in self.transitions.iter().enumerate() {
            let base = format!("/transitions/{index}");
            Self::validate_transition_shape(transition, &base, errors);
            require_reference(
                layer_ids,
                &transition.layer_id,
                &format!("{base}/layer_id"),
                "scene.reference.layer_unknown",
                errors,
            );
            require_reference(
                entity_ids,
                &transition.from_entity_id,
                &format!("{base}/from_entity_id"),
                "scene.reference.entity_unknown",
                errors,
            );
            require_reference(
                entity_ids,
                &transition.to_entity_id,
                &format!("{base}/to_entity_id"),
                "scene.reference.entity_unknown",
                errors,
            );
            validate_source_refs(
                &transition.source_refs,
                provenance_ids,
                &format!("{base}/source_refs"),
                errors,
            );
            validate_source_refs(
                &transition.geometry_mapping.source_refs,
                provenance_ids,
                &format!("{base}/geometry_mapping/source_refs"),
                errors,
            );
            self.validate_transition_roles(transition, &base, errors);
        }
    }

    fn validate_transition_shape(
        transition: &Transition,
        base: &str,
        errors: &mut Vec<ValidationError>,
    ) {
        validate_identifier(&transition.id, &format!("{base}/id"), errors);
        validate_identifier(&transition.layer_id, &format!("{base}/layer_id"), errors);
        validate_identifier(
            &transition.from_entity_id,
            &format!("{base}/from_entity_id"),
            errors,
        );
        validate_identifier(
            &transition.to_entity_id,
            &format!("{base}/to_entity_id"),
            errors,
        );
        validate_timestamp(
            &transition.timestamp_utc,
            &format!("{base}/timestamp_utc"),
            errors,
        );
        validate_identifier(&transition.trial_id, &format!("{base}/trial_id"), errors);
        validate_identifier(
            &transition.correlation_id,
            &format!("{base}/correlation_id"),
            errors,
        );
        validate_identifier(&transition.node_id, &format!("{base}/node_id"), errors);
        if let Some(device_id) = &transition.device_id {
            validate_identifier(device_id, &format!("{base}/device_id"), errors);
        }
        validate_identifier(
            &transition.geometry_mapping.method_id,
            &format!("{base}/geometry_mapping/method_id"),
            errors,
        );
        validate_exclusion_reasons(transition, base, errors);
        if let Some(uncertainty) = &transition.uncertainty {
            validate_uncertainty(uncertainty, &format!("{base}/uncertainty"), errors);
        }
    }

    fn validate_transition_roles(
        &self,
        transition: &Transition,
        base: &str,
        errors: &mut Vec<ValidationError>,
    ) {
        if transition.observation_role == ScientificRole::Measured
            && transition.interpolation != Interpolation::None
        {
            errors.push(ValidationError::new(
                "scene.transition.measured_interpolation",
                format!("{base}/interpolation"),
                "measured observations cannot be interpolated",
            ));
        }
        if self.coordinate_system.abstract_space
            && transition.observation_role == ScientificRole::Measured
            && transition.geometry_mapping.scientific_role == ScientificRole::Measured
        {
            errors.push(ValidationError::new(
                "scene.transition.abstract_measured_geometry",
                format!("{base}/geometry_mapping/scientific_role"),
                "measured observations in abstract coordinates require non-measured geometry",
            ));
        }
    }
}

fn unique_ids<'a, T>(
    values: &'a [T],
    id: impl Fn(&'a T) -> &'a str,
    kind: &str,
    base: &str,
    errors: &mut Vec<ValidationError>,
) -> HashSet<&'a str> {
    let mut ids = HashSet::new();
    for (index, value) in values.iter().enumerate() {
        let value_id = id(value);
        if !ids.insert(value_id) {
            errors.push(ValidationError::new(
                "scene.identifier.duplicate",
                format!("{base}/{index}/id"),
                format!("duplicate {kind} identifier '{value_id}'"),
            ));
        }
    }
    ids
}

fn validate_source_refs(
    references: &[SourceReference],
    provenance_ids: &HashSet<&str>,
    base: &str,
    errors: &mut Vec<ValidationError>,
) {
    if references.is_empty() {
        errors.push(ValidationError::new(
            "scene.source_refs.empty",
            base,
            "at least one record-level source reference is required",
        ));
    }
    let mut unique = HashSet::new();
    for (index, reference) in references.iter().enumerate() {
        let path = format!("{base}/{index}");
        if !unique.insert(reference) {
            errors.push(ValidationError::new(
                "scene.source_ref.duplicate",
                &path,
                "record-level source reference must be unique",
            ));
        }
        validate_identifier(
            &reference.artifact_id,
            &format!("{path}/artifact_id"),
            errors,
        );
        validate_identifier(&reference.run_id, &format!("{path}/run_id"), errors);
        validate_identifier(&reference.record_id, &format!("{path}/record_id"), errors);
        if let Some(event_id) = &reference.event_id {
            validate_identifier(event_id, &format!("{path}/event_id"), errors);
        }
        if let Some(partition) = &reference.partition {
            require_non_empty(partition, &format!("{path}/partition"), errors);
        }
        require_reference(
            provenance_ids,
            &reference.artifact_id,
            &format!("{path}/artifact_id"),
            "scene.reference.artifact_unknown",
            errors,
        );
    }
}

fn require_reference(
    known_ids: &HashSet<&str>,
    target_id: &str,
    path: &str,
    code: &'static str,
    errors: &mut Vec<ValidationError>,
) {
    if !known_ids.contains(target_id) {
        errors.push(ValidationError::new(
            code,
            path,
            format!("unknown reference '{target_id}'"),
        ));
    }
}

fn validate_uncertainty(uncertainty: &Uncertainty, base: &str, errors: &mut Vec<ValidationError>) {
    for (index, value) in uncertainty.standard_deviation.iter().enumerate() {
        if *value < 0.0 {
            errors.push(ValidationError::new(
                "scene.uncertainty.standard_deviation.negative",
                format!("{base}/standard_deviation/{index}"),
                "standard deviation components must be nonnegative",
            ));
        }
    }
    if !(uncertainty.confidence_level > 0.0 && uncertainty.confidence_level <= 1.0) {
        errors.push(ValidationError::new(
            "scene.uncertainty.confidence.invalid",
            format!("{base}/confidence_level"),
            "confidence level must be greater than zero and at most one",
        ));
    }
}

fn validate_exclusion_reasons(
    transition: &Transition,
    base: &str,
    errors: &mut Vec<ValidationError>,
) {
    let path = format!("{base}/exclusion_reasons");
    if transition.valid && !transition.exclusion_reasons.is_empty() {
        errors.push(ValidationError::new(
            "scene.transition.valid_with_exclusions",
            &path,
            "valid observation cannot have exclusion reasons",
        ));
    }
    if !transition.valid && transition.exclusion_reasons.is_empty() {
        errors.push(ValidationError::new(
            "scene.transition.invalid_without_exclusion",
            &path,
            "invalid observation requires at least one exclusion reason",
        ));
    }
    let mut unique = HashSet::new();
    for (index, reason) in transition.exclusion_reasons.iter().enumerate() {
        if !is_exclusion_reason(reason) {
            errors.push(ValidationError::new(
                "scene.transition.exclusion_reason.invalid",
                format!("{path}/{index}"),
                "exclusion reason must contain only lowercase letters, digits and underscores",
            ));
        }
        if !unique.insert(reason) {
            errors.push(ValidationError::new(
                "scene.transition.exclusion_reason.duplicate",
                format!("{path}/{index}"),
                "exclusion reasons must be unique",
            ));
        }
    }
}

fn validate_identifier(value: &str, path: &str, errors: &mut Vec<ValidationError>) {
    if !is_identifier(value) {
        errors.push(ValidationError::new(
            "scene.identifier.invalid",
            path,
            "identifier must match [A-Za-z0-9][A-Za-z0-9._:-]{0,127}",
        ));
    }
}

fn require_non_empty(value: &str, path: &str, errors: &mut Vec<ValidationError>) {
    if value.is_empty() {
        errors.push(ValidationError::new(
            "scene.string.empty",
            path,
            "string must not be empty",
        ));
    }
}

fn require_equal(
    value: &str,
    expected: &str,
    path: &str,
    code: &'static str,
    errors: &mut Vec<ValidationError>,
) {
    if value != expected {
        errors.push(ValidationError::new(
            code,
            path,
            format!("expected '{expected}'"),
        ));
    }
}

fn validate_timestamp(value: &str, path: &str, errors: &mut Vec<ValidationError>) {
    if OffsetDateTime::parse(value, &Rfc3339).is_err() {
        errors.push(ValidationError::new(
            "scene.timestamp.invalid",
            path,
            "timestamp must use RFC 3339 date-time syntax",
        ));
    }
}

fn is_identifier(value: &str) -> bool {
    let bytes = value.as_bytes();
    (1..=128).contains(&bytes.len())
        && bytes[0].is_ascii_alphanumeric()
        && bytes[1..]
            .iter()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(*byte, b'.' | b'_' | b':' | b'-'))
}

fn is_experiment_identifier(value: &str) -> bool {
    let bytes = value.as_bytes();
    bytes.len() >= 3 && bytes[0] == b'E' && bytes[1..].iter().all(u8::is_ascii_digit)
}

fn is_bundle_relative_path(value: &str) -> bool {
    !value.is_empty()
        && value.split('/').all(|segment| {
            !segment.is_empty()
                && segment != "."
                && segment != ".."
                && !segment.starts_with('.')
                && segment
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'.' | b'_' | b'-'))
        })
}

fn is_lowercase_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn is_exclusion_reason(value: &str) -> bool {
    !value.is_empty()
        && value
            .bytes()
            .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'_')
}

fn serde_path_to_json_path(path: &str) -> String {
    if path == "." {
        return "/".to_owned();
    }
    let mut pointer = String::from("/");
    let mut chars = path.trim_start_matches('.').chars().peekable();
    while let Some(character) = chars.next() {
        match character {
            '.' => pointer.push('/'),
            '[' => {
                pointer.push('/');
                for next in chars.by_ref() {
                    if next == ']' {
                        break;
                    }
                    pointer.push(next);
                }
            }
            _ => pointer.push(character),
        }
    }
    pointer
}

#[cfg(test)]
mod tests {
    use super::*;

    const E09_FIXTURE: &str =
        include_str!("../../contracts/v1/fixtures/visualization-scene-e09.json");

    #[test]
    fn produces_an_opaque_validated_scene() {
        let scene = parse_and_validate(E09_FIXTURE).expect("reference scene must be valid");

        assert_eq!(scene.scene_id(), "e09-reference-scene");
        assert_eq!(scene.experiment_id(), "E09");
        assert_eq!(scene.entity_count(), 4);
        assert_eq!(scene.transition_count(), 3);
    }

    #[test]
    fn builds_e09_render_state_with_scientific_cues_and_provenance() {
        let scene = parse_and_validate(E09_FIXTURE).expect("reference scene must be valid");
        let render = scene.render_scene();

        assert_eq!(render.entities.len(), 4);
        assert_eq!(render.transitions.len(), 3);
        assert!(render.coordinates.abstract_space);
        assert!(
            render
                .coordinates
                .warning
                .contains("not measured physical geometry")
        );
        assert!(
            render
                .entities
                .iter()
                .all(|entity| entity.role == VisualRole::Derived)
        );

        let invalid = render
            .transitions
            .iter()
            .find(|transition| !transition.valid)
            .expect("fixture must retain its excluded transition");
        assert_eq!(invalid.line_pattern, LinePattern::Dashed);
        assert_eq!(
            invalid.exclusion_reasons,
            vec!["missing_peer_event".to_owned()]
        );
        assert_eq!(invalid.observation_role, VisualRole::Measured);
        assert_eq!(invalid.geometry_role, VisualRole::Derived);
        assert_eq!(invalid.provenance[0].artifact_id, "event-node-b-000043");
        assert_eq!(invalid.geometry_provenance[0].artifact_id, "completed-abox");
        assert_eq!(
            invalid.geometry_provenance[0].record_id,
            "e09-abstract-layout-v1"
        );
    }

    #[test]
    fn selection_resolves_to_the_source_record() {
        let scene = parse_and_validate(E09_FIXTURE).expect("reference scene must be valid");
        let render = scene.render_scene();
        let selected = render
            .selection(&crate::RenderSelectionId::Transition(
                "trial-000043-node-b-invalid".to_owned(),
            ))
            .expect("transition must be selectable");

        assert!(!selected.valid);
        assert_eq!(
            selected.exclusion_reasons,
            vec!["missing_peer_event".to_owned()]
        );
        assert_eq!(selected.provenance[0].run_id, "reference-seed-7");
        assert_eq!(
            selected.provenance[0].record_id,
            "e09-reference-trial-000043-node-b"
        );
        assert_eq!(
            selected.geometry_provenance[0].artifact_id,
            "completed-abox"
        );
        assert_eq!(
            selected.geometry_provenance[0].record_id,
            "e09-abstract-layout-v1"
        );
    }

    #[test]
    fn preserves_hidden_layer_membership_in_render_state() {
        let mut changed: serde_json::Value =
            serde_json::from_str(E09_FIXTURE).expect("fixture must parse");
        changed["layers"][0]["visible_by_default"] = false.into();
        changed["layers"][1]["visible_by_default"] = false.into();

        let scene =
            parse_and_validate(&changed.to_string()).expect("hidden layers must be valid");
        let render = scene.render_scene();

        let state_layer = render
            .layers
            .iter()
            .find(|layer| layer.id == "state-space")
            .expect("state layer must be retained");
        let transition_layer = render
            .layers
            .iter()
            .find(|layer| layer.id == "event-geometry")
            .expect("transition layer must be retained");

        assert!(!state_layer.visible_by_default);
        assert!(!transition_layer.visible_by_default);
        assert!(
            render
                .entities
                .iter()
                .all(|entity| entity.layer_id == "state-space")
        );
        assert!(
            render
                .transitions
                .iter()
                .all(|transition| transition.layer_id == "event-geometry")
        );
    }

    #[test]
    fn preserves_coordinate_handedness_in_render_state() {
        let mut changed: serde_json::Value =
            serde_json::from_str(E09_FIXTURE).expect("fixture must parse");
        changed["coordinate_system"]["handedness"] = "left".into();

        let scene =
            parse_and_validate(&changed.to_string()).expect("left-handed scene must be valid");

        assert_eq!(
            scene.render_scene().coordinates.handedness,
            RenderHandedness::Left
        );
    }

    #[test]
    fn rejects_unknown_entity_reference_with_a_path() {
        let mut changed: serde_json::Value =
            serde_json::from_str(E09_FIXTURE).expect("fixture must parse");
        changed["transitions"][0]["to_entity_id"] = "missing-state".into();
        let report = parse_and_validate(&changed.to_string()).expect_err("scene must fail");

        assert!(report.errors.iter().any(|error| {
            error.code == "scene.reference.entity_unknown"
                && error.path == "/transitions/0/to_entity_id"
        }));
    }

    #[test]
    fn rejects_measured_geometry_in_abstract_coordinates() {
        let mut changed: serde_json::Value =
            serde_json::from_str(E09_FIXTURE).expect("fixture must parse");
        changed["transitions"][0]["geometry_mapping"]["scientific_role"] = "measured".into();
        let report = parse_and_validate(&changed.to_string()).expect_err("scene must fail");

        assert!(
            report
                .errors
                .iter()
                .any(|error| { error.code == "scene.transition.abstract_measured_geometry" })
        );
    }

    #[test]
    fn rejects_trailing_json_after_the_scene() {
        let changed = format!("{E09_FIXTURE}{{}}");
        let report = parse_and_validate(&changed).expect_err("concatenated JSON must fail");

        assert_eq!(report.errors[0].code, "scene.json.trailing_data");
        assert_eq!(report.errors[0].path, "/");
    }
}
