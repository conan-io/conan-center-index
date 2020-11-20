#include <iostream>

#include <dbus/dbus.h>

int main() {
    int major_version = 0;
    int minor_version = 0;
    int micro_version = 0;

    dbus_get_version(&major_version, &minor_version, &micro_version);

    std::cout << "D-Bus version: "
        << major_version << "."
        << minor_version << "." 
        << micro_version << std::endl;
}
