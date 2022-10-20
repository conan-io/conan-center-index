#include <iostream>

#include "watcher/watcher.hpp"

int main(int argc, char** argv) {
  using water::watcher::event::event, water::watcher::watch, std::cout, std::endl;
  cout << R"({"water.watcher.stream":{)" << "\n";

  const auto is_watch_ok = watch<16>(
      ".",
      [](const event& this_event) { cout << this_event << ',' << endl; });

  cout << '}' << endl << '}' << endl;
  return is_watch_ok;
}
