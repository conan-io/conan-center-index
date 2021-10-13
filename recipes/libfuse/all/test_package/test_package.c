#define FUSE_USE_VERSION 34

#include <fuse.h>

int main() {
    fuse_get_context();
    return 0;
}
