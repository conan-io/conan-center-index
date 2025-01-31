#include <mavlink/minimal/mavlink.h>

#include <stdio.h>

int main() {
    printf("Payload size for minimal dialect: %d bytes\n", MAVLINK_MAX_DIALECT_PAYLOAD_SIZE);
}
