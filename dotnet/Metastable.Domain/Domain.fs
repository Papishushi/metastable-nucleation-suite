namespace Metastable.Domain

open System

[<RequireQualifiedAccess>]
type ExperimentStatus =
    | Planned
    | Running
    | Completed
    | Failed of reason: string

[<CLIMutable>]
type ExperimentRequest = {
    SchemaVersion: string
    RequestId: Guid
    ExperimentId: string
    SubmittedAtUtc: DateTimeOffset
}

module Validation =
    let validateRequest request =
        if String.IsNullOrWhiteSpace request.SchemaVersion then
            Error "schema_version is required"
        elif String.IsNullOrWhiteSpace request.ExperimentId then
            Error "experiment_id is required"
        else
            Ok request
