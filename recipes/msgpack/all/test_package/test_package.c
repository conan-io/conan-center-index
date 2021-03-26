#include <msgpack.h>

#include <stdio.h>

int main() {
    printf("msgpack version %s\n", msgpack_version());
    return 0;
}
