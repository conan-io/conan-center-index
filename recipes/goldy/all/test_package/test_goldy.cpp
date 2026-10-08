// Test that goldy headers can be included and library can be linked
#include <goldy.h>
#include <iostream>

int main() {
    // Just verify we can call a function from the library
    // Don't actually create an instance (requires GPU)
    std::cout << "Goldy C API header included successfully" << std::endl;
    
    // Check that symbols are available by taking address of a function
    auto fn = &goldy_instance_create;
    (void)fn;  // Suppress unused warning
    
    std::cout << "Goldy library linked successfully" << std::endl;
    return 0;
}

