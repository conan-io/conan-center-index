#include <cstdlib>
#include <iostream>

#include "date/date.h"
#include "date/tz.h"

int main() {
    auto& db = date::get_tzdb();
    std::cout << date::weekday{date::jul/4/2001} << '\n';
    return EXIT_SUCCESS;
}