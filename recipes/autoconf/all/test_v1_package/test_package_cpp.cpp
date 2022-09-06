#include "config.h"

#include <iostream>

extern "C" {
    int hello_from_c(void);
}

void hello_from_cxx() {
    std::cout << "Hello world (" PACKAGE_NAME ") from c++!\n";
}

int main(int argc, char** argv) {
    hello_from_cxx();
    hello_from_c();
    return 0;
}
