using System.Reflection;

namespace Metastable.ControlPlane;

internal static class ControlPlaneOpenApi
{
    internal static object Create()
    {
        var version = Assembly.GetExecutingAssembly()
            .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?
            .InformationalVersion
            ?? "0.0.0+unknown";
        return new
        {
            openapi = "3.1.0",
            info = new
            {
                title = "Metastable Nucleation Suite control plane",
                version,
            },
            paths = new Dictionary<string, object>
            {
                ["/v1/capabilities"] = Operation("get", "Discover server capabilities", "CapabilityManifest"),
                ["/v1/runs"] = Operation("post", "Submit an idempotent run", "Run"),
                ["/v1/runs/{runId}"] = Operation("get", "Read durable run state", "Run"),
                ["/v1/runs/{runId}/cancel"] = Operation("post", "Cancel a run", "Run"),
                ["/v1/runs/{runId}/artifacts/{artifactId}"] = Operation("get", "Read artifact metadata", "ArtifactIndex"),
            },
            components = new
            {
                schemas = new Dictionary<string, object>
                {
                    ["ExperimentRequest"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "request_id", "experiment_id", "submitted_at_utc" },
                        additionalProperties = false,
                    },
                    ["Run"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "run_id", "request_id", "experiment_id", "state", "transitions" },
                    },
                    ["ArtifactIndex"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "run_id", "artifact", "indexed_at_utc" },
                    },
                    ["CapabilityManifest"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "server_version", "generated_at_utc", "capabilities" },
                    },
                },
            },
        };
    }

    private static Dictionary<string, object> Operation(
        string method,
        string summary,
        string schema)
    {
        return new Dictionary<string, object>
        {
            [method] = new
            {
                summary,
                responses = new Dictionary<string, object>
                {
                    ["200"] = new
                    {
                        description = "Success",
                        content = new Dictionary<string, object>
                        {
                            ["application/json"] = new
                            {
                                schema = new Dictionary<string, string>
                                {
                                    ["$ref"] = $"#/components/schemas/{schema}",
                                },
                            },
                        },
                    },
                },
            },
        };
    }
}
