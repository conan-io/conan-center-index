#include <cstdlib>
#include <iostream>
#include <limits.h>
#include <cpptrace/cpptrace.hpp>
#ifdef CTRACE
#include <ctrace/ctrace.h>
#endif

int main() {
    cpptrace::generate_trace().print();
    
    #ifdef CTRACE
    ctrace_stacktrace c_trace = ctrace_generate_trace(0, SIZE_MAX);
    #endif

    return EXIT_SUCCESS;
}
