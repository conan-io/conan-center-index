#include <cstdlib>
#include <iostream>

#include "pqxx/pqxx"

int main()
{
    std::cout << "libpqxx version: " << PQXX_VERSION << std::endl;

    pqxx::connection conn("postgres://tpilupsd:7hJFAnmfyuD27orImLVfKQX1mdMUJTq_@stampy.db.elephantsql.com:5432/tpilupsd");
    std::cout << "is connected: "<< conn.is_open() << std::endl;

    return EXIT_SUCCESS;
}
