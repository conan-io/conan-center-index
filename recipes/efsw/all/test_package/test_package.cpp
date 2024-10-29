#include <iostream>
#include "efsw/efsw.hpp"

int main(void) {
    using namespace std::chrono_literals;
    
    efsw::FileWatcher* fileWatcher = new efsw::FileWatcher();

    std::cout << "works" << std::endl;

    delete fileWatcher;

    return EXIT_SUCCESS;
}
