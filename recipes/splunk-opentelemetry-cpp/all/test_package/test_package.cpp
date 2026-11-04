#include <splunk/opentelemetry.h>

int main() {
  splunk::OpenTelemetryOptions otelOptions = splunk::OpenTelemetryOptions()
                                               .WithServiceName("my-service")
                                               .WithServiceVersion("1.0")
                                               .WithDeploymentEnvironment("test");
}
