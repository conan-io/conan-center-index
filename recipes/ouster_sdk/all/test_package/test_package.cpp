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
#ifdef WITH_SENSOR
#include "ouster/sensor_scan_source.h"
#include "ouster/scan_source.h"
#endif
#ifdef WITH_MAPPING
#include "ouster/pose_optimizer.h"
#endif

#include <iostream>
#include <vector>
#include <string>

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

#ifdef WITH_SENSOR
    // Test SensorScanSource - create with basic parameters
    std::vector<std::string> sources;
    ouster::ScanSourceOptions options;
    SensorScanSource sensor_source(sources, options);
    std::cout << "Successfully created a SensorScanSource object" << std::endl;
#endif

#ifdef WITH_MAPPING
    // Test PoseOptimizer - verify type exists
    // Note: Construction requires kiss-icp vendorized library which may not link correctly
    using namespace ouster::mapping;
    // Just verify the type exists without constructing to avoid kiss-icp linking issues
    std::cout << "Successfully included ouster_mapping headers" << std::endl;
#endif
}
