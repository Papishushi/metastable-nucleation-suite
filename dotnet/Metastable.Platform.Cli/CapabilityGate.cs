using System.Globalization;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace Metastable.Platform.Cli;

internal sealed record CapabilityManifest(
    [property: JsonPropertyName("schema_version")] string? SchemaVersion,
    [property: JsonPropertyName("server_version")] string? ServerVersion,
    [property: JsonPropertyName("generated_at_utc")] DateTimeOffset? GeneratedAtUtc,
    [property: JsonPropertyName("capabilities")] Capability[]? Capabilities);

internal sealed record Capability(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("since_version")] string? SinceVersion,
    [property: JsonPropertyName("deprecated_since_version")]
    string? DeprecatedSinceVersion,
    [property: JsonPropertyName("sunset_at_utc")] DateTimeOffset? SunsetAtUtc,
    [property: JsonPropertyName("replacement")] string? Replacement);

internal enum CapabilityDisposition
{
    Unsupported,
    Active,
    Deprecated,
}

internal static partial class CapabilityGate
{
    private const string SupportedSchemaVersion = "1.0.0";

    [GeneratedRegex(
        "^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*\\.v[1-9][0-9]*$",
        RegexOptions.CultureInvariant)]
    private static partial Regex CapabilityIdPattern();

    internal static async Task<CapabilityManifest?> FetchAsync(
        HttpClient client,
        CancellationToken cancellationToken = default)
    {
        try
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
            if (manifest is null || !ValidateManifest(manifest))
            {
                Console.Error.WriteLine("invalid or unsupported capability manifest");
                return null;
            }

            return manifest;
        }
        catch (HttpRequestException exception)
        {
            Console.Error.WriteLine(
                $"capability discovery request failed: {exception.Message}");
            return null;
        }
        catch (JsonException exception)
        {
            Console.Error.WriteLine(
                $"capability manifest JSON is invalid: {exception.Message}");
            return null;
        }
        catch (NotSupportedException exception)
        {
            Console.Error.WriteLine(
                $"capability manifest format is unsupported: {exception.Message}");
            return null;
        }
        catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            Console.Error.WriteLine("capability discovery timed out");
            return null;
        }
    }

    internal static bool ValidateManifest(CapabilityManifest manifest)
    {
        if (
            !string.Equals(
                manifest.SchemaVersion,
                SupportedSchemaVersion,
                StringComparison.Ordinal)
            || string.IsNullOrWhiteSpace(manifest.ServerVersion)
            || manifest.GeneratedAtUtc is null
            || manifest.Capabilities is null)
        {
            return false;
        }

        var identifiers = new HashSet<string>(StringComparer.Ordinal);
        foreach (var capability in manifest.Capabilities)
        {
            if (
                capability.Id is null
                || !CapabilityIdPattern().IsMatch(capability.Id)
                || !identifiers.Add(capability.Id)
                || string.IsNullOrWhiteSpace(capability.SinceVersion))
            {
                return false;
            }

            if (string.Equals(capability.Status, "active", StringComparison.Ordinal))
            {
                continue;
            }

            if (
                string.Equals(capability.Status, "deprecated", StringComparison.Ordinal)
                && !string.IsNullOrWhiteSpace(capability.DeprecatedSinceVersion)
                && (
                    capability.Replacement is null
                    || CapabilityIdPattern().IsMatch(capability.Replacement)))
            {
                continue;
            }

            return false;
        }

        return true;
    }

    internal static CapabilityDisposition Evaluate(
        CapabilityManifest manifest,
        string capabilityId)
    {
        var capability = manifest.Capabilities?.FirstOrDefault(
            item => string.Equals(item.Id, capabilityId, StringComparison.Ordinal));
        if (capability is null)
        {
            return CapabilityDisposition.Unsupported;
        }

        return capability.Status switch
        {
            "active" => CapabilityDisposition.Active,
            "deprecated" => CapabilityDisposition.Deprecated,
            _ => CapabilityDisposition.Unsupported,
        };
    }

    internal static bool Allows(CapabilityManifest manifest, string capabilityId)
    {
        var disposition = Evaluate(manifest, capabilityId);
        if (disposition == CapabilityDisposition.Active)
        {
            return true;
        }

        if (disposition == CapabilityDisposition.Unsupported)
        {
            Console.Error.WriteLine(
                $"server does not advertise active or deprecated capability '{capabilityId}'");
            return false;
        }

        var capability = manifest.Capabilities!.Single(
            item => string.Equals(item.Id, capabilityId, StringComparison.Ordinal));
        var replacement = capability.Replacement is null
            ? string.Empty
            : $"; use '{capability.Replacement}' instead";
        var sunset = capability.SunsetAtUtc is null
            ? string.Empty
            : $"; sunset at {capability.SunsetAtUtc.Value.ToString("O", CultureInfo.InvariantCulture)}";
        Console.Error.WriteLine(
            $"warning: capability '{capabilityId}' is deprecated{replacement}{sunset}");
        return true;
    }

    internal static bool SelfTest()
    {
        var manifest = new CapabilityManifest(
            SupportedSchemaVersion,
            "0.1.0",
            DateTimeOffset.UnixEpoch,
            [
                new Capability(
                    "experiments.execute.v1",
                    "active",
                    "0.1.0",
                    null,
                    null,
                    null),
                new Capability(
                    "experiments.plan.v1",
                    "deprecated",
                    "0.1.0",
                    "0.2.0",
                    DateTimeOffset.UnixEpoch.AddYears(1),
                    "experiments.execute.v1"),
            ]);

        return ValidateManifest(manifest)
            && Evaluate(manifest, "experiments.execute.v1")
                == CapabilityDisposition.Active
            && Evaluate(manifest, "experiments.plan.v1")
                == CapabilityDisposition.Deprecated
            && Evaluate(manifest, "experiments.missing.v1")
                == CapabilityDisposition.Unsupported;
    }
}
