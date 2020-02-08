#include "modbus/modbus.h"

#include <cstdlib>
#include <iostream>

int main() {
    if (modbus_get_slave(NULL) != -1) {
        std::cerr << "modbus_get_slave(NULL) failed\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
