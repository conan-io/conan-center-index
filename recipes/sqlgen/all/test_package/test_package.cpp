#include <sqlgen.hpp>
#ifdef TEST_SQLITE3_ENABLED
#include <sqlgen/sqlite.hpp>
#endif
#ifdef TEST_MYSQL_ENABLED
#include <sqlgen/mysql.hpp>
#endif
#ifdef TEST_POSTGRES_ENABLED
#include <sqlgen/postgres.hpp>
#endif

#include <iostream>
struct Person {
    int id;
    std::string first_name;
    std::string last_name;
    int age;
};

int main() {
   using namespace sqlgen;
   using namespace sqlgen::literals;

   // Define a query
   const auto query = sqlgen::read<std::vector<Person>> |
                      where("age"_c < 18 and "first_name"_c != "Hugo") |
                      order_by("age"_c);

    #ifdef TEST_SQLITE3_ENABLED
    std::cout << "sqlite: " << sqlgen::sqlite::to_sql(query) << std::endl;
    #endif
    #ifdef TEST_MYSQL_ENABLED
    std::cout << "mysql: " << sqlgen::mysql::to_sql(query) << std::endl;
    #endif
    #ifdef TEST_POSTGRES_ENABLED
    std::cout << "postgress: " << sqlgen::postgres::to_sql(query) << std::endl;
    #endif

    return 0;
}
