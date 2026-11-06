#include <depz_sensor_io.h>
#include <depz_sensor_sdk.h>

#include <stdint.h>
#include <stdio.h>

int main(void) {
    const uint8_t data[] = {0x01, 0x02, 0x03, 0x04};
    uint8_t crc = depz_crc8_maxim(data, sizeof(data));
    printf("depz_crc8_maxim -> 0x%02X\n", crc);

    /* Links the serial-port layer: opening a port that does not exist fails cleanly. */
    depz_device *dev = NULL;
    int rc = depz_device_open("depz-test-package-no-such-port", &dev);
    printf("depz_device_open(no such port) -> %d: %s\n", rc, depz_last_error());
    return rc == 0 ? 1 : 0;
}
