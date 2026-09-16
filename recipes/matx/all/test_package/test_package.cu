#include "matx.h"
#include <math.h>
#include "matx/version_config.h"
#include <iostream>

int main([[maybe_unused]] int argc, [[maybe_unused]] char **argv)
{
    std::cout << "MATX Version: " << MATX_VERSION_MAJOR << "." << MATX_VERSION_MINOR << "." << MATX_VERSION_PATCH << std::endl;
    auto a = matx::make_tensor<float>({10});
    a.SetVals({1, 2, 3, 4, 5, 6, 7, 8, 9, 10});

    matx::print(a);

    return 0;
}
