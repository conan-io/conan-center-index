#include <libdeflate.h>

int main () {
    struct libdeflate_compressor *c;
    c = libdeflate_alloc_compressor(12);
    libdeflate_free_compressor(c);
    return 0;
}
