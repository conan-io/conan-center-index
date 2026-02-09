#include <iostream>
#include "process.hpp"

int main()
{
    TinyProcessLib::Process p("", "", [](const char* bytes, size_t n){});
    auto exit_status = p.get_exit_status();
    std::cout << "\nexit=" << exit_status << "\n";
    return 0;
}