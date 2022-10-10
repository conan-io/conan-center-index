#include <opentelemetry/exporters/ostream/span_exporter.h>
#include <opentelemetry/sdk/trace/simple_processor.h>
#include <opentelemetry/sdk/trace/tracer_provider.h>
#include <opentelemetry/trace/provider.h>
#include <opentelemetry/metrics/meter_provider.h>
#include <opentelemetry/sdk/metrics/meter_provider.h>

int main(int argc, char** argv) {
  auto exporter = std::unique_ptr<opentelemetry::sdk::trace::SpanExporter>(
    new opentelemetry::exporter::trace::OStreamSpanExporter);
  auto processor = std::unique_ptr<opentelemetry::sdk::trace::SpanProcessor>(
    new opentelemetry::sdk::trace::SimpleSpanProcessor(std::move(exporter)));
  auto provider = opentelemetry::nostd::shared_ptr<opentelemetry::trace::TracerProvider>(
    new opentelemetry::sdk::trace::TracerProvider(std::move(processor)));

  auto tracer = provider->GetTracer("simple");

  opentelemetry::nostd::shared_ptr<opentelemetry::trace::Span> span = tracer->StartSpan(
    "op", {
            {"my.attribute", "123"},
          });

  // Metrics testing
  auto metricsProvider = std::shared_ptr<opentelemetry::v1::metrics::MeterProvider>(new opentelemetry::sdk::metrics::MeterProvider());
  auto p = std::static_pointer_cast<opentelemetry::sdk::metrics::MeterProvider>(metricsProvider);

  opentelemetry::v1::nostd::shared_ptr<opentelemetry::v1::metrics::Meter> meter = metricsProvider->GetMeter("test", "1.2.0");
  auto double_counter = meter->CreateDoubleCounter("MyGreatCounter");
  double_counter->Add(1);

  return 0;
}
