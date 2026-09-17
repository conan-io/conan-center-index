#include <odb/version.hxx>
#include <odb/exception.hxx>
#include <odb/database.hxx>

#include <cassert>
#include <iostream>

int main()
{
    unsigned int maj = ODB_VERSION / 100000;
    unsigned int min = (ODB_VERSION / 1000) % 100;

    std::cout << "libodb version: " << maj << "." << min << std::endl;

    assert(maj == 2);

    return 0;
}
