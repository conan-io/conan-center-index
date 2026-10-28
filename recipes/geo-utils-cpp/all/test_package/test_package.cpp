#include <cstdlib>
#include <iostream>

#include <geo/spherical.hpp>

int main() {
    const geo::LatLng nyc{40.7128, -74.0060};
    const geo::LatLng london{51.5074, -0.1278};

    const double d = geo::distance_between(nyc, london);
    std::cout << "NYC -> London: " << d << " m\n";

    return (d > 5'000'000.0 && d < 6'000'000.0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
