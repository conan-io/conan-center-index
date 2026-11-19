#include <cstdlib>
#include <iostream>
#include <perfcpp/event_counter.hpp>

int
main()
{
  // Only build the counter definition; opening the counter would need perf_event access.
  auto counter_definitions = perf::CounterDefinition{};
  auto event_counter = perf::EventCounter{ counter_definitions };
  event_counter.add("instructions");

  std::cout << "perf-cpp: successfully configured the 'instructions' counter." << std::endl;

  return EXIT_SUCCESS;
}
