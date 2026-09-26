#include <cstdlib>
#include "linxer/linxer.h"

int main(void) {
    try {
        (void)linxer::new_accessor("/fake/file");
    } catch (...) {
        // do nothing
    }

    return EXIT_SUCCESS;
}
