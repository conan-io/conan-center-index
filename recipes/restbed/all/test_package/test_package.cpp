#include <restbed>

#include <memory>
#include <cstdio>
#include <cstdlib>

static void post_method_handler( const std::shared_ptr< restbed::Session > session )
{
    const auto request = session->get_request( );

    int content_length = request->get_header( "Content-Length", 0 );

    session->fetch( content_length, [ ]( const std::shared_ptr< restbed::Session > session, const restbed::Bytes & body )
    {
        fprintf( stdout, "%.*s\n", ( int ) body.size( ), body.data( ) );
        session->close( restbed::OK, "Hello, World!", { { "Content-Length", "13" } } );
    } );
}

int main(void)
{
    auto resource = std::make_shared< restbed::Resource >( );
    resource->set_path( "/resource" );
    resource->set_method_handler( "POST", post_method_handler );

    auto settings = std::make_shared< restbed::Settings >( );
    settings->set_port( 1984 );
    settings->set_default_header( "Connection", "close" );

    restbed::Service service;
    service.publish( resource );
#if 0
    // Don't start the service to avoid blocking
    service.start( settings );
#endif

    return EXIT_SUCCESS;
}
