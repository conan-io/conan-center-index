#include <iostream>
#include <isa-l/crc.h>

const uint16_t init_crc_16 = 0x8005;

uint16_t getIsalCrc16 (unsigned char *buf, uint64_t len) {
    return crc16_t10dif(init_crc_16, buf, len);
}

int main(void) {
    unsigned char buf[] = "32311E333530";
    if ( getIsalCrc16(buf, 12) != 0xb4c9 ) {
        std::cout << "Failed to install ISA-L\n";
        return -1;
    }
    std::cout << "Success\n";
    return 0;
}
