#include <iostream>
#include <NvCloth/Factory.h>

int main()
{
    std::cout << "Hello, NvCloth!" << std::endl;
    nv::cloth::Factory* factory = NvClothCreateFactoryCPU();
    if (factory == nullptr)
    {
        std::cout << "Failed to create factory" << std::endl;
        return -1;
    }

    NvClothDestroyFactory(factory);
    return 0;
}
