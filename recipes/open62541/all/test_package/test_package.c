#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#endif
#include <stdlib.h>

int main(void) {
    UA_Server *server = UA_Server_new();
}
