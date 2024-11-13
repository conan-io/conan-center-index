
// General tests for manual testing during development

#include <iostream>
#include "logfault/logfault.h"

using namespace std;

int main( int argc, char *argv[]) {

    logfault::LogManager::Instance().AddHandler(std::make_unique<logfault::StreamHandler>(clog, logfault::LogLevel::DEBUGGING));
    LFLOG_INFO << "Testing" << 1 << 2 << 3;
}
