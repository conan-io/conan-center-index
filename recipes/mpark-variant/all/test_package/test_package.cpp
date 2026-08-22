#include <cstdlib>
#include <iostream>

#include <mpark/variant.hpp>

int main()
{
    std::cout << "mpark/variant\n";
    mpark::variant<int, std::string> v(42);
    std::cout << mpark::get<int>(v) << "\n";

    return EXIT_SUCCESS;
}
