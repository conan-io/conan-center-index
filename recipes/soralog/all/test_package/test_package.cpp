#include <cstdlib>
#include <memory>
#include <string>

#include <soralog/impl/configurator_from_yaml.hpp>
#include <soralog/logger.hpp>
#include <soralog/logging_system.hpp>

int main() {
  auto configurator = std::make_shared<soralog::ConfiguratorFromYAML>(std::string(R"(
sinks:
  - name: console
    type: console
groups:
  - name: main
    sink: console
    level: info
)"));
  soralog::LoggingSystem log_system(configurator);
  if (log_system.configure().has_error) {
    return EXIT_FAILURE;
  }
  log_system.getLogger("test_package", "main")->info("soralog works");
  return EXIT_SUCCESS;
}
