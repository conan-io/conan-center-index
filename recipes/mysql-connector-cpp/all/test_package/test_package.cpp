#include <cstdlib>
#include <iostream>

#include <mysqlx/xdevapi.h>


int main() {
    auto driver = sql::mysql::get_mysql_driver_instance();
    std::cout << "MySQL connector cpp works" << std::endl;

    return EXIT_SUCCESS;
}
