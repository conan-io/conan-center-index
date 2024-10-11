#include <open62541pp/node.hpp>
#include <open62541pp/server.hpp>

int main() {
    opcua::Server server;
    opcua::Node parentNode(server, opcua::ObjectId::ObjectsFolder);
}
