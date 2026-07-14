//! Deterministic render state derived exclusively from a validated scene.

/// How a rendered element relates to the scientific source data.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum VisualRole {
    Measured,
    Derived,
    Inferred,
    Illustrative,
}

/// A non-colour cue applied to rendered transition geometry.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum LinePattern {
    Solid,
    Dashed,
}

/// A stable reference back to one source record.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ProvenanceRef {
    pub artifact_id: String,
    pub run_id: String,
    pub record_id: String,
    pub event_id: Option<String>,
    pub partition: Option<String>,
    pub row_group: Option<u64>,
}

/// Uncertainty retained for inspection and later GPU encodings.
#[derive(Clone, Debug, PartialEq)]
pub struct RenderUncertainty {
    pub standard_deviation: [f64; 3],
    pub confidence_level: f64,
}

/// One validated scene entity ready for GPU buffer construction.
#[derive(Clone, Debug, PartialEq)]
pub struct RenderEntity {
    pub id: String,
    pub label: String,
    pub position: [f64; 3],
    pub role: VisualRole,
    pub provenance: Vec<ProvenanceRef>,
    pub uncertainty: Option<RenderUncertainty>,
}

/// One validated transition ready for GPU buffer construction.
#[derive(Clone, Debug, PartialEq)]
pub struct RenderTransition {
    pub id: String,
    pub from_entity: usize,
    pub to_entity: usize,
    pub observation_role: VisualRole,
    pub geometry_role: VisualRole,
    pub valid: bool,
    pub line_pattern: LinePattern,
    pub exclusion_reasons: Vec<String>,
    pub provenance: Vec<ProvenanceRef>,
    pub uncertainty: Option<RenderUncertainty>,
}

/// Axis metadata that must remain visible beside abstract geometry.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RenderAxis {
    pub label: String,
    pub unit: String,
}

/// Coordinate metadata retained by every rendered frame.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct RenderCoordinates {
    pub frame_id: String,
    pub abstract_space: bool,
    pub warning: String,
    pub axes: [RenderAxis; 3],
}

/// Immutable, deterministic state consumed by the upcoming GPU renderer.
#[derive(Clone, Debug, PartialEq)]
pub struct RenderScene {
    pub scene_id: String,
    pub coordinates: RenderCoordinates,
    pub entities: Vec<RenderEntity>,
    pub transitions: Vec<RenderTransition>,
}

/// Identifier used by pointer and keyboard selection.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RenderSelectionId {
    Entity(String),
    Transition(String),
}

/// Inspection data returned without exposing internal scene models.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SelectionDetails {
    pub id: RenderSelectionId,
    pub label: String,
    pub valid: bool,
    pub exclusion_reasons: Vec<String>,
    pub provenance: Vec<ProvenanceRef>,
}

impl RenderScene {
    /// Resolve a rendered identifier to record-level provenance.
    #[must_use]
    pub fn selection(&self, id: &RenderSelectionId) -> Option<SelectionDetails> {
        match id {
            RenderSelectionId::Entity(target) => self
                .entities
                .iter()
                .find(|entity| entity.id == *target)
                .map(|entity| SelectionDetails {
                    id: id.clone(),
                    label: entity.label.clone(),
                    valid: true,
                    exclusion_reasons: Vec::new(),
                    provenance: entity.provenance.clone(),
                }),
            RenderSelectionId::Transition(target) => self
                .transitions
                .iter()
                .find(|transition| transition.id == *target)
                .map(|transition| SelectionDetails {
                    id: id.clone(),
                    label: transition.id.clone(),
                    valid: transition.valid,
                    exclusion_reasons: transition.exclusion_reasons.clone(),
                    provenance: transition.provenance.clone(),
                }),
        }
    }
}

/// Camera input expressed independently of browser events.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum CameraAction {
    Orbit {
        yaw_delta: f64,
        pitch_delta: f64,
    },
    Pan {
        x_delta: f64,
        y_delta: f64,
    },
    Zoom {
        factor: f64,
    },
    Focus {
        position: [f64; 3],
    },
    Reset,
}

/// Deterministic orbit-camera state shared by native and browser builds.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CameraState {
    pub target: [f64; 3],
    pub yaw: f64,
    pub pitch: f64,
    pub distance: f64,
    initial: CameraSnapshot,
}

#[derive(Clone, Copy, Debug, PartialEq)]
struct CameraSnapshot {
    target: [f64; 3],
    yaw: f64,
    pitch: f64,
    distance: f64,
}

impl CameraState {
    const MIN_DISTANCE: f64 = 0.05;
    const MAX_PITCH: f64 = 1.553_343_034_274_953_2;

