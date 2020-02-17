#include <cstdlib>
#include <iostream>

#include "pqxx/pqxx"

int main()
{
    std::cout << "libpqxx version: " << PQXX_VERSION << std::endl;

    return EXIT_SUCCESS;
}
