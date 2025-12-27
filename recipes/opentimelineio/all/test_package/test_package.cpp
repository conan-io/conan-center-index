#include <iostream>
#include <string>

//#include <opentime/version.h>
#include <opentime/rationalTime.h>
#include <opentimelineio/color.h>

namespace otime = opentime::OPENTIME_VERSION;
namespace otio  = opentimelineio::OPENTIME_VERSION;

int main (int argc, char *argv[])
{
    // Test a function from the opentime library.
    const auto rational_time = otime::RationalTime::from_time_string("01:02:03", 25.0);
    std::cout << "Parsed time string: " << rational_time.value() << '\n';

    // Test a function from the opentimelineio library.
    auto color = otio::Color::purple;
    std::cout << "Color pink as hex: " << color.to_hex() << '\n';

    return EXIT_SUCCESS;
}
