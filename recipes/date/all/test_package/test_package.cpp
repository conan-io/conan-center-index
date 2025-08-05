#include "date/date.h"
#include "date/tz.h"
#include <iostream>
#include <chrono>

int main() {
    const date::year_month_day conan_two(date::year(2023), date::month(2), date::day(22));
    std::cout << "Conan was released on: " << conan_two << std::endl;

#ifndef DATE_HEADER_ONLY
    const date::time_zone* tz = date::current_zone();
#endif
}
