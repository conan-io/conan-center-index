#include <tinycolormap.hpp>

#include <iostream>

int main() {
    double value = 0.75;
    auto color = tinycolormap::GetColor(value, tinycolormap::ColormapType::Viridis);
    std::cout << "Viridis RGB values at " << value << ": "
              << (int)color.ri() << " " << (int)color.gi() << " " << (int)color.bi() << std::endl;
#ifdef TINYCOLORMAP_WITH_QT5
    auto qt_color = color.ConvertToQColor();
    std::cout << "Viridis QColor values at " << value << ": "
              << qt_color.red() << " " << qt_color.green() << " " << qt_color.blue() << std::endl;
#endif
}
