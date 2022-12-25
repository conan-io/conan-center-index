#include <unifex/scheduler_concepts.hpp>
#include <unifex/sync_wait.hpp>
#include <unifex/then.hpp>
#include <unifex/timed_single_thread_context.hpp>

#include <chrono>

using namespace unifex;
using namespace std::chrono_literals;

int main() {
  timed_single_thread_context context;
  auto scheduler = context.get_scheduler();

  int count = 0;
  sync_wait(then(schedule_after(scheduler, 200ms), [&] { ++count; }));

  return !(count == 1);
}
