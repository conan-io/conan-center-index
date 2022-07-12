#include <cstdlib>
#include <iostream>

#include <GeographicLib/Geodesic.hpp>

int main()
{
    const GeographicLib::Geodesic& geod = GeographicLib::Geodesic::WGS84();
    GeographicLib::Math::real lat1 = 40.6, lon1 = -73.8; // JFK Airport
    GeographicLib::Math::real lat2 = 51.6, lon2 = -0.5;  // LHR Airport
    GeographicLib::Math::real s12;

    geod.Inverse(lat1, lon1, lat2, lon2, s12);
    std::cout << "The distance from JFK to LHR is " << s12 / 1000 << " km\n";

    return EXIT_SUCCESS;
}
