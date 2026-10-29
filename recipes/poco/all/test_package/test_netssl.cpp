#include "Poco/Net/Utility.h"
#include <iostream>

int main() {
    const auto last_error = Poco::Net::Utility::getLastError();
    std::cout << "Poco Net SSL (Last Error): " << last_error << std::endl;
    return 0;
}
