#include <openjpeg.h>

#include <stdio.h>
#include <stdlib.h>


int main() {
    printf("opj_has_thread_support: %d\n", opj_has_thread_support());
    printf("opj_get_num_cpus: %d\n", opj_get_num_cpus());

    return EXIT_SUCCESS;
}
