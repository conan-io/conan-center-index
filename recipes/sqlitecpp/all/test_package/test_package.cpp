#include <cstdlib>
#include <iostream>
#include <SQLiteCpp/SQLiteCpp.h>

int main()
{
    std::cout << "SQLite3 version " << SQLite::VERSION << " (" << SQLite::getLibVersion() << ")" << std::endl;
    return EXIT_SUCCESS;
}
