#include <stdlib.h>
#include "girepository.h"

int main() {
    GIRepository* repository = g_irepository_get_default();
    return EXIT_SUCCESS;
}
