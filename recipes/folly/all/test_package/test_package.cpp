#include <cstdlib>
#include <iostream>

#include <folly/Format.h>
#include <folly/IPAddress.h>


int main() {
    folly::fbstring address{"127.0.0.1"};
    folly::IPAddress::validate(address);
    return EXIT_SUCCESS;
}
