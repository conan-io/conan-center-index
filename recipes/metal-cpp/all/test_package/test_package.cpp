#include <iostream>

#define NS_PRIVATE_IMPLEMENTATION
#define MTL_PRIVATE_IMPLEMENTATION

#include <Foundation/Foundation.hpp>
#include <Metal/Metal.hpp>


int main()
{
    // Create a metal device to check the library functions
    MTL::Device* metalDevice = MTL::CreateSystemDefaultDevice();

    std::cout << "Metal device detected: " << metalDevice->name()->cString(NS::ASCIIStringEncoding) << std::endl;

    return EXIT_SUCCESS;
}
