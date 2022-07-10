/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <rdma/fabric.h>
#include <stdio.h>
#include <stdlib.h>

int main () {
    const uint32_t version = fi_version();
    printf("hello libfabric version %d.%d\n", FI_MAJOR(version), FI_MINOR(version));
    return EXIT_SUCCESS;
}
