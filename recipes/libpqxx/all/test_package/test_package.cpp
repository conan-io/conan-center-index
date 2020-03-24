#include "pqxx/pqxx"

#include <cstdlib>
#include <iostream>


int main()
{
    std::cout << "libpqxx version: " << PQXX_VERSION << std::endl;

    try {
        pqxx::connection conn("hostaddr='.conan' port=5432 dbname=conan user=conan connect_timeout=2");

        pqxx::work tx(conn);

        pqxx::row row = tx.exec1("SELECT 1");

        tx.commit();

        std::cout << row[0].as<int>() << "\n";
    } catch (const pqxx::broken_connection &ex) {
        std::cout << "error thrown: " << ex.what() << "\n";

        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
