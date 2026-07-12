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
    let validateRequest (request: ExperimentRequest) =
        if String.IsNullOrWhiteSpace request.SchemaVersion then
            Error "schema_version is required"
        elif String.IsNullOrWhiteSpace request.ExperimentId then
            Error "experiment_id is required"
        else
            Ok request

    let selfTest () =
        let request = {
            SchemaVersion = "1.0.0"
            RequestId = Guid.Parse "11111111-1111-1111-1111-111111111111"
            ExperimentId = "self-test"
            SubmittedAtUtc = DateTimeOffset.UnixEpoch
        }
        validateRequest request |> Result.isOk
