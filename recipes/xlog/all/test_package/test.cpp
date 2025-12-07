#include <xlog/logger.hpp>
#include <xlog/sinks/stdout_sink.hpp>

int main() {
    auto logger = std::make_shared<xlog::Logger>("test");
    logger->add_sink(std::make_shared<xlog::StdoutSink>());
    logger->info("XLog works!");
    return 0;
}
