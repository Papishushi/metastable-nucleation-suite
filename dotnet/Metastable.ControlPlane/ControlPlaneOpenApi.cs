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
                ["/v1/runs"] = Operation(
                    "post",
                    "Submit an idempotent run",
                    "Run",
                    requestSchema: "ExperimentRequest",
                    parameters: [IdempotencyKeyParameter()],
                    includeCreatedResponse: true),
                ["/v1/runs/{runId}"] = Operation(
                    "get",
                    "Read durable run state",
                    "Run",
                    parameters: [PathParameter("runId", "uuid")]),
                ["/v1/runs/{runId}/cancel"] = Operation(
                    "post",
                    "Cancel a run",
                    "Run",
                    parameters: [PathParameter("runId", "uuid")]),
                ["/v1/runs/{runId}/artifacts/{artifactId}"] = Operation(
                    "get",
                    "Read artifact metadata",
                    "ArtifactIndex",
                    parameters:
                    [
                        PathParameter("runId", "uuid"),
                        PathParameter("artifactId"),
                    ]),
            },
            components = new
            {
                schemas = new Dictionary<string, object>
                {
                    ["ExperimentRequest"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "request_id", "experiment_id", "submitted_at_utc" },
                        properties = new Dictionary<string, object>
                        {
                            ["schema_version"] = new Dictionary<string, object>
                            {
                                ["const"] = "1.0.0",
                            },
                            ["request_id"] = new
                            {
                                type = "string",
                                format = "uuid",
                            },
                            ["experiment_id"] = new
                            {
                                type = "string",
                                minLength = 1,
                                maxLength = 128,
                            },
                            ["submitted_at_utc"] = new
                            {
                                type = "string",
                                format = "date-time",
                            },
                        },
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
        string schema,
        string? requestSchema = null,
        object[]? parameters = null,
        bool includeCreatedResponse = false)
    {
        var responses = new Dictionary<string, object>
        {
            ["200"] = JsonResponse("Success", schema),
        };
        if (includeCreatedResponse)
        {
            responses["201"] = JsonResponse("Created", schema);
        }

        var operation = new Dictionary<string, object>
        {
            ["summary"] = summary,
            ["parameters"] = parameters ?? [],
            ["responses"] = responses,
        };

        if (requestSchema is not null)
        {
            operation["requestBody"] = new
            {
                required = true,
                content = new Dictionary<string, object>
                {
                    ["application/json"] = new
                    {
                        schema = new Dictionary<string, string>
                        {
                            ["$ref"] = $"#/components/schemas/{requestSchema}",
                        },
                    },
                },
            };
        }

        return new Dictionary<string, object>
        {
            [method] = operation,
        };
    }

    private static object JsonResponse(string description, string schema) => new
    {
        description,
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
    };

    private static object PathParameter(string name, string? format = null)
    {
        var schema = new Dictionary<string, object>
        {
            ["type"] = "string",
        };
        if (format is not null)
        {
            schema["format"] = format;
        }

        return new
        {
            name,
            @in = "path",
            required = true,
            schema,
        };
    }

    private static object IdempotencyKeyParameter() => new
    {
        name = "Idempotency-Key",
        @in = "header",
        required = true,
        schema = new
        {
            type = "string",
            minLength = 1,
            maxLength = 128,
            pattern = "^[!-~]+$",
        },
    };
}
