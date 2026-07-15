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
                                pattern = @"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$",
                            },
                        },
                        additionalProperties = false,
                    },
                    ["Run"] = new
                    {
                        type = "object",
                        required = new[]
                        {
                            "schema_version",
                            "run_id",
                            "request_id",
                            "experiment_id",
                            "state",
                            "created_at_utc",
                            "updated_at_utc",
                            "transitions",
                        },
                        properties = new Dictionary<string, object>
                        {
                            ["schema_version"] = new Dictionary<string, object>
                            {
                                ["const"] = "1.0.0",
                            },
                            ["run_id"] = UuidSchema(),
                            ["request_id"] = UuidSchema(),
                            ["experiment_id"] = new
                            {
                                type = "string",
                                minLength = 1,
                                maxLength = 128,
                            },
                            ["state"] = RunStateSchema(),
                            ["created_at_utc"] = DateTimeSchema(),
                            ["updated_at_utc"] = DateTimeSchema(),
                            ["artifact"] = new
                            {
                                oneOf = new object[]
                                {
                                    ArtifactReferenceSchema(),
                                    new { type = "null" },
                                },
                            },
                            ["failure"] = new
                            {
                                type = new[] { "string", "null" },
                            },
                            ["transitions"] = new
                            {
                                type = "array",
                                minItems = 1,
                                items = new
                                {
                                    type = "object",
                                    required = new[] { "state", "at_utc" },
                                    properties = new Dictionary<string, object>
                                    {
                                        ["state"] = RunStateSchema(),
                                        ["at_utc"] = DateTimeSchema(),
                                        ["reason"] = new
                                        {
                                            type = new[] { "string", "null" },
                                        },
                                    },
                                    additionalProperties = false,
                                },
                            },
                        },
                        additionalProperties = false,
                    },
                    ["ArtifactIndex"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "run_id", "artifact", "indexed_at_utc" },
                        properties = new Dictionary<string, object>
                        {
                            ["schema_version"] = new Dictionary<string, object>
                            {
                                ["const"] = "1.0.0",
                            },
                            ["run_id"] = UuidSchema(),
                            ["artifact"] = ArtifactReferenceSchema(),
                            ["indexed_at_utc"] = DateTimeSchema(),
                        },
                        additionalProperties = false,
                    },
                    ["CapabilityManifest"] = new
                    {
                        type = "object",
                        required = new[] { "schema_version", "server_version", "generated_at_utc", "capabilities" },
                        properties = new Dictionary<string, object>
                        {
                            ["schema_version"] = new Dictionary<string, object>
                            {
                                ["const"] = "1.0.0",
                            },
                            ["server_version"] = VersionSchema(),
                            ["generated_at_utc"] = DateTimeSchema(),
                            ["capabilities"] = new
                            {
                                type = "array",
                                items = CapabilitySchema(),
                            },
                        },
                        additionalProperties = false,
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

    private static object UuidSchema() => new
    {
        type = "string",
        format = "uuid",
    };

    private static object DateTimeSchema() => new
    {
        type = "string",
        format = "date-time",
    };

    private static object RunStateSchema() => new
    {
        @enum = new[]
        {
            RunStates.Queued,
            RunStates.Running,
            RunStates.Succeeded,
            RunStates.Failed,
            RunStates.Cancelled,
            RunStates.RecoveryRequired,
        },
    };

    private static object ArtifactReferenceSchema() => new
    {
        type = "object",
        required = new[] { "artifact_id", "uri", "media_type", "response_sha256" },
        properties = new Dictionary<string, object>
        {
            ["artifact_id"] = new
            {
                type = "string",
                minLength = 1,
                maxLength = 64,
            },
            ["uri"] = new
            {
                type = "string",
                minLength = 1,
            },
            ["media_type"] = new Dictionary<string, object>
            {
                ["const"] = "application/json",
            },
            ["response_sha256"] = new
            {
                type = "string",
                pattern = "^[0-9a-f]{64}$",
            },
        },
        additionalProperties = false,
    };

    private static object VersionSchema() => new
    {
        type = "string",
        pattern = "^[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$",
    };

    private static object CapabilitySchema() => new
    {
        type = "object",
        required = new[] { "id", "status", "since_version" },
        properties = new Dictionary<string, object>
        {
            ["id"] = CapabilityIdSchema(),
            ["status"] = new
            {
                @enum = new[] { "active", "deprecated" },
            },
            ["since_version"] = VersionSchema(),
            ["deprecated_since_version"] = VersionSchema(),
            ["sunset_at_utc"] = DateTimeSchema(),
            ["replacement"] = CapabilityIdSchema(),
        },
        allOf = new object[]
        {
            new Dictionary<string, object>
            {
                ["if"] = new
                {
                    properties = new Dictionary<string, object>
                    {
                        ["status"] = new Dictionary<string, object>
                        {
                            ["const"] = "deprecated",
                        },
                    },
                    required = new[] { "status" },
                },
                ["then"] = new
                {
                    required = new[] { "deprecated_since_version" },
                },
            },
        },
        additionalProperties = false,
    };

    private static object CapabilityIdSchema() => new
    {
        type = "string",
        pattern = "^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*\\.v[1-9][0-9]*$",
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
