#include <iostream>
#include <instinct/transformer_all.hpp>


int main(void) {
    using namespace INSTINCT_TRANSFORMER_NS;
    std::cout << print_system_info() << std::endl;
    return EXIT_SUCCESS;
}
