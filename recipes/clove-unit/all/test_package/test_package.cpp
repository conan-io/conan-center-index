#include <clove-unit.h>

int main() {
    const char* version = __CLOVE_VERSION;
    if (version) return 0;
    return 1;
}


