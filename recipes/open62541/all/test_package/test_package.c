#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#endif

int main(void) {
    UA_Server *server = UA_Server_new();
    UA_Server_delete(server);
    return 0;
}
