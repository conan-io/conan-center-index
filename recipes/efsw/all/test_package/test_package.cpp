#include <iostream>
#include <cstdlib>  // EXIT_SUCCESS
#include "efsw/efsw.hpp"

int main() {
    efsw::FileWatcher* fileWatcher = new efsw::FileWatcher();

    std::cout << "Follows symlinks?: " << fileWatcher->followSymlinks() << std::endl;

    delete fileWatcher;

    return EXIT_SUCCESS;
}
