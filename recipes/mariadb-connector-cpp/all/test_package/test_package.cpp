#include <iostream>
#include <mariadb/conncpp.hpp>

int main() {
        auto driver = sql::mariadb::get_driver_instance();
        std::cout << "Mariadb JDBC connector cpp works" << std::endl;
    return 0;
}
