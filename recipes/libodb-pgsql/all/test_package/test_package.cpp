#include <odb/pgsql/version.hxx>
#include <odb/pgsql/traits.hxx>
#include <odb/pgsql/database.hxx>

#include <cassert>
#include <iostream>

int main()
{
    unsigned int maj = LIBODB_PGSQL_VERSION / 100000;
    unsigned int min = (LIBODB_PGSQL_VERSION / 1000) % 100;

    std::cout << "libodb-pgsql version: " << maj << "." << min << std::endl;

    assert(maj == 2);

    // odb::pgsql::database constructor is NOT called here — that would require
    // a running PostgreSQL instance. We just verify the header compiles and the
    // type is accessible.
    (void)sizeof(odb::pgsql::database);

    return 0;
}
