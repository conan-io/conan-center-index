// Logger frontend library for C++.
//
// Copyright (c) 2020 - present,  Nicolai Grodzitski
// See LICENSE file in the root of the project.


#include <iostream>

#include <logr/logr.hpp>
#include <logr/ostream_backend.hpp>


int main() {
    auto logger =  logr::basic_ostream_logger_t<1024u>(std::cout);
 
    logger.info( "Hello World! [raw message]" );
    logger.info( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.info( []() { return "Hello World! [cb]"; } );
    logger.info( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.info( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.info( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );
    logger.info( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.info( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

    logger.flush();

    return 0;
}
