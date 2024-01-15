#include <opentracing/tracer.h>
#include <opentracing/noop.h>

using namespace opentracing;

int main() {
  auto tracer = MakeNoopTracer();

  auto span1 = tracer->StartSpan("a");

  return 0;
}
