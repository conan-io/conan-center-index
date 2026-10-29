#include <open62541pp/node.hpp>
#include <open62541pp/server.hpp>
#include <iostream>

int main() {
    const UA_String nativeString = opcua::detail::toNativeString("Hello World");
    const auto nativeStr = opcua::detail::toStringView(nativeString);
    std::cout << "open62541pp: " << nativeStr << std::endl;
    return 0;
}
