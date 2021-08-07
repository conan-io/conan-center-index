#include <cddlib/cdd.h>

int main(void) {
    dd_set_global_constants();
    dd_free_global_constants();
    return 0;
}
