#include <iostream>
#ifdef FAKER_CXX_2
    #include "faker-cxx/Internet.h"
    #include "faker-cxx/String.h"
    #include "faker-cxx/Date.h"
#else
    #include "faker-cxx/internet.h"
    #include "faker-cxx/string.h"
    #include "faker-cxx/date.h"
#endif

int main()
{
    const auto id = faker::string::uuid();
    const auto email = faker::internet::email();
    const auto password = faker::internet::password();
    const auto createdAt = faker::date::pastDate(5, faker::date::DateFormat::ISO);
    const auto updatedAt = faker::date::recentDate(2, faker::date::DateFormat::ISO);

    std::cout << "id: " << id << ", email: " << email << ", password: " <<  password << ", createdAt: " << createdAt << ", updatedAt: " << updatedAt << "\n";

    return 0;
}
