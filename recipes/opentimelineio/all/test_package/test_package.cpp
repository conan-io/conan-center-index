#include <iostream>
#include <opentimelineio/color.h>

namespace otio = opentimelineio::OPENTIMELINEIO_VERSION;

int main() {
    const auto time = otio::RationalTime::from_time_string("01:02:03", 25.0);
    otio::Color color(0.5, 0.0, 0.5);
    std::cout << time.value() << " frames, color " << color.to_hex() << '\n';
}
