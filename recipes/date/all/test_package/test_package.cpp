#include "date/date.h"
#include "date/tz.h"
#include <iostream>
#include <chrono>

int main() {
    const date::year_month_day conan_two(date::year(2023), date::month(2), date::day(22));
    std::cout << "Conan was released on: " << conan_two << std::endl;

#ifndef DATE_HEADER_ONLY
    try {
        // Test 1: Get current timezone
        const date::time_zone* tz = date::current_zone();
        std::cout << "Current timezone: " << tz->name() << std::endl;

        // Test 2: Verify IANA database is available by locating specific timezones
        auto ny_tz = date::locate_zone("America/New_York");
        auto london_tz = date::locate_zone("Europe/London");
        auto tokyo_tz = date::locate_zone("Asia/Tokyo");
        
        std::cout << "IANA timezone database is available:" << std::endl;
        std::cout << "  - " << ny_tz->name() << std::endl;
        std::cout << "  - " << london_tz->name() << std::endl;
        std::cout << "  - " << tokyo_tz->name() << std::endl;

        // Test 3: Simple timezone conversion to verify database works
        auto now = std::chrono::system_clock::now();
        auto ny_time = date::make_zoned(ny_tz, now);
        std::cout << "Current time in New York: " << ny_time << std::endl;

        std::cout << "IANA timezone database is working correctly." << std::endl;
    }
    catch (const std::exception & e) {
        std::cerr << "IANA timezone database test failed: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
#else
    std::cout << "Header-only mode: timezone functionality not available" << std::endl;
#endif

    return EXIT_SUCCESS;
}
