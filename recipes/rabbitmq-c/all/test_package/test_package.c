#include <stdio.h>

/* Public headers have moved to rabbitmq-c/ directory since 0.12.0 */
#if !defined(RABBITMQ_C_0_12_0_LATER)
    #include <amqp.h>
    #include <amqp_framing.h>

    #ifdef WITH_SSL
        #include <amqp_ssl_socket.h>
    #else
        #include <amqp_tcp_socket.h>
    #endif
#else
    #include <rabbitmq-c/amqp.h>
    #include <rabbitmq-c/framing.h>

    #ifdef WITH_SSL
        #include <rabbitmq-c/ssl_socket.h>
    #else
        #include <rabbitmq-c/tcp_socket.h>
    #endif
#endif

int main(int argc, char const *argv[]) {
    amqp_connection_state_t conn = amqp_new_connection();
    amqp_socket_t *socket = NULL;
#ifdef WITH_SSL
    socket = amqp_ssl_socket_new(conn);
#else
    socket = amqp_tcp_socket_new(conn);
#endif

    printf(
        "\n"
        "----------------->Tests are done.<---------------------\n"
        "Using version %s\n"
        "///////////////////////////////////////////////////////\n",
        amqp_version()
    );

    return 0;
}
