#include "kickcat/Bus.h"
#include "kickcat/Link.h"
#include "kickcat/Prints.h"
#include "kickcat/SocketNull.h"

#include <iostream>

using namespace kickcat;

int main(int argc, char *argv[])
{
    std::shared_ptr<AbstractSocket> socket = std::make_shared<SocketNull>();
    try
    {
        socket->open("null");
    }
    catch (std::exception const &e)
    {
        std::cerr << e.what() << std::endl;
        return 1;
    }

    auto report_redundancy = []() {
    };

    std::shared_ptr<Link> link = std::make_shared<Link>(socket, socket, report_redundancy);
    link->setTimeout(2ms);
    link->checkRedundancyNeeded();

    Bus bus(link);
    return 0;
}
