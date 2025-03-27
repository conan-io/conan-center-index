#include "log4cxx/log4cxx.h"
#include <iostream>

int main()
{
    std::cout << "log4cxx version: " <<  log4cxx::libraryVersion() << "\n";
    return 0;
}
