#include <iostream>
#include "syscalls-cpp/syscall.hpp"
#include "syscalls-cpp/platform.hpp"
int main()
{
    std::cout << "Syscall-CPP: Is Windows: " << std::boolalpha << syscall::platform::isWindows << std::endl;
    return 0;
}
