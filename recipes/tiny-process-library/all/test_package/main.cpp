#include <iostream>
#include "process.hpp"

int main()
{
#ifdef _WIN32
    TinyProcessLib::Process p("cmd /C echo hello", "", [](const char* bytes, size_t n){
        std::cout.write(bytes, n);
    });
#else
    TinyProcessLib::Process p("echo hello", "", [](const char* bytes, size_t n){
        std::cout.write(bytes, n);
    });
#endif
    auto exit_status = p.get_exit_status();
    std::cout << "\nexit=" << exit_status << "\n";
    return exit_status;
}