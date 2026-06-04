#include <iostream>
#include "test.hpp"
#include "testPubSubTypes.hpp"

int main() {
    TestModule::TestStruct test_struct;
    test_struct.message("Hello from generated code");
    test_struct.id(42);

    TestModule::TestStructPubSubType pubsub_type;

    std::cout << "Successfully compiled and used generated code!" << std::endl;
    return 0;
}
