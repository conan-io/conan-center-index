#include <cstdlib>
#include <iostream>
#include <ortools/base/version.h>


int main() {
    std::cout << "Google OR-Tools version: "
              << operations_research::OrToolsMajorVersion() << "."
              << operations_research::OrToolsMinorVersion() << "."
              << operations_research::OrToolsPatchVersion() << std::endl;
    return EXIT_SUCCESS;
}
