using System.Net.Http.Headers;
using System.Text.Json;
using Metastable.Domain;
using Metastable.Platform.Cli;

const string Version = "0.1.0";
const string ExecuteCapability = "experiments.execute.v1";

if (args is ["--version"])
{
    Console.WriteLine($"metastable-platform {Version}");
    return 0;
}

if (args is ["--self-test"])
{
    if (!Validation.selfTest())
    {
        Console.Error.WriteLine("domain self-test failed");
        return 1;
    }

    Console.WriteLine("self-test: ok");
    return 0;
}

var workerUrl = Environment.GetEnvironmentVariable("METASTABLE_SCIENTIFIC_WORKER_URL")
    ?? "http://127.0.0.1:8081";
using var client = new HttpClient
{
    BaseAddress = new Uri(workerUrl),
    Timeout = TimeSpan.FromSeconds(30),
};

if (args is ["capabilities"])
{
    var manifest = await CapabilityGate.FetchAsync(client);
    if (manifest is null)
    {
        return 3;
    }

    Console.WriteLine(JsonSerializer.Serialize(
        manifest,
        new JsonSerializerOptions { WriteIndented = true }));
    return 0;
}

if (args is ["execute", var experimentId])
{
    var manifest = await CapabilityGate.FetchAsync(client);
    if (manifest is null || !CapabilityGate.Allows(manifest, ExecuteCapability))
    {
        return 3;
    }

    var request = new Dictionary<string, string>
    {
        ["schema_version"] = "1.0.0",
        ["request_id"] = Guid.NewGuid().ToString("D"),
        ["experiment_id"] = experimentId,
        ["submitted_at_utc"] = DateTimeOffset.UtcNow.ToString("O"),
    };
    var payload = JsonSerializer.SerializeToUtf8Bytes(request);
    using var content = new ByteArrayContent(payload);
    content.Headers.ContentType = new MediaTypeHeaderValue("application/json")
    {
        CharSet = "utf-8",
    };

    using var response = await client.PostAsync("/v1/experiments", content);
    var responseBody = await response.Content.ReadAsStringAsync();
    Console.WriteLine(responseBody);
    return response.IsSuccessStatusCode ? 0 : 1;
}

Console.Error.WriteLine(
    "Usage: metastable-platform --version | --self-test | capabilities | execute <experiment-id>");
return 2;
