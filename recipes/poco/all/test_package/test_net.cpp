#include "Poco/Net/IPAddress.h"
#include <iostream>

int main() {
    Poco::Net::IPAddress ip("127.0.0.1");
    std::cout << "Poco Net: " << ip.family() << std::endl;
    return 0;
}
