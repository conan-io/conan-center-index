#include <cstdlib>
#include <iostream>
#ifdef CONAN_ASSERT_ASSERT_ASSERT
#include <assert/assert/assert.hpp>
#else
#include <assert/assert.hpp>
#endif

int main(void) {
    std::cout << "Testing libassert\n";

    try{
        VERIFY(1 != 1);
    }
    catch (...){
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
