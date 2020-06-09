#include <stdio.h>
#include <open62541/client.h>
#include <open62541/client_config.h>
#include <open62541/client_config_default.h>

#ifdef TEST_ENABLE_PUBSUB_CUSTOM_PUBLISH_HANDLING

UA_StatusCode
UA_PubSubManager_addRepeatedCallback(UA_Server *server, UA_ServerCallback callback,
                                     void *data, UA_Double interval_ms, UA_UInt64 *callbackId) {
    return UA_STATUSCODE_GOOD;
}

UA_StatusCode
UA_PubSubManager_changeRepeatedCallbackInterval(UA_Server *server, UA_UInt64 callbackId,
                                                UA_Double interval_ms) {
    return UA_STATUSCODE_GOOD;
}

void
UA_PubSubManager_removeRepeatedPubSubCallback(UA_Server *server, UA_UInt64 callbackId) {
}
#endif

int main(int argc, char *argv[])
{
    /* Create a client and connect */
    UA_Client *client = UA_Client_new();
    UA_ClientConfig_setDefault(UA_Client_getConfig(client));

    UA_SessionState session;
    UA_Client_getState(client, NULL, &session, NULL);

    switch (session)
    {
    case UA_SESSIONSTATE_CLOSED: printf("session closed\n"); break;
    case UA_SESSIONSTATE_CREATED: printf("session created\n"); break;
    case UA_SESSIONSTATE_ACTIVATED: printf("session activated\n"); break;
    case UA_SESSIONSTATE_CLOSING: printf("session closing\n"); break;
    default: break;
    }
    UA_Client_delete(client); /* Disconnects the client internally */
    return 0;
}
