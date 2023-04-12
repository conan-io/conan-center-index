#include <iostream>
#include <chrono>
#include <thread>

#ifdef WATCHER_WATCH_OBJECT
#  include "wtr/watcher.hpp"
#else
#  include "watcher/watcher.hpp"
#endif

int main(int argc, char** argv) {
  std::cout << R"({
  "water.watcher.stream":{
)";

  auto const show_event_json = [](const WATCHER_EVENT_NAMESPACE::event& this_event) {
    std::cout << "    " << this_event;
    if (this_event.kind != WATCHER_NAMESPACE::event::kind::watcher) {
      std::cout << ",";
    }
    std::cout << "\n";
  };

  auto const time_until_death = std::chrono::seconds(3);

#ifdef WATCHER_WATCH_OBJECT
  auto lifetime = wtr::watch(".", show_event_json);
  std::this_thread::sleep_for(time_until_death);
  auto const is_watch_dead = lifetime.close();
#else
  std::thread([&]() { WATCHER_NAMESPACE::watcher::watch(".", show_event_json); }).detach();
  std::this_thread::sleep_for(time_until_death);
#  ifdef WATCHER_DIE_WITH_PATH
  auto const is_watch_dead = WATCHER_NAMESPACE::watcher::die(".", show_event_json);
#  else
  auto const is_watch_dead = WATCHER_NAMESPACE::watcher::die(show_event_json);
#  endif
#endif

  std::cout << "  },\n"
            << R"(  "milliseconds":)" << time_until_death.count() << "," << std::endl
            << R"(  "expired":)" << std::boolalpha << is_watch_dead << "\n"
            << "}"
            << std::endl;

  return 0;
}
