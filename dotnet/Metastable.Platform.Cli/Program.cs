using System.Net.Http.Json;
using Metastable.Domain;

const string Version = "0.1.0";

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

if (args is ["execute", var experimentId])
{
    var workerUrl = Environment.GetEnvironmentVariable("METASTABLE_SCIENTIFIC_WORKER_URL")
        ?? "http://127.0.0.1:8081";
    using var client = new HttpClient { BaseAddress = new Uri(workerUrl) };
    var request = new
    {
        schema_version = "1.0.0",
        request_id = Guid.NewGuid(),
        experiment_id = experimentId,
        submitted_at_utc = DateTimeOffset.UtcNow,
    };
    using var response = await client.PostAsJsonAsync("/v1/experiments", request);
    Console.WriteLine(await response.Content.ReadAsStringAsync());
    return response.IsSuccessStatusCode ? 0 : 1;
}

Console.Error.WriteLine("Usage: metastable-platform --version | --self-test | execute <experiment-id>");
return 2;
