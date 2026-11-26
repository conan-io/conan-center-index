#include <Foundation/Foundation.hpp>
#include <Metal/Metal.hpp>
#include <iostream>

// Header-only check: only verify the headers can be included and their
// declarations referenced. Nothing is called, so no linking is required.
using MetalDevice = MTL::Device;
using FoundationString = NS::String;

int main() {
    std::cout << "metal-cpp: Test package successful\n";
    return 0;
}