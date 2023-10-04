#include <stdlib.h>

#include <gudev/gudev.h>


int main(void) {
    GUdevClient * test = g_udev_client_new(NULL);
    if (!test) {
      return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
