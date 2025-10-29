#include <cstdlib>
#include <astarte_device_sdk/device_grpc.hpp>

using AstarteDeviceSdk::AstarteDeviceGRPC;

int main(void) {
    std::string server_addr = "localhost:50051";
    std::string node_id("aa04dade-9401-4c37-8c6a-d8da15b083ae");
    std::shared_ptr<AstarteDeviceGRPC> device =
        std::make_shared<AstarteDeviceGRPC>(server_addr, node_id);

    return EXIT_SUCCESS;
}
