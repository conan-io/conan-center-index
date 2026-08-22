#include <cstdlib>
#include <iostream>
#include <limits.h>
#include <cpptrace/cpptrace.hpp>
#include <ctrace/ctrace.h>

int main() {
    ctrace_stacktrace c_trace = ctrace_generate_trace(0, SIZE_MAX);
    std::cout << "Stack trace generated with " << c_trace.count << " frames." << std::endl;

    return EXIT_SUCCESS;
}
