#include <iostream>
#include <string>
#include <vector>

#include "ouster/algorithm/voxel_downsample.h"
#include "ouster/core/lidar_frame.h"

#ifdef WITH_OSF
#include "ouster/osf/writer.h"
#endif
#ifdef WITH_PCAP
#include "ouster/pcap/pcap_frame_set_source.h"
#endif
#ifdef WITH_VIZ
#include "ouster/viz/point_viz.h"
#endif
#ifdef WITH_SENSOR
#include "ouster/sensor/sensor_frame_set_source.h"
#endif
#ifdef WITH_MAPPING
#include "ouster/mapping/constraint_config.h"
#include "ouster/mapping/pose_optimizer_constraint.h"
#endif

int main() {
    const ouster::sdk::core::LidarFrameFieldTypes field_types;
    ouster::sdk::core::LidarFrame frame(64, 1024, field_types, 16);
    std::cout << "Successfully created a core::LidarFrame object with " << frame.fields().size()
              << " fields" << std::endl;

    ouster::sdk::core::ArrayX3dR points(1, 3);
    points << 1.0, 2.0, 3.0;
    ouster::sdk::core::ArrayX3dR normals(1, 3);
    normals << 0.0, 0.0, 1.0;
    auto downsampled = ouster::sdk::algorithm::voxel_downsample_with_normals(points, normals, 0.5);
    std::cout << "Successfully downsampled " << downsampled.first.rows() << " point(s)" << std::endl;

#ifdef WITH_OSF
    ouster::sdk::osf::Writer writer("tmp.osf");
    std::cout << "Successfully created an osf::Writer object" << std::endl;
#endif

#ifdef WITH_PCAP
    try {
        ouster::sdk::pcap::PcapFrameSetSource pcap_source("tmp.pcap");
    } catch (const std::exception&) {
    }
    std::cout << "Successfully created a pcap::PcapFrameSetSource object" << std::endl;
#endif

#ifdef WITH_VIZ
    ouster::sdk::viz::PointViz viz("Viz example");
    std::cout << "Successfully created a viz::PointViz object" << std::endl;
#endif

#ifdef WITH_SENSOR
    try {
        std::vector<std::string> sensors;
        ouster::sdk::sensor::SensorFrameSetSource sensor_source(
            sensors, ouster::sdk::sensor::SensorFrameSetSourceOptions{});
    } catch (const std::exception&) {
    }
    std::cout << "Successfully created a sensor::SensorFrameSetSource object" << std::endl;
#endif

#ifdef WITH_MAPPING
    ouster::sdk::mapping::SolverConfig config;
    config.key_frame_distance = 1.5;
    config.loss_function = ouster::sdk::mapping::LossFunction::HUBER_LOSS;
    const std::string serialized = ouster::sdk::mapping::serialize_constraints_to_json(config);
    std::cout << "Successfully serialized a mapping::SolverConfig of " << serialized.size()
              << " bytes" << std::endl;
#endif
}
