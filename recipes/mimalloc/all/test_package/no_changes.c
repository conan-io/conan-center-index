#include <stdlib.h>
#include <string.h>

int main() {
    void *data = malloc(1024);

    memset(data, '6', 1024);

    free(data);

    return 0;
}
