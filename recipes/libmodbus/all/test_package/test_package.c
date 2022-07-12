#include <modbus/modbus.h>

#include <stdio.h>
#include <stdlib.h>

int main() {
    if (modbus_get_slave(NULL) != -1) {
        fprintf(stderr, "modbus_get_slave(NULL) failed\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
