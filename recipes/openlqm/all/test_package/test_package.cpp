#include <openlqm/openlqm.hpp>
#include <iostream>

int main() {
    OpenLQM::Coordinate fpCoord{};
    OpenLQM::ConvertQualityMapCoordinateToFingerprintCoordinate(
        {1, 2}, fpCoord, OpenLQM::PixelDensity::ppi500);

    std::cout << OpenLQM::VERSION << std::endl;

    return 0;
}
