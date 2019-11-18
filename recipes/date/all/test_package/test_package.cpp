#include <cstdlib>
#include <iostream>
#include <chrono>

#include "date/date.h"
#include "date/tz.h"


int main() {
    using namespace std::chrono;
    using namespace date;

    constexpr auto date1 = 2015_y/March/22;
    std::cout << date1 << '\n';
    constexpr auto date2 = March/22/2015;
    std::cout << date2 << '\n';
    constexpr auto date3 = 22_d/March/2015;
    std::cout << date3 << '\n';

    auto timezone = make_zoned(current_zone(), system_clock::now());
    std::cout << timezone << '\n';
    return EXIT_SUCCESS;
}