#include <stdlib.h>

int test_package_function(void);

int main() {
    int var = test_package_function();
    if (var != 1337) {
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
