#include "ouster/lidar_scan.h"

#ifdef WITH_OSF
#include "ouster/osf/writer.h"
#endif
#ifdef WITH_PCAP
#include "ouster/os_pcap.h"
#endif
#ifdef WITH_VIZ
#include "ouster/point_viz.h"
#endif

#include <iostream>

int main() {
    size_t w = 100;
    size_t h = 100;
    using namespace ouster::sensor;
    ouster::LidarScan scan(w, h, UDPProfileLidar::PROFILE_RNG19_RFL8_SIG16_NIR16_DUAL);
    std::cout << "Successfully created a sensor::LidarScan object" << std::endl;

#ifdef WITH_OSF
    ouster::osf::Writer writer("tmp.osf");
    std::cout << "Successfully created a osf::Writer object" << std::endl;
#endif

#ifdef WITH_PCAP
    try {
        ouster::sensor_utils::PcapReader pcap_reader("tmp.pcap");
    } catch (...) { }
    std::cout << "Successfully created a sensor_utils::PcapReader object" << std::endl;
#endif

#ifdef WITH_VIZ
    ouster::viz::PointViz viz("Viz example");
    std::cout << "Successfully created a viz::PointViz object" << std::endl;
#endif
}
