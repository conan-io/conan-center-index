#include <cstdio>

#include "zmij.h"

int main() {
    char buf[zmij::double_buffer_size + 1];
    auto end = zmij::write(buf, sizeof(buf), 5.0507837461e-27);
    *end = '\0';
    puts(buf);
    return 0;
}
