#include "ctrack.hpp"

void expensiveOperation() {
    CTRACK;
    // Simulating some work
    for (int i = 0; i < 1000000; ++i) {
        // Do something
    }
}

int main() {
    for (int i = 0; i < 100; ++i) {
        expensiveOperation();
    }

    // Print results to console
    ctrack::result_print();

    return 0;
}
