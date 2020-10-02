#include <iostream>
#include <nativeipc/ConnectionExports.h>

int main() {
    auto server = Twitch_IPC_ConnectionCreateServer("test");
    auto client = Twitch_IPC_ConnectionCreateClient("test");

    if(server && client)
    {
        std::cout << "success\n";
        Twitch_IPC_ConnectionDestroy(server);
        Twitch_IPC_ConnectionDestroy(client);
    }
    else
    {
        abort();
    }
}
