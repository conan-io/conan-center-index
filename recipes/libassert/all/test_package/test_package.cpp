#include <cstdlib>
#include <iostream>
#ifdef LIBASSERT2
#include <libassert/assert.hpp>
#else
#include <assert/assert.hpp>
#endif

int main(void) {
    std::cout << "Testing libassert\n";
    
    #ifdef LIBASSERT2
    libassert::set_failure_handler([](const libassert::assertion_info& info) {
        std::cerr<<info.to_string();
        throw std::runtime_error("Assertion failed");
    });
    #endif

    try{
        #ifdef LIBASSERT2
        DEBUG_ASSERT(1 != 1);
        ASSERT(1 != 1);
        #else
        VERIFY(1 != 1);
        #endif
    }
    catch (...){
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
