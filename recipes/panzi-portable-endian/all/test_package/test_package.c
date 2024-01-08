#include <stdint.h>

#include <portable_endian.h>

int main() {
    uint64_t num = 100;
    le64toh(num);
}
