#include <stdio.h>

#include "girepository.h"

int main() {
    printf("gobject introspection version %d.%d.%d\n",
           gi_get_major_version(),
           gi_get_minor_version(),
           gi_get_micro_version());
    return 0;
}
