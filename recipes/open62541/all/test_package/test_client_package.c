#include <stdio.h>
#include <open62541/client.h>
#include <open62541/client_config.h>
#include <open62541/client_config_default.h>

int main(int argc, char *argv[])
{
    /* Create a client and connect */
    UA_Client *client = UA_Client_new();
    UA_ClientConfig_setDefault(UA_Client_getConfig(client));

    UA_ClientState state = UA_Client_getState(client);
    switch (state)
    {
    case UA_CLIENTSTATE_DISCONNECTED: printf("disconnected\n"); break;
    case UA_CLIENTSTATE_CONNECTED: printf("connected\n"); break;
    case UA_CLIENTSTATE_SECURECHANNEL: printf("secure channel\n"); break;
    case UA_CLIENTSTATE_SESSION: printf("session\n"); break;
    case UA_CLIENTSTATE_SESSION_RENEWED: printf("session renewed\n"); break;
    default: break;
    }
    UA_Client_delete(client); /* Disconnects the client internally */
    return 0;
}
