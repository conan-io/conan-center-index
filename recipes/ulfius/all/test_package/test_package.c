/**
 * test.c
 * Small Hello World! example
 * to compile with gcc, run the following command
 * gcc -o test test.c -lulfius
 */
#include <ulfius.h>

#include <stdio.h>
#include <string.h>

#define PORT 8080

/**
 * Callback function for the web application on /helloworld url call
 */
int callback_hello_world (const struct _u_request * request, struct _u_response * response, void * user_data) {
    ulfius_set_string_body_response(response, 200, "Hello World!");
    return U_CALLBACK_CONTINUE;
}

/**
 * main function
 */
int main(int argc, char *argv[]) {
    struct _u_instance instance;

    if (ulfius_global_init() != U_OK) {
        fprintf(stderr, "Error ulfius_global_init, abort\n");
        return(1);
    }

    // Avoid running a server on CI
    if (argc > 1 && strcmp(argv[1], "run") == 0) {

        // Initialize instance with the port number
        if (ulfius_init_instance(&instance, PORT, NULL, NULL) != U_OK) {
            fprintf(stderr, "Error ulfius_init_instance, abort\n");
            return(1);
        }

        // Endpoint list declaration
        ulfius_add_endpoint_by_val(&instance, "GET", "/helloworld", NULL, 0, &callback_hello_world, NULL);

        // Start the framework
        if (ulfius_start_framework(&instance) == U_OK) {
            printf("Start framework on port %d\n", instance.port);

            // Wait for the user to press <enter> on the console to quit the application
            getchar();
        } else {
            fprintf(stderr, "Error starting framework\n");
        }
        printf("End framework\n");

        ulfius_stop_framework(&instance);

        ulfius_clean_instance(&instance);
    }

    ulfius_global_close();

    return 0;
}
