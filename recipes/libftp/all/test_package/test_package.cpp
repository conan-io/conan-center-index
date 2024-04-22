#include <iostream>
#include "ftp/ftp.hpp"

int main(void) {
    try {
        /* Test that libftp provides OpenSSL routines. */
        ftp::ssl::context_ptr ssl_context
            = std::make_unique<ftp::ssl::context>(ftp::ssl::context::tlsv13_client);
        SSL_CTX_set_session_cache_mode(ssl_context->native_handle(), SSL_SESS_CACHE_CLIENT);

        ftp::client client(std::move(ssl_context));
    }
    catch (const std::exception & ex) {
        std::cerr << ex.what() << std::endl;
    }
    return 0;
}
