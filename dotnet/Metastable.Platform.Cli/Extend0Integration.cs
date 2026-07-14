using System.Reflection;
using System.Text.Json.Serialization;
using Extend0.Metadata;

namespace Metastable.Platform.Cli;

internal sealed record Extend0Status(
    [property: JsonPropertyName("package_version")] string PackageVersion,
    [property: JsonPropertyName("metadb_ready")] bool MetaDbReady);

internal static class Extend0Integration
{
    internal static Extend0Status Diagnose()
    {
        var manager = new MetaDBManager(logger: null);
        return new Extend0Status(GetPackageVersion(), manager is not null);
    }

    internal static bool SelfTest()
    {
        return Diagnose().MetaDbReady;
    }

    private static string GetPackageVersion()
    {
        var assembly = typeof(MetaDB).Assembly;
        return assembly
            .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
            .InformationalVersion
            ?? assembly.GetName().Version?.ToString()
            ?? "unknown";
    }
}
