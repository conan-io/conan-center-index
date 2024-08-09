#include "ctrack.hpp"
#include <iostream>

void expensiveOperation() {
    CTRACK;
    // Simulating some work
    for (int i = 0; i < 5; ++i) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
}

int main() {
    for (int i = 0; i < 2; ++i) {
        expensiveOperation();
    }

    // Print results to console
    ctrack::result_print();

    return 0;
}
