#include "Poco/Data/SQLite/Utility.h"
#include <iostream>

int main()  {
    const auto threadMode = Poco::Data::SQLite::Utility::getThreadMode();
    std::cout << "Poco Data SQLite (Thread Mode): " << threadMode << std::endl;
    return 0;
}
