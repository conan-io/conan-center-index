#include <cstdio>

#include "polylineencoder.h"

int main(void)
{
    gepaf::PolylineEncoder encoder;

    // Poles and equator.
    encoder.addPoint(-90.0, -180.0);
    encoder.addPoint(.0, .0);
    encoder.addPoint(90.0, 180.0);

    auto res = encoder.encode(); // "~bidP~fsia@_cidP_gsia@_cidP_gsia@"
    encoder.clear(); // Clear the list of points.

    // Decode a string using static function.
    auto polyline = gepaf::PolylineEncoder::decode("~bidP~fsia@_cidP_gsia@_cidP_gsia@");

    // Iterate over all points and print coordinates of each.
    for (const auto& point : polyline) {
        printf("(%f, %f)\n", point.latitude(), point.longitude());
    }
    return 0;
}
