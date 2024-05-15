#include <tinycolormap.hpp>

#include <iostream>

int main() {
    double value = 0.75;
    auto color = tinycolormap::GetColor(value, tinycolormap::ColormapType::Viridis);
    std::cout << "Viridis RGB values at " << value << ": "
              << (int)color.ri() << " " << (int)color.gi() << " " << (int)color.bi() << std::endl;
}
