#include <zmq.h>
#include <cstdlib>
#include <iostream>
#include <stdexcept>

int main() try
{
    void *context = zmq_ctx_new();
    void *requester = zmq_socket(context, ZMQ_REQ);
#if defined(WITH_LIBSODIUM)
    int is_server = 0;
    if (0 != zmq_setsockopt(requester, ZMQ_CURVE_SERVER, &is_server, sizeof(is_server)))
        throw std::runtime_error("zmq_setsockopt with ZMQ_CURVE_SERVER failed");
#endif
    zmq_close(requester);
    zmq_ctx_destroy (context);

    return EXIT_SUCCESS;
}
catch (std::runtime_error & e) {
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}
