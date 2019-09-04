#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include <limits>

#ifdef FMT_HEADER_ONLY
    #define FMT_EXTENDED_COLORS
#endif

#include "fmt/format.h"
#include "fmt/printf.h"
#include "fmt/ostream.h"
#include "fmt/time.h"


void vreport(const char *format, fmt::format_args args) {
    fmt::vprint(format, args);
}

template <typename... Args>
void report(const char *format, const Args & ... args) {
    vreport(format, fmt::make_format_args(args...));
}

class Date {
    int year_, month_, day_;
  public:
    Date(int year, int month, int day) : year_(year), month_(month), day_(day) {}

    friend std::ostream &operator<<(std::ostream &os, const Date &d) {
        return os << d.year_ << '-' << d.month_ << '-' << d.day_;
    }
};

int main() {
    const std::string thing("World");
    fmt::print("PRINT: Hello {}!\n", thing);
    fmt::printf("PRINTF: Hello, %s!\n", thing);

    const std::string formatted = fmt::format("{0}{1}{0}", "abra", "cad");
    fmt::print("{}\n", formatted);

    fmt::memory_buffer buf;
    fmt::format_to(buf, "{}", 2.7182818);
    fmt::print("Euler number: {}\n", buf.data());

    const std::string date = fmt::format("The date is {}\n", Date(2012, 12, 9));
    fmt::print(date);

    report("{} {} {}\n", "Conan", 42, 3.14159);

    std::tm tm = std::tm();
    tm.tm_year = 116;
    tm.tm_mon  = 3;
    tm.tm_mday = 25;
    fmt::print("{}\n", fmt::format("The date is {:%Y-%m-%d}.", tm));

    fmt::print(std::cout, "{} {}\n", "Magic number", 42);

#ifdef FMT_EXTENDED_COLORS
    fmt::print(fmt::color::aqua, "Bincrafters\n");
#endif

    return EXIT_SUCCESS;
}
