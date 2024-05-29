// Logger frontend library for C++.
//
// Copyright (c) 2020 - present,  Nicolai Grodzitski
// See LICENSE file in the root of the project.


#include <iostream>

#include <logr/logr.hpp>
#include <logr/ostream_backend.hpp>


int main() {
    auto logger =  logr::basic_ostream_logger_t<1024u>(std::cout);
    logger.trace( "Hello World! [raw message]" );
    logger.trace( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.trace( []() { return "Hello World! [cb]"; } );
    logger.trace( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.trace( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.trace( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.trace( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.trace( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

    logger.debug( "Hello World! [raw message]" );
    logger.debug( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.debug( []() { return "Hello World! [cb]"; } );
    logger.debug( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.debug( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.debug( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );
    logger.debug( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.debug( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

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

    logger.warn( "Hello World! [raw message]" );
    logger.warn( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.warn( []() { return "Hello World! [cb]"; } );
    logger.warn( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.warn( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.warn( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );
    logger.warn( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.warn( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

    logger.error( "Hello World! [raw message]" );
    logger.error( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.error( []() { return "Hello World! [cb]"; } );
    logger.error( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.error( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.error( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );
    logger.error( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.error( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

    logger.critical( "Hello World! [raw message]" );
    logger.critical( LOGR_SRC_LOCATION, "Hello World! [raw message]" );

    logger.critical( []() { return "Hello World! [cb]"; } );
    logger.critical( LOGR_SRC_LOCATION, []() { return "Hello World! [cb]"; } );

    logger.critical( []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );

    logger.critical( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out, "Hello {}! [{}]", "World", "cb with explicit out" );
    } );
    logger.critical( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   FMT_STRING( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and FMT_STRING" );
    } );

    logger.critical( LOGR_SRC_LOCATION, []( auto out ) {
        format_to( out,
                   fmt::runtime( "Hello {}! [{}]" ),
                   "World",
                   "cb with explicit out and runtime-string" );
    } );

    logger.flush();

    return 0;
}
