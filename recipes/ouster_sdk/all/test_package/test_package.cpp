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
#include "ouster/impl/preprocessing.h"
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
    ouster::mapping::SolverConfig config;
    config.key_frame_distance = 1.5;
    config.loss_function = ouster::mapping::LossFunction::HuberLoss;
    
    ouster::Preprocessor preprocessor(100.0, 0.1, true, 4);
    
    std::vector<Eigen::Vector3d> test_frame = {
        Eigen::Vector3d(1.0, 2.0, 3.0),
        Eigen::Vector3d(4.0, 5.0, 6.0)
    };
    std::vector<double> test_timestamps = {0.0, 0.1};
    auto processed = preprocessor.Preprocess(test_frame, test_timestamps, Eigen::Matrix4d::Identity());
    
    std::cout << "Successfully verified mapping component (SolverConfig, Preprocessor, dependencies)" << std::endl;
#endif
}
