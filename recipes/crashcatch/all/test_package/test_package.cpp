#include "CrashCatch.hpp"
#include <iostream>

int main() {
    CrashCatch::enable();
    std::cout << "CrashCatch enabled successfully.\n";
    return 0;
}