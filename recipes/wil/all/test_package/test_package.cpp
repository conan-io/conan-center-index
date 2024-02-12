#include <cstdlib>
#include <iostream>
#include "wil/resource.h"


int main(void) {
    SetLastError(42);
    // check for simple function call:
    auto error42 = wil::last_error_context();
    
    return EXIT_SUCCESS;
}
