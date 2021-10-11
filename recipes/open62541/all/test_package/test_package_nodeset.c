#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#endif

/* Files namespace_foo_flt_generated.h and namespace_foo_flt_generated.c are created from FooFlt.NodeSet2.xml in the
 * /src_generated directory by CMake */
#include "foo_flt_nodeids.h"
#include "namespace_foo_flt_generated.h"

#include <signal.h>
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
    /* create nodes from nodeset */
    if(namespace_foo_flt_generated(server) != UA_STATUSCODE_GOOD) 
    {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "Could not add the Foo FLT nodeset. "
        "Check previous output for any error.");
        return_code = UA_STATUSCODE_BADUNEXPECTEDERROR;
    } 
    else 
    {
        // Do some additional stuff with the nodes
        // this will just get the namespace index, since it is already added to the server
        UA_UInt16 nsIdx = UA_Server_addNamespace(server, "https://new.foo.com/zebra-compression/flattening-and-subspacefolding/UA/");
        UA_NodeId testInstanceId = UA_NODEID_NUMERIC(nsIdx, UA_FOO_FLTID_APE);
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "The Ape has ns=%d;id=%d",
                    testInstanceId.namespaceIndex, testInstanceId.identifier.numeric);

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
    }
    UA_Server_delete(server);
    return return_code == UA_STATUSCODE_GOOD ? EXIT_SUCCESS : EXIT_FAILURE;
}
