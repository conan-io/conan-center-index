#include <cstdlib>

#include <nablanet/nablanet.hpp>


int main() {
    const auto network = nablanet::make_zero_network({1, 1});
    return nablanet::parameter_count(network) == 2 ? EXIT_SUCCESS : EXIT_FAILURE;
}
