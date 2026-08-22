#include <cstdint>

extern "C" {
#include "huffman/huffman.h"
}

int main() {
    uint8_t in[3] = {'a', 'b', 'c'};
    uint8_t *out = new uint8_t[10];
    uint32_t out_len = 0;
    huffman_encode_memory(in, 3, &out, &out_len);

    return 0;
}
