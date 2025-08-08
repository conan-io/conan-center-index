#include <librdtsc/rdtsc.h>
#include <stdio.h>
#include <unistd.h>

int main() {

    int res = rdtsc_init();
    if (res != 0) {
        printf("ERROR DURING INITIALIZATION!!!\n");
        return res;
    }
    uint64_t tsc_hz = rdtsc_get_tsc_hz();

    uint64_t tsc_old = rdtsc();
    sleep(1);
    uint64_t tsc_new = rdtsc();

    printf("TSC OLD:  %ld\n", tsc_old);
    printf("TSC NEW:  %ld\n", tsc_new);
    printf("TSC DIFF: %ld\n", tsc_new - tsc_old);
    printf("TSC HZ:   %ld\n", tsc_hz);
    printf("Elapsed time ( s): %ld\n", rdtsc_elapsed_s(tsc_old, tsc_new));
    printf("Elapsed time (ms): %ld\n", rdtsc_elapsed_ms(tsc_old, tsc_new));
    printf("Elapsed time (us): %ld\n", rdtsc_elapsed_us(tsc_old, tsc_new));
    printf("Elapsed time (ns): %ld\n", rdtsc_elapsed_ns(tsc_old, tsc_new));

    return 0;
}
