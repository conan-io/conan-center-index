#include <stdlib.h>

int main() {
    void *data = malloc(1024);
    free(data);

    return 0;
}
