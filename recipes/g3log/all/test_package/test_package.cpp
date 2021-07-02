#include <g3log/g3log.hpp>
#include <g3log/logworker.hpp>
#include <iostream>

int main()
{
    auto worker = g3::LogWorker::createLogWorker();
    auto defaultHandler = worker->addDefaultLogger("my_log", ".");
    g3::initializeLogging(worker.get());
    LOG(INFO) << "Make a log call";
    return 0;
}

