#include <open62541pp/node.hpp>
#include <open62541pp/server.hpp>

int main() {
    int port = 0;
    opcua::Server server(port);
    opcua::Node parentNode(server, opcua::ObjectId::ObjectsFolder);
    opcua::Node myIntegerNode = parentNode.addVariable({1, 1000}, "TheAnswer");
    myIntegerNode.writeValueScalar(42);
}
