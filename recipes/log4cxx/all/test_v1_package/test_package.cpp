#include "log4cxx/logger.h"
#include "log4cxx/xml/domconfigurator.h"

#include <iostream>

using namespace log4cxx;
using namespace log4cxx::xml;

int main(int argc, const char* argv[])
{
    LoggerPtr logger(Logger::getLogger("TEST"));
    if (argc < 2) {
        std::cerr << "Expected path to config xml\n";
        return -1;
    }
    DOMConfigurator::configure(argv[1]);
    LOG4CXX_INFO(logger, "App started!");
    LOG4CXX_ERROR(logger, "Some error!");
    return 0;
}
