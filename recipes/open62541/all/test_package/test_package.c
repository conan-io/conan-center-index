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
    UA_UInt16 portNumber = 4840;
    UA_ServerConfig_setMinimal(UA_Server_getConfig(server), portNumber, NULL);

    UA_StatusCode return_code;
    UA_Server_addRepeatedCallback(server, server_stop_callback, NULL, 150., NULL);
    
    return_code = UA_Server_run(server, &running);
    while(return_code == UA_STATUSCODE_BADCOMMUNICATIONERROR)
    {
            
        portNumber = portNumber + 1;
        UA_Server_getConfig(server)->networkLayers[0].handle.port = portNumber;
        
        return_code = UA_Server_run(server, &running);

        if(return_code == UA_STATUSCODE_GOOD)
        {
            printf("free port found");
            break;
        }
        else if(portNumber>4850)
        {
            printf("ports from 4840 to 4850 are not avilable");
            break;
        }

    }
    UA_Server_delete(server);
    return return_code == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
