#include <iostream>
#include <chrono>
#include <thread>

#include "watcher/watcher.hpp"

int main(int argc, char** argv) {
  std::cout << R"({
  "water.watcher.stream":{
)";

  auto const show_event_json = [](const water::watcher::event::event& this_event) {
    std::cout << "    " << this_event;
    if (this_event.kind != water::watcher::event::kind::watcher) {
      std::cout << ",";
    }
    std::cout << "\n";
  };

  std::thread([&]() { water::watcher::watch(".", show_event_json); }).detach();
  auto const time_until_death = std::chrono::seconds(3);
  std::this_thread::sleep_for(time_until_death);
  auto const is_watch_dead = water::watcher::die(show_event_json);

  std::cout << "  },\n"
            << R"(  "milliseconds":)" << time_until_death.count() << "," << std::endl
            << R"(  "expired":)" << std::boolalpha << is_watch_dead << "\n"
            << "}"
            << std::endl;

  return 0;
}
