#include "unicorn/unicorn.h"

#include <stdio.h>

int main() {
    int major, minor;
    uc_version(&major, &minor);
    printf("unicorn version %d.%d\n", major, minor);
}
