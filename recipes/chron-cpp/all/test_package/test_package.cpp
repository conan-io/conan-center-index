#include <iostream>

#include <oryx/chron.hpp>

using namespace std::chrono_literals;

auto main() -> int {
    oryx::chron::Scheduler scheduler;

    scheduler.AddSchedule("Task-1", "* * * * * ?",
                          [](auto info) { std::cout << info.name << " called with delay " << info.delay << "\n"; });
    scheduler.Tick();
    return EXIT_SUCCESS;
}