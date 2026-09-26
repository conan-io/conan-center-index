#include <depz_sensor_sdk.h>

#include <stdint.h>
#include <stdio.h>

int main(void) {
    const uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
    uint8_t crc = depz_crc8_maxim(data, sizeof(data));
    printf("depz_crc8_maxim -> 0x%02X\n", crc);
    return 0;
}
