#include <cpptrace/cpptrace.hpp>

void foo(int) {
    cpptrace::print_trace();
}

int main() {
    foo(1);
}
