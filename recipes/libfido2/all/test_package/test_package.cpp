#include <cstdlib>
#include <fido.h>


int main(void) {
    fido_init(0);

    fido_dev_t* dev = fido_dev_new();

    if (dev == nullptr) {
        return EXIT_FAILURE;
    }

    fido_dev_free(&dev);


    return EXIT_SUCCESS;
}
