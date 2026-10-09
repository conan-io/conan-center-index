#include <cppmicroservices/Framework.h>
#include <cppmicroservices/FrameworkFactory.h>

#include <cstdlib>
#include <iostream>

int main(void) {
    auto framework = cppmicroservices::FrameworkFactory().NewFramework();
    framework.Init();
    framework.Start();
    framework.Stop();
    std::cout << "cppmicroservices test package" << std::endl;

    return EXIT_SUCCESS;
}
