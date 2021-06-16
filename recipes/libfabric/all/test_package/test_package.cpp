/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <rdma/fabric.h>
#include <iostream>

int main () {
    const uint32_t version = fi_version();
    std::cout << "hello libfabric version " << FI_MAJOR(version) << "." << FI_MINOR(version) << "\n";
}
