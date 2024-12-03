#include <iostream>
#include <cantera/base/global.h>

int main()
{
    const auto canteraVersion = Cantera::version();
    std::cout << "Cantera version: " << canteraVersion << "\n";

    return 0;
}
