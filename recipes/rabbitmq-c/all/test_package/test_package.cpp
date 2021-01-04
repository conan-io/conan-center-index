#include <iostream>
#include <amqp.h>
#include <amqp_framing.h>

#ifdef WITH_SSL
#include <amqp_ssl_socket.h>
#else
#include <amqp_tcp_socket.h>
#endif

int main(int argc, char const *argv[]) {
    amqp_connection_state_t conn = amqp_new_connection();
    amqp_socket_t *socket = NULL;
#ifdef WITH_SSL
    socket = amqp_ssl_socket_new(conn);
#else
    socket = amqp_tcp_socket_new(conn);
#endif
    std::cout << std::endl
              << "----------------->Tests are done.<---------------------" << std::endl
	      << "Using version " << amqp_version() << std::endl
              << "///////////////////////////////////////////////////////" << std::endl;
    return 0;
}
