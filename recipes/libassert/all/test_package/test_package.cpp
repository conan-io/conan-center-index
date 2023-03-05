#include <cstdlib>
#include <iostream>
#include <assert/assert/assert.hpp>

int main(void) {
    std::cout << "Testing libassert\n";

    try{
        VERIFY(1 != 1);
    }
    catch (libassert::verification_failure){
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
