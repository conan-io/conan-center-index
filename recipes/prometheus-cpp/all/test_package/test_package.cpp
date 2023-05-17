#include <chrono>
#include <map>
#include <memory>
#include <string>
#include <thread>

#include <prometheus/counter.h>
#include <prometheus/registry.h>

#include <prometheus/exposer.h>
#include <prometheus/gateway.h>

using namespace prometheus;

int main(int argc, char** argv) {
  auto registry = std::make_shared<Registry>();
  auto& counter_family = BuildCounter()
                             .Name("time_running_seconds_total")
                             .Help("How many seconds is this server running?")
                             .Labels({{"label", "value"}})
                             .Register(*registry);
  auto& second_counter = counter_family.Add(
      {{"another_label", "value"}, {"yet_another_label", "value"}});
  second_counter.Increment();
  return 0;
}
