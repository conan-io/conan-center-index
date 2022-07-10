#include <cpuinfo.h>

#include <stdio.h>

int main() {
    bool initialized = cpuinfo_initialize();
    if (!initialized) {
        printf("cpuinfo doesn't support this platforn\n");
        return 0;
    }
    printf("processors count: %u\n", cpuinfo_get_processors_count());
    printf("cores count: %u\n", cpuinfo_get_cores_count());
    printf("clusters count: %u\n", cpuinfo_get_clusters_count());
    printf("packages count: %u\n", cpuinfo_get_packages_count());
    printf("uarchs count: %u\n", cpuinfo_get_uarchs_count());
    printf("l1i caches count: %u\n", cpuinfo_get_l1i_caches_count());
    printf("l1d caches count: %u\n", cpuinfo_get_l1d_caches_count());
    printf("l2 count: %u\n", cpuinfo_get_l2_caches_count());
    printf("l3 count: %u\n", cpuinfo_get_l3_caches_count());
    printf("l4 count: %u\n", cpuinfo_get_l4_caches_count());
    cpuinfo_deinitialize();
    return 0;
}
