#include <iostream>
#include <cantera/base/global.cpp>

int main()
{
    const auto canteraVersion = Cantera::version()
    std::cout << "Cantera version: " << canteraVersion << "\n";

    return 0;
}
