#include <Kokkos_Core.hpp>
#include <iostream>

int main(void) {
    std::cout << "Hello World on Kokkos execution space " << Kokkos::DefaultExecutionSpace::name();
    return 0;
}
