#include <mapbox/polylabel.hpp>
#include <mapbox/geometry.hpp>

int main() {
    mapbox::geometry::linear_ring<double> ring{
        mapbox::geometry::point<double>(0.0, 0.0),
        mapbox::geometry::point<double>(210.0, 50.7),
        mapbox::geometry::point<double>(-70.3, -40.9),
    };
    mapbox::geometry::polygon<double> polygon;
    polygon.push_back(ring);
    mapbox::geometry::point<double> p = mapbox::polylabel(polygon, 1.0);
    std::cout << "x: " << p.x << " y: " << p.y << std::endl;
    return 0;
}
