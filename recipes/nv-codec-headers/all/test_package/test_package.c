/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <ffnvcodec/nvEncodeAPI.h>
#include <stdio.h>
#include <stdlib.h>

int main () {
    printf("hello NVENC API version %u.%u\n", NVENCAPI_MAJOR_VERSION, NVENCAPI_MINOR_VERSION);
    return EXIT_SUCCESS;
}
