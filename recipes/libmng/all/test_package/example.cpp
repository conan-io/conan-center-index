#include <iostream>
#include <cstdlib>
#include <libmng.h>

// Callback functions required by libmng
mng_ptr MNG_DECL mng_malloc(mng_size_t size) {
    return calloc(1, size);
}

void MNG_DECL mng_free(mng_ptr ptr, mng_size_t size) {
    free(ptr);
}

int main() {
    // Initialize libmng
    mng_handle handle = mng_initialize(NULL, mng_malloc, mng_free, NULL);
    if (handle == MNG_NULL) {
        std::cerr << "mng_initialize failed\n";
        return EXIT_FAILURE;
    }

    // Get version information
    std::cout << "libmng version: " << mng_version_text() << std::endl;

    // Cleanup
    mng_cleanup(&handle);

    return EXIT_SUCCESS;
}
