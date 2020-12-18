#include <iostream>

#include <spdlog/sinks/stdout_sinks.h>

#include <logr/config.hpp>
#include <logr/spdlog_backend.hpp>

auto make_logger()
{
    auto sink = std::make_shared< spdlog::sinks::stdout_sink_st >();
    sink->set_pattern("[%Y-%m-%d %T][%n][%l] %v [%g]");

    return logr::spdlog_logger_t<>{
        "console",
        std::move( sink ),
        logr::log_message_level::trace
    };
}

int main()
{
    auto logger = make_logger();

    logger.info( []( auto & out ){
        format_to( out,
                   "Welcome to logr (v{}.{}.{}), package is provided by Conan!",
                   LOGR_VERSION_MAJOR,
                   LOGR_VERSION_MINOR,
                   LOGR_VERSION_PATCH );
    } );
}
