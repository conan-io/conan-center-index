// Smoke test for the apibrasil Conan package: confirms the headers are on the
// include path and the compiled library links. It does not make network calls.

#include <iostream>

#include <apibrasil/apibrasil.hpp>

int main() {
    // Constructing the client forces linking against the compiled library.
    // The default constructor only reads environment variables (no network).
    apibrasil::ApiBrasil api;
    (void)api;

    std::cout << "APIBrasil SDK C++ " << apibrasil::kSdkVersion
              << " - Conan package OK\n";
    return 0;
}
