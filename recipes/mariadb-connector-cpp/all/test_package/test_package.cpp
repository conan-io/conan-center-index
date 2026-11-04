#include <iostream>
#include <mariadb/conncpp.hpp>

int main (int argc, char *argv[])
{
    sql::Driver* driver = sql::mariadb::get_driver_instance();
    sql::Properties properties({{"user", "test"}, {"password", "test"}});


    return 0;
}
