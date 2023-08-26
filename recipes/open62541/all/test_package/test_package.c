#ifdef UA_ENABLE_AMALGAMATION
#include <open62541.h>
#else
#include <open62541/plugin/log_stdout.h>
#include <open62541/server.h>
#include <open62541/server_config_default.h>
#include <open62541/network_tcp.h>
#endif

/* Files namespace_foo_flt_generated.h and namespace_foo_flt_generated.c are created from FooFlt.NodeSet2.xml in the
 * /src_generated directory by CMake */
#include "foo_flt_nodeids.h"
#include "namespace_foo_flt_generated.h"
#include <open62541/plugin/network.h>

int main(void) {
    UA_Server *server = UA_Server_new();

    UA_Server_delete(server);
    return 0;
}
