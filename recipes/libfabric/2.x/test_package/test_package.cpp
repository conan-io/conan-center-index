#include <rdma/fabric.h>
#include <iostream>

int main () {
    const uint32_t version = fi_version();
    std::cout << "hello libfabric version " << FI_MAJOR(version) << "." << FI_MINOR(version) << "\n";
    return 0;
}
