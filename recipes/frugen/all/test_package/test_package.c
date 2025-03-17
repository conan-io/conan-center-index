#include <stdio.h>
#include "fru.h"

int main(void) {
    uint8_t buffer[64] = {0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF};
    if (!find_fru_header(buffer, sizeof(buffer), FRU_NOFLAGS)) {
        printf("Failed to find FRU information block");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
