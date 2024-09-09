#include <cstdlib>
#include <iostream>
#include <libassert/assert.hpp>

int main(void) {
    std::cout << "Testing libassert\n";

    libassert::set_failure_handler([](const libassert::assertion_info& info) {
        std::cerr<<info.to_string();
        throw std::runtime_error("Assertion failed");
    });

    try{
        DEBUG_ASSERT(1 != 1);
        ASSERT(1 != 1);
    }
    catch (...){
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
