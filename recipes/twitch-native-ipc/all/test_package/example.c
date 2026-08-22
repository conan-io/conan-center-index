#include <nativeipc/ConnectionExports.h>

#include <stdio.h>
#include <stdlib.h>

int main() {
    void *server = Twitch_IPC_ConnectionCreateServer("test");
    void *client = Twitch_IPC_ConnectionCreateClient("test");

    if (server && client) {
        printf("success\n");
        Twitch_IPC_ConnectionDestroy(server);
        Twitch_IPC_ConnectionDestroy(client);
    } else {
        abort();
    }
}
