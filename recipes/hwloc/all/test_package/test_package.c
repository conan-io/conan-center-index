#include <hwloc.h>

int main(void) {
    hwloc_topology_t topology;

    hwloc_topology_init(&topology);
    hwloc_topology_destroy(topology);

    return 0;
}
