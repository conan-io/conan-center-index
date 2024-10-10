#include "samarium/samarium.hpp"
#include <iostream>
int main()
{
    const auto im = sm::Image{sm::dimsFHD};
    std::cout << "Version: " << sm::version.major << '.' << sm::version.minor << '.' << sm::version.patch << std::endl;
    std::cout << "Image size: " << im.size() << std::endl;
    const auto as_sfml = sm::sfml(sm::Vector2_t{1.0, 2.0});
    sm::print("A Vector2:", sm::Vector2{.x = 5, .y = -3});
    // sm::print("A Color:  ", sm::Color{.r = 5, .g = 200, .b = 255});
    // sm::print("Is space pressed?", sm::Keyboard::is_key_pressed(sm::Keyboard::Key::Space));
    return 0;

}
