#include "bsd/libutil.h"

#include <stdio.h>

int main() {
    char buffer[256];
    const int nb = 123456789;
    int res = humanize_number(buffer, 8, nb, "b", HN_AUTOSCALE, 0);
    if (res == -1) {
        fprintf(stderr, "humanize_number failed\n");
        return 1;
    }
    printf("%d -> %s\n", nb, buffer);
    return 0;
}
