#include <stdio.h>

#include "ip_connection.h"
#include "brick_master.h"

#define HOST "localhost"
#define PORT 4223
#define UID "XXYYZZ" // Change XXYYZZ to the UID of your Master Brick

int main(void) {
    // Create IP connection
    IPConnection ipcon;
    ipcon_create(&ipcon);

    // Create device object
    Master master;
    master_create(&master, UID, &ipcon);

    // Connect to brickd
    if(ipcon_connect(&ipcon, HOST, PORT) < 0) {
        fprintf(stderr, "Could not connect\n");
        return 0;
    }
    fprintf(stdout, "Connected!\n");
    return 0;
}
