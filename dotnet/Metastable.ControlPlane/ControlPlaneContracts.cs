using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace Metastable.ControlPlane;

internal static class RunStates
{
    internal const string Queued = "queued";
    internal const string Running = "running";
    internal const string Succeeded = "succeeded";
    internal const string Failed = "failed";
    internal const string Cancelled = "cancelled";
    internal const string RecoveryRequired = "recovery_required";

    internal static bool IsTerminal(string state) =>
        state is Succeeded or Failed or Cancelled;
}

[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
internal sealed partial record ExperimentRequest(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("experiment_id")] string ExperimentId,
    [property: JsonPropertyName("submitted_at_utc")] string SubmittedAtUtc)
{
    internal bool IsValid()
    {
        return SchemaVersion == "1.0.0"
            && Guid.TryParseExact(RequestId, "D", out _)
            && !string.IsNullOrWhiteSpace(ExperimentId)
            && ExperimentId.Length <= 128
            && !string.IsNullOrWhiteSpace(SubmittedAtUtc)
            && Rfc3339DateTime().IsMatch(SubmittedAtUtc)
            && DateTimeOffset.TryParse(
                SubmittedAtUtc.ToUpperInvariant(),
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.RoundtripKind,
                out var submitted)
            && submitted.Offset >= TimeSpan.FromHours(-14)
            && submitted.Offset <= TimeSpan.FromHours(14);
    }

    [GeneratedRegex(
        @"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$",
        RegexOptions.CultureInvariant)]
    private static partial Regex Rfc3339DateTime();
}

internal sealed record RunTransition(
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("at_utc")] DateTimeOffset AtUtc,
    [property: JsonPropertyName("reason")] string? Reason);

internal sealed record ArtifactReference(
    [property: JsonPropertyName("artifact_id")] string ArtifactId,
    [property: JsonPropertyName("uri")] string Uri,
    [property: JsonPropertyName("media_type")] string MediaType,
    [property: JsonPropertyName("response_sha256")] string ResponseSha256);

internal sealed record RunRecord(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("run_id")] Guid RunId,
    [property: JsonPropertyName("idempotency_key")] string IdempotencyKey,
    [property: JsonPropertyName("request")] ExperimentRequest Request,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("created_at_utc")] DateTimeOffset CreatedAtUtc,
    [property: JsonPropertyName("updated_at_utc")] DateTimeOffset UpdatedAtUtc,
    [property: JsonPropertyName("artifact")] ArtifactReference? Artifact,
    [property: JsonPropertyName("failure")] string? Failure,
    [property: JsonPropertyName("transitions")] IReadOnlyList<RunTransition> Transitions)
{
    internal RunResponse ToResponse() => new(
        SchemaVersion,
        RunId,
        Request.RequestId,
        Request.ExperimentId,
        State,
        CreatedAtUtc,
        UpdatedAtUtc,
        Artifact,
        Failure,
        Transitions);
}

internal sealed record RunResponse(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("run_id")] Guid RunId,
    [property: JsonPropertyName("request_id")] string RequestId,
    [property: JsonPropertyName("experiment_id")] string ExperimentId,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("created_at_utc")] DateTimeOffset CreatedAtUtc,
    [property: JsonPropertyName("updated_at_utc")] DateTimeOffset UpdatedAtUtc,
    [property: JsonPropertyName("artifact")] ArtifactReference? Artifact,
    [property: JsonPropertyName("failure")] string? Failure,
    [property: JsonPropertyName("transitions")] IReadOnlyList<RunTransition> Transitions);

internal sealed record ArtifactIndexRecord(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("run_id")] Guid RunId,
    [property: JsonPropertyName("artifact")] ArtifactReference Artifact,
    [property: JsonPropertyName("indexed_at_utc")] DateTimeOffset IndexedAtUtc);

internal sealed record CreateRunResult(
    RunRecord Run,
    bool Created,
    bool Conflict);
