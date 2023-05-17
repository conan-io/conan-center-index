#include <microhttpd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define PORT 8888
#define PAGE                                        \
    "<html>"                                        \
        "<head>"                                    \
            "<title>libmicrohttpd demo</title>"     \
        "</head>"                                   \
        "<body>"                                    \
            "libmicrohttpd demo"                    \
        "</body>"                                   \
    "</html>"

static enum MHD_Result ahc_echo(void * cls,
        struct MHD_Connection *connection,
        const char *url,
        const char *method,
        const char *version,
        const char *upload_data,
        long unsigned int *upload_data_size,
        void **con_cls) {
    struct MHD_Response *response;
    int ret;

    if (strcmp(method, "GET") != 0) {
        /**
         * unexpected method
         */
        return MHD_NO;
    }
    if (*con_cls == NULL) {
        /**
         * The first time only the headers are valid,
         * do not respond in the first round.
         * But accept the connection.
         */
        *con_cls = connection;
        return MHD_YES;
    }
    if (*upload_data_size != 0) {
        /**
         * upload data in a GET!?
         */
        return MHD_NO;
    }
    response = MHD_create_response_from_buffer(strlen(PAGE), (void*)PAGE, MHD_RESPMEM_PERSISTENT);
    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response);
    return ret;
}

int main(int argc, char *argv[]) {
    struct MHD_Daemon *daemon;

    // Don't open a port and do not block so CI isn't interrupted.
#if 0
    daemon = MHD_start_daemon(MHD_USE_INTERNAL_POLLING_THREAD,
        PORT, NULL, NULL,
        &ahc_echo, NULL, MHD_OPTION_END);
    if (daemon == NULL) {
        return 1;
    }

    (void)getchar();
#else
    daemon = NULL;
#endif

    MHD_stop_daemon(daemon);
    return 0;
}
