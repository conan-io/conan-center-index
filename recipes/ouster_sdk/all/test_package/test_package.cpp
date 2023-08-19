#include "ouster/lidar_scan.h"

#include <iostream>

using namespace ouster::sensor;

int main() {
    size_t w = 100;
    size_t h = 100;
    ouster::LidarScan scan(w, h, UDPProfileLidar::PROFILE_RNG19_RFL8_SIG16_NIR16_DUAL);
    std::cout << "Successfully created a LidarScan object" << std::endl;
}
