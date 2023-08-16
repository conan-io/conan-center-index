#include <cstdlib>
#include <iostream>
#include <Wt/WEnvironment.h>

int main(void) {
    std::cout << "WT Library version: " << Wt::WEnvironment::libraryVersion() << std::endl;

    return EXIT_SUCCESS;
}
