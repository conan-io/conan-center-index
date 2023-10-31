#include <cstdlib>
#include <iostream>
#include "cpptrace/cpptrace.hpp"

int main() {
    cpptrace::generate_trace().print();

    return EXIT_SUCCESS;
}
