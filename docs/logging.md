# Logging

Som standard brukes Serilog i alle .NET applikasjoner. ([https://serilog.net/](https://serilog.net/) )

Verdt å lese : [What Are We Doing Wrong with Logging in C#?](https://mabroukmahdhi.medium.com/what-we-are-doing-wrong-with-logging-in-c-798dd7a4ec6d)

## nuget pakker

bruk nyeste versjon

```
<!-- Serilog pakker for standard oppsett -->
<PackageReference Include="Serilog.AspNetCore" Version="6.1.0" />
<PackageReference Include="Serilog.Enrichers.Environment" Version="2.2.0" />
<PackageReference Include="Bufdir.InternalResources" Version="6.1.18" />
<!-- Serilog pakker for seq oppsett -->
<PackageReference Include="Serilog.Sinks.Seq" Version="5.2.2" />
```

## BootstrapLogger

For å logge feil under oppstart av applikasjoner anbefales det å opprette serilog i to omganger ([https://github.com/serilog/serilog-aspnetcore#two-stage-initialization](https://github.com/serilog/serilog-aspnetcore#two-stage-initialization))

Eksempel:

```
bool isRunningInAzure = !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("WEBSITE\_SITE\_NAME"));

var bootstrapLogFile = isRunningInAzure
    ? Path.Combine(Environment.GetEnvironmentVariable("HOME")!, "LogFiles", "Application", "diagnostics-.txt")
    : Path.Combine("LogFiles", "startup-.txt");

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File(
        bootstrapLogFile,
        rollingInterval: RollingInterval.Day,
        fileSizeLimitBytes: 10 \* 1024 \* 1024,
        retainedFileCountLimit: 2,
        rollOnFileSizeLimit: true,
        shared: true,
        flushToDiskInterval: TimeSpan.FromSeconds(1))
    .CreateBootstrapLogger(); // 1. Sørger for at vi logger til console og fil under oppstart av applikasjon


try
{
    var builder = WebApplication.CreateBuilder(args);
     builder.Services.AddStuff();
    
    builder.Host.UseSerilog((ctx, cfg) =>
        cfg.ReadFrom.Configuration(ctx.Configuration)); // 2. Sørger for å lese konfigurasjon for betemme hvordan vi skal logge når applikasjon kjører

    Serilog.Debugging.SelfLog.Enable(Console.WriteLine);

    Log.Debug("Building and launching web application.");
    var app = builder.Build();
    app.UseStuff();
}
catch (Exception exception)
{
    Log.Fatal(exception, "An unhandled exception occured during bootstrapping");
}
finally
{
    Log.CloseAndFlush();
}

```

## **Konfigurasjon**

Eksempel på appsettings.json for å konfigurere serilog:

(for logging til fil så er standarden nå og logge til /Logfiles, så husk å gitignore denne mappen)

Overrides er nyttig å bruke så man ikke får altfor mye “støy” som ikke har med din kode å gjøre

Ikke bruk arrays til å konfigurere usings/sinks/enrichers, det vil gjøre det mer forvirrende når vi trenger å bytte konfigurasjon med enviroment-variabler

```
Serilog\_\_WriteTo\_\_2\_\_Args\_\_apiKey vs Serilog\_\_WriteTo\_\_SeqSink\_\_Args\_\_apiKey
```

```
 "Serilog": {
   "Properties": {
     "ApplicationName": "Applikasjonsnavn"
   },
   "MinimumLevel": {
     "Default": "Information",
     "Override": {
       "Microsoft.AspNetCore": "Warning",
       "Microsoft.IdentityModel": "Warning",
       "Microsoft.EntityFrameworkCore": "Information"
     }
   },
    "Using": { "CustomBufdirEncricher": "Bufdir.InternalResources" },
    "Enrich": {
      "LogContextEnricher": "FromLogContext",
      "MachineEnricher": "WithMachineName",
      "EnvironmentNameEnricher": "WithEnvironmentName",
      "CorrelationIdEnricher": {
        "Name": "WithCorrelationIdHeader",
        "Args": {
          "headerKey": "x-bufdirno-correlation-id"
        }
      }
    },
   "WriteTo": {
     "ConsoleSink": {
       "Name": "Console",
       "Args": {
         "theme": "Serilog.Sinks.SystemConsole.Themes.AnsiConsoleTheme::Code, Serilog.Sinks.Console",
         "outputTemplate": "\[{Timestamp:HH:mm:ss} {Level:u3}\] {SourceContext} {Message:lj}{NewLine}{Exception}"
       }
     },
     "FileSink": {
       "Name": "File",
       "Args": {
         "path": "LogFiles/AppNavn-.log",
         "outputTemplate": "\[{Timestamp:HH:mm:ss} {Level:u3}\] {SourceContext} {Message:lj}{NewLine}{Exception}",
         "rollingInterval": "Day",
         "shared": true,
         "flushToDiskInterval": "00:00:01"
       }
     },
      "SeqSink": {
        "Name": "Seq",
        "Args": {
          "serverUrl": "http://localhost:5341",
          "apiKey": ""
        }
      }
   }
 },
```

## CorrelationId

For interne ressurser så finnes det en egenutviklet enricher og interceptor som har som ansvar å legge til en header så vi kan logge på tvers av applikasjoner

*   `Bufdir.InternalResources.Enrichers`.`BufdirCorrelationIdEnricher`
    
    *   Brukes av enricher i config: `WithCorrelationIdHeader` ( pass på og få med `"Using": { "CustomBufdirEncricher": "Bufdir.InternalResources" }`)
        
*   `Bufdir.InternalResources.Interception`.`HeaderPropagationInterceptor`
    
    *   ```
        services
            .AddInternalResources(configuration)
            .AddScoped<IInternalResourceInterceptor, HeaderPropagationInterceptor>()
        ```
        

## Seq:

Url: [https://buflog.norwayeast.azurecontainer.io](https://buflog.norwayeast.azurecontainer.io)

Seq brukes i test/qa/prod for å ha et felles sted å lese alle loggene.

## Best practices:

```
//BAD
\_logger.LogInformation($"Logging interesting stuff {someThingInterstingToLog}");
//GOOD
\_logger.LogInformation("Logging interesting stuff {SomeThingInterstingToLog}", someThingInterstingToLog);
```
