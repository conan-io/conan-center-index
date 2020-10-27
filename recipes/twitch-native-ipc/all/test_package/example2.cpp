#include <iostream>
#include <nativeipc/ConnectionFactory.h>

int main() {
    using namespace Twitch::IPC;
    auto server = ConnectionFactory::newServerConnection("test");
    auto client = ConnectionFactory::newClientConnection("test");

    if(server && client) {
        std::cout << "success\n";
        server.reset();
        client.reset();
    } else {
        abort();
    }
}
