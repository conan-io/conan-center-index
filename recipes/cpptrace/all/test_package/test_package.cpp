#include <cstdlib>
#include <iostream>
#include <limits.h>
#include <cpptrace/cpptrace.hpp>
#include <ctrace/ctrace.h>

int main() {
    cpptrace::generate_trace().print();
    
    ctrace_stacktrace c_trace = ctrace_generate_trace(0, SIZE_MAX);

    return EXIT_SUCCESS;
}
