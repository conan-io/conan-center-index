#include <opentelemetry/sdk/resource/resource.h>
#include <opentelemetry/sdk/trace/tracer_provider.h>
#include <splunk/opentelemetry.h>

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
      {"my.attribute", "1234"},
    },
    startOptions);

  span->End();

  dynamic_cast<opentelemetry::sdk::trace::TracerProvider*>(provider.get())
    ->ForceFlush(std::chrono::microseconds(10));

  return 0;
}
