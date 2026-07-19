#include <iostream>

#ifdef TMC_STANDALONE_COMPILATION
#define TMC_IMPL
#endif

#include "tmc/all_headers.hpp"

namespace {
tmc::task<int> hello_world() {
  std::cout << "Hello, async world!" << std::endl;
#ifdef TMC_USE_HWLOC
  auto topo = tmc::topology::query();
  std::cout << "TMC_USE_HWLOC enabled. Detected " << topo.core_count()
            << " cores." << std::endl;
#endif
  co_return 0;
};
} // namespace

int main() { return tmc::async_main(hello_world()); }
