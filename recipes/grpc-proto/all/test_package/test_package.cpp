#include <iostream>
#include "grpc/health/v1/health.pb.h"

int main() {
    std::cout << "Conan - test package for grpc-proto\n";

    grpc::health::v1::HealthCheckResponse h;
    h.set_status(::grpc::health::v1::HealthCheckResponse_ServingStatus::HealthCheckResponse_ServingStatus_NOT_SERVING);

    std::cout << h.DebugString();

    return 0;
}
