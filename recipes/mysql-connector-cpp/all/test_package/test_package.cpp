#include <iostream>
#if USING_JDBC
    #include <mysql/jdbc.h>
#else
    #include <mysqlx/xdevapi.h>
#endif

int main() {
    #if USING_JDBC
        auto driver = sql::mysql::get_mysql_driver_instance();
        std::cout << "MySQL JDBC connector cpp works" << std::endl;
    #else
        using namespace mysqlx::abi2::r0;
        Session sess("localhost", 33060, "user", "password");
        std::cout << "MySQL xdevapi connector cpp works" << std::endl;
    #endif
    return 0;
}
