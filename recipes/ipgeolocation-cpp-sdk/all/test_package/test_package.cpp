#include <cstdlib>
#include <iostream>
#include <ipgeolocation/ipgeolocation.hpp>


int main() {
    ipgeolocation::IpGeolocationClientConfig config;
    config.api_key = "test-key";

    ipgeolocation::IpGeolocationClient client(config);
    client.Close();

    std::cout << ipgeolocation::VERSION << '\n';
    return EXIT_SUCCESS;
}
