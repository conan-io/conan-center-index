#include <rosx_introspection/ros_message.hpp>

#include <iostream>
#include <string>

int main() {
    const std::string vector_def = "float64 x\n";
    RosMsgParser::ROSMessage msg(vector_def);
    std::cout << "The name of the first message field is: " << msg.field(0).name() << std::endl;
}
