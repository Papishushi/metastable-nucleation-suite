using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace Metastable.Platform.Cli;

internal sealed record CapabilityManifest(
    [property: JsonPropertyName("schema_version")] string SchemaVersion,
    [property: JsonPropertyName("server_version")] string ServerVersion,
    [property: JsonPropertyName("generated_at_utc")] DateTimeOffset GeneratedAtUtc,
    [property: JsonPropertyName("capabilities")] Capability[] Capabilities);

internal sealed record Capability(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("since_version")] string SinceVersion,
    [property: JsonPropertyName("deprecated_since_version")]
    string? DeprecatedSinceVersion,
    [property: JsonPropertyName("sunset_at_utc")] DateTimeOffset? SunsetAtUtc,
    [property: JsonPropertyName("replacement")] string? Replacement);

internal static class CapabilityGate
{
    private const string SupportedSchemaVersion = "1.0.0";

    internal static async Task<CapabilityManifest?> FetchAsync(
        HttpClient client,
        CancellationToken cancellationToken = default)
    {
        using var response = await client.GetAsync(
            "/v1/capabilities",
            cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            Console.Error.WriteLine(
                $"capability discovery failed with HTTP {(int)response.StatusCode}");
            return null;
        }

        var manifest = await response.Content.ReadFromJsonAsync<CapabilityManifest>(
            cancellationToken: cancellationToken);
        if (manifest is null || manifest.SchemaVersion != SupportedSchemaVersion)
        {
            Console.Error.WriteLine("unsupported or empty capability manifest");
            return null;
        }

        return manifest;
    }

    internal static bool Allows(CapabilityManifest manifest, string capabilityId)
    {
        var capability = manifest.Capabilities.FirstOrDefault(
            item => string.Equals(item.Id, capabilityId, StringComparison.Ordinal));
        if (capability is null)
        {
            Console.Error.WriteLine(
                $"server does not advertise required capability '{capabilityId}'");
            return false;
        }

        if (string.Equals(capability.Status, "active", StringComparison.Ordinal))
        {
            return true;
        }

        if (string.Equals(capability.Status, "deprecated", StringComparison.Ordinal))
        {
            var replacement = capability.Replacement is null
                ? string.Empty
                : $"; use '{capability.Replacement}' instead";
            var sunset = capability.SunsetAtUtc is null
                ? string.Empty
                : $"; sunset at {capability.SunsetAtUtc:O}";
            Console.Error.WriteLine(
                $"warning: capability '{capabilityId}' is deprecated{replacement}{sunset}");
            return true;
        }

        Console.Error.WriteLine(
            $"server advertised unsupported capability status '{capability.Status}'");
        return false;
    }
}
