#include <cstdlib>
#include <iostream>
#include <string>

#include <urdf_parser/urdf_parser.h>

int main() {
    std::string test_str =
        "<robot name=\"test\" version=\"1.0\">"
        "  <link name=\"l1\"/>"
        "</robot>";
    urdf::ModelInterfaceSharedPtr urdf = urdf::parseURDF(test_str);
    std::cout << "urdf::parseURDF() ran successfully" << std::endl;
    return EXIT_SUCCESS;
}
