#include <iostream>
#include "tmc/all_headers.hpp"


int main() {
    std::cout << "TooManyCooks version: " << TMC_VERSION << std::endl;
#ifdef TMC_USE_HWLOC
    std::cout << "HWLOC enabled. Detected " << tmc::topology::query().core_count() << " cores." << std::endl;
#endif
    return 0;
}
