#include <cstdlib>
#include <iostream>

#include "pqxx/pqxx"


int main() {
    (void)sizeof(pqxx::connection);
    (void)sizeof(pqxx::sl);
    std::cout << "libpqxx version: " << pqxx::version << std::endl;
    return EXIT_SUCCESS;
}
