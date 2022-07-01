#include <opentelemetry/sdk/trace/tracer_provider.h>
#include <splunk/opentelemetry.h>

#include <stdio.h>

int main(int argc, char** argv) {
  splunk::OpenTelemetryOptions otelOptions = splunk::OpenTelemetryOptions()
                                               .WithServiceName("my-service")
                                               .WithServiceVersion("1.0")
                                               .WithExporter(splunk::ExporterType_JaegerThriftHttp)
                                               .WithDeploymentEnvironment("test");
  auto provider = splunk::InitOpentelemetry(otelOptions);
  auto span = opentelemetry::trace::Tracer::GetCurrentSpan();

  char traceId[32] = {0};
  char spanId[16] = {0};
  span->GetContext().trace_id().ToLowerBase16(traceId);
  span->GetContext().span_id().ToLowerBase16(spanId);
  printf("current span: %.*s:%.*s\n", 32, traceId, 16, spanId);

  return 0;
}
