using System.Reflection;
using System.Text.Json.Serialization;
using Extend0.Metadata.Schema;

namespace Metastable.Platform.Cli;

internal sealed record Extend0Status(
    [property: JsonPropertyName("package_version")] string PackageVersion,
    [property: JsonPropertyName("metadata_contract_ready")] bool MetadataContractReady);

internal static class Extend0Integration
{
    internal static Extend0Status Diagnose()
    {
        var metadataContractReady = string.Equals(
            typeof(TableSpec).FullName,
            "Extend0.Metadata.Schema.TableSpec",
            StringComparison.Ordinal);
        return new Extend0Status(GetPackageVersion(), metadataContractReady);
    }

    internal static bool SelfTest()
    {
        return Diagnose().MetadataContractReady;
    }

    private static string GetPackageVersion()
    {
        var assembly = typeof(TableSpec).Assembly;
        return assembly
            .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
            .InformationalVersion
            ?? assembly.GetName().Version?.ToString()
            ?? "unknown";
    }
}
