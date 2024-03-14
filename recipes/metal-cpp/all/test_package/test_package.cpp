#include <iostream>

#include <Foundation/Foundation.hpp>
#include <Metal/Metal.hpp>

#ifdef METALCPP_HEADER_ONLY
#define NS_PRIVATE_IMPLEMENTATION
#define MTL_PRIVATE_IMPLEMENTATION
#endif

int main()
{
    // Create a metal device to check the library functions
    MTL::Device* metalDevice = MTL::CreateSystemDefaultDevice();

    std::cout << "Metal device detected: " << metalDevice->name()->cString(NS::ASCIIStringEncoding) << std::endl;

    return EXIT_SUCCESS;
}
