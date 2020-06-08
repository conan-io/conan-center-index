#include <cstdlib>
#include <iostream>
#include <chrono>

#include "date/date.h"
#include "date/tz.h"

int main() {
    using namespace std::chrono;
    using namespace date;

    auto date1 = 2015_y/March/22;
    std::cout << date1 << '\n';
    auto date2 = March/22/2015;
    std::cout << date2 << '\n';
    auto date3 = 22_d/March/2015;
    std::cout << date3 << '\n';

    try {
        auto tz = date::current_zone()->name();
        std::cout << "timezone: " << tz << std::endl;
    } catch (const std::exception & e) {
         std::cout << "exception caught " << e.what() << std::endl;
    }

    return EXIT_SUCCESS;
}
