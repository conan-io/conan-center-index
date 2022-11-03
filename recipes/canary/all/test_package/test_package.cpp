#include <iostream>
#include <canary/interface_index.hpp>

int main()
{
    try {
        auto index = canary::get_interface_index("vcan0");
        std::cout << "vcan0 interface index: " << index << "\n";
    }
    catch (std::exception& exc) {
        std::cout << "unable to find vcan0: " << exc.what() << "\n";
    }

    return 0;
}
