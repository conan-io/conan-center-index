#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "serial/serial.h"

using namespace std;

int main() {
    vector<serial::PortInfo> devices_found = serial::list_ports();

    vector<serial::PortInfo>::iterator iter = devices_found.begin();

    while (iter != devices_found.end()) {
        serial::PortInfo device = *iter++;

        printf("(%s, %s, %s)\n", device.port.c_str(),
               device.description.c_str(), device.hardware_id.c_str());
    }

    return 0;
}
