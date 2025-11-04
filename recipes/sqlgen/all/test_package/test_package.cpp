#include <sqlgen.hpp>
#ifdef TEST_SQLITE_ENABLED
#include <sqlgen/sqlite.hpp>
#endif
#ifdef TEST_MYSQL_ENABLED
#include <sqlgen/mysql.hpp>
#endif
#ifdef TEST_POSTGRES_ENABLED
#include <sqlgen/postgres.hpp>
#endif

#include <iostream>

int main() {
    // TODO: Example that does not try to connect
    return 0;
}
