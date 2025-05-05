#include <aws/checksums/crc.h>

#include <stdlib.h>
#include <stdio.h>

#define LOG_LEVEL AWS_LOG_LEVEL_TRACE


static int fill(uint8_t *buffer, size_t size) {
    size_t i;
    for(i = 0; i < size; ++i) {
        buffer[i] = i;
    }
}

/**
 * reference:
 * import binascii
 * hex(binascii.crc32(b''.join(binascii.a2b_hex('{:02x}'.format(i)) for i in range(128)))
 */

#define CRC32_REF 0x24650d57

int main() {
    int crc32;
    uint8_t buffer[128];
    fill(buffer, sizeof(buffer));
    crc32 = aws_checksums_crc32(buffer, sizeof(buffer), 0x0);

    printf("reference crc32:  0x%8x\n", CRC32_REF);
    printf("calculated crc32: 0x%8x\n", crc32);

    if (crc32 != CRC32_REF) {
        printf("MISMATCH\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
