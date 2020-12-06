#include <iostream>

#include <logr/ostream_backend.hpp>
#include <logr/config.hpp>

int main()
{
    logr::ostream_logger_t<> logger{ std::cout,
                                     logr::log_message_level::trace };

    logger.info( []( auto & out ){
        fmt::format_to( out,
                        "Welcome to logr (v{}.{}.{}), package is provided by Conan!",
                        LOGR_VERSION_MAJOR,
                        LOGR_VERSION_MINOR,
                        LOGR_VERSION_PATCH );
    } );
}
