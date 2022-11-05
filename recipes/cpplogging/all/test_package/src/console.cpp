/*!
    \file console.cpp
    \brief Console logger example
    \author Ivan Shynkarenka
    \date 29.07.2016
    \copyright MIT License
*/

#include "logging/config.h"
#include "logging/logger.h"

void ConfigureLogger()
{
    // Create default logging sink processor with a text layout
    auto sink = std::make_shared<CppLogging::Processor>(std::make_shared<CppLogging::TextLayout>());
    // Add console appender
    sink->appenders().push_back(std::make_shared<CppLogging::ConsoleAppender>());

    // Configure default logger
    CppLogging::Config::ConfigLogger(sink);

    // Startup the logging infrastructure
    CppLogging::Config::Startup();
}

int main(int argc, char** argv)
{
    // Configure logger
    ConfigureLogger();

    // Create default logger
    CppLogging::Logger logger;

    // Log some messages with different level
    logger.Debug("Debug message");
    logger.Info("Info message");
    logger.Warn("Warning message");
    logger.Error("Error message");
    logger.Fatal("Fatal message");

    return 0;
}
