#include <Kokkos_Core.hpp>
#include <iostream>

int main(void) {
    const auto initialized = Kokkos::is_initialized();
    std::cout << "Kokkos test package: " << initialized << std::endl;
    return 0;
}
