#include <datadog/opentracing.h>
#include <iostream>
#include <string>

int main(int argc, char *argv[])
{
  datadog::opentracing::TracerOptions tracer_options{"localhost", 8126, "compiled-in example"};
  auto tracer = datadog::opentracing::makeTracer(tracer_options);

  tracer->Close();
  return 0;
}