    /// Create a camera centered on the renderable entity bounds.
    #[must_use]
    pub fn for_scene(scene: &RenderScene) -> Self {
        let (target, distance) = scene_bounds(scene);
        let initial = CameraSnapshot {
            target,
            yaw: 0.0,
            pitch: 0.0,
            distance,
        };
        Self {
            target,
            yaw: initial.yaw,
            pitch: initial.pitch,
            distance,
            initial,
        }
    }

    /// Apply one normalized interaction action.
    pub fn apply(&mut self, action: CameraAction) {
        match action {
            CameraAction::Orbit {
                yaw_delta,
                pitch_delta,
            } => {
                self.yaw += yaw_delta;
                self.pitch = (self.pitch + pitch_delta).clamp(-Self::MAX_PITCH, Self::MAX_PITCH);
            }
            CameraAction::Pan { x_delta, y_delta } => {
                self.target[0] += x_delta;
                self.target[1] += y_delta;
            }
            CameraAction::Zoom { factor } if factor.is_finite() && factor > 0.0 => {
                self.distance = (self.distance * factor).max(Self::MIN_DISTANCE);
            }
            CameraAction::Focus { position } => self.target = position,
            CameraAction::Reset => {
                self.target = self.initial.target;
                self.yaw = self.initial.yaw;
                self.pitch = self.initial.pitch;
                self.distance = self.initial.distance;
            }
            CameraAction::Zoom { .. } => {}
        }
    }
}

fn scene_bounds(scene: &RenderScene) -> ([f64; 3], f64) {
    let Some(first) = scene.entities.first() else {
        return ([0.0; 3], 1.0);
    };
    let mut minimum = first.position;
    let mut maximum = first.position;
    for entity in &scene.entities[1..] {
        for (axis, value) in entity.position.iter().copied().enumerate() {
            minimum[axis] = minimum[axis].min(value);
            maximum[axis] = maximum[axis].max(value);
        }
    }
    let target = [
        (minimum[0] + maximum[0]) / 2.0,
        (minimum[1] + maximum[1]) / 2.0,
        (minimum[2] + maximum[2]) / 2.0,
    ];
    let diagonal = ((maximum[0] - minimum[0]).powi(2)
        + (maximum[1] - minimum[1]).powi(2)
        + (maximum[2] - minimum[2]).powi(2))
    .sqrt();
    (target, diagonal.max(1.0) * 1.5)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_scene() -> RenderScene {
        RenderScene {
            scene_id: "test".to_owned(),
            coordinates: RenderCoordinates {
                frame_id: "test-frame".to_owned(),
                abstract_space: true,
                warning: "abstract".to_owned(),
                axes: [
                    RenderAxis {
                        label: "x".to_owned(),
                        unit: "1".to_owned(),
                    },
                    RenderAxis {
                        label: "y".to_owned(),
                        unit: "1".to_owned(),
                    },
                    RenderAxis {
                        label: "z".to_owned(),
                        unit: "1".to_owned(),
                    },
                ],
            },
            entities: vec![
                RenderEntity {
                    id: "a".to_owned(),
                    label: "A".to_owned(),
                    position: [-1.0, -2.0, 0.0],
                    role: VisualRole::Derived,
                    provenance: Vec::new(),
                    uncertainty: None,
                },
                RenderEntity {
                    id: "b".to_owned(),
                    label: "B".to_owned(),
                    position: [1.0, 2.0, 0.0],
                    role: VisualRole::Derived,
                    provenance: Vec::new(),
                    uncertainty: None,
                },
            ],
            transitions: Vec::new(),
        }
    }

    #[test]
    fn camera_actions_are_deterministic_and_resettable() {
        let mut camera = CameraState::for_scene(&test_scene());
        let initial = camera;

        camera.apply(CameraAction::Orbit {
            yaw_delta: 0.5,
            pitch_delta: 10.0,
        });
        camera.apply(CameraAction::Pan {
            x_delta: 2.0,
            y_delta: -1.0,
        });
        camera.apply(CameraAction::Zoom { factor: 0.5 });
        camera.apply(CameraAction::Focus {
            position: [4.0, 5.0, 6.0],
        });

        assert!(camera
            .target
            .iter()
            .zip([4.0, 5.0, 6.0])
            .all(|(actual, expected)| (*actual - expected).abs() < f64::EPSILON));
        assert!((camera.yaw - 0.5).abs() < f64::EPSILON);
        assert!((camera.pitch - CameraState::MAX_PITCH).abs() < f64::EPSILON);
        assert!(camera.distance < initial.distance);

        camera.apply(CameraAction::Reset);
        assert_eq!(camera, initial);
    }

    #[test]
    fn invalid_zoom_is_ignored() {
        let mut camera = CameraState::for_scene(&test_scene());
        let distance = camera.distance;

        camera.apply(CameraAction::Zoom { factor: 0.0 });
        camera.apply(CameraAction::Zoom { factor: f64::NAN });

        assert!((camera.distance - distance).abs() < f64::EPSILON);
    }
}
