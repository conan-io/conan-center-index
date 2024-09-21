#include "test_shared.h"
#include "test_static.h"

#include <iostream>

int main() {
    std::cout << get_test_shared_text() << "\n";
    std::cout << get_test_static_text() << "\n";
    return 0;
}
