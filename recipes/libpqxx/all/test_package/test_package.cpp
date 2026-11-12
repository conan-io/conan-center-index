#include <cstdlib>
#include <iostream>
#include "pqxx/version"
#include "pqxx/separated_list"


int main() {
    (void)sizeof(pqxx::sl);
    std::cout << "libpqxx version: " << pqxx::version << std::endl;
    return EXIT_SUCCESS;
}
