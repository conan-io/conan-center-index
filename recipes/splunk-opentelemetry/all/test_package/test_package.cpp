#include <splunk/opentelemetry.h>
#include <opentelemetry/sdk/resource/resource.h>

int main(int argc, char** argv) {
  splunk::OpenTelemetryOptions otelOptions = splunk::OpenTelemetryOptions()
                                               .WithServiceName("my-service")
                                               .WithServiceVersion("1.0")
                                               .WithDeploymentEnvironment("test");
  auto provider = splunk::InitOpentelemetry(otelOptions);

  auto tracer = opentelemetry::trace::Provider::GetTracerProvider()->GetTracer("simple");

  opentelemetry::trace::StartSpanOptions startOptions;
  startOptions.kind = opentelemetry::trace::SpanKind::kServer;

  opentelemetry::nostd::shared_ptr<opentelemetry::trace::Span> span = tracer->StartSpan(
    "child-op",
    {
      {"my.attribute", "123"},
    },
    startOptions);

  return 0;
}
