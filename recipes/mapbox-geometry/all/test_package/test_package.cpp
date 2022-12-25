#include <mapbox/geometry.hpp>

#include <iostream>

int main() {
    mapbox::geometry::point<double> pt(1.0, 0.0);
    std::cout << "x: " << pt.x << " y: " << pt.y << std::endl;
    return 0;
}
