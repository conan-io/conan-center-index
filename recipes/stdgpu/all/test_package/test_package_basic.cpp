#include <stdgpu/config.h>
#include <stdgpu/device.h>

#include <iostream>

int main() {
    // Minimal test to confirm that the non-platform-specific portion of the library links correctly
    std::cout << "stdgpu version: " << STDGPU_VERSION_STRING << std::endl;
    stdgpu::print_device_information();
}
