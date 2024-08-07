#include <open62541pp/open62541pp.h>

#include <iostream>


int main() {
    opcua::Server server(4840 /* port */);

    server.setApplicationName("open62541pp server example");
    server.setLogger([](auto level, auto category, auto msg) {
        std::cout << "[" << opcua::getLogLevelName(level) << "] "
                  << "[" << opcua::getLogCategoryName(category) << "] " << msg << std::endl;
    });

    const opcua::NodeId myIntegerNodeId{1, "the.answer"};
    const std::string myIntegerName{"the answer"};

    // add variable node
    auto parentNode = server.getObjectsNode();
    auto myIntegerNode = parentNode.addVariable(myIntegerNodeId, myIntegerName);

    // set node attributes
    myIntegerNode.writeDataType(opcua::DataTypeId::Int32);
    myIntegerNode.writeDisplayName({"en-US", "the answer"});
    myIntegerNode.writeDescription({"en-US", "the answer"});

    // write value
    myIntegerNode.writeValueScalar(42);

    // read value
    std::cout << "The answer is: " << myIntegerNode.readValueScalar<int>() << std::endl;
}
