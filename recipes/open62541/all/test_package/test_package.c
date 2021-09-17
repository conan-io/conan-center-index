#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#endif

#include <stdlib.h>

UA_Boolean running = true;

static void server_stop_callback(UA_Server *server, void *data) {
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "stopping server due to timer");
    running = false;
}

int main(void) {
    UA_Server *server = UA_Server_new();
    UA_ServerConfig_setDefault(UA_Server_getConfig(server));
    UA_StatusCode return_code;
    UA_Server_addRepeatedCallback(server, server_stop_callback, NULL, 500., NULL);
    return_code = UA_Server_run(server, &running);
    UA_Server_delete(server);
    return return_code == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
