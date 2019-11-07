#include <aws/checksums/crc.h>

#include <algorithm>
#include <cstdlib>
#include <cstdio>
#include <vector>

#define LOG_LEVEL AWS_LOG_LEVEL_TRACE


static int f() {
    static int i = 0;
    return i++;
}

/**
 * reference:
 * import binascii
 * hex(binascii.crc32(b''.join(binascii.a2b_hex('{:02x}'.format(i)) for i in range(128)))
 */

#define CRC32_REF 0x24650d57

int main() {
    std::vector<uint8_t> buffer(128);
    std::generate(buffer.begin(), buffer.end(), f);
    auto crc32 = aws_checksums_crc32(buffer.data(), buffer.size(), 0x0);

    printf("reference crc32:  0x%8x\n", CRC32_REF);
    printf("calculated crc32: 0x%8x\n", crc32);

    if (crc32 != CRC32_REF) {
        printf("MISMATCH\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
