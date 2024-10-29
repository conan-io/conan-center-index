#include <iostream>
#include "efsw/efsw.hpp"

int main(void) {
    using namespace std::chrono_literals;
    
    efsw::FileWatcher* fileWatcher = new efsw::FileWatcher();

    std::cout << "Follows symlinks?: " << fileWatcher->followSymlinks() << std::endl;

    delete fileWatcher;

    return EXIT_SUCCESS;
}
