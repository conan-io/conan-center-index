#include <iostream>
#include <mysql/jdbc.h>
#include <jdbc/mysql_driver.h>
#include <jdbc/cppconn/driver.h>
#include <jdbc/cppconn/exception.h>

int main() {
          auto driver = sql::mysql::get_mysql_driver_instance();
          std::cout << "MySQL connector cpp works" << std::endl;
    return 0;
}
