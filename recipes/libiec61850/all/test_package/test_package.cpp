#include <iostream>
#include <format>
#include <cstdlib>

#include "libiec61850/iec61850_client.h"

int main(int argc, char **argv)
{
    std::string hostname("localhost");
    int tcpPort = 102;

    IedClientError error;

    IedConnection con = IedConnection_create();

    IedConnection_connect(con, &error, hostname.c_str(), tcpPort);

    std::cout << std::format("Connecting to {}:{}\n", hostname, tcpPort);

    if (error == IED_ERROR_OK)
    {
        std::cout << "Connected\n";
        IedConnection_close(con);
    }
    else
    {
        std::cerr << std::format("Failed to connect to {}:{}\n", hostname, tcpPort);
    }

    IedConnection_destroy(con);

    return 0;
}
