#include "date/date.h"
#include "date/tz.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <type_traits>

class ZoneOffset {
public:
    explicit ZoneOffset(std::chrono::minutes offset)
        : _offset(offset) {}

    template <class Duration>
    auto to_local(date::sys_time<Duration> tp) const
        -> date::local_time<typename std::common_type<Duration, std::chrono::minutes>::type> {
        using namespace date;
        using namespace std::chrono;
        using LT = local_time<typename std::common_type<Duration, minutes>::type>;
        return LT{(tp + _offset).time_since_epoch()};
    }

    template <class Duration>
    auto to_sys(date::local_time<Duration> tp) const
        -> date::sys_time<typename std::common_type<Duration, std::chrono::minutes>::type> {
        using namespace date;
        using namespace std::chrono;
        using ST = sys_time<typename std::common_type<Duration, minutes>::type>;
        return ST{(tp - _offset).time_since_epoch()};
    }

private:
    std::chrono::minutes _offset;
};

int main() {
    using namespace std::chrono;
    using namespace date;

    auto date1 = 2015_y/March/22;
    std::cout << date1 << '\n';
    auto date2 = March/22/2015;
    std::cout << date2 << '\n';
    auto date3 = 22_d/March/2015;
    std::cout << date3 << '\n';

    ZoneOffset p3_45{hours{3} + minutes{45}};
    zoned_time<milliseconds, ZoneOffset*> zt{&p3_45, floor<milliseconds>(system_clock::now())};
    std::cout << zt.get_sys_time() << " (sys time)\n";
    std::cout << zt.get_local_time() << " (local time)\n";

#ifndef DATE_HEADER_ONLY
    try {
        auto tz = date::current_zone()->name();
        std::cout << "timezone: " << tz << std::endl;
    } catch (const std::exception & e) {
         std::cout << "exception caught " << e.what() << std::endl;
    }
#endif

    return EXIT_SUCCESS;
}
