#include "log4cxx/logmanager.h"
#include "log4cxx/xml/domconfigurator.h"

#include <iostream>

int main(int argc, const char* argv[])
{
    if (argc < 2) {
        std::cerr << "Usage error. Expected an argument, the path to a xml configuration file\n";
        return -1;
    }
    log4cxx::xml::DOMConfigurator::configure(argv[1]);
    auto logger = log4cxx::LogManager::getLogger("TEST");
    LOG4CXX_INFO(logger, "App started");
    LOG4CXX_ERROR(logger, "Information message");
    log4cxx::LogManager::shutdown();
    return 0;
}
