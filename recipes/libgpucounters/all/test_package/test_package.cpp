#include <hwcpipe/gpu.hpp>
#include <iostream>


int main(void) {
    for (const auto &gpu : hwcpipe::find_gpus()) {
        std::cout << "------------------------------------------------------------\n"
                  << " GPU Device " << gpu.get_device_number() << ":\n"
                  << "------------------------------------------------------------\n";
        std::cout << "    Number of Cores: " << gpu.num_shader_cores() << '\n';
        std::cout << "    Bus Width:       " << gpu.bus_width() << '\n';
    }

    auto gpu = hwcpipe::gpu(0);
    if (!gpu) {
        std::cout << "No Mali GPU devices found.\n";
    }

    return 0;
}
