#include <stdio.h>
#include <dbus/dbus.h>

int main() {
    int major_version = 0;
    int minor_version = 0;
    int micro_version = 0;

    dbus_get_version(&major_version, &minor_version, &micro_version);

    printf("D-Bus version: v%i.%i.%i\n", major_version, minor_version, micro_version);
    return 0;
}
