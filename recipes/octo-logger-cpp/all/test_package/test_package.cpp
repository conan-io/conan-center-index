#include "octo-logger-cpp/manager.hpp"
#include "octo-logger-cpp/logger.hpp"

int main(int argc, char** argv)
{
    auto config = std::make_shared<octo::logger::ManagerConfig>();
    config->set_option(octo::logger::ManagerConfig::LoggerOption::DEFAULT_CHANNEL_LEVEL,
                       static_cast<int>(octo::logger::Log::LogLevel::TRACE));
    octo::logger::SinkConfig console_sink("Console", octo::logger::SinkConfig::SinkType::CONSOLE_SINK);
    config->add_sink(console_sink);
    octo::logger::Manager::instance().configure(config);

    octo::logger::Logger logger("Test");
    logger.trace() << "A";
    logger.debug() << "B";
    logger.info() << "C";
    logger.notice() << "D";
    logger.warning() << "E";
    logger.error() << "F";
    octo::logger::Manager::instance().terminate();
}