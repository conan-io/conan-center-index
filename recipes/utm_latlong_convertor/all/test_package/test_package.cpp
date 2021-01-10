#include "UTM.h"
#include <iostream>

using namespace UTM;

int main() {

    double Lat = 37.31204642;
    double Long = -122.04506233;
    int long_zone = 10;
    char lat_zone[512];
    double northing{0.0};
    double easting{0.0};

    LLtoUTM(Lat, Long, northing, easting, lat_zone);
    std::cout << "Lat : " << Lat << ", Lon : " << Long << " converts to Northing : " << northing << ", Easting : " << easting << "\n";

    UTMtoLL(northing, easting, lat_zone, Lat, Long);
    std::cout << "Northing : " << northing << ", Easting : " << easting << ", converts to Lat : " << Lat << ", Lon : " << Long << "\n";
    return 0;
}
