#include <iostream>
#include "esc/true_color.hpp"

int main(void) {
    esc::RGB red_rgb(255, 0, 0);

    auto red_hsl = esc::rgb_to_hsl(red_rgb);

    std::cout
        << "red => hue : " << static_cast<uint>(red_hsl.hue)
        << " sat: " << static_cast<uint>(red_hsl.saturation)
        << " lightness: " << static_cast<uint>(red_hsl.lightness)
        << std::endl;
}
